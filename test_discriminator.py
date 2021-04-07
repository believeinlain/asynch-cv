'''
Simple test of basic_consumer functionality
'''
import event_player
import event_processing

import xmltodict

aedat_path = 'C:/Users/steph/OneDrive/Documents/NIWC/NeuroComp/boat_tests/'
annot_path = './example_annotations/'
group = 'june_12'
test = 2

boat_tests = {
    'june_12':{
        1: 'Davis346red-2020-06-12T12-09-55-0700-0_Test_1',
        2: 'Davis346red-2020-06-12T12-11-45-0700-0_Test_2',
        3: 'Davis346red-2020-06-12T12-15-01-0700-0_Test_3',
        5: 'Davis346red-2020-06-12T12-24-03-0700-0_Test_5',
        6: 'Davis346red-2020-06-12T12-25-39-0700-0_Test_6',
        9: 'Davis346red-2020-06-12T12-55-32-0700-0_Test_9',
        10: 'Davis346red-2020-06-12T12-58-00-0700-0_Test_10',
        13: 'Davis346red-2020-06-12T13-04-12-0700-0_Test_13'
    },
    'june_26':{
        1: 'Davis346red-2020-06-26T12-25-58-0700-00000195-0_Test_1',
        2: 'Davis346red-2020-06-26T12-26-42-0700-00000195-0_Test_2',
        3: 'Davis346red-2020-06-26T12-27-39-0700-00000195-0_Test_3',
        4: 'Davis346red-2020-06-26T12-28-38-0700-00000195-0_Test_4',
        5: 'Davis346red-2020-06-26T12-29-49-0700-00000195-0_Test_5',
        6: 'Davis346red-2020-06-26T12-30-20-0700-00000195-0_Test_6',
        7: 'Davis346red-2020-06-26T12-30-41-0700-00000195-0_Test_7',
        8: 'Davis346red-2020-06-26T12-30-58-0700-00000195-0_Test_8',
        9: 'Davis346red-2020-06-26T12-32-12-0700-00000195-0_Test_9',
        16: 'Davis346red-2020-06-26T13-01-17-0700-00000195-0_Test_16',
        17: 'Davis346red-2020-06-26T13-03-06-0700-00000195-0_Test_17',
        19: 'Davis346red-2020-06-26T13-09-47-0700-00000195-0_Test_19',
        21: 'Davis346red-2020-06-26T13-22-40-0700-00000195-0_Test_21',
        23: 'Davis346red-2020-06-26T13-31-43-0700-00000195-0_Test_23'
    }
}

filename = group+'/'+boat_tests[group][test]

annot = None
with open(annot_path+filename+'.xml') as fd:
    doc = xmltodict.parse(fd.read())
    annot = doc['annotations']

event_player.play_file(
    # filename='example_data/Cars_sequence.aedat4',
    # filename='example_data/hand_spinner.raw',
    # filename='example_data/Davis346red-2020-06-12T12-31-10-0700-0_Test_7.aedat',
    filename=aedat_path+filename+'.aedat4',
    dt=50,  # exact 52.533375?
    event_consumer=event_processing.discriminator,
    consumer_args={
        'annotations': annot,
        'do_segmentation': True,
        'segmentation_parameters': {
            'region_lifetime': 80_000,
            'unassign_period': 1_000,
            'filter_n': 4,
            'filter_dt': 150_000,
            'v_range': 1,
            'min_region_weight': 15,
            'min_region_life': 150_000,
            'locale_size': 500
        }
    })
