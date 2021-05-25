
`include "globals.sv"

module moduleName (
  input event_buffer_entry in_event;
  input event_buffer_addr addr;
  input specify_depth;
  input add_event;
  input clk;
  output event_buffer_entry out_event;
);
  event_buffer_entry buffer [SENSOR_WIDTH][SENSOR_HEIGHT];
  bit [EB_DEPTH_BITS-1:0] buffer_top [SENSOR_WIDTH][SENSOR_HEIGHT];
  
  // Assign the output to the value at the specified address
  assign out_event = buffer[addr.x][addr.y][specify_depth ? addr.depth : buffer_top[addr.x][addr.y]];

  // Update the buffer
  always_ff @(posedge clk) begin
    if (add_event) begin
      
    end
  end
  
endmodule