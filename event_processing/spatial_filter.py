
import numpy as np

class spatial_filter:
    '''
    '''

    def __init__(self, width, height, threshold):
        self.dt = threshold
        self.width = width
        self.height = height
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

        # temporal pre-filtering before updating surface
        if self.surface[x, y] + self.dt < t:

            nearby_depth = 100_000
            neighbor_depth = 10_000
            nearby_range = 1
            neighbor_range = 3
            min_nearby = 2
            neighbor_effect = 0.5
            
            # query nearby for surrounding events
            row = np.arange(x-nearby_range, x+nearby_range+1).clip(0, self.width-1)
            col = np.arange(y-nearby_range, y+nearby_range+1).clip(0, self.height-1)

            nearby = self.surface[row[:, np.newaxis], col]
            nearby_count = nearby[nearby>t-nearby_depth].size

            # query neighborhood for surrounding events
            row = np.arange(x-neighbor_range, x+neighbor_range+1).clip(0, self.width-1)
            col = np.arange(y-neighbor_range, y+neighbor_range+1).clip(0, self.height-1)

            neighbor = self.surface[row[:, np.newaxis], col]
            neighbor_count = neighbor[neighbor>t-neighbor_depth].size

            # update the surface
            self.surface[x, y] = t

            if nearby_count > neighbor_count*neighbor_effect + min_nearby:
                return True

        else:
            return False