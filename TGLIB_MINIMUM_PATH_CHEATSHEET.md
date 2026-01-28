# TGLib Minimum Path Analysis Cheat Sheet

> A quick reference guide for temporal path and distance functions in TGLib

---

## 📦 Installation & Import

```python
# Install via PyPI
pip install temporalgraphlib

# Import the library
import pytglib as tgl
```

---

## 📁 Loading Data

### Loading Temporal Graphs

```python
# Load as Ordered Edge List (for distance computations)
tgs = tgl.load_ordered_edge_list("path/to/file.tg")

# Convert to Incident Lists (required for path computations)
tg = tgl.to_incident_lists(tgs)

# Get time interval of the graph
ti = tgs.getTimeInterval()
```

### File Format
Each line represents a temporal edge: `u v t [tt]`
- `u`: tail node (source)
- `v`: head node (destination)  
- `t`: timestamp (availability time)
- `tt`: transition time (optional, defaults to 1)

**Example file content:**
```
0 1 2 1
0 1 5 2 
0 3 1 5
1 3 7 2
2 1 6 1
3 2 6 2
3 2 8 4
```

---

## 🛤️ Path Functions (Returns Actual Paths)

> **Note:** Path functions require `IncidentLists` representation (`tg = tgl.to_incident_lists(tgs)`)

| Function | Description | Returns |
|----------|-------------|---------|
| `minimum_duration_path(tg, start, target, ti)` | Fastest path (minimizes total travel time from start to arrival) | `VectorTemporalEdge` |
| `earliest_arrival_path(tg, start, target, ti)` | Path that arrives earliest at destination | `VectorTemporalEdge` |
| `minimum_transition_time_path(tg, start, target, ti)` | Shortest path (minimizes sum of edge transition times) | `VectorTemporalEdge` |
| `minimum_hops_path(tg, start, target, ti)` | Path with fewest edges/hops | `VectorTemporalEdge` |

### Usage Examples

```python
# Load and convert graph
tgs = tgl.load_ordered_edge_list("example_datasets/example_from_paper.tg")
tg = tgl.to_incident_lists(tgs)
ti = tgs.getTimeInterval()

# Fastest path (minimum duration)
path = tgl.minimum_duration_path(tg, 0, 2, ti)
# Output: VectorTemporalEdge[(0 1 5 2), (1 2 7 2)]

# Earliest arrival path
path = tgl.earliest_arrival_path(tg, 0, 2, ti)
# Output: VectorTemporalEdge[(0 2 1 5)]

# Shortest path (minimum transition time)
path = tgl.minimum_transition_time_path(tg, 0, 2, ti)
# Output: VectorTemporalEdge[(0 1 2 1), (1 2 7 2)]
```

---

## 📏 Distance Functions (Returns Distances to All Nodes)

> Distance functions work with both `OrderedEdgeList` (`tgs`) and `IncidentLists` (`tg`)

| Function | Description | Returns |
|----------|-------------|---------|
| `minimum_durations(tgs/tg, nid, ti)` | Duration of fastest paths from `nid` to all reachable nodes | `VectorTime` |
| `earliest_arrival_times(tgs/tg, nid, ti)` | Earliest arrival times from `nid` to all reachable nodes | `VectorTime` |
| `minimum_transition_times(tgs/tg, nid, ti)` | Minimum sum of transition times from `nid` to all nodes | `VectorTime` |
| `minimum_hops(tgs/tg, nid, ti)` | Minimum number of hops from `nid` to all nodes | `VectorDistance` |
| `latest_departure_times(tgs, nid, ti)` | Latest departure times from `nid` to all nodes | `VectorTime` |

### Usage Examples

```python
tgs = tgl.load_ordered_edge_list("example_datasets/example_from_paper.tg")
ti = tgs.getTimeInterval()

# Minimum durations (fastest path distances)
durations = tgl.minimum_durations(tgs, 0, ti)
# Output: VectorTime[0, 1, 4, 7] (from node 0 to nodes 0,1,2,3)

# Earliest arrival times
arrivals = tgl.earliest_arrival_times(tgs, 0, ti)
# Output: VectorTime[0, 3, 6, 8]

# Minimum transition times (shortest path distances)
transitions = tgl.minimum_transition_times(tgs, 0, ti)
# Output: VectorTime[0, 1, 3, 7]
```

---

## 🎯 Distance Types Enum

Used for centrality measures that depend on path definitions:

```python
tgl.Distance_Type.Earliest_Arrival
tgl.Distance_Type.Fastest
tgl.Distance_Type.Latest_Departure
tgl.Distance_Type.Minimum_Transition_Times
tgl.Distance_Type.Minimum_Hops
```

### Example with Temporal Closeness

```python
closeness_fastest = tgl.temporal_closeness(tgs, tgl.Distance_Type.Fastest)
closeness_ea = tgl.temporal_closeness(tgs, tgl.Distance_Type.Earliest_Arrival)
```

---

## 📊 Data Structures

| Structure | Description | Use Case |
|-----------|-------------|----------|
| `OrderedEdgeList` | Edges sorted by time | Distance computations, streaming algorithms |
| `IncidentLists` | Adjacency list format | Path computations, graph traversal |
| `TRSGraph` | Time-respecting static graph | Alternative representation for some algorithms |

