
`include "globals.sv"

// Given an event, determines the target queue and event handler
module EventStream (
  input event_t in_event;
  output [X_DIV_BITS-1:0] x_dest,
  output [Y_DIV_BITS-1:0] y_dest,
);
  parameter [XY_BITS-1:0] X_BOUNDARIES [X_DIVISIONS] = x_bound();
  parameter [XY_BITS-1:0] Y_BOUNDARIES [Y_DIVISIONS] = y_bound();

  typedef bit [XY_BITS-1:0] x_div_t [X_DIVISIONS];
  function x_div_t x_bound();
    for(int i=0; i<X_DIVISIONS; i++)
      result[i] = (SENSOR_WIDTH/X_DIVISIONS)*i;
  endfunction : result

  typedef bit [XY_BITS-1:0] y_div_t [Y_DIVISIONS];
  function y_div_t y_bound();
    for(int i=0; i<Y_DIVISIONS; i++)
      result[i] = (SENSOR_HEIGHT/Y_DIVISIONS)*i;
  endfunction : result

  always_comb begin : assignX
    x_dest = 0;
    for (int i=0; i<X_DIV; i++) begin
      if (x <= X_BOUNDARIES[i]) begin
        x_dest = i;
        break;
      end
    end
  end

  always_comb begin : assignY
    y_dest = 0;
    for (int i=0; i<Y_DIV; i++) begin
      if (y <= Y_BOUNDARIES[i]) begin
        y_dest = i;
        break;
      end
    end
  end

endmodule
