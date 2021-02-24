'''
Command line interface to use the async-cv tools.
Doesn't work for more complex consumers yet
'''

import argparse

import event_player
import event_processing

parser = argparse.ArgumentParser(
    description='Play an Inivision *.aedat or Metavision *.dat or *.raw file \
    with optional processing. Press \'q\' to quit during playback.')
parser.add_argument('-p','--play', dest='filename',
    help='File to open.')
parser.add_argument('-c','--consumer', dest='consumer', default='basic_consumer',
    help='Specify which consumer to use.')
parser.add_argument('-l','--consumer-list', dest='list_consumers', action='store_true',
    help='List valid consumers.')
# parser.add_argument('-a', '--consumer-args', dest='consumer_args', type=str, nargs='*',
#     help='Specify arguments for the consumer.')

args = parser.parse_args()

if args.list_consumers:
    consumers = list(filter(lambda x: x.endswith('consumer'), dir(event_processing)))
    for consumer in consumers:
        consumer_class = getattr(event_processing, consumer)
        print(consumer_class.__name__, consumer_class.__doc__)

if args.filename is not None:
    event_player.play_file(
        filename=args.filename,
        dt=30,
        event_consumer=getattr(event_processing, args.consumer),
        consumer_args=args.consumer_args
    )
