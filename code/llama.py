import logging
import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

import pytglib as tgl

logging.basicConfig(level=logging.INFO)

# =============================================================================
# Global Graph Data (loaded once at startup)
# =============================================================================

DATASET_FILES = {
    1: "2021-07_top50_lcc.tg",
    2: "2021-08_top50_lcc.tg",
    3: "2022-03_top50_lcc.tg",
    4: "2022-04_top50_lcc.tg",
    5: "2022-05_top50_lcc.tg",
    6: "2022-06_top50_lcc.tg",
    7: "2022-07_top50_lcc.tg",
    8: "2022-08_top50_lcc.tg",
    9: "2022-09_top50_lcc.tg",
    10: "2022-10_top50_lcc.tg",
}

DATASET_LABELS = {
    1: "July-2021",
    2: "August-2021",
    3: "March-2022",
    4: "April-2022",
    5: "May-2022",
    6: "June-2022",
    7: "July-2022",
    8: "August-2022",
    9: "September-2022",
    10: "October-2022",
}

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MONTHLY_DATASETS_DIR = PROJECT_ROOT / "cached_datasets" / "monthly_subgraphs"
AIRPORT_NODE_FEAT_CSV = PROJECT_ROOT / "tgbl-flight-v2" / "airport_node_feat_v2.csv"

# Graph state - initialized on first use
_graph_state = {
    "tgs": None,  # OrderedEdgeList
    "tg": None,   # IncidentLists
    "ti": None,   # TimeInterval
    "loaded": False,
    "selected_filepath": None,
    "loaded_filepath": None,
    "code_to_original": None,
    "original_to_code": None,
}


def load_airport_code_mapping(mapping_file: Path = AIRPORT_NODE_FEAT_CSV):
    """Load airport code <-> original index mapping from node feature CSV."""
    if _graph_state["code_to_original"] is not None and _graph_state["original_to_code"] is not None:
        return

    if not mapping_file.exists():
        raise FileNotFoundError(f"Airport mapping file not found: {mapping_file}")

    code_to_original = {}
    original_to_code = {}

    with mapping_file.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            code = row.get("airport_code", "").strip().upper()
            if not code:
                continue
            code_to_original[code] = idx
            original_to_code[idx] = code

    _graph_state["code_to_original"] = code_to_original
    _graph_state["original_to_code"] = original_to_code


def get_dataset_filepath(choice: int) -> Path:
    """Resolve a dataset choice (1-10) to a monthly subgraph file path."""
    filename = DATASET_FILES.get(choice)
    if filename is None:
        raise ValueError("Invalid choice. Please select a number between 1 and 10.")
    return MONTHLY_DATASETS_DIR / filename


def set_active_dataset(choice: int) -> Path:
    """Set the active dataset for the current session."""
    selected_path = get_dataset_filepath(choice)
    _graph_state["selected_filepath"] = str(selected_path)
    return selected_path


def load_graph(filepath: Optional[str] = None):
    """Load the temporal graph data for the selected dataset if not already loaded."""
    load_airport_code_mapping()

    target_filepath = filepath or _graph_state["selected_filepath"]
    if target_filepath is None:
        target_filepath = str(get_dataset_filepath(1))

    if _graph_state["loaded"] and _graph_state["loaded_filepath"] == target_filepath:
        return

    _graph_state["tgs"] = None
    _graph_state["tg"] = None
    _graph_state["ti"] = None
    _graph_state["loaded"] = False
    
    logging.info(f"Loading temporal graph from {target_filepath}...")
    _graph_state["tgs"] = tgl.load_ordered_edge_list(target_filepath)
    _graph_state["tg"] = tgl.to_incident_lists(_graph_state["tgs"])
    _graph_state["ti"] = _graph_state["tgs"].getTimeInterval()
    _graph_state["loaded"] = True
    _graph_state["loaded_filepath"] = target_filepath
    logging.info("Graph loaded successfully!")


def get_internal_node_id(original_id: int) -> Optional[int]:
    """Convert original node ID to internal ID."""
    node_map = _graph_state["tgs"].getNodeMap()
    return node_map.get(original_id)


def get_original_id_from_airport(airport_input: str) -> Optional[int]:
    """Convert airport code (or numeric original ID string) to original node ID."""
    if airport_input is None:
        return None

    token = str(airport_input).strip().upper()
    if not token:
        return None

    if token.isdigit():
        return int(token)

    return _graph_state["code_to_original"].get(token)


