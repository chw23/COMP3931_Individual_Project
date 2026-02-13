"""
Optimized data loading for tgbl-flight dataset.
Converts CSV data to pytglib's .tg format and caches it for fast subsequent loads.

Features:
- Airport code ↔ index mapping for human-readable results
- Estimated flight durations based on geographic distance
- City/airport name resolution for NLP interface

First run: Converts and saves to disk
Subsequent runs: Loads directly from cached .tg file
"""

import os
import math
import pickle
from typing import Dict, Tuple, Optional, List
import pandas as pd
import pytglib as tgl

# =============================================================================
# Configuration
# =============================================================================
CACHE_DIR = "cached_datasets"
TG_CACHE_FILE = os.path.join(CACHE_DIR, "tgbl_flight.tg")
MAPPING_CACHE_FILE = os.path.join(CACHE_DIR, "airport_mapping.pkl")

# Data source files
EDGELIST_CSV = "tgbl-flight-v2/tgbl-flight_edgelist_v2.csv"
NODE_FEAT_CSV = "tgbl-flight-v2/airport_node_feat_v2.csv"

# Constants for flight duration estimation
AVERAGE_FLIGHT_SPEED_KMH = 800  # Average commercial aircraft speed
EARTH_RADIUS_KM = 6371


# =============================================================================
# Airport Mapping Functions
# =============================================================================

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth.
    
    Args:
        lat1, lon1: Latitude and longitude of first point (degrees)
        lat2, lon2: Latitude and longitude of second point (degrees)
    
    Returns:
        Distance in kilometers
    """
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return EARTH_RADIUS_KM * c


def estimate_flight_duration(distance_km: float) -> int:
    """
    Estimate flight duration in seconds based on distance.
    Includes ~30 min overhead for takeoff/landing.
    
    Args:
        distance_km: Distance in kilometers
    
    Returns:
        Estimated duration in seconds
    """
    flight_hours = distance_km / AVERAGE_FLIGHT_SPEED_KMH
    overhead_hours = 0.5  # 30 minutes for takeoff/landing
    total_seconds = int((flight_hours + overhead_hours) * 3600)
    return max(total_seconds, 1800)  # Minimum 30 minutes


def build_airport_mapping(node_feat_path: str = NODE_FEAT_CSV) -> Tuple[Dict, Dict, pd.DataFrame]:
    """
    Build bidirectional mapping between airport codes and numeric indices.
    
    Args:
        node_feat_path: Path to airport node features CSV
    
    Returns:
        code_to_idx: dict mapping airport code (e.g., "KLAX") -> index
        idx_to_code: dict mapping index -> airport code
        airport_info: DataFrame with full airport details (type, continent, region, lat, lon)
    """
    airport_info = pd.read_csv(node_feat_path)
    code_to_idx = {code: idx for idx, code in enumerate(airport_info['airport_code'])}
    idx_to_code = {idx: code for code, idx in code_to_idx.items()}
    return code_to_idx, idx_to_code, airport_info


def load_airport_mapping() -> Tuple[Dict, Dict, pd.DataFrame]:
    """
    Load airport mapping from cache, or build and cache it.
    
    Returns:
        code_to_idx, idx_to_code, airport_info
    """
    if os.path.exists(MAPPING_CACHE_FILE):
        with open(MAPPING_CACHE_FILE, 'rb') as f:
            data = pickle.load(f)
            return data['code_to_idx'], data['idx_to_code'], data['airport_info']
    
    code_to_idx, idx_to_code, airport_info = build_airport_mapping()
    
    # Cache it
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(MAPPING_CACHE_FILE, 'wb') as f:
        pickle.dump({
            'code_to_idx': code_to_idx,
            'idx_to_code': idx_to_code,
            'airport_info': airport_info
        }, f)
    
    return code_to_idx, idx_to_code, airport_info


def get_airport_info(code: str, airport_info: pd.DataFrame = None) -> Optional[pd.Series]:
    """
    Get detailed information about an airport.
    
    Args:
        code: ICAO airport code (e.g., "KLAX")
        airport_info: DataFrame with airport data (loaded if not provided)
    
    Returns:
        Series with airport details or None if not found
    """
    if airport_info is None:
        _, _, airport_info = load_airport_mapping()
    
    matches = airport_info[airport_info['airport_code'] == code]
    if len(matches) > 0:
        return matches.iloc[0]
    return None


def search_airports(query: str, airport_info: pd.DataFrame = None) -> pd.DataFrame:
    """
    Search airports by code or region (useful for NLP interface).
    
    Args:
        query: Search string (case-insensitive)
        airport_info: DataFrame with airport data
    
    Returns:
        DataFrame of matching airports
    """
    if airport_info is None:
        _, _, airport_info = load_airport_mapping()
    
    query = query.upper()
    mask = (
        airport_info['airport_code'].str.contains(query, na=False) |
        airport_info['iso_region'].str.contains(query, na=False)
    )
    return airport_info[mask]


# =============================================================================
# Data Conversion Functions
# =============================================================================

def convert_csv_to_tg_file(
    edgelist_path: str = EDGELIST_CSV,
    output_path: str = TG_CACHE_FILE,
    node_feat_path: str = NODE_FEAT_CSV,
    estimate_duration: bool = True
) -> str:
    """
    Convert original CSV directly to .tg format with proper airport indexing.
    
    This bypasses tgx and loads directly from your CSV files, giving you
    control over the mapping and transition times.
    
    Args:
        edgelist_path: Path to edge list CSV (timestamp, src, dst, callsign, typecode)
        output_path: Where to save the .tg file
        node_feat_path: Path to airport features CSV
        estimate_duration: If True, estimate flight duration from coordinates
    
    Returns:
        Path to the created .tg file
    
    .tg format: source destination timestamp transition_time
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Build airport mapping
    code_to_idx, idx_to_code, airport_info = build_airport_mapping(node_feat_path)
    
    # Build coordinate lookup for duration estimation
    coord_lookup = {}
    if estimate_duration:
        for _, row in airport_info.iterrows():
            coord_lookup[row['airport_code']] = (row['latitude'], row['longitude'])
    
    # Cache for estimated durations between airport pairs
    duration_cache = {}
    
    print(f"Converting {edgelist_path} to .tg format...")
    edge_count = 0
    skipped = 0
    
    with open(output_path, 'w') as out_f:
        for chunk in pd.read_csv(edgelist_path, chunksize=100000):
            for _, row in chunk.iterrows():
                src_code = row['src']
                dst_code = row['dst']
                
                src_idx = code_to_idx.get(src_code)
                dst_idx = code_to_idx.get(dst_code)
                
                if src_idx is None or dst_idx is None:
                    skipped += 1
                    continue
                
                # Calculate transition time (flight duration)
                if estimate_duration:
                    pair_key = (src_code, dst_code)
                    if pair_key not in duration_cache:
                        src_coord = coord_lookup.get(src_code)
                        dst_coord = coord_lookup.get(dst_code)
                        if src_coord and dst_coord:
                            distance = haversine_distance(
                                src_coord[0], src_coord[1],
                                dst_coord[0], dst_coord[1]
                            )
                            duration_cache[pair_key] = estimate_flight_duration(distance)
                        else:
                            duration_cache[pair_key] = 1  # Fallback
                    transition_time = duration_cache[pair_key]
                else:
                    transition_time = 1
                
                # Write: source dest timestamp transition_time
                out_f.write(f"{src_idx} {dst_idx} {int(row['timestamp'])} {transition_time}\n")
                edge_count += 1
            
            print(f"  Processed {edge_count:,} edges...")
    
    print(f"Saved {edge_count:,} edges to {output_path}")
    if skipped > 0:
        print(f"  (Skipped {skipped:,} edges with unknown airport codes)")
    
    # Save the mapping
    with open(MAPPING_CACHE_FILE, 'wb') as f:
        pickle.dump({
            'code_to_idx': code_to_idx,
            'idx_to_code': idx_to_code,
            'airport_info': airport_info
        }, f)
    print(f"Saved airport mapping to {MAPPING_CACHE_FILE}")
    
    return output_path

