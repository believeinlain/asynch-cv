`timescale 1ns / 1ps

module input_queue # (
    parameter X_BITS = 16,
    parameter Y_BITS = 16,
    parameter T_BITS = 64,
    parameter DEPTH = 64
) (
    input [X_BITS-1:0] x_in,
    input [Y_BITS-1:0] y_in,
    input p_in,
    input [T_BITS-1:0] t_in,
    input clk,
    input do_push,
    input do_pop,
    input [X_BITS-1:0] x_front,
    input [Y_BITS-1:0] y_front,
    input p_front,
    input [T_BITS-1:0] t_front
);
    typedef struct packed {
        bit [X_BITS-1:0] x; 
        bit [Y_BITS-1:0] y;
        bit p;
        bit [T_BITS-1:0] t;
    } event_t;
    
    localparam Q_BITS = $clog2(DEPTH);
    
    bit [Q_BITS-1:0] front = 0;
    bit [Q_BITS-1:0] back = 0;
    event_t queue [DEPTH];
    
    assign {x_front, y_front, p_front, t_front} = queue[back];
    
    always_ff @ (posedge clk) begin
        // Update the queue after reading an event
        if (do_pop) begin
            back++;
        end
        // Add a new event to the queue
        if (do_push) begin
            front++;
            queue[front] = {x_in, y_in, p_in, t_in};
            // if we ran out of space, forget the oldest event
            if (front == back) begin
                back++;
            end
        end
    end
    
endmodule