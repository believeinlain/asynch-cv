# asynch-cv
Python3 library for asynchronous event-based computer vision applications.  

To install requirements, run `pip3 install -r requirements.txt`. Note that in order to read Metavision .RAW or .DAT files or connect to a Prophesee camera, you must install Metavision Designer separately.  

To run, simply run `python3 async_cv` from the command line.  

Or execute one of the `test_*.py` scripts to see a demonstration.  
***
# Asynchronous Filtering and Segmentation of Temporal Contrast Events for Object Detection and Analysis
This algorithm can be divided into three main parts:
- **Pre-Filter:** Reduces local event density below a set threshold to speed up processing and aid in isolating different objects.
- **Correlational Segmentation Filter:** Groups individual events into spatio-temporal regions which are stored in a fixed-size buffer, and ignores events which do not have enough adjacent neighbors
- **Object Detection and Analysis:** Characterizes different regions to distinguish objects of potential concern from dynamic background such as ocean waves.

## Pre-Filter


## Correlational Segmentation Filter
The filter receives as input from the pre-filter a set of events $E_i$ where $e\in E_i=\{ x,y,p,t\}$. $(x,y)$ is the position of the event on the dynamic vision sensor, in the range $x=[0, width)$, $y=[0, height)$, where $(width, height)$ are the dimensions of the sensor. $p$ is the polarity of the event. $p=1$ for an increasing brightness or "on" event, and $p=0$ for a decreasing brightness or "off" event. $t$ is the time at which the event was recorded, in microseconds.  
Incoming events are stored in a persistent fixed size 3D buffer $B$, with dimensions $(width, height, d)$, where $d$ represents the "buffer depth". For each location $(x,y)$, the $d$ most recently received events at that location are stored in the buffer. As each new event comes in, it displaces the oldest event in $B$ at that location.  
Event $e$ will pass the filter if and only if there are at least $n_f$ total events in $E_f\subset B$. $E_f$ contains all buffered events at locations $(x\plusmn 1,y\plusmn 1)$ with timestamps within $\tau_f$ $\mu s$ of $t$. $n_f$ will be called the "filter count" and $\tau_f$ will be called the "filter threshold".
If $e$ does not pass the filter, it will remain in the buffer to be counted by future events. If $e$ does pass the filter, it will be assigned a region identifier $r\in R$.  
To choose $r$, we consider the events in $E_r\subset B$, where $E_r$ contains all buffered events at locations $(x\plusmn 1,y\plusmn 1)$ with timestamps within $\tau_r$ $\mu s$ of $t$, and $\tau_r$ is the "segmentation threshold". If none of the events in $E_r$ have been assigned region identifiers, $e$ will be assigned to a new region with a unique value for $r$. Otherwise, $r$ will be set to the region identifier that occurs the most in $E_r$.  
After all events in $E_i$ are buffered, filtered, and assigned to a region if applicable, the number of events in each region within $\tau_r$ of $ts$ are counted, where $ts$ is greater than the timestamp of the last event in $E_i$, and less than or equal to the timestamp of the first event in the following event buffer $E_{i+1}$. This count provides a weight $w$ for each region, which is used to determine which regions are empty, and provided as an input to the next stage.
***
**Algorithm 2:** Correlational Segmentation Filter
***
**Input:** $e={x,y,p,t}$, $B(width, height, d)$, $n_f$, $\tau_f$, $\tau_r$  
1 $B(x, y, \mathrm{min}(B(x, y, :)))=t$  
2 $A = \mathrm{CountAdjacentEvents}(x,y,\tau_f)$  
3 **If** $A\geq n_f$ **then**  
4 | $r = \mathrm{MostAdjacentRegion}(x,y,\tau_r)$


## Object Detection and Analysis
