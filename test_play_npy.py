'''
Simple test of basic_consumer functionality
'''
import event_player
import event_processing

event_player.play_npy(
    filename='spinner.npy',
    dt=30,
    event_consumer=event_processing.basic_consumer
)
