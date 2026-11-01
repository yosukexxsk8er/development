module aaa(
    input clk,
    input rstn,
    output, cnt
    );


always @(posedge clk or negedge rstn) begin
    if(rstn) cnt = 0;
    else     cnt = cnt + 1;
end


endmodule



