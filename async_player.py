'''
Command line interface to use the async-cv tools
TODO: Implement consumer arguments from command line.
'''

import argparse

import event_player
import event_processing

parser = argparse.ArgumentParser(
    description='Play an Inivision *.aedat or Metavision *.dat or *.raw file \
    with optional processing.')
parser.add_argument('-p','--play', dest='filename',
    help='File to open.')
parser.add_argument('-c','--consumer', dest='consumer', default='basic_consumer',
    help='Specify which consumer to use.')
parser.add_argument('-l','--consumer-list', dest='list_consumers', action='store_true',
    help='List valid consumers.')
parser.add_argument('-a','--consumer-args', dest='consumer_args', 
    help='Specify arguments for the consumer.')

args = parser.parse_args()

if args.list_consumers:
    consumers = list(filter(lambda x: x.endswith('consumer'), dir(event_processing)))
    for consumer in consumers:
        consumer_class = getattr(event_processing, consumer)
        print(consumer_class.__name__, consumer_class.__doc__)

if args.filename is not None:
    if args.filename.endswith('.aedat'):
        play_function = event_player.play_aedat
    elif args.filename.endswith('.dat') or args.filename.endswith('.raw'):
        play_function = event_player.play_metavision
    else:
        print('Invalid file input specified. Please specify a .aedat, .raw, or .dat file.')
        exit(2)

    play_function(
        filename=args.filename,
        dt=30,
        event_consumer=getattr(event_processing, args.consumer),
        consumer_args=None
    )
