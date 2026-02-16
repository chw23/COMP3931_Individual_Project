import logging
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

# Graph state - initialized on first use
_graph_state = {
    "tgs": None,  # OrderedEdgeList
    "tg": None,   # IncidentLists
    "ti": None,   # TimeInterval
    "loaded": False
}


def load_graph(filepath: str = "../cached_datasets/tgbl_flight_filtered.tg"):
    """Load the temporal graph data if not already loaded."""
    if _graph_state["loaded"]:
        return
    
    logging.info(f"Loading temporal graph from {filepath}...")
    _graph_state["tgs"] = tgl.load_ordered_edge_list(filepath)
    _graph_state["tg"] = tgl.to_incident_lists(_graph_state["tgs"])
    _graph_state["ti"] = _graph_state["tgs"].getTimeInterval()
    _graph_state["loaded"] = True
    logging.info("Graph loaded successfully!")


def get_internal_node_id(original_id: int) -> Optional[int]:
    """Convert original node ID to internal ID."""
    node_map = _graph_state["tgs"].getNodeMap()
    return node_map.get(original_id)


def get_original_node_id(internal_id: int) -> Optional[int]:
    """Convert internal node ID to original ID."""
    reverse_map = _graph_state["tgs"].getReverseNodeMap()
    if internal_id < len(reverse_map):
        return reverse_map[internal_id]
    return None


def format_path_result(path, algorithm_name: str) -> str:
    """Format the path result into human-readable text."""
    if len(path) == 0:
        return "No path found between the specified airports within the given time interval."
    
    result = f"Found {algorithm_name} with {len(path)} flight(s):\n"
    for i, edge in enumerate(path, 1):
        # edge contains: u (source), v (dest), t (timestamp), tt (transition time)
        src_original = get_original_node_id(edge.u)
        dst_original = get_original_node_id(edge.v)
        result += f"  Flight {i}: Airport {src_original} → Airport {dst_original} "
        result += f"(Departure: {edge.t}, Duration: {edge.tt}s)\n"
    return result


# =============================================================================
# Tool Definitions - Using @tool decorator from langchain_core.tools
# =============================================================================

@tool
def minimum_duration_path(start_airport: int, target_airport: int) -> str:
    """
    Find the path that minimizes total travel time between two airports.
    Use this when user wants the fastest/quickest route considering all time.
    
    Args:
        start_airport: The origin airport node ID
        target_airport: The destination airport node ID
    """
    load_graph()
    
    start_internal = get_internal_node_id(start_airport)
    target_internal = get_internal_node_id(target_airport)
    
    if start_internal is None:
        return f"Error: Airport {start_airport} not found in the dataset."
    if target_internal is None:
        return f"Error: Airport {target_airport} not found in the dataset."
    
    path = tgl.minimum_duration_path(
        _graph_state["tg"], 
        start_internal, 
        target_internal, 
        _graph_state["ti"]
    )
    return format_path_result(path, "minimum duration path")


@tool
def earliest_arrival_path(start_airport: int, target_airport: int) -> str:
    """
    Find the path that arrives at the destination as early as possible.
    Use this when user wants to arrive at destination the soonest.
    
    Args:
        start_airport: The origin airport node ID
        target_airport: The destination airport node ID
    """
    load_graph()
    
    start_internal = get_internal_node_id(start_airport)
    target_internal = get_internal_node_id(target_airport)
    
    if start_internal is None:
        return f"Error: Airport {start_airport} not found in the dataset."
    if target_internal is None:
        return f"Error: Airport {target_airport} not found in the dataset."
    
    path = tgl.earliest_arrival_path(
        _graph_state["tg"], 
        start_internal, 
        target_internal, 
        _graph_state["ti"]
    )
    return format_path_result(path, "earliest arrival path")


@tool
def minimum_transition_time_path(start_airport: int, target_airport: int) -> str:
    """
    Find the path that minimizes total time spent in transit/layovers.
    Use this when user wants to minimize waiting time between connections.
    
    Args:
        start_airport: The origin airport node ID
        target_airport: The destination airport node ID
    """
    load_graph()
    
    start_internal = get_internal_node_id(start_airport)
    target_internal = get_internal_node_id(target_airport)
    
    if start_internal is None:
        return f"Error: Airport {start_airport} not found in the dataset."
    if target_internal is None:
        return f"Error: Airport {target_airport} not found in the dataset."
    
    path = tgl.minimum_transition_time_path(
        _graph_state["tg"], 
        start_internal, 
        target_internal, 
        _graph_state["ti"]
    )
    return format_path_result(path, "minimum transition time path")


@tool
def minimum_hops_path(start_airport: int, target_airport: int) -> str:
    """
    Find the path with the fewest number of flights/connections.
    Use this when user wants fewest stops, layovers, or transfers.
    
    Args:
        start_airport: The origin airport node ID
        target_airport: The destination airport node ID
    """
    load_graph()
    
    start_internal = get_internal_node_id(start_airport)
    target_internal = get_internal_node_id(target_airport)
    
    if start_internal is None:
        return f"Error: Airport {start_airport} not found in the dataset."
    if target_internal is None:
        return f"Error: Airport {target_airport} not found in the dataset."
    
    path = tgl.minimum_hops_path(
        _graph_state["tg"], 
        start_internal, 
        target_internal, 
        _graph_state["ti"]
    )
    return format_path_result(path, "minimum hops path")


# =============================================================================
# Agent Setup
# =============================================================================

# Collect all tools in a list
tools = [
    minimum_duration_path,
    earliest_arrival_path,
    minimum_transition_time_path,
    minimum_hops_path
]

# Model setup
model = ChatOllama(
    model="llama3.1:8b",
    temperature=0.0,  # Lower temperature for more deterministic tool selection
    num_predict=512,
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

Algorithm Selection Rules:
- If user wants "fastest", "quickest", or "minimum travel time" → use minimum_duration_path
- If user wants to "arrive early/soonest" or "earliest arrival" → use earliest_arrival_path
- If user wants "least waiting", "minimal layovers", or "shortest transitions" → use minimum_transition_time_path
- If user wants "fewest stops", "direct", "least connections", or "fewest flights" → use minimum_hops_path

Always extract the source and destination airport IDs from the query and call the appropriate tool.
After receiving the tool result, provide a clear, natural language summary to the user."""

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

def run_interactive():
    print("=" * 60)
    print("Flight Path Analyzer with Temporal Graph Analysis")
    print("=" * 60)
    print("\nExamples of queries you can ask:")
    print("  - 'Find the fastest route from airport 17308 to 54417'")
    print("  - 'I need to arrive at airport 54417 as early as possible from 17308'")
    print("  - 'What's the route with fewest stops from 17308 to 54417?'")
    print("\nType 'quit' or 'exit' to stop.\n")
    
    # Thread ID for conversation memory - each session gets a unique thread
    config = {"configurable": {"thread_id": "flight_session_1"}}
    
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
    run_interactive()
