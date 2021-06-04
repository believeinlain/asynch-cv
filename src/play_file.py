
# pylint: disable=import-outside-toplevel
# pylint: disable=invalid-name
from os import path
import sys
import time
import cv2
import numpy as np

def play_file(filename, dt, event_consumer, consumer_args=None):
    '''
    Play a recorded event stream in any of the supported formats.
    '''
    # translate None into an empty dict
    if consumer_args is None:
        consumer_args = {}

    # convert dt into microseconds for event streaming
    dt_us = dt*1_000

    # Check validity of input arguments
    if not(path.exists(filename) and path.isfile(filename)):
        print("Error: provided input path '{}' does not exist or is not a file.".format(filename))
        return -1

    if filename.endswith('.raw') or filename.endswith('.dat'):
        play_metavision_file(filename, dt, event_consumer, consumer_args)

    elif filename.endswith('.aedat'):
        from PyAedatTools import ImportAedat

        # Create a dict with which to pass in the input parameters.
        aedat = {}
        aedat['importParams'] = {}

        # Put the filename, including full path, in the 'filePath' field.
        aedat['importParams']['filePath'] = filename

        # Invoke the import function
        aedat = ImportAedat.ImportAedat(aedat)

        # legacy support is incomplete, for now just assume we have the Davis346Red
        # here are the field sizes for reference:
        # devices = {
        #     'Dvs128':		    [128, 128],
        #     'Davis240':		[240, 180],
        #     'Davis128':		[128, 128],
        #     'Davis208':		[208, 192],
        #     'Davis346':		[346, 260],
        #     'Davis640':		[640, 480]
        # }
        width = 346
        height = 260

        # create data structure to process into frames
        event_data = np.array([ 
            np.subtract(width-1, aedat['data']['polarity']['x']), # flip x
            np.subtract(height-1, aedat['data']['polarity']['y']), # flip y
            aedat['data']['polarity']['polarity'],
            aedat['data']['polarity']['timeStamp']
        ]).transpose()
        
        consumer = event_consumer(width, height, consumer_args)

        play_numpy_array_dt(event_data, consumer, dt, dt_us)
    
    elif filename.endswith('.aedat4'):
        from dv import AedatFile

        # Invoke the import function
        aedat = AedatFile(filename)

        # get frame shape
        height, width = aedat['events'].size

        # events will be a named numpy array
        events = np.hstack([packet for packet in aedat['events'].numpy()])

        # create data structure to process into frames
        event_data = np.array([ 
            events['x'],
            events['y'],
            events['polarity'],
            events['timestamp']
        ]).transpose()

        # get frames if available
        try:
            frames = [(frame.image, frame.timestamp) for frame in aedat['frames']]
        except RuntimeError:
            frames = None

        consumer = event_consumer(width, height, consumer_args)

        if frames is not None:
            play_numpy_array_frames(event_data, consumer, frames)
        else:  
            play_numpy_array_dt(event_data, consumer, dt, dt_us)

    else:
        print("Error: provided input path '{}' does not have a known extension. ".format(filename))
        return -1

    # finish displaying events
    cv2.destroyAllWindows()
    return 0

