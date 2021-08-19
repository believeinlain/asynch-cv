function [a, b, c] = fitPower(x, y)

[xData, yData, weights] = prepareCurveData(x, y, 1./y);

% Set up fittype and options.
ft = fittype( 'power2' );
opts = fitoptions( 'Method', 'NonlinearLeastSquares' );
% opts.Display = 'Off';
opts.Robust = 'LAR';
opts.Weights = weights;

% Fit model to data.
[fitresult, ~] = fit( xData, yData, ft, opts );
c = num2cell(coeffvalues(fitresult));
[a, b, c] = deal(c{:});