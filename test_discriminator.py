'''
Simple test of basic_consumer functionality
'''
import event_player
import event_processing

import xmltodict

annot = 'example_annotations/june26_boat_tests_xml/Davis346red-2020-06-26T12-26-42-0700-00000195-0_Test_2.xml'
with open(annot) as fd:
  doc = xmltodict.parse(fd.read())

  event_player.play_file(
    # filename='example_data/Cars_sequence.aedat4',
    # filename='example_data/hand_spinner.raw',
    # filename='example_data/Davis346red-2020-06-12T12-31-10-0700-0_Test_7.aedat',
    # filename='C:/Users/steph/OneDrive/Documents/NIWC/NeuroComp/AEDATA_11-12-20/Davis346red-2020-06-26T12-30-20-0700-00000195-0_Test_6.aedat',
    filename='C:/Users/steph/OneDrive/Documents/NIWC/NeuroComp/AEDATA_11-12-20/Davis346red-2020-06-26T12-26-42-0700-00000195-0_Test_2.aedat',
    dt=105, # exact 52.533375?
    event_consumer=event_processing.discriminator,
    consumer_args=doc['annotations'])
