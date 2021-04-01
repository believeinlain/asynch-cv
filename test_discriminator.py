'''
Simple test of basic_consumer functionality
'''
import event_player
import event_processing

import xmltodict

annot_path = 'example_annotations/june26_boat_tests_xml/'
aedat_path = 'C:/Users/steph/OneDrive/Documents/NIWC/NeuroComp/AEDATA_11-12-20/'
filename_1 = 'Davis346red-2020-06-26T12-25-58-0700-00000195-0_Test_1'
filename_2 = 'Davis346red-2020-06-26T12-26-42-0700-00000195-0_Test_2'
filename_3 = 'Davis346red-2020-06-26T12-27-39-0700-00000195-0_Test_3'
filename_4 = 'Davis346red-2020-06-26T12-28-38-0700-00000195-0_Test_4'
# filename_5 = 'Davis346red-2020-06-26T12-30-20-0700-00000195-0_Test_5'
filename_6 = 'Davis346red-2020-06-26T12-30-20-0700-00000195-0_Test_6'
filename_7 = 'Davis346red-2020-06-26T12-30-41-0700-00000195-0_Test_7'
filename_8 = 'Davis346red-2020-06-26T12-30-58-0700-00000195-0_Test_8'
filename_9 = 'Davis346red-2020-06-26T12-32-12-0700-00000195-0_Test_9'
filename_16 = 'Davis346red-2020-06-26T13-01-17-0700-00000195-0_Test_16'
filename_17 = 'Davis346red-2020-06-26T13-03-06-0700-00000195-0_Test_17'
# filename_19 = 'Davis346red-2020-06-26T13-09-47-0700-00000195-0_Test_19_Airplane'
filename_21 = 'Davis346red-2020-06-26T13-22-40-0700-00000195-0_Test_21'
# filename_23 = 'Davis346red-2020-06-26T13-31-43-0700-00000195-0_Test_23'

filename = filename_2

annot = None
with open(annot_path+filename+'.xml') as fd:
    doc = xmltodict.parse(fd.read())
    annot = doc['annotations']

event_player.play_file(
    # filename='example_data/Cars_sequence.aedat4',
    # filename='example_data/hand_spinner.raw',
    # filename='example_data/Davis346red-2020-06-12T12-31-10-0700-0_Test_7.aedat',
    filename=aedat_path+filename+'.aedat',
    dt=105,  # exact 52.533375?
    event_consumer=event_processing.discriminator,
    consumer_args={
        'annotations': annot,
        'do_segmentation': False
    })