def get_original_node_id(internal_id: int) -> Optional[int]:
    """Convert internal node ID to original ID."""
    reverse_map = _graph_state["tgs"].getReverseNodeMap()
    if internal_id < len(reverse_map):
        return reverse_map[internal_id]
    return None


def get_airport_code_from_original(original_id: int) -> Optional[str]:
    """Convert original node ID to airport code."""
    return _graph_state["original_to_code"].get(original_id)


def _format_seconds_hhmmss(total_seconds: int) -> str:
    """Format seconds as HH:MM:SS, allowing hours greater than 24."""
    seconds = max(int(total_seconds), 0)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def _format_unix_timestamp_utc(unix_seconds: int) -> str:
    """Format a Unix timestamp into UTC date-time text."""
    dt = datetime.fromtimestamp(int(unix_seconds), tz=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def _path_waiting_seconds(path) -> int:
    """Return total waiting/layover time between consecutive flights in a path."""
    waiting = 0
    for current_edge, next_edge in zip(path, path[1:]):
        current_arrival = current_edge.t + current_edge.tt
        waiting += max(0, next_edge.t - current_arrival)
    return waiting


def _path_elapsed_seconds(path) -> int:
    """Return elapsed journey time from first departure to final arrival."""
    if len(path) == 0:
        return 0
    first_departure = path[0].t
    final_arrival = path[-1].t + path[-1].tt
    return max(0, final_arrival - first_departure)


def format_path_result(path, algorithm_name: str) -> str:
    """Format the path result into human-readable text."""
    if len(path) == 0:
        return "No path found between the specified airports within the given time interval."

    in_flight_seconds = _path_duration_seconds(path)
    waiting_seconds = _path_waiting_seconds(path)
    elapsed_seconds = _path_elapsed_seconds(path)

    result = f"Found {algorithm_name} with {len(path)} flight(s):\n"
    for i, edge in enumerate(path, 1):
        # edge contains: u (source), v (dest), t (timestamp), tt (transition time)
        src_original = get_original_node_id(edge.u)
        dst_original = get_original_node_id(edge.v)
        src_code = get_airport_code_from_original(src_original) or "UNKNOWN"
        dst_code = get_airport_code_from_original(dst_original) or "UNKNOWN"
        arrival_time = edge.t + edge.tt
        departure_utc = _format_unix_timestamp_utc(edge.t)
        arrival_utc = _format_unix_timestamp_utc(arrival_time)
        result += f"  Flight {i}: {src_code} ({src_original}) → {dst_code} ({dst_original}) "
        result += (
            f"(Departure: {edge.t} [{departure_utc}], Arrival: {arrival_time} [{arrival_utc}], "
            f"Duration: {edge.tt}s / {_format_seconds_hhmmss(edge.tt)})\n"
        )

    first_departure = path[0].t
    final_arrival = path[-1].t + path[-1].tt

    result += (
        "\nJourney timing summary:\n"
        f"  - First departure: {first_departure} ({_format_unix_timestamp_utc(first_departure)})\n"
        f"  - Final arrival: {final_arrival} ({_format_unix_timestamp_utc(final_arrival)})\n"
        f"  - In-flight time: {in_flight_seconds}s ({_format_seconds_hhmmss(in_flight_seconds)})\n"
        f"  - Waiting/layover time: {waiting_seconds}s ({_format_seconds_hhmmss(waiting_seconds)})\n"
        f"  - Total elapsed time (departure to arrival): {elapsed_seconds}s ({_format_seconds_hhmmss(elapsed_seconds)})"
    )

    return result


def _path_duration_seconds(path) -> int:
    """Return total in-flight duration for a path (sum of edge transition times)."""
    return sum(edge.tt for edge in path)


def _nodes_in_path(start_internal: int, path) -> list[int]:
    """Return node sequence visited by a path, including the start node."""
    nodes = [start_internal]
    for edge in path:
        nodes.append(edge.v)
    return nodes


def _find_fastest_path_to_any_target(start_internal: int, candidate_targets: set[int]):
    """Find fastest (minimum-duration) path from start to any candidate target.

    Returns:
        tuple[target_internal | None, path]
    """
    best_target = None
    best_path = []
    best_score = None

    for target_internal in sorted(candidate_targets):
        if target_internal == start_internal:
            continue

        path = tgl.minimum_duration_path(
            _graph_state["tg"],
            start_internal,
            target_internal,
            _graph_state["ti"],
        )
        if len(path) == 0:
            continue

        score = (_path_duration_seconds(path), len(path), target_internal)
        if best_score is None or score < best_score:
            best_score = score
            best_target = target_internal
            best_path = path

    return best_target, best_path


# =============================================================================
# Tool Definitions - Using @tool decorator from langchain_core.tools
# =============================================================================

@tool
def minimum_duration_path(start_airport: str, target_airport: str) -> str:
    """
    Find the path that minimizes total travel time between two airports.
    Use this when user wants the fastest/quickest route considering all time.
    
    Args:
        start_airport: Origin airport code (e.g., VHHH)
        target_airport: Destination airport code (e.g., EGCC)
    """
    load_graph()
    
    start_original = get_original_id_from_airport(start_airport)
    target_original = get_original_id_from_airport(target_airport)

    if start_original is None:
        return f"Error: Airport '{start_airport}' not found in the airport mapping."
    if target_original is None:
        return f"Error: Airport '{target_airport}' not found in the airport mapping."

    start_internal = get_internal_node_id(start_original)
    target_internal = get_internal_node_id(target_original)
    
    if start_internal is None:
        return f"Error: Airport '{start_airport}' (original ID {start_original}) is not present in the selected dataset."
    if target_internal is None:
        return f"Error: Airport '{target_airport}' (original ID {target_original}) is not present in the selected dataset."
    
    path = tgl.minimum_duration_path(
        _graph_state["tg"], 
        start_internal, 
        target_internal, 
        _graph_state["ti"]
    )
    return format_path_result(path, "minimum duration path")


@tool
def earliest_arrival_path(start_airport: str, target_airport: str) -> str:
    """
    Find the path that arrives at the destination as early as possible.
    Use this when user wants to arrive at destination the soonest.
    
    Args:
        start_airport: Origin airport code (e.g., VHHH)
        target_airport: Destination airport code (e.g., EGCC)
    """
    load_graph()
    
    start_original = get_original_id_from_airport(start_airport)
    target_original = get_original_id_from_airport(target_airport)

    if start_original is None:
        return f"Error: Airport '{start_airport}' not found in the airport mapping."
    if target_original is None:
        return f"Error: Airport '{target_airport}' not found in the airport mapping."

    start_internal = get_internal_node_id(start_original)
    target_internal = get_internal_node_id(target_original)
    
    if start_internal is None:
        return f"Error: Airport '{start_airport}' (original ID {start_original}) is not present in the selected dataset."
    if target_internal is None:
        return f"Error: Airport '{target_airport}' (original ID {target_original}) is not present in the selected dataset."
    
    path = tgl.earliest_arrival_path(
        _graph_state["tg"], 
        start_internal, 
        target_internal, 
        _graph_state["ti"]
    )
    return format_path_result(path, "earliest arrival path")


@tool
def minimum_transition_time_path(start_airport: str, target_airport: str) -> str:
    """
    Find the path that minimizes total time spent in transit/layovers.
    Use this when user wants to minimize waiting time between connections.
    
    Args:
        start_airport: Origin airport code (e.g., VHHH)
        target_airport: Destination airport code (e.g., EGCC)
    """
    load_graph()
    
    start_original = get_original_id_from_airport(start_airport)
    target_original = get_original_id_from_airport(target_airport)

    if start_original is None:
        return f"Error: Airport '{start_airport}' not found in the airport mapping."
    if target_original is None:
        return f"Error: Airport '{target_airport}' not found in the airport mapping."

    start_internal = get_internal_node_id(start_original)
    target_internal = get_internal_node_id(target_original)
    
    if start_internal is None:
        return f"Error: Airport '{start_airport}' (original ID {start_original}) is not present in the selected dataset."
    if target_internal is None:
        return f"Error: Airport '{target_airport}' (original ID {target_original}) is not present in the selected dataset."
    
    path = tgl.minimum_transition_time_path(
        _graph_state["tg"], 
        start_internal, 
        target_internal, 
        _graph_state["ti"]
    )
    return format_path_result(path, "minimum transition time path")


@tool
def minimum_hops_path(start_airport: str, target_airport: str) -> str:
    """
    Find the path with the fewest number of flights/connections.
    Use this when user wants fewest stops, layovers, or transfers.
    
    Args:
        start_airport: Origin airport code (e.g., VHHH)
        target_airport: Destination airport code (e.g., EGCC)
    """
    load_graph()
    
    start_original = get_original_id_from_airport(start_airport)
    target_original = get_original_id_from_airport(target_airport)

    if start_original is None:
        return f"Error: Airport '{start_airport}' not found in the airport mapping."
    if target_original is None:
        return f"Error: Airport '{target_airport}' not found in the airport mapping."

    start_internal = get_internal_node_id(start_original)
    target_internal = get_internal_node_id(target_original)
    
    if start_internal is None:
        return f"Error: Airport '{start_airport}' (original ID {start_original}) is not present in the selected dataset."
    if target_internal is None:
        return f"Error: Airport '{target_airport}' (original ID {target_original}) is not present in the selected dataset."
    
    path = tgl.minimum_hops_path(
        _graph_state["tg"], 
        start_internal, 
        target_internal, 
        _graph_state["ti"]
    )
    return format_path_result(path, "minimum hops path")


@tool
def convert_unix_timestamp(timestamp_seconds: int) -> str:
    """
    Convert a Unix timestamp to UTC date-time.

    Args:
        timestamp_seconds: Unix timestamp in seconds.
    """
    try:
        ts = int(timestamp_seconds)
    except (TypeError, ValueError):
        return f"Error: '{timestamp_seconds}' is not a valid integer Unix timestamp."

    try:
        utc_text = _format_unix_timestamp_utc(ts)
    except (OverflowError, OSError, ValueError) as exc:
        return f"Error: Cannot convert timestamp {ts}: {exc}"

    return f"{ts} -> {utc_text}"

@tool
def list_available_airports() -> str:
    """
    List all available airports in the currently loaded dataset.
    This can help users know which airport codes are valid for queries.
    """
    load_graph()
    
    if _graph_state["tgs"] is None:
        return "No graph data loaded. Please load a dataset first."
    
    node_map = _graph_state["tgs"].getNodeMap()
    reverse_map = _graph_state["tgs"].getReverseNodeMap()
    
    airports = []
    for internal_id, original_id in enumerate(reverse_map):
        code = get_airport_code_from_original(original_id) or "UNKNOWN"
        airports.append(f"{code} (original ID: {original_id})")
    
    return "Available airports in the current dataset:\n" + "\n".join(airports)

@tool
def greedy_algo() -> str:
    """
    Cover all nodes using the smallest number of minimum temporal paths.
    Implemented by iterations of TGL's minimum duration path finding methods.
    """
    load_graph()

    if _graph_state["tgs"] is None:
        return "No graph data loaded. Please load a dataset first."

    reverse_map = _graph_state["tgs"].getReverseNodeMap()
    node_count = len(reverse_map)

    if node_count == 0:
        return "The current dataset has no nodes."

    # initialise the list of nodes that have not been visited yet
    uncovered = set(range(node_count))
    routes = []

    while uncovered:
        start = min(uncovered)

        first_target, first_path = _find_fastest_path_to_any_target(start, uncovered)

        if first_target is None:
            uncovered.remove(start)
            routes.append(
                {
                    "start": start,
                    "path": [],
                    "covered_now": {start},
                }
            )
            continue

        route_path = list(first_path)
        route_nodes = set(_nodes_in_path(start, route_path))
        current = first_target

        while True:
            remaining_uncovered = uncovered - route_nodes
            if not remaining_uncovered:
                break

            next_target, extension = _find_fastest_path_to_any_target(current, remaining_uncovered)
            if next_target is None or len(extension) == 0:
                break

            previous_current = current
            route_path.extend(extension)
            route_nodes.update(_nodes_in_path(previous_current, extension))
            current = next_target

        covered_now = uncovered.intersection(route_nodes)
        uncovered -= covered_now

        routes.append(
            {
                "start": start,
                "path": route_path,
                "covered_now": covered_now,
            }
        )

    lines = [
        f"Greedy route cover completed: {len(routes)} route(s) to cover {node_count} node(s).",
        "",
    ]

    for idx, route in enumerate(routes, 1):
        start_internal = route["start"]
        path = route["path"]
        covered_now = route["covered_now"]

        start_original = get_original_node_id(start_internal)
        start_code = get_airport_code_from_original(start_original) or "UNKNOWN"

        if len(path) == 0:
            lines.append(
                f"Route {idx}: {start_code} ({start_original}) [isolated/no reachable uncovered node], "
                f"newly covered nodes: {len(covered_now)}"
            )
            continue

        node_seq = _nodes_in_path(start_internal, path)
        airport_seq = []
        for internal_id in node_seq:
            original_id = get_original_node_id(internal_id)
            code = get_airport_code_from_original(original_id) or "UNKNOWN"
            airport_seq.append(f"{code} ({original_id})")

        lines.append(
            f"Route {idx}: flights={len(path)}, total_duration={_path_duration_seconds(path)}s, "
            f"newly covered nodes={len(covered_now)}"
        )
        lines.append("  " + " -> ".join(airport_seq))

    return "\n".join(lines)


# =============================================================================
# Agent Setup
# =============================================================================

# Collect all tools in a list
tools = [
    minimum_duration_path,
    earliest_arrival_path,
    minimum_transition_time_path,
    minimum_hops_path,
    convert_unix_timestamp,
    list_available_airports,
    greedy_algo
]

# Model setup
model = ChatOllama(
    model="llama3.1:8b",
    temperature=0.0,  # Lower temperature for more deterministic tool selection
    num_ctx=4096,
    base_url="http://localhost:11434"
)

# System prompt for the agent
prompt = """You are an expert flight path analyzer. Your job is to help users find optimal flight routes between airports using temporal graph analysis.

The timestamp structure of the graph is as follows:
- Timestamps are defined with Unix timestamps
- The edges are collected on a daily basis
- The transitional time (tt) is in seconds

You have access to these tools:
- minimum_duration_path: Finds the fastest overall route (minimizes total travel time)
- earliest_arrival_path: Finds the route that gets you there soonest
- minimum_transition_time_path: Finds the route with least layover/waiting time
- minimum_hops_path: Finds the route with fewest connections/stops
- convert_unix_timestamp: Converts Unix timestamps to UTC date-time text
- list_available_airports: Lists all airports available in the currently loaded dataset
- greedy_algo: Covers all graph nodes with greedy concatenations of fastest temporal paths

Algorithm Selection Rules:
- If user wants "fastest", "quickest", or "minimum travel time" → use minimum_duration_path
- If user wants to "arrive early/soonest" or "earliest arrival" → use earliest_arrival_path
- If user wants "least waiting", "minimal layovers", or "shortest transitions" → use minimum_transition_time_path
- If user wants "fewest stops", "direct", "least connections", or "fewest flights" → use minimum_hops_path
- If user asks to cover all airports/nodes with minimum number of fastest temporal routes → use greedy_algo
- If user asks for available airports in the dataset → use list_available_airports
- If user asks to translate/convert timestamps to calendar date-time → use convert_unix_timestamp

Always extract the source and destination airport codes from the query and call the appropriate tool.
After receiving the tool result, provide a clear, natural language summary to the user with time format HH:MM:SS.
For calendar date-time, treat Unix timestamps as UTC and do not infer a date-time without the conversion tool output.
Be concise but informative in your responses. 
If the user query is ambiguous, ask for clarification on which aspect they want to optimize for (e.g., fastest vs earliest arrival). 
Always ensure that the airport codes are valid and present in the dataset before calling the tools.
"""

# Create the agent with checkpointer for short-term memory
agent = create_agent(
    model,
    tools=tools,
    system_prompt=prompt,
    checkpointer=InMemorySaver(),  # Enables short-term memory
)


# =============================================================================
# Interactive Loop
# =============================================================================

def run_interactive(choice: int):
    
    if choice < 1 or choice > 10:
        print("Invalid choice. Please select a number between 1 and 10.")
        return 1
    
    selected_path = set_active_dataset(choice)
    print(f"Running analysis for {DATASET_LABELS[choice]} ({selected_path.name})")
    load_graph()
    print("\nExamples of queries you can ask:")
    print("  - 'Find the fastest route from VHHH to EGCC'")
    print("  - 'I need to arrive at EGCC as early as possible from VHHH'")
    print("  - 'What's the route with fewest stops from VHHH to EGCC?'")
    print("\nType 'quit' or 'exit' to stop.\n")
    
    # Thread ID for conversation memory - each session gets a unique thread
    config = {"configurable": {"thread_id": f"flight_session_{choice}"}}
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            # Run the agent with thread_id for memory persistence
            response = agent.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config  # Pass config with thread_id
            )
            # Get the last AI message
            last_message = response["messages"][-1]
            print(f"\nAssistant: {last_message.content}\n")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            logging.error(f"Error: {str(e)}")
            print(f"Sorry, an error occurred: {str(e)}\n")


if __name__ == "__main__":
    
    print("=" * 60)
    print("Flight Path Analyser with Temporal Graph Analysis")
    print("=" * 60)
    
    print("The following datasets are available for analysis:")
    print("1. July-2021")
    print("2. August-2021")
    print("3. March-2022")
    print("4. April-2022")
    print("5. May-2022")
    print("6. June-2022")
    print("7. July-2022")
    print("8. August-2022")
    print("9. September-2022")
    print("10. October-2022")
    try:
        choice = int(input("Choose the month to analyze (1-10): ").strip())
    except ValueError:
        print("Invalid input. Please enter a number between 1 and 10.")
        raise SystemExit(1)
    
    run_interactive(choice)
