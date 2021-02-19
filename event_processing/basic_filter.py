
import numpy as np

class basic_filter:
    '''
    Only allows events through if that location has not allowed an event within time threshold
    '''

    def __init__(self, width, height, threshold):
        self.dt = threshold
        self.surface = np.zeros((width, height), dtype=np.uint)
    
    def is_event_allowed(self, event):
        '''
        Determines if an event is filtered out.

        Parameters:
            event: tuple or array or list in the form ('x','y','p','t')

        Returns:
            True if the event should be allowed, False if the event should be filtered out
        '''
        # unpack for readability
        (x, y, p, t) = event
        # p is currently unused
        del p

        # allow the event only if we havent allowed an event through within dt
        if self.surface[x, y] + self.dt < t:
            self.surface[x, y] = t
            return True
        else:
            return False
        