'''
Simple test of basic_consumer functionality
'''
import event_player
import event_processing
import os

aedat_path = f'C:/Users/Stephanie/OneDrive/Documents/NIWC/NeuroComp/boat_tests/'
annot_path = './example_annotations/'
group = 'april_29'
test = 2
file_type = '.raw'

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
    },
    'april_29':{
        1: 'out_2021-04-29_17-56-14',
        2: 'out_2021-04-29_17-57-47',
        3: 'out_2021-04-29_18-02-48',
        4: 'out_2021-04-29_18-04-41',
        5: 'out_2021-04-29_18-06-47',
        6: 'out_2021-04-29_18-10-59',
        7: 'out_2021-04-29_18-17-21',
        8: 'out_2021-04-29_18-20-10'
    }
}

for i in range(7, 8):
    filename = group+'/'+boat_tests[group][i]
    run_name = f'{group}_run_{i:02d}'

    event_player.play_file(
        filename=aedat_path+filename+file_type,
        dt=30,
        event_consumer=event_processing.pmd_consumer,
        consumer_args={
            'run_name': run_name,
            'video_out': run_name+'.avi',
            'parameters': {
                'x_div': 8,
                'y_div': 8,
                'input_queue_depth': 128,
                'event_buffer_depth': 4,
                'tf': 200_000, # how far back in time to consider events for filtering
                'n': 4, # minimum number of correlated events required to allow a particular event through the filter
                'tc': 200_000, # how far back in time to consider events for clustering
                'num_cluster_analyzers': 16,
                'temporal_filter': 500,
                'cluster_profile_length': 32,
                'stability_threshold': 1.5,
                'stability_loss_rate': 0.1,
                'confidence_rate': 0.05,
                'confidence_threshold': 0.75,
                'merge_clusters': False
            }
        })