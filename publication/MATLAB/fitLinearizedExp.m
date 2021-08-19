function [m, b] = fitLinearizedExp(x, y)

[xData, yData] = prepareCurveData(x, y);

% Set up fittype and options.
ft = fittype('exp1');
opts = fitoptions('Method', 'NonlinearLeastSquares');

% Fit model to data.
[fitresult, ~] = fit( xData, yData, ft, opts );
c = num2cell(coeffvalues(fitresult));
[c1, c2] = deal(c{:});
b = log(c1);
m = c2;