'''
def convert_tgx_to_tg_file(output_path: str, dataset_name: str = "tgbl-flight"):
    """
    Load dataset from tgx and save to .tg format.
    Use convert_csv_to_tg_file() instead for better control over mappings.
    """
    import tgx
    
    print(f"Loading {dataset_name} from tgx (this may take a while)...")
    dataset = tgx.tgb_data(dataset_name)
    ctdg = tgx.Graph(dataset)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"Converting to .tg format and saving to {output_path}...")
    
    edge_data = ctdg.data
    edge_count = 0
    with open(output_path, 'w') as f:
        for timestamp, edges in sorted(edge_data.items()):
            for edge in edges:
                u, v = edge[0], edge[1]
                f.write(f"{u} {v} {timestamp} 1\n")
                edge_count += 1
    
    print(f"Saved {edge_count} edges to {output_path}")
    return output_path
'''

# =============================================================================
# Graph Loading Functions
# =============================================================================

def load_as_ordered_edge_list(use_cache: bool = True) -> tgl.OrderedEdgeList:
    """
    Load tgbl-flight as pytglib OrderedEdgeList.
    
    Args:
        use_cache: If True, use cached .tg file if available (much faster).
                   If False, rebuild from CSV.
    
    Returns:
        pytglib OrderedEdgeList ready for analysis
    """
    if use_cache and os.path.exists(TG_CACHE_FILE):
        print(f"Loading from cache: {TG_CACHE_FILE}")
        return tgl.load_ordered_edge_list(TG_CACHE_FILE)
    
    # Convert from CSV and cache
    convert_csv_to_tg_file()
    
    print(f"Loading cached file into pytglib...")
    return tgl.load_ordered_edge_list(TG_CACHE_FILE)


