
import numpy as np

# Input parameters
X_DIVISIONS = 4; # Number of horizontal divisions
Y_DIVISIONS = 4; # Number of vertical divisions
EVENT_BUFFER_DEPTH = 4; # How many events per (x, y) can the buffer hold

# Data type constants
DIV_T = 'u1'
XY_T = 'u2'
TIMESTAMP_T = 'u8'
CLUSTER_ID_T = 'u2'
BUFFER_DEPTH_T = 'u1'

# Dependent constants
UNASSIGNED_CLUSTER = np.iinfo(np.dtype(CLUSTER_ID_T)).max
MAX_CLUSTERS = UNASSIGNED_CLUSTER+1

# Structs
EVENT_T = [
  ('x', XY_T), 
  ('y', XY_T),
  ('p', '?'),
  ('t', TIMESTAMP_T)
]

EVENT_BUFFER_T = [
  ('t', TIMESTAMP_T),
  ('c', CLUSTER_ID_T)
]