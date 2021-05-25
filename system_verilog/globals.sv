
// Input parameters
parameter SENSOR_WIDTH = 640; // prophessee camera has 640*480 sensor
parameter SENSOR_HEIGHT = 480;
parameter INPUT_QUEUE_DEPTH = 32; // how many events can we hold for each Event Handler
parameter X_DIVISIONS = 4; // Number of horizontal divisions
parameter Y_DIVISIONS = 4; // Number of vertical divisions
parameter EVENT_BUFFER_DEPTH = 4; // How many events per (x, y) can the buffer hold
parameter CLUSTER_ID_BITS = 16; // How many bits to store each cluster ID
parameter T_BITS = 64; // prophessee camera uses long long (64-bit) timestamps

// Dependent constants
parameter X_DIV_BITS = $clog2(X_DIVISIONS);
parameter Y_DIV_BITS = $clog2(Y_DIVISIONS);
parameter EB_DEPTH_BITS = $clog2(EVENT_BUFFER_DEPTH);
parameter MAX_CLUSTERS = 2**CLUSTER_ID_BITS;
parameter XY_BITS = $clog2(max(SENSOR_WIDTH, SENSOR_HEIGHT));

// Structs
typedef struct packed {
  bit [XY_BITS-1:0] x = 0, 
  bit [XY_BITS-1:0] y = 0,
  bit p = 0,
  bit [T_BITS-1] t = 0, 
} event_t;

typedef struct packed {
  bit [XY_BITS-1:0] x;
  bit [XY_BITS-1:0] y;
  bit [EB_DEPTH_BITS-1:0] depth;
} event_buffer_addr;

typedef struct packed {
  bit [T_BITS-1:0] = 0; 
  bit [CLUSTER_ID_BITS-1:0] = -1; 
} event_buffer_entry;
