# asynch-cv
Python3 library for asynchronous event-based computer vision algorithms. Provides a layer of abstraction between different event data formats for processing. Currently capable of handling aedat4 and metavision raw or live input.

In order to read Metavision format files or connect to a Prophesee camera, you must install Metavision Designer separately, as Metavision Designer is not publicly available in a package repository.

If using conda, an appropriate environment can be created from the included YAML file with `conda env create --file async-cv.yml`.

Uses Cython for event processing to run in real-time. To build, first execute `python setup.py build_ext -i` to compile the Cython extensions. Requires [CTPL](https://github.com/vit-vit/CTPL) if compiled with thread support. To install CTPL, simply clone the repository into a directory parallel to this one. For example, if this repository is cloned into `C:\dev\async-cv`, then clone CTPL into `C:\dev\CTPL`.

Simply run one of the test scripts in `asynch-cv\tests\` for a demonstration.  