### Conversion Functions

```python
# OrderedEdgeList → IncidentLists
tg = tgl.to_incident_lists(tgs)

# Load directly as TRSGraph
trs = tgl.load_TRS("file.tg", directed=True)
```

---

## 📝 Basic Types

| Type | Description |
|------|-------------|
| `NodeId` | 32-bit integer for node identifiers |
| `Time` | 64-bit integer for timestamps |
| `Distance` | 64-bit integer for distances |
| `TimeInterval` | Pair of (start_time, end_time) |
| `TemporalEdge` | Tuple of (u, v, t, tt) |

### TemporalEdge Structure
- `u`: tail (source node)
- `v`: head (destination node)
- `t`: availability time (timestamp)
- `tt`: transition time (traversal duration)

---

## 🧪 Test Datasets

Located in `example_datasets/`:

### 1. `example_from_paper.tg`
Basic temporal graph example (4 nodes, 7 edges):
```
0 1 2 1    # Edge from 0→1 at time 2, transition time 1
0 1 5 2    # Edge from 0→1 at time 5, transition time 2
0 3 1 5    # Edge from 0→3 at time 1, transition time 5
1 3 7 2    # Edge from 1→3 at time 7, transition time 2
2 1 6 1    # Edge from 2→1 at time 6, transition time 1
3 2 6 2    # Edge from 3→2 at time 6, transition time 2
3 2 8 4    # Edge from 3→2 at time 8, transition time 4
```

### 2. `example_from_paper_with_loops_and_multiedges.tg`
Extended version with self-loops and multi-edges for testing edge cases.

---

## 🧪 Test Files Reference

| Test File | Functions Tested |
|-----------|------------------|
| `temporal_paths_tests.py` | `minimum_duration_path`, `earliest_arrival_path`, `minimum_transition_time_path` |
| `temporal_distance_tests.py` | `minimum_durations`, `earliest_arrival_times`, `minimum_transition_times` |

---

## 🔄 Complete Workflow Example

```python
import pytglib as tgl

# 1. Load the temporal graph
tgs = tgl.load_ordered_edge_list("example_datasets/example_from_paper.tg")

# 2. Get basic statistics
stats = tgl.get_statistics(tgs)
print(stats)

# 3. Get time interval
ti = tgs.getTimeInterval()

# 4. Compute distances from node 0 to all nodes
durations = tgl.minimum_durations(tgs, 0, ti)
arrivals = tgl.earliest_arrival_times(tgs, 0, ti)
transitions = tgl.minimum_transition_times(tgs, 0, ti)

print(f"Minimum durations from node 0: {durations}")
print(f"Earliest arrivals from node 0: {arrivals}")
print(f"Minimum transitions from node 0: {transitions}")

# 5. Find actual paths (requires IncidentLists)
tg = tgl.to_incident_lists(tgs)

path_fast = tgl.minimum_duration_path(tg, 0, 2, ti)
path_early = tgl.earliest_arrival_path(tg, 0, 2, ti)
path_short = tgl.minimum_transition_time_path(tg, 0, 2, ti)

print(f"Fastest path 0→2: {path_fast}")
print(f"Earliest arrival path 0→2: {path_early}")
print(f"Shortest path 0→2: {path_short}")

# 6. Compute temporal closeness centrality
closeness = tgl.temporal_closeness(tgs, tgl.Distance_Type.Fastest)
print(f"Temporal closeness (fastest): {closeness}")
```

---

## 📚 Path Type Definitions

| Path Type | Optimization Goal | Formula |
|-----------|-------------------|---------|
| **Minimum Duration (Fastest)** | Minimize total travel time | `arrival_time - start_time` |
| **Earliest Arrival** | Arrive as early as possible | `min(arrival_time)` |
| **Latest Departure** | Leave as late as possible | `max(departure_time)` |
| **Minimum Transition Time (Shortest)** | Minimize sum of edge weights | `Σ transition_times` |
| **Minimum Hops** | Minimize number of edges | `count(edges)` |

---

## 💡 Key Differences

| Concept | Fastest Path | Earliest Arrival | Shortest Path |
|---------|--------------|------------------|---------------|
| Optimizes | Duration (end - start) | Arrival time | Sum of edge weights |
| Good for | Minimizing trip time | Time-critical arrivals | Route efficiency |
| May wait? | Yes (for faster edges) | No (uses first available) | Yes (for shorter edges) |

---

## ⚠️ Important Notes

1. **Unreachable nodes**: Distance functions return `inf` (max int64) for unreachable nodes
2. **Self-distance**: Distance from a node to itself is always 0
3. **Time intervals**: All path/distance functions accept a time interval `ti` to restrict computation
4. **Directed graphs**: By default, graphs are loaded as directed; use `load_ordered_edge_list(filename, False)` for undirected

---

## 📖 References

- [TGLib Paper (IEEE ICDMW 2022)](https://www.computer.org/csdl/proceedings-article/icdmw/2022/460900b1240/1KBr115pQRO)
- [arXiv Version](https://arxiv.org/abs/2209.12587)
- [GitLab Repository](https://gitlab.com/tgpublic/tglib)
- [Online C++ Documentation](https://tgpublic.gitlab.io/tglib/)
