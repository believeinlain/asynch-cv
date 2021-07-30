"""Module containing the play_file() function, which is used as an abstraction \
layer to playback various event data formats and feed events to an event \
consumer class.
"""

# Ignore warnings for packages not found, since support for everything is optional
# pyright: reportMissingImports=false

from os import path
import sys
from time import time_ns
import cv2
import numpy as np
from pynput.keyboard import Listener, KeyCode

from async_cv.event_processing.basic_consumer import basic_consumer


def play_file(filename: str, dt: int, event_consumer: basic_consumer, **kwargs):
    """ Play a recorded event stream in any of the supported formats.

    Currently Metavision live, .dat, .raw and Inivation .aedat4 are supported.

    Args:
        filename (str): Path to the file to be played. \
            Use filename='' to play a live feed.
        dt (int): Number of milliseconds to collect for each displayed frame. \
            If the file has frames, this argument will be ignored and events \
            will be synchronized to the existing framerate.
        event_consumer (basic_consumer): The consumer class to use to process \
            and display events. Any class inheriting basic_consumer can be \
            used here.
        **kwargs: Optional arguments to pass to the consumer. \
            If none given, defaults will be used.

    Returns:
        -1 if a fatal error occurs, 0 if successful.
    """
    # define the callback function
    def on_press(key):
        global is_running
        if key == KeyCode.from_char('q'):
            is_running = False
            return False
            
    # start the keyboard listener
    listener = Listener(on_press=on_press)
    listener.start()
    global is_running
    is_running = True

    # play live camera if no filename provided
    if filename is '':
        return play_metavision_live(dt, event_consumer, **kwargs)

    # Check validity of input arguments
    if not(path.exists(filename) and path.isfile(filename)):
        print(
            f'Error: provided input path "{filename}" does not exist or is not a file.')
        return -1

    print(f'Playing file "{filename}".')

    if filename.endswith('.raw') or filename.endswith('.dat'):
        play_metavision_file(filename, dt, event_consumer, **kwargs)

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

        # play with frames
        frames = [(frame.image, frame.timestamp)
                  for frame in aedat['frames']]

        consumer = event_consumer(width, height, **kwargs)

        play_numpy_array_frames(event_data, consumer, frames)

    else:
        print(f'Error: provided input path "{filename}" \
            does not have a known extension.')
        return -1

    return 0


def play_metavision_live(dt, event_consumer, **kwargs):
    """Begin playback of a live feed from a Prophesee camera"""

    import metavision_designer_engine as mvd_engine
    import metavision_designer_core as mvd_core
    import metavision_hal as mv_hal

    controller = mvd_engine.Controller()

    device = mv_hal.DeviceDiscovery.open('')
    if not device:
        print('Could not open camera. Make sure you have an event-based \
            device plugged in.')
        return -1

    # Add the device interface to the pipeline
    interface = mvd_core.HalDeviceInterface(device)
    controller.add_device_interface(interface)

    cd_producer = mvd_core.CdProducer(interface)

    # get dimensions from interface
    i_geom = device.get_i_geometry()
    width = i_geom.get_width()
    height = i_geom.get_height()

    # set biases
    biases = device.get_i_ll_biases()
    biases.set('bias_diff_off', 0)
    biases.set('bias_diff_on', 400)

    # Start the streaming of events
    i_events_stream = device.get_i_events_stream()
    i_events_stream.start()

    # Add cd_producer to the pipeline
    controller.add_component(cd_producer, 'CD Producer')

    # We use PythonConsumer to "grab" the output of two components: cd_producer and frame_gen
    # pyconsumer will callback the application each time it receives data, using the event_callback function
    ev_proc = event_consumer(width, height, **kwargs)
    pyconsumer = mvd_core.PythonConsumer(ev_proc.metavision_event_callback)
    pyconsumer.add_source(cd_producer, ev_proc.mv_cd_prod_name)
    controller.add_component(pyconsumer, 'PythonConsumer')

    controller.set_slice_duration(dt*1000)
    controller.set_batch_duration(dt*1000)
    # controller.set_sync_mode(mvd_engine.Controller.SyncMode(1))
    do_sync = True

    # Start the camera
    camera_device = device.get_i_device_control()
    camera_device.start()

    # Run pipeline & print execution statistics
    global is_running
    while is_running and not controller.is_done():
        start_time = begin_loop()

        # process events
        controller.run(do_sync)

        # Render frame
        ev_proc.draw_frame()

        end_loop(start_time, dt)

    controller.print_stats(False)

    ev_proc.end()

    return 0


def play_metavision_file(filename, dt, event_consumer, **kwargs):
    """Begin file playback of a metavision .raw or .dat file"""

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
            print(f'Error: could not open file "{filename}".')
            return -1

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
    controller.add_component(cd_producer, 'CD Producer')

    # We use PythonConsumer to "grab" the output of two components: cd_producer and frame_gen
    # pyconsumer will callback the application each time it receives data, using the event_callback function
    ev_proc = event_consumer(width, height, **kwargs)
    pyconsumer = mvd_core.PythonConsumer(ev_proc.metavision_event_callback)
    pyconsumer.add_source(cd_producer, 'CDProd')
    controller.add_component(pyconsumer, 'PythonConsumer')

    controller.set_slice_duration(dt*1_000)
    controller.set_batch_duration(dt*1_000)
    do_sync = True

    # Run pipeline & print execution statistics
    global is_running
    while is_running and not controller.is_done():
        start_time = begin_loop()

        # process events
        controller.run(do_sync)

        # Render frame
        ev_proc.draw_frame()

        end_loop(start_time, dt)

    ev_proc.end()

    return 0


def play_numpy_array_frames(event_data, consumer, frames):
    """Playback numpy array with recorded frames"""

    timestamps = event_data[:, 3]
    num_events = len(timestamps)
    last_index = num_events-1
    frame_start_time = timestamps[0]
    frame_end_time = frames[0][1]
    frames_drawn = 0

    global is_running
    while is_running:
        start_time = begin_loop()

        # get indices for the current frame
        [frame_start, frame_end] = np.searchsorted(
            timestamps, [frame_start_time, frame_end_time])

        # end if we run out of events
        if frame_end >= last_index:
            frame_end = last_index
            is_running = False
        # process buffered events into frame
        event_array = event_data[frame_start:frame_end, :]
        struct_array = np.core.records.fromarrays(
            event_array.transpose(),
            dtype=np.dtype({
                'names': ['x', 'y', 'p', 't'],
                'formats': ['u2', 'u2', 'i2', 'i8'],
                'offsets': [0, 2, 4, 8],
                'itemsize': 16
            })
        )
        consumer.process_buffers(struct_array, frames[frames_drawn][0])
        # draw frame with the events
        consumer.draw_frame()

        # end the loop
        end_loop(start_time, (frame_end_time-frame_start_time)//1_000)

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
    """Call at the beginning of each loop to mark frame start"""

    return time_ns() // 1_000_000  # time in msec


def end_loop(start_time, dt):
    """Call at the end of each loop to evaluate time to process and display \
    the frame.
    """

    end_time = time_ns() // 1_000_000  # time in msec
    end_of_frame = start_time + dt

    if end_time < end_of_frame:
        cv2.waitKey(end_of_frame-end_time)
    else:
        cv2.waitKey(1)

    # update time elapsed
    sys.stdout.write(f'\rFrame time: {end_time-start_time:3}/{dt:2}(ms)')
    sys.stdout.flush()
