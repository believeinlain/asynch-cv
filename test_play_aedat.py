'''
Simple test of basic_consumer functionality
'''
import event_player

event_player.play_aedat(
    filename='example_data/Davis346red-2020-06-12T12-31-10-0700-0_Test_7.aedat',
    dt=30,
    event_consumer=event_player.basic_consumer)
