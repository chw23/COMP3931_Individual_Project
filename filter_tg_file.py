"""n
Script to filter a .tg file to keep only the first N records per timestamp.

.tg file format: each line represents a temporal edge: u v t tt
- u: source node
- v: destination node  
- t: timestamp
- tt: transition time

NOTE: pytglib automatically remaps node IDs to contiguous values (0 to N-1)
when loading a .tg file, so we don't need to do it here.
"""

from collections import defaultdict


def filter_tg_file(input_path: str, output_path: str, max_records_per_timestamp: int = 3):
    """
    Read a .tg file and write a new one with only the first N records per timestamp.
    
    Args:
        input_path: Path to the input .tg file
        output_path: Path to the output .tg file
        max_records_per_timestamp: Maximum number of records to keep per timestamp
    """
    timestamp_counts = defaultdict(int)
    filtered_edges = []
    
    print(f"Reading from: {input_path}")
    
    with open(input_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) >= 4:
                u, v, t, tt = parts[0], parts[1], int(parts[2]), parts[3]
                
                if timestamp_counts[t] < max_records_per_timestamp:
                    filtered_edges.append(f"{u} {v} {t} {tt}")
                    timestamp_counts[t] += 1
    
    # Write filtered output
    print(f"Writing to: {output_path}")
    with open(output_path, 'w') as f:
        for edge in filtered_edges:
            f.write(edge + '\n')
    
    # Print summary
    print(f"\nSummary:")
    print(f"  Total edges written: {len(filtered_edges)}")
    print(f"  Unique timestamps: {len(timestamp_counts)}")
    print(f"  Max records per timestamp: {max_records_per_timestamp}")


if __name__ == "__main__":
    input_file = "cached_datasets/tgbl_flight.tg"
    output_file = "cached_datasets/tgbl_flight_filtered.tg"
    
    filter_tg_file(input_file, output_file, max_records_per_timestamp=3)
