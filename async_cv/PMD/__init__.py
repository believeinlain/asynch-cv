"""Persistent Motion Detector module.

This module receives a buffer of events and performs filtering and clustering \
to identify and track clusters, which are further analyzed by the pmd_consumer \
class.

PyPMD is the Cython wrapper class to interface with Python. The \
PersistentMotionDetector class and all subclasses are written in pure C++.

"""