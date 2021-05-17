# asynch-cv
Python3 library for asynchronous event-based computer vision applications.  

To install requirements, run `pip3 install -r requirements.txt`. Note that in order to read Metavision .RAW or .DAT files or connect to a Prophesee camera, you must install Metavision Designer separately.  

To run, simply run `python3 async_cv` from the command line.  

Or execute one of the `test_*.py` scripts to see a demonstration.  
***
# Asynchronous Filtering and Segmentation of Temporal Contrast Events for Object Detection and Analysis
This algorithm can be divided into three main parts:
- **Pre-filter:** Reduces local event density below a set threshold to speed up processing and isolate different objects.
- **Correlational Segmentation Filter:** Groups individual events into spatio-temporal regions which are stored in a fixed-size buffer, and ignores events which do not have enough adjacent neighbors
- **Object detection and analysis:** Characterizes different regions to distinguish objects of potential concern against dynamic background such as ocean waves.
## Correlational Segmentation Filter
$e=\{ x,y,p,t\}$ where $e$ is a single temporal contrast event allowed through the pre-filter.  
$(x,y)$ is the position of the event on the dynamic vision sensor, in the range $x=[0, width)$, $y=[0, height)$  
$p$ is the polarity of the event. $p=1$ for an increasing brightness event, and $p=0$ for a decreasing brightness event.  
$t$ is the time that the event was recorded, in microseconds.
Incoming events are stored in a fixed size 3D buffer $B\subset\mathbb{Z}^3$, where for all buffered events $e_B\in B$, $e=\{ x,y,t\}$