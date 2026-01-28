import pytglib as tgl

tgs = tgl.load_ordered_edge_list("tglib/example_datasets/example_from_paper.tg")
stats = tgl.get_statistics(tgs)
print(stats)


