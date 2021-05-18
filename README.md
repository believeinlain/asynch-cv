# asynch-cv
Python3 library for asynchronous event-based computer vision applications.  

To install requirements, run `pip3 install -r requirements.txt`. Note that in order to read Metavision .RAW or .DAT files or connect to a Prophesee camera, you must install Metavision Designer separately.  

To run, simply run `python3 async_cv` from the command line.  

Or execute one of the `test_*.py` scripts to see a demonstration.  
***
# Asynchronous Filtering and Segmentation of Temporal Contrast Events for Object Detection and Analysis
This algorithm can be divided into three main parts:
- **Pre-filter:** Reduces local event density below a set threshold to speed up processing and aid in isolating different objects.
- **Correlational Segmentation Filter:** Groups individual events into spatio-temporal regions which are stored in a fixed-size buffer, and ignores events which do not have enough adjacent neighbors
- **Object detection and analysis:** Characterizes different regions to distinguish objects of potential concern from dynamic background such as ocean waves.
## Correlational Segmentation Filter
The filter receives as input from the pre-filter a set of events $E$ where $e\in E=\{ x,y,p,t\}$. $(x,y)$ is the position of the event on the dynamic vision sensor, in the range $x=[0, width)$, $y=[0, height)$, where $(width, height)$ are the dimensions of the sensor. $p$ is the polarity of the event. $p=1$ for an increasing brightness or "on" event, and $p=0$ for a decreasing brightness or "off" event. $t$ is the time at which the event was recorded, in microseconds.  
Incoming events are stored in a fixed size 3D buffer $B$, with dimensions $(width, height, d)$, where $d$ represents the "buffer depth". For each location $(x,y)$, the $d$ most recently received events at that location are stored in the buffer. As each new event comes in, it displaces the oldest event in $B$ at that location.  
Event $e$ will pass the filter if and only if there are at least $n_f$ total events in $E_f\subset B$. $E_f$ contains all buffered events at locations $(x\plusmn 1,y\plusmn 1)$ with timestamps within $\tau_f$ $\mu s$ of $t$. $n_f$ will be called the "filter count" and $\tau_f$ will be called the "filter threshold".
If $e$ does not pass the filter, it will remain in the buffer to be counted by future events. If $e$ does pass the filter, it will be assigned a region identifier $r\in R$.  
To choose $r$, we consider the events in $E_r\subset B$, where $E_r$ contains all buffered events at locations $(x\plusmn 1,y\plusmn 1)$ with timestamps within $\tau_r$ $\mu s$ of $t$, and $\tau_r$ is the "segmentation threshold".