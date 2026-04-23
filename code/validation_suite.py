"""
Standalone validation suite for implementation claims in Section 3.

This script is separate from existing demo scripts and focuses on four validation subjects:
1) Reproducing reference minimum-path outputs from the TGLib paper example dataset.
2) Unit tests on path algorithms with handcrafted known-answer inputs.
3) Dataset pipeline integrity checks (ordering + expected node/edge counts from manifest).
4) Labelled query interpretation tests that route to the expected algorithm/tool.

Run:
  python code/validation_suite.py

Optional arguments:
  --queries code/validation_queries.json
  --output cached_datasets/validation_results.json
  --dataset-choice 1
"""

from __future__ import annotations

import argparse
import json
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pytglib as tgl


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_QUERIES = PROJECT_ROOT / "code" / "validation_queries.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "cached_datasets" / "validation_results.json"
MANIFEST_PATH = PROJECT_ROOT / "cached_datasets" / "monthly_subgraphs" / "manifest.json"
MONTHLY_DIR = PROJECT_ROOT / "cached_datasets" / "monthly_subgraphs"
WU_EXAMPLE_FILE = PROJECT_ROOT / "tglib" / "example_datasets" / "example_from_paper.tg"


@dataclass
class SuiteResult:
    name: str
    justification: str
    passed: bool
    checks_passed: int
    checks_total: int
    details: List[Dict[str, Any]]


def _as_path_tuples(path: Iterable[Any]) -> List[Tuple[int, int, int, int]]:
    return [(int(edge.u), int(edge.v), int(edge.t), int(edge.tt)) for edge in path]


def _as_int_list(vector_like: Iterable[Any]) -> List[int]:
    return [int(value) for value in vector_like]


def _internal_id_for_original(tgs: Any, original_id: int) -> int:
    node_map = tgs.getNodeMap()
    if original_id not in node_map:
        raise ValueError(f"Original node ID {original_id} not found in graph")
    return int(node_map[original_id])


