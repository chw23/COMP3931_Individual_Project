import pytglib as tgl
'''
from load_data import load_as_ordered_edge_list

# Load tgbl-flight dataset (fast after first run due to caching)
tgs = load_as_ordered_edge_list()

# Now you can use pytglib for analysis
stats = tgl.get_statistics(tgs)
print(stats)
'''

tgs = tgl.load_ordered_edge_list("cached_datasets/tgbl_flight.tg")
tg = tgl.to_incident_lists(tgs)
ti = tgs.getTimeInterval()

path = tgl.minimum_duration_path(tg, 0, 10, ti)
stats = tgl.get_statistics(tgs)
print(stats)
print("Minimum duration path from node 0 to 10:", path)


