# asynch-cv
Python3 library for asynchronous event-based computer vision applications.  

To install requirements, run `pip3 install -r requirements.txt`. Note that in order to read Metavision .RAW or .DAT files or connect to a Prophesee camera, you must install Metavision Designer separately.

To build, first run `python setup.py build_ext --inplace` to compile the cython modules.

Requires Boost library.

To run, simply execute one of the `test_*.py` scripts to see a demonstration.  
***
