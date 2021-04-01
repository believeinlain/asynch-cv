'''
Simple test of basic_consumer functionality
'''
import event_player
import event_processing

import xmltodict


aedat_path = 'C:/Users/steph/OneDrive/Documents/NIWC/NeuroComp/AEDATA_11-12-20/'

annot_path_jun26 = 'example_annotations/june26_boat_tests_xml/'
jun26_1 = 'Davis346red-2020-06-26T12-25-58-0700-00000195-0_Test_1'
jun26_2 = 'Davis346red-2020-06-26T12-26-42-0700-00000195-0_Test_2'
jun26_3 = 'Davis346red-2020-06-26T12-27-39-0700-00000195-0_Test_3'
jun26_4 = 'Davis346red-2020-06-26T12-28-38-0700-00000195-0_Test_4'
# jun26_5 = 'Davis346red-2020-06-26T12-30-20-0700-00000195-0_Test_5'
jun26_6 = 'Davis346red-2020-06-26T12-30-20-0700-00000195-0_Test_6'
jun26_7 = 'Davis346red-2020-06-26T12-30-41-0700-00000195-0_Test_7'
jun26_8 = 'Davis346red-2020-06-26T12-30-58-0700-00000195-0_Test_8'
jun26_9 = 'Davis346red-2020-06-26T12-32-12-0700-00000195-0_Test_9'
jun26_16 = 'Davis346red-2020-06-26T13-01-17-0700-00000195-0_Test_16'
jun26_17 = 'Davis346red-2020-06-26T13-03-06-0700-00000195-0_Test_17'
# filename_19 = 'Davis346red-2020-06-26T13-09-47-0700-00000195-0_Test_19_Airplane'
jun26_21 = 'Davis346red-2020-06-26T13-22-40-0700-00000195-0_Test_21'
# filename_23 = 'Davis346red-2020-06-26T13-31-43-0700-00000195-0_Test_23'
# filename = jun26_2

annot_path_jun12 = 'example_annotations/june12_boat_tests_xml/'
jun12_1 = 'Davis346red-2020-06-12T12-09-55-0700-0_Test_1'
jun12_2 = 'Davis346red-2020-06-12T12-11-45-0700-0_Test_2'
jun12_3 = 'Davis346red-2020-06-12T12-15-01-0700-0_Test_3'
jun12_4 = 'Davis346red-2020-06-12T12-21-47-0700-0_Test_4'
jun12_5 = 'Davis346red-2020-06-12T12-24-03-0700-0_Test_5'
jun12_6 = 'Davis346red-2020-06-12T12-25-39-0700-0_Test_6'
jun12_7 = 'Davis346red-2020-06-12T12-31-10-0700-0_Test_7'
jun12_8 = 'Davis346red-2020-06-12T12-33-22-0700-0_Test_8'
jun12_13 = 'Davis346red-2020-06-12T13-04-12-0700-0_Test_13'
filename = jun12_2

annot_path = annot_path_jun12

annot = None
with open(annot_path+filename+'.xml') as fd:
    doc = xmltodict.parse(fd.read())
    annot = doc['annotations']

event_player.play_file(
    # filename='example_data/Cars_sequence.aedat4',
    # filename='example_data/hand_spinner.raw',
    # filename='example_data/Davis346red-2020-06-12T12-31-10-0700-0_Test_7.aedat',
    filename=aedat_path+filename+'.aedat',
    dt=53,  # exact 52.533375?
    event_consumer=event_processing.discriminator,
    consumer_args={
        'annotations': annot,
        'do_segmentation': False
    })
