'''
Simple test of basic_consumer functionality
'''
import event_player
import event_processing

event_player.play_file(
    # filename='example_data/Cars_sequence.aedat4',
    # filename='example_data/Davis346red-2020-06-12T12-31-10-0700-0_Test_7.aedat',
    # filename='example_data/hand_spinner.raw',
    # filename='C:/Users/steph/OneDrive/Documents/NIWC/NeuroComp/AEDATA_11-12-20/Davis346red-2020-06-26T12-30-20-0700-00000195-0_Test_6.aedat',
    # filename='C:/Users/steph/OneDrive/Documents/NIWC/NeuroComp/AEDATA_11-12-20/Davis346red-2020-06-26T12-26-42-0700-00000195-0_Test_2.aedat',
    filename='C:/Users/steph/OneDrive/Documents/NIWC/NeuroComp/boat_tests/april_29/out_2021-04-29_17-56-14.raw',
    dt=30,
    event_consumer=event_processing.basic_consumer)
