import pytglib as tgl
import doctest


def temporal_clustering_coefficient_test():
    """
    >>> temporal_clustering_coefficient_test()
    0.045454545454545456
    """
    tgs = tgl.load_ordered_edge_list("../example_datasets/example_from_paper.tg")
    tg = tgl.to_incident_lists(tgs)

    c = tgl.temporal_clustering_coefficient(tg, 0, tg.getTimeInterval())
    return c


def temporal_clustering_coefficient_test_all_nodes():
    """
    >>> temporal_clustering_coefficient_test_all_nodes()
    VectorDouble[0.0454545, 0, 0, 0]
    """
    tgs = tgl.load_ordered_edge_list("../example_datasets/example_from_paper.tg")
    tg = tgl.to_incident_lists(tgs)

    c = tgl.temporal_clustering_coefficient(tg, tg.getTimeInterval())
    return c


if __name__ == "__main__":
    doctest.testmod()
