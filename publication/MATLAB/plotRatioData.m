function plotRatioData(ratio)

% count data points
[counts, edges] = histcounts(ratio, 'BinMethod', 'fd');
% interpolate between edges
x = edges + (edges(2)-edges(1))/2;
x(end) = [];
% take the log of counts
log_counts = log(counts);
log_counts(log_counts<=0) = NaN;
log_log_counts = log(log_counts);

% linearize an exponential fit
[m, b] = fitLinearizedExp(x, log_counts);

figure();
hold on;
scatter(x, log_log_counts);
plot(x, m*x+b);
