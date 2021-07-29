"""Event processing module.

This module contains classes for receiving input events and displaying them \
or processing them further. Consumer classes are derived from the \
basic_consumer class.

Per-event computation should be restricted to compiled extensions. The \
draw_events module is an example. It is written in Cython so that events can \
be displayed as they are recieved without making calls to the Python Runtime \
Environment for each event.

"""
