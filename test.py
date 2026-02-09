"""
Temporal graph path analysis using pytglib.

IMPORTANT: pytglib automatically remaps node IDs to contiguous values (0 to N-1)
when loading a .tg file. The original node IDs from the file are NOT used directly.

To translate between original and internal IDs:
  - tgs.getNodeMap(): original_id -> internal_id
  - tgs.getReverseNodeMap(): internal_id -> original_id
"""

import pytglib as tgl
import time
import sys


def log(msg=""):
    """Print with immediate flush to avoid buffering issues."""
    print(msg, flush=True)


def validate_node_ids(tg, start, target):
    """Validate that node IDs are within bounds (prevents segfault)."""
    num_nodes = tg.getNumberOfNodes()
    if start < 0 or start >= num_nodes:
        raise ValueError(f"Start node {start} out of range [0, {num_nodes})")
    if target < 0 or target >= num_nodes:
        raise ValueError(f"Target node {target} out of range [0, {num_nodes})")


def get_internal_node_id(tgs, original_id):
    """Convert original node ID (from file) to internal ID (0 to N-1)."""
    node_map = tgs.getNodeMap()
    if original_id in node_map:
        return node_map[original_id]
    raise ValueError(f"Original node ID {original_id} not found in graph")


def get_original_node_id(tgs, internal_id):
    """Convert internal node ID (0 to N-1) to original ID (from file)."""
    reverse_map = tgs.getReverseNodeMap()
    if internal_id < len(reverse_map):
        return reverse_map[internal_id]
    raise ValueError(f"Internal node ID {internal_id} out of range")


def main():
    print("=" * 50)
    print("Temporal Graph Path Analysis")
    print("=" * 50)

    # Step 1: Load the graph
    print("\n[1/5] Loading ordered edge list...")
    start_time = time.time()
    tgs = tgl.load_ordered_edge_list("cached_datasets/tgbl_flight.tg")
    print(f"      Done! Loaded in {time.time() - start_time:.2f}s")

    # Step 2: Get statistics
    print("\n[2/5] Computing graph statistics...")
    start_time = time.time()
    stats = tgl.get_statistics(tgs)
    print(f"      Done! Computed in {time.time() - start_time:.2f}s")
    print(f"\n{stats}")

    # Step 3: Get time interval
    print("\n[3/5] Getting time interval...")
    ti = tgs.getTimeInterval()
    print(f"      Time interval: {ti}")

    # Step 4: Convert to incident lists (required for path computation)
    print("\n[4/5] Converting to incident lists...")
    start_time = time.time()
    tg = tgl.to_incident_lists(tgs)
    print(f"      Done! Converted in {time.time() - start_time:.2f}s")

    # Show node ID information
    num_nodes = tg.getNumberOfNodes()
    print(f"\n      Graph has {num_nodes} nodes")
    print(f"      Valid internal IDs: 0 to {num_nodes - 1}")
    
    # Show example node ID mappings
    print("\n      Example node mappings (internal -> original):")
    reverse_map = tgs.getReverseNodeMap()
    for i in range(min(5, num_nodes)):
        print(f"        {i} -> {reverse_map[i]}")

    # Define source and target using INTERNAL IDs (0 to N-1)
    start_node = get_internal_node_id(tgs, 17308)
    target_node = min(get_internal_node_id(tgs, 54417), num_nodes - 1)
    
    # Validate before calling
    validate_node_ids(tg, start_node, target_node)

    # Step 5: Compute minimum duration path
    print(f"\n[5/5] Computing minimum duration path...")
    print(f"      From internal node {start_node} (original: {reverse_map[start_node]})")
    print(f"      To internal node {target_node} (original: {reverse_map[target_node]})")
    start_time = time.time()
    path = tgl.minimum_duration_path(tg, start_node, target_node, ti)
    print(f"      Done! Computed in {time.time() - start_time:.2f}s")

    # Results
    print("\n" + "=" * 50)
    print("RESULTS")
    print("=" * 50)
    
    if len(path) == 0:
        print("No path found (nodes may not be reachable within the time interval)")
    else:
        print(f"Path found with {len(path)} edge(s):")
        for edge in path:
            # edge has: u, v, t, tt
            print(f"  {edge}")

    print("\nAnalysis complete!")


if __name__ == "__main__":
    main()
