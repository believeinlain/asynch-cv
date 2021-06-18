import metavision_designer_engine as mvd_engine
import metavision_designer_core as mvd_core
import metavision_hal as mv_hal
import time

#input_path = 'PATH_TO_DAT'  # use a DAT file
# input_path = 'PATH_TO_RAW'  # use a RAW file
input_path = ''  # use a live camera

# Check input
is_live_camera = is_raw = False
if input_path == '':
    is_live_camera = True
else:
    is_raw = input_path.endswith('.raw')

# Instantiate custom CD producer, depending on RAW/DAT format or live camera
cd_producer = None

# Create controller
controller = mvd_engine.Controller()

if is_raw or is_live_camera:
    # using a RAW file or a live camera requires the same steps

    # Open RAW file using Metavision Hardware Abstraction Layer
    if is_raw:
        mv_reader = mv_hal.DeviceDiscovery.open_raw_file(input_path)
        if mv_reader is None:
            raise RuntimeError('Failed to open RAW file: ' + input_path)
    elif is_live_camera:
        # Open camera
        mv_reader = mv_hal.DeviceDiscovery.open('')
        if not mv_reader:
            raise RuntimeError("Could not open camera. Make sure you have an event-based device plugged in")

    # from here on, it is transparent to the user whether it is a RAW file or a live camera

    # We can get the geometry of the source, if needed.
    i_geom = mv_reader.get_i_geometry()
    width = i_geom.get_width()
    height = i_geom.get_height()

    # Add interface to controller, to poll events from file
    polling_interval = 1e-3  # Interval to poll data from the camera in seconds
    mv_interface = mvd_core.HalDeviceInterface(mv_reader, polling_interval)

    # we need to add the device to the controller
    controller.add_device_interface(mv_interface)

    # Create Producer
    cd_producer = mvd_core.CdProducer(mv_interface)

    # Add producer to the pipeline
    controller.add_component(cd_producer, "CD Producer")

# Else, assume .dat file
if not (is_raw or is_live_camera):
    cd_producer = mvd_core.FileProducer(input_path)

    # We can get the size of the event stream, if needed.
    width = cd_producer.get_width()
    height = cd_producer.get_height()

    # Add producer to the pipeline
    controller.add_component(cd_producer, "CD Producer")

# Print on console, input path and geometry
if is_live_camera:
    print('Will read from a live camera with a %d x %d geometry' % (width, height))
else:
    print('Will read from %s with a %d x %d geometry' % (input_path, width, height))

# Create Frame Generator @25 FPS
frame_gen = mvd_core.FrameGenerator(cd_producer)
controller.add_component(frame_gen, "FrameGenerator")

# Create image display window
img_display = mvd_core.ImageDisplayCV(frame_gen)
img_display.set_name("Metavision Designer Events Player")
controller.add_component(img_display,"ImgDisplay")

# We need to access the **I_EventsStream** interface in order to start reading and streaming events from the file.\n",
i_events_stream = mv_reader.get_i_events_stream()
i_events_stream.start()

# Start the camera if needed
if is_live_camera:
    camera_device = mv_reader.get_i_device_control()
    camera_device.start()

# rendering
controller.add_renderer(img_display, mvd_engine.Controller.RenderingMode.SimulationClock, 25.)
controller.enable_rendering(True)

# Run pipeline & print execution statistics
done = False
cnt = 0
start_time = time.time()

controller.set_slice_duration(30000)
controller.set_batch_duration(30000)
do_sync = False if is_live_camera else True
while not (done or controller.is_done()):

    # Check if key pressed in window
    last_key = controller.get_last_key_pressed()

    # if 'q' key pressed -> quit application
    if last_key == ord('q'):
        done = True

    ini_time = controller.get_time()  # get current timestamp of the controller (which events we are processing)
    real_run_time = controller.run(do_sync)  # execute this loop and get the execution time
    theo_run_time = (controller.get_time() - ini_time) / 1e6  # computes the length in seconds of the events we processed
    cur_time = time.time()  # current clock time
    print("%.1f/%.1f : run_time = %f for %f s --> %f" % (controller.get_time() / 1e6,
                                                         cur_time - start_time,
                                                         real_run_time,
                                                         theo_run_time,
                                                         theo_run_time / real_run_time))
    cnt = cnt + 1
    if cnt % 500 == 0:
        controller.print_stats(False)

controller.print_stats(False)