[//]: # (/tableofcontents)
# Introduction to TGLib

**TGLib is an open-source temporal graph library focusing on temporal distance and centrality 
computations, and other local and global temporal graph statistics.** 

TGLib is designed for performance and usability by an efficient and modular C++ implementation of the 
core data structures and algorithms and an easy-to-use Python front-end provided by PyBind11. 


[GitLab Repository](https://gitlab.com/tgpublic/tglib)


## Easy Python Usage

**New:** TGLib is now easily installable via [PyPI](https://pypi.org/project/temporalgraphlib/)!
You can install it using pip:

```bash
pip install temporalgraphlib
```

This installs the precompiled Python bindings for TGLib, allowing you to use it directly in your Python environment without building from source.

After installation, TGLib can be used in python as follows:

```
import pytglig as tgl
tgs = tgl.load_ordered_edge_list("example_datasets/example_from_paper.tg")
stats = tgl.get_statistics(tgs)
print(stats)
```

## Easy C++ Usage

The C++ part of TGLib is a header-only template library that can be directly used in other C++ projects
by including the headers in your project.


## Compilation and Installation
The following describes how to compile the python bindings.

### Building the Python library
For compiling the PyBind11 binding and the Doxygen documentation, 
first clone the repository recursively to obtain the PyBind11 submodule via
```
git clone --recurse-submodules https://gitlab.com/tgpublic/tglib.git
```

Then, run the following:

```
cd tglib/tglib_cpp
mkdir build-release
cd build-release
cmake .. -DCMAKE_BUILD_TYPE=Release
make
```
After the compilation, the Python binding is in the subfolder `build-release/src/python-binding`.

#### Importing the Python library
Running the above commands will produce a binary module file 
that can be imported to Python. 
Assuming that the compiled module is located in the 
current directory, TGLib can be imported in Python with ```import pytglib as tgl```.



#### Python version
Note that the CMake will try to automatically detect the installed 
Python version and link against that. 
You can specify a version by adding `-DPYTHON_EXECUTABLE=$(which python)` 
when calling `cmake`, where $(which python) a path to 
Python (see 
[PyBind11 documentation](https://pybind11.readthedocs.io/en/stable/faq.html?highlight=cmake#cmake-doesn-t-detect-the-right-python-version)).


### Building the documentation
In order to additionally generate the C++ documentation, call `make doxygen`.
The documentation can be found in the subfolder `build-release/html`.
Note that you need Doxygen for generating the documentation.

## Quick Start

### First example

The following Python code loads a temporal graph from the file with name `temporal_graph_file` 
and computes basic network statistics by calling `get_statistics`.
The results is printed using the `print` command.

```python
import pytglib as tgl  
tg = tgl.load_ordered_edge_list("temporal_graph_file")
stats = tgl.get_statistics(tg)
print(stats)
```

The folder `tglib_python` contains further examples for
the usage of TGLib in Python.

### Temporal graph file format
Temporal graphs can be read from text files that contain edge lists in
which each line represents the information of the edge.
Each edge can consists of three or four values:
`u v t` or  `u v t tt` where `u` is the tail, `v` the head, 
`t` the time stamp (availability time), and `tt` an optional transition time.

The folder `example_datasets` contains examples.



## Implemented Data Structures and Algorithms 

### Data structures
TGLib supports the temporal edge stream data structure from 
[Wu et al.](https://dl.acm.org/doi/10.14778/2732939.2732945),
the incident lists data structure used in 
[Oettershagen and Mutzel](https://ieeexplore.ieee.org/document/9338392), and the 
time-respecting static graph representation introduced in 
[Gheibi et al.](https://ieeexplore.ieee.org/abstract/document/9631469).
Furthermore, TGLib supports further static graph representations, e.g.,
the weighted aggregated underlying graph or directed line graph representation.

[//]: # (For further details about the implemented data structures and algorithms, )
[//]: # (as well as the corresponding references are described in our [paper]&#40;&#41;.)

### Algorithms and network properties

So far, we implemented the following algorithms and measures, e.g.,

* **Temporal paths and distance algorithms:** Based on 
[Wu et al.](https://dl.acm.org/doi/10.14778/2732939.2732945),
[Oettershagen and Mutzel](https://ieeexplore.ieee.org/document/9338392),
[Gheibi et al.](https://ieeexplore.ieee.org/abstract/document/9631469), (and new techniques), for
  * minimum duration paths
  * earliest arrival paths
  * latest departure paths
  * shortest paths
  * minimum hops paths
* **Temporal centrality measures:** 
  * temporal closeness ([Oettershagen and Mutzel](https://ieeexplore.ieee.org/document/9338392) and new variants)
  * temporal edge betweenness (new)
  * temporal Katz ([Béres et al.](https://doi.org/10.1007/s41109-018-0080-5))
  * temporal PageRank ([Rozenshtein and Gionis](https://doi.org/10.1007/978-3-319-46227-1_42))
  * temproal walk centrality ([Oettershagen et al.](https://dl.acm.org/doi/fullHtml/10.1145/3485447.3512210))
* **Temporal graph properties:** 
  * edge/node burstiness ([Goh and Barabási](https://arxiv.org/abs/physics/0610233))
  * topological overlap ([Tang et al.](https://arxiv.org/abs/0909.1712))
  * temporal clustering coefficient ([Tang et al.](https://dl.acm.org/doi/10.1145/1592665.1592674))
  * temporal eccentricity and diameter
  * temporal efficiency ([Tang et al.](https://dl.acm.org/doi/10.1145/1592665.1592674))
  * temporal (k,h)-core decomposition ([Wu et al.](https://ieeexplore.ieee.org/abstract/document/7363809))
  * temporal (L,K)-lasting core ([Hung and Tseng](https://link.springer.com/chapter/10.1007/978-3-030-73216-5_23))

## C++ Documentation
The C++ code is fully documented using Doxygen.
You can read the documentation [online here](https://tgpublic.gitlab.io/tglib/).

## Contact and Cite

Contact information can be found [here](https://ca.cs.uni-bonn.de/doku.php?id=people:oettershagen).

Please cite our [paper](https://www.computer.org/csdl/proceedings-article/icdmw/2022/460900b240/1KBr115pQRO) ([arxiv version](https://arxiv.org/abs/2209.12587)), and the respective papers of the methods used,
if you use TGLib:

```
@inproceedings{oettershagen2022tglib,
  title={Tglib: an open-source library for temporal graph analysis},
  author={Oettershagen, Lutz and Mutzel, Petra},
  booktitle={2022 IEEE International Conference on Data Mining Workshops (ICDMW)},
  pages={1240--1245},
  year={2022},
  organization={IEEE}
}
```

## License
TGLib is released under MIT license.
See [LICENSE.md](LICENSE.md) for details.


