from os import path
import sys
import metavision_designer_engine as mvd_engine
import metavision_designer_core as mvd_core
import metavision_hal as mv_hal

import cv2

from event_consumer import EventConsumer

input_filename = 'spinner.dat'
#input_filename = "PATH_TO_RAW"

# Check validity of input arguments
if not(path.exists(input_filename) and path.isfile(input_filename)):
    print("Error: provided input path '{}' does not exist or is not a file.".format(input_filename))
    sys.exit(1)

is_raw = input_filename.endswith('.raw')
is_dat = input_filename.endswith('.dat')

if not (is_raw or is_dat):
    print("Error: provided input path '{}' does not have the right extension. ".format(input_filename) +
            "It has either to be a .raw or a .dat file")
    sys.exit(1)

controller = mvd_engine.Controller()

if is_dat:
    cd_producer = mvd_core.FileProducer(input_filename)
else:
    device = mv_hal.DeviceDiscovery.open_raw_file(input_filename)
    if not device:
        print("Error: could not open file '{}'.".format(input_filename))
        sys.exit(1)

    # Add the device interface to the pipeline
    interface = mvd_core.HalDeviceInterface(device)
    controller.add_device_interface(interface)

    cd_producer = mvd_core.CdProducer(interface)

    # Start the streaming of events
    i_events_stream = device.get_i_events_stream()
    i_events_stream.start()

# Add cd_producer to the pipeline
controller.add_component(cd_producer, "CD Producer")
# Create Frame Generator with 20ms accumulation time
frame_gen = mvd_core.FrameGenerator(cd_producer)
frame_gen.set_dt(20000)
controller.add_component(frame_gen, "FrameGenerator")

# We use PythonConsumer to "grab" the output of two components: cd_producer and frame_gen
# pyconsumer will callback the application each time it receives data, using the event_callback function
ev_proc = EventConsumer(cd_producer.get_width(), cd_producer.get_height())
pyconsumer = mvd_core.PythonConsumer(ev_proc.metavision_event_callback)
pyconsumer.add_source(cd_producer, ev_proc.mv_cd_prod_name)
pyconsumer.add_source(frame_gen, ev_proc.mv_frame_gen_name)
controller.add_component(pyconsumer, "PythonConsumer")

controller.set_batch_duration(40000)
do_sync = True

# Run pipeline & print execution statistics
while not controller.is_done():

    controller.run(do_sync)

    # Render frame
    ev_proc.draw_frame()

cv2.destroyAllWindows()