def _evaluate_check(
    name: str,
    expected: Any,
    actual: Any,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    passed = actual == expected
    result = {
        "name": name,
        "passed": passed,
        "expected": expected,
        "actual": actual,
    }
    if context:
        result["context"] = context
    return result


def validate_wu_reference_results() -> SuiteResult:
    """
    Reproduce known expected outputs from the TGLib paper example dataset.

    Justification:
    This validates algorithmic correctness against trusted reference outputs,
    not just against self-generated baselines.
    """
    tgs = tgl.load_ordered_edge_list(str(WU_EXAMPLE_FILE))
    tg = tgl.to_incident_lists(tgs)
    ti = tgs.getTimeInterval()

    checks: List[Dict[str, Any]] = []

    md_path = _as_path_tuples(tgl.minimum_duration_path(tg, 0, 2, ti))
    ea_path = _as_path_tuples(tgl.earliest_arrival_path(tg, 0, 2, ti))
    mt_path = _as_path_tuples(tgl.minimum_transition_time_path(tg, 0, 2, ti))

    md_dist = _as_int_list(tgl.minimum_durations(tgs, 0, ti))
    ea_dist = _as_int_list(tgl.earliest_arrival_times(tgs, 0, ti))
    mt_dist = _as_int_list(tgl.minimum_transition_times(tgs, 0, ti))

    checks.append(
        _evaluate_check(
            "minimum_duration_path_0_to_2",
            [(0, 1, 5, 2), (1, 2, 7, 2)],
            md_path,
        )
    )
    checks.append(
        _evaluate_check(
            "earliest_arrival_path_0_to_2",
            [(0, 2, 1, 5)],
            ea_path,
        )
    )
    checks.append(
        _evaluate_check(
            "minimum_transition_time_path_0_to_2",
            [(0, 1, 2, 1), (1, 2, 7, 2)],
            mt_path,
        )
    )
    checks.append(_evaluate_check("minimum_durations_from_0", [0, 1, 4, 7], md_dist))
    checks.append(_evaluate_check("earliest_arrival_times_from_0", [0, 3, 6, 8], ea_dist))
    checks.append(_evaluate_check("minimum_transition_times_from_0", [0, 1, 3, 7], mt_dist))

    passed = all(check["passed"] for check in checks)
    return SuiteResult(
        name="wu_reference_results",
        justification=(
            "Reproduces canonical outputs from TGLib's paper example so correctness "
            "is tied to established reference behaviour."
        ),
        passed=passed,
        checks_passed=sum(1 for check in checks if check["passed"]),
        checks_total=len(checks),
        details=checks,
    )


def _run_algorithms_for_case(
    tg_lines: List[str],
    start_original: int,
    target_original: int,
) -> Dict[str, List[Tuple[int, int, int, int]]]:
    with tempfile.NamedTemporaryFile("w", suffix=".tg", delete=False, encoding="utf-8") as tmp:
        for line in tg_lines:
            tmp.write(line.strip() + "\n")
        tmp_path = Path(tmp.name)

    try:
        tgs = tgl.load_ordered_edge_list(str(tmp_path))
        tg = tgl.to_incident_lists(tgs)
        ti = tgs.getTimeInterval()

        start = _internal_id_for_original(tgs, start_original)
        target = _internal_id_for_original(tgs, target_original)

        return {
            "minimum_duration_path": _as_path_tuples(tgl.minimum_duration_path(tg, start, target, ti)),
            "earliest_arrival_path": _as_path_tuples(tgl.earliest_arrival_path(tg, start, target, ti)),
            "minimum_transition_time_path": _as_path_tuples(
                tgl.minimum_transition_time_path(tg, start, target, ti)
            ),
            "minimum_hops_path": _as_path_tuples(tgl.minimum_hops_path(tg, start, target, ti)),
        }
    finally:
        tmp_path.unlink(missing_ok=True)


def validate_path_algorithm_unit_cases() -> SuiteResult:
    """
    Unit tests with known-answer handcrafted temporal graphs.

    Justification:
    Handcrafted cases isolate edge conditions and objective differences,
    allowing direct verification of each path definition.
    """
    cases = [
        {
            "name": "earliest_vs_fastest_diverge",
            "graph": [
                "0 1 0 10",
                "0 2 9 1",
                "2 1 10 1",
            ],
            "start": 0,
            "target": 1,
            "expected": {
                "minimum_duration_path": [(0, 2, 9, 1), (2, 1, 10, 1)],
                "earliest_arrival_path": [(0, 1, 0, 10)],
            },
            "justification": "Separates earliest-arrival objective from fastest-duration objective.",
        },
        {
            "name": "min_transition_vs_min_hops_diverge",
            "graph": [
                "0 1 0 100",
                "0 2 0 1",
                "2 1 2 1",
            ],
            "start": 0,
            "target": 1,
            "expected": {
                "minimum_transition_time_path": [(0, 2, 0, 1), (2, 1, 2, 1)],
                "minimum_hops_path": [(0, 1, 0, 100)],
            },
            "justification": "Separates transition-time minimisation from hop-count minimisation.",
        },
        {
            "name": "unreachable_target_returns_empty_path",
            "graph": [
                "0 1 0 1",
                "2 2 0 1",
            ],
            "start": 0,
            "target": 2,
            "expected": {
                "minimum_duration_path": [],
                "earliest_arrival_path": [],
                "minimum_transition_time_path": [],
                "minimum_hops_path": [],
            },
            "justification": "Checks no-path handling to avoid false positives in disconnected temporal states.",
        },
        {
            "name": "single_edge_base_case",
            "graph": [
                "0 1 5 3",
            ],
            "start": 0,
            "target": 1,
            "expected": {
                "minimum_duration_path": [(0, 1, 5, 3)],
                "earliest_arrival_path": [(0, 1, 5, 3)],
                "minimum_transition_time_path": [(0, 1, 5, 3)],
                "minimum_hops_path": [(0, 1, 5, 3)],
            },
            "justification": "Confirms all path variants return the same result in the simplest valid graph.",
        },
    ]

    checks: List[Dict[str, Any]] = []
    for case in cases:
        actual = _run_algorithms_for_case(case["graph"], case["start"], case["target"])
        for algo_name, expected_value in case["expected"].items():
            checks.append(
                _evaluate_check(
                    f"{case['name']}::{algo_name}",
                    expected_value,
                    actual[algo_name],
                    context={"case_justification": case["justification"]},
                )
            )

    passed = all(check["passed"] for check in checks)
    return SuiteResult(
        name="path_algorithm_unit_cases",
        justification=(
            "Uses known-answer micro-graphs to verify each algorithm objective and boundary behaviour "
            "under controlled conditions."
        ),
        passed=passed,
        checks_passed=sum(1 for check in checks if check["passed"]),
        checks_total=len(checks),
        details=checks,
    )


def _month_key_from_filename(filename: str) -> str:
    # Example: 2022-06_top50_lcc.tg -> 2022-06
    return filename.split("_")[0]


def validate_dataset_pipeline_integrity() -> SuiteResult:
    """
    Verify generated monthly subgraphs preserve temporal ordering and manifest counts.

    Justification:
    Confirms the data pipeline outputs remain structurally correct and reproducible,
    supporting all downstream analysis validity.
    """
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    expected_by_month = {entry["month"]: entry for entry in manifest["windows"]}

    checks: List[Dict[str, Any]] = []
    tg_files = sorted(path for path in MONTHLY_DIR.glob("*_top50_lcc.tg") if path.is_file())

    for tg_file in tg_files:
        month_key = _month_key_from_filename(tg_file.name)
        expected = expected_by_month.get(month_key)

        if expected is None:
            checks.append(
                {
                    "name": f"{tg_file.name}::manifest_entry_exists",
                    "passed": False,
                    "expected": "manifest entry present",
                    "actual": "missing",
                }
            )
            continue

        edge_count = 0
        nodes = set()
        monotonic = True
        invalid_format_lines = 0
        non_positive_tt_lines = 0
        prev_timestamp: Optional[int] = None

        with tg_file.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                stripped = line.strip()
                if not stripped:
                    continue
                parts = stripped.split()
                if len(parts) != 4:
                    invalid_format_lines += 1
                    continue

                try:
                    u = int(parts[0])
                    v = int(parts[1])
                    t = int(parts[2])
                    tt = int(parts[3])
                except ValueError:
                    invalid_format_lines += 1
                    continue

                edge_count += 1
                nodes.add(u)
                nodes.add(v)

                if tt <= 0:
                    non_positive_tt_lines += 1

                if prev_timestamp is not None and t < prev_timestamp:
                    monotonic = False
                prev_timestamp = t

        checks.append(
            _evaluate_check(
                f"{tg_file.name}::temporal_order_non_decreasing",
                True,
                monotonic,
            )
        )
        checks.append(
            _evaluate_check(
                f"{tg_file.name}::edge_count_matches_manifest",
                int(expected["final_edges"]),
                edge_count,
            )
        )
        checks.append(
            _evaluate_check(
                f"{tg_file.name}::node_count_matches_manifest",
                int(expected["lcc_nodes"]),
                len(nodes),
            )
        )
        checks.append(
            _evaluate_check(
                f"{tg_file.name}::valid_line_format",
                0,
                invalid_format_lines,
                context={"note": "Each line must contain 4 integers: u v t tt."},
            )
        )
        checks.append(
            _evaluate_check(
                f"{tg_file.name}::positive_transition_time",
                0,
                non_positive_tt_lines,
                context={"note": "Transition times must be positive for meaningful traversal."},
            )
        )

    passed = all(check["passed"] for check in checks)
    return SuiteResult(
        name="dataset_pipeline_integrity",
        justification=(
            "Checks that cached monthly subgraphs preserve ordering and declared size constraints, "
            "which validates preprocessing reliability."
        ),
        passed=passed,
        checks_passed=sum(1 for check in checks if check["passed"]),
        checks_total=len(checks),
        details=checks,
    )


def _extract_tool_calls_from_agent_response(agent_response: Any) -> List[Dict[str, Any]]:
    """Extract tool call names/args from LangChain agent response messages."""
    calls: List[Dict[str, Any]] = []

    messages = agent_response.get("messages", []) if isinstance(agent_response, dict) else []
    for message in messages:
        message_tool_calls = None

        if isinstance(message, dict):
            message_tool_calls = message.get("tool_calls")
        else:
            message_tool_calls = getattr(message, "tool_calls", None)

        if not message_tool_calls:
            continue

        for call in message_tool_calls:
            if isinstance(call, dict):
                call_name = call.get("name")
                call_args = call.get("args")
            else:
                call_name = getattr(call, "name", None)
                call_args = getattr(call, "args", None)

            calls.append(
                {
                    "name": call_name,
                    "args": call_args,
                }
            )

    return calls


def _find_reachable_original_pair(llama_module: Any, tool_name: str, scan_limit: int = 12) -> Optional[Tuple[str, str]]:
    tgs = llama_module._graph_state["tgs"]
    tg = llama_module._graph_state["tg"]
    ti = llama_module._graph_state["ti"]

    reverse_map = tgs.getReverseNodeMap()
    n = min(int(len(reverse_map)), int(scan_limit))

    if tool_name == "minimum_duration_path":
        fn = tgl.minimum_duration_path
    elif tool_name == "earliest_arrival_path":
        fn = tgl.earliest_arrival_path
    elif tool_name == "minimum_transition_time_path":
        fn = tgl.minimum_transition_time_path
    elif tool_name == "minimum_hops_path":
        fn = tgl.minimum_hops_path
    else:
        return None

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            path = fn(tg, i, j, ti)
            if len(path) > 0:
                return str(int(reverse_map[i])), str(int(reverse_map[j]))
    return None


def validate_labelled_query_routing(
    queries_path: Path,
    dataset_choice: int = 1,
) -> SuiteResult:
    """
    Validate labelled natural-language query routing and tool invocation.

    Justification:
    Uses labelled prompts to verify tool selection from actual LLM agent behaviour,
    then invokes the selected tool where runtime is practical.
    """
    query_items = json.loads(queries_path.read_text(encoding="utf-8"))

    import llama as llama_module

    llama_module.set_active_dataset(dataset_choice)
    llama_module.load_graph()

    tool_registry = {tool.name: tool for tool in llama_module.tools}

    reachable_pairs: Dict[str, Optional[Tuple[str, str]]] = {}
    for tool_name in [
        "minimum_duration_path",
        "earliest_arrival_path",
        "minimum_transition_time_path",
        "minimum_hops_path",
    ]:
        reachable_pairs[tool_name] = _find_reachable_original_pair(llama_module, tool_name)

    checks: List[Dict[str, Any]] = []

    for item in query_items:
        query_id = item["id"]
        query_text = item["query"]
        expected_tool = item["expected_tool"]
        should_invoke = bool(item.get("invoke", False))

        tool_calls: List[Dict[str, Any]] = []
        llm_error: Optional[str] = None
        predicted_tool: Optional[str] = None

        try:
            config = {"configurable": {"thread_id": f"validation_query_{dataset_choice}_{query_id}"}}
            response = llama_module.agent.invoke(
                {"messages": [{"role": "user", "content": query_text}]},
                config,
            )
            tool_calls = _extract_tool_calls_from_agent_response(response)
            if tool_calls:
                predicted_tool = tool_calls[0].get("name")
        except Exception as exc:  # pragma: no cover - runtime/env dependent
            llm_error = f"{type(exc).__name__}: {exc}"

        routing_pass = predicted_tool == expected_tool

        invocation_pass = True
        invocation_note = "skipped"

        if llm_error is not None:
            invocation_pass = False
            invocation_note = "agent_invoke_exception"
        elif should_invoke and routing_pass and predicted_tool is not None:
            tool_obj = tool_registry.get(predicted_tool)
            if tool_obj is None:
                invocation_pass = False
                invocation_note = f"tool_not_found:{predicted_tool}"
            else:
                try:
                    if predicted_tool in (
                        "minimum_duration_path",
                        "earliest_arrival_path",
                        "minimum_transition_time_path",
                        "minimum_hops_path",
                    ):
                        pair = reachable_pairs.get(predicted_tool)
                        if pair is None:
                            invocation_pass = False
                            invocation_note = "no_reachable_pair_found"
                        else:
                            start_original, target_original = pair
                            output = tool_obj.invoke(
                                {
                                    "start_airport": start_original,
                                    "target_airport": target_original,
                                }
                            )
                            invocation_pass = isinstance(output, str) and not output.startswith("Error:")
                            invocation_note = "ok" if invocation_pass else "tool_returned_error"
                    else:
                        output = tool_obj.invoke({})
                        invocation_pass = isinstance(output, str) and len(output.strip()) > 0
                        invocation_note = "ok" if invocation_pass else "empty_output"
                except Exception as exc:  # pragma: no cover - defensive runtime guard
                    invocation_pass = False
                    invocation_note = f"exception:{type(exc).__name__}"
        elif should_invoke and not routing_pass:
            invocation_note = "not_attempted_routing_mismatch"

        checks.append(
            {
                "name": f"{query_id}::routing_and_invocation",
                "passed": bool(routing_pass and invocation_pass),
                "expected": expected_tool,
                "actual": predicted_tool,
                "context": {
                    "query": query_text,
                    "routing_pass": routing_pass,
                    "invocation_attempted": should_invoke,
                    "invocation_pass": invocation_pass,
                    "invocation_note": invocation_note,
                    "tool_calls": tool_calls,
                    "llm_error": llm_error,
                    "justification": item.get("justification", ""),
                },
            }
        )

    passed = all(check["passed"] for check in checks)
    return SuiteResult(
        name="labelled_query_routing",
        justification=(
            "Assesses query-to-algorithm interpretation against labelled intents and validates that selected "
            "tools can be invoked with valid dataset nodes."
        ),
        passed=passed,
        checks_passed=sum(1 for check in checks if check["passed"]),
        checks_total=len(checks),
        details=checks,
    )


def run_all_suites(queries_path: Path, dataset_choice: int) -> Dict[str, Any]:
    suites = [
        validate_wu_reference_results(),
        validate_path_algorithm_unit_cases(),
        validate_dataset_pipeline_integrity(),
        validate_labelled_query_routing(queries_path=queries_path, dataset_choice=dataset_choice),
    ]

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_root": str(PROJECT_ROOT),
        "overall_passed": all(suite.passed for suite in suites),
        "suites": [asdict(suite) for suite in suites],
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Run standalone validation suite.")
    parser.add_argument(
        "--queries",
        type=Path,
        default=DEFAULT_QUERIES,
        help="Path to labelled query JSON file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Path to output JSON report.",
    )
    parser.add_argument(
        "--dataset-choice",
        type=int,
        default=1,
        help="Dataset choice used for tool invocation checks (1-10).",
    )

    args = parser.parse_args()

    if not args.queries.exists():
        raise FileNotFoundError(f"Labelled query file not found: {args.queries}")

    if args.dataset_choice < 1 or args.dataset_choice > 10:
        raise ValueError("--dataset-choice must be between 1 and 10")

    results = run_all_suites(queries_path=args.queries, dataset_choice=args.dataset_choice)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print("Validation run completed.")
    print(f"Overall passed: {results['overall_passed']}")
    print(f"Result file: {args.output}")

    for suite in results["suites"]:
        print(
            f"- {suite['name']}: {suite['checks_passed']}/{suite['checks_total']} checks passed "
            f"(passed={suite['passed']})"
        )

    return 0 if results["overall_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