def play_metavision_file(filename, dt, event_consumer, consumer_args):
    '''
    Begin file playback if we know it is a metavision .raw or .dat file
    '''
    import metavision_designer_engine as mvd_engine
    import metavision_designer_core as mvd_core
    import metavision_hal as mv_hal

    controller = mvd_engine.Controller()

    if filename.endswith('.dat'):
        cd_producer = mvd_core.FileProducer(filename)
        # get dimensions from file
        width = cd_producer.get_width()
        height = cd_producer.get_height()
    else:
        device = mv_hal.DeviceDiscovery.open_raw_file(filename)
        if not device:
            print(f"Error: could not open file '{filename}'.")
            sys.exit(1)

        # Add the device interface to the pipeline
        interface = mvd_core.HalDeviceInterface(device)
        controller.add_device_interface(interface)

        cd_producer = mvd_core.CdProducer(interface)

        # get dimensions from interface
        i_geom = device.get_i_geometry()
        width = i_geom.get_width()
        height = i_geom.get_height()

        # Start the streaming of events
        i_events_stream = device.get_i_events_stream()
        i_events_stream.start()

    # Add cd_producer to the pipeline
    controller.add_component(cd_producer, "CD Producer")
    # Create Frame Generator with accumulation time based on set dt
    frame_gen = mvd_core.FrameGenerator(cd_producer)
    frame_gen.set_dt(dt*1_000)
    controller.add_component(frame_gen, "FrameGenerator")

    # We use PythonConsumer to "grab" the output of two components: cd_producer and frame_gen
    # pyconsumer will callback the application each time it receives data, using the event_callback function
    ev_proc = event_consumer(width, height, consumer_args)
    pyconsumer = mvd_core.PythonConsumer(ev_proc.metavision_event_callback)
    pyconsumer.add_source(cd_producer, ev_proc.mv_cd_prod_name)
    pyconsumer.add_source(frame_gen, ev_proc.mv_frame_gen_name)
    controller.add_component(pyconsumer, "PythonConsumer")

    controller.set_slice_duration(dt*1_000)
    controller.set_batch_duration(dt*1_000)
    do_sync = True

    # Run pipeline & print execution statistics
    running = True
    while running and not controller.is_done():
        start_time = begin_loop()

        # process events
        controller.run(do_sync)
        
        # Render frame
        ev_proc.draw_frame()

        running = end_loop(start_time, dt)

def play_numpy_array_dt(event_data, consumer, dt, dt_us):
    '''
    Playback numpy array with the no frames and a fixed dt
    '''
    timestamps = event_data[:,3]
    num_events = len(timestamps)
    last_index = num_events-1
    ts = timestamps[0]

    running = True
    while running:
        start_time = begin_loop()
        
        # get indices for the current frame
        [frame_start, frame_end] = np.searchsorted(timestamps, [ts, ts+dt_us])
        # advance frame by dt
        ts += dt_us
        # end if we run out of events
        if frame_end >= last_index:
            frame_end = last_index
            running = False
        # process buffered events into frame
        consumer.process_event_array(ts, event_data[frame_start:frame_end,:])
        # draw frame with the events
        consumer.draw_frame()
        
        running = end_loop(start_time, dt)

def play_numpy_array_frames(event_data, consumer, frames):
    '''
    Playback numpy array with recorded frames (recorded frames determine dt)
    '''
    timestamps = event_data[:,3]
    num_events = len(timestamps)
    last_index = num_events-1
    frame_start_time = timestamps[0]
    frame_end_time = frames[0][1]
    frames_drawn = 0

    running = True
    while running:
        start_time = begin_loop()

        # get indices for the current frame
        [frame_start, frame_end] = np.searchsorted(timestamps, [frame_start_time, frame_end_time])
        
        # end if we run out of events
        if frame_end >= last_index:
            frame_end = last_index
            running = False
        # process buffered events into frame
        consumer.process_event_array(frame_end_time, event_data[frame_start:frame_end,:], frames[frames_drawn][0])
        # draw frame with the events
        consumer.draw_frame()
        
        # end the loop
        running = end_loop(start_time, (frame_end_time-frame_start_time)//1_000)

        # advance frame times
        frames_drawn += 1
        frame_start_time = frame_end_time
        # end if we're out of frames
        if frames_drawn >= len(frames):
            break
        frame_end_time = frames[frames_drawn][1]
    
    # end consumer execution
    consumer.end()

def begin_loop():
    '''
    Call at the beginning of each loop to mark frame start
    '''
    return time.time_ns() // 1_000_000 # time in msec

def end_loop(start_time, dt):
    '''
    Call at the end of each loop to evaluate time to process and display each frame
    '''
    end_time = time.time_ns() // 1_000_000 # time in msec
    end_of_frame = start_time + dt
    
    if end_time < end_of_frame:
        last_key = cv2.waitKey(end_of_frame-end_time)
        actual_dt = dt
    else:
        last_key = cv2.waitKey(1)
        actual_dt = end_time-start_time
    # update time elapsed
    sys.stdout.write(f'\rFrame time: {actual_dt:3}/{dt:2}(ms) ')
    sys.stdout.flush()

    # if 'q' key pressed -> quit application
    return not last_key == ord('q')