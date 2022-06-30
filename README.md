# asynch-cv
Code for [Real-Time Event-Based Tracking and Detection for Maritime Environments](https://doi.org/10.1109/AIPR52630.2021.9762225), presented at 2021 IEEE Applied Imagery Pattern Recognition Workshop (AIPR).

If you find this code useful, please cite:  
```
@INPROCEEDINGS{9762225,  author={Aelmore, Stephanie and Ordonez, Richard C. and Parameswaran, Shibin and Mauger, Justin},  booktitle={2021 IEEE Applied Imagery Pattern Recognition Workshop (AIPR)},   title={Real-Time Event-Based Tracking and Detection for Maritime Environments},   year={2021},  volume={},  number={},  pages={1-6},  doi={10.1109/AIPR52630.2021.9762225}}
```

Python3 library for asynchronous event-based computer vision algorithms. Provides a layer of abstraction between different event data formats for processing. Currently capable of handling aedat4 and metavision raw or live input.

In order to read Metavision format files or connect to a Prophesee camera, you must install Metavision Designer separately, as Metavision Designer is not publicly available in a package repository.

If using conda, an appropriate environment can be created from the included YAML file with `conda env create --file async-cv.yml`.

Uses Cython for event processing to run in real-time. To build, first execute `python setup.py build_ext -i` to compile the Cython extensions. Requires [CTPL](https://github.com/vit-vit/CTPL) if compiled with thread support. To install CTPL, simply clone the repository into a directory parallel to this one. For example, if this repository is cloned into `C:\dev\async-cv`, then clone CTPL into `C:\dev\CTPL`.

Simply run one of the test scripts in `asynch-cv\tests\` for a demonstration.  
