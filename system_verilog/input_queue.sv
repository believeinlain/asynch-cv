
`include "globals.sv"

module InputQueue (
  input event_t in_event;
  input push,
  input pop,
  input clk;
  output event_t front_event;
);
  parameter I_BITS = log2(INPUT_QUEUE_DEPTH);

  event queue [INPUT_QUEUE_DEPTH];
  bit [I_BITS-1:0] front = 0;
  bit [I_BITS-1:0] back = 0;

  // Assign the output to the oldest event in the queue
  assign front_event = queue[back];

  always_ff @(posedge clk) begin
    // Update the queue after getting an event
    if (pop) begin
      back <= back + 1;
    end

    // Add a new event to the queue
    if (push) begin
      front = front + 1;
      queue[front] = in_event;
      // if we ran out of space, forget the oldest event
      if (front == back) begin
        back = back + 1;
      end
    end
  end

endmodule
