'''
Simple test of basic_consumer functionality
'''
import event_player
import event_processing

event_player.play_file(
    filename='example_data/hand_spinner.raw',
    dt=30,
    event_consumer=event_processing.basic_consumer)
