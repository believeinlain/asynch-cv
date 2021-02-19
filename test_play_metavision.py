'''
Simple test of basic_consumer functionality
'''
import event_player

event_player.play_metavision(
    filename='example_data/hand_spinner.raw',
    dt=30,
    event_consumer=event_player.basic_consumer)
