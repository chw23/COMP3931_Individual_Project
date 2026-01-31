"""
Optimized data loading for tgbl-flight dataset.
Converts tgx data to pytglib's .tg format and caches it for fast subsequent loads.

First run: ~10 minutes (converts and saves to disk)
Subsequent runs: ~seconds (loads directly from .tg file)
"""

import os
import pytglib as tgl

# Configuration
CACHE_DIR = "cached_datasets"
TG_CACHE_FILE = os.path.join(CACHE_DIR, "tgbl_flight.tg")


def convert_tgx_to_tg_file(output_path: str, dataset_name: str = "tgbl-flight"):
    """
    Load dataset from tgx and save to .tg format for pytglib.
    This is slow but only needs to be done once.
    
    .tg format: source destination timestamp [transition_time]
    One edge per line, space-separated.
    """
    import tgx
    
    print(f"Loading {dataset_name} from tgx (this may take a while)...")
    dataset = tgx.tgb_data(dataset_name)
    ctdg = tgx.Graph(dataset)
    
    # Ensure cache directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"Converting to .tg format and saving to {output_path}...")
    
    # Get edges from the tgx graph
    # tgx stores edges as: {timestamp: [(u, v, weight), ...]}
    edge_data = ctdg.data
    
    edge_count = 0
    with open(output_path, 'w') as f:
        for timestamp, edges in sorted(edge_data.items()):
            for edge in edges:
                u, v = edge[0], edge[1]
                # Format: source dest timestamp transition_time
                # Using transition_time=1 as default
                f.write(f"{u} {v} {timestamp} 1\n")
                edge_count += 1
    
    print(f"Saved {edge_count} edges to {output_path}")
    return output_path


def load_as_ordered_edge_list(use_cache: bool = True) -> tgl.OrderedEdgeList:
    """
    Load tgbl-flight as pytglib OrderedEdgeList.
    
    Args:
        use_cache: If True, use cached .tg file if available (much faster).
                   If False, always reload from tgx.
    
    Returns:
        pytglib OrderedEdgeList ready for analysis
    """
    if use_cache and os.path.exists(TG_CACHE_FILE):
        print(f"Loading from cache: {TG_CACHE_FILE}")
        return tgl.load_ordered_edge_list(TG_CACHE_FILE)
    
    # Convert and cache
    convert_tgx_to_tg_file(TG_CACHE_FILE)
    
    print(f"Loading cached file into pytglib...")
    return tgl.load_ordered_edge_list(TG_CACHE_FILE)


def load_as_incident_lists(use_cache: bool = True) -> tgl.IncidentLists:
    """
    Load tgbl-flight as pytglib IncidentLists representation.
    Better for neighbor-based operations.
    """
    if use_cache and os.path.exists(TG_CACHE_FILE):
        print(f"Loading from cache: {TG_CACHE_FILE}")
        return tgl.load_incident_lists(TG_CACHE_FILE)
    
    convert_tgx_to_tg_file(TG_CACHE_FILE)
    return tgl.load_incident_lists(TG_CACHE_FILE)


def rebuild_cache():
    """Force rebuild the cache file from tgx."""
    if os.path.exists(TG_CACHE_FILE):
        os.remove(TG_CACHE_FILE)
    convert_tgx_to_tg_file(TG_CACHE_FILE)


if __name__ == "__main__":
    # Example usage - first run will be slow, subsequent runs will be fast
    tgs = load_as_ordered_edge_list()
    
    stats = tgl.get_statistics(tgs)
    print("\nDataset Statistics:")
    print(stats)