def load_as_incident_lists(use_cache: bool = True) -> tgl.IncidentLists:
    """
    Load tgbl-flight as pytglib IncidentLists representation.
    Better for neighbor-based operations and path algorithms.
    
    Args:
        use_cache: If True, use cached .tg file if available.
    
    Returns:
        pytglib IncidentLists ready for path analysis
    """
    if use_cache and os.path.exists(TG_CACHE_FILE):
        print(f"Loading from cache: {TG_CACHE_FILE}")
        return tgl.load_incident_lists(TG_CACHE_FILE)
    
    convert_csv_to_tg_file()
    return tgl.load_incident_lists(TG_CACHE_FILE)


def rebuild_cache(estimate_duration: bool = True):
    """
    Force rebuild the cache file from CSV.
    
    Args:
        estimate_duration: If True, estimate flight durations from coordinates
    """
    if os.path.exists(TG_CACHE_FILE):
        os.remove(TG_CACHE_FILE)
    if os.path.exists(MAPPING_CACHE_FILE):
        os.remove(MAPPING_CACHE_FILE)
    convert_csv_to_tg_file(estimate_duration=estimate_duration)


# =============================================================================
# Result Translation Functions (for NLP interface)
# =============================================================================

def translate_path_to_airports(node_indices: List[int]) -> List[str]:
    """
    Convert a list of node indices to airport codes.
    
    Args:
        node_indices: List of numeric node IDs from pytglib
    
    Returns:
        List of airport codes (e.g., ["KLAX", "KJFK", "EGLL"])
    """
    _, idx_to_code, _ = load_airport_mapping()
    return [idx_to_code.get(idx, f"UNKNOWN_{idx}") for idx in node_indices]


def format_path_result(
    node_indices: List[int],
    timestamps: List[int] = None,
    include_details: bool = True
) -> str:
    """
    Format a path result as human-readable string.
    
    Args:
        node_indices: List of node IDs from pytglib path result
        timestamps: Optional list of departure timestamps
        include_details: If True, include airport type and region
    
    Returns:
        Formatted string describing the path
    """
    from datetime import datetime
    
    _, idx_to_code, airport_info = load_airport_mapping()
    
    if not node_indices:
        return "No path found."
    
    lines = [f"Path with {len(node_indices)} stops ({len(node_indices)-1} flights):"]
    lines.append("-" * 50)
    
    for i, idx in enumerate(node_indices):
        code = idx_to_code.get(idx, f"UNKNOWN_{idx}")
        info = get_airport_info(code, airport_info)
        
        # Format timestamp if available
        time_str = ""
        if timestamps and i < len(timestamps):
            dt = datetime.utcfromtimestamp(timestamps[i])
            time_str = f" @ {dt.strftime('%Y-%m-%d %H:%M')} UTC"
        
        if info is not None and include_details:
            lines.append(
                f"  {i+1}. {code} ({info['type']}) - {info['iso_region']}{time_str}"
            )
        else:
            lines.append(f"  {i+1}. {code}{time_str}")
    
    return "\n".join(lines)


def get_airport_index(code_or_name: str) -> Optional[int]:
    """
    Get the numeric index for an airport (for use with pytglib).
    Supports partial matching for NLP interface.
    
    Args:
        code_or_name: Airport ICAO code or partial search string
    
    Returns:
        Numeric index or None if not found
    """
    code_to_idx, _, airport_info = load_airport_mapping()
    
    # Try exact match first
    code_upper = code_or_name.upper()
    if code_upper in code_to_idx:
        return code_to_idx[code_upper]
    
    # Try search
    matches = search_airports(code_or_name, airport_info)
    if len(matches) == 1:
        return code_to_idx[matches.iloc[0]['airport_code']]
    elif len(matches) > 1:
        print(f"Multiple matches for '{code_or_name}':")
        for _, row in matches.head(5).iterrows():
            print(f"  {row['airport_code']} - {row['iso_region']} ({row['type']})")
        return None
    
    return None


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    # Example usage - rebuild cache with estimated flight durations
    print("Rebuilding cache from CSV with estimated flight durations...")
    rebuild_cache(estimate_duration=True)
    
    # Load and show statistics
    tgs = load_as_ordered_edge_list()
    stats = tgl.get_statistics(tgs)
    print("\nDataset Statistics:")
    print(stats)
    
    # Show sample airport mappings
    print("\nSample airport mappings:")
    _, idx_to_code, airport_info = load_airport_mapping()
    for idx in [0, 1, 2, 100, 1000]:
        if idx in idx_to_code:
            code = idx_to_code[idx]
            info = get_airport_info(code, airport_info)
            if info is not None:
                print(f"  Index {idx}: {code} - {info['iso_region']} ({info['type']})")