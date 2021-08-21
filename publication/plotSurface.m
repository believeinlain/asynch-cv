function t = plotSurface(xLim, yLim, timeFrame, SAEslice, pslice, colorSlice)

timeStamps = nonzeros(reshape(SAEslice, [numel(SAEslice) 1]));
t = max(timeStamps);
startTime = t - timeFrame;
dim = size(SAEslice);

eventHeight = 3000;

bar3(SAEslice);

set(gca,'YTickLabel',xLim(1):1:xLim(2));
set(gca,'XTickLabel',yLim(1):1:yLim(2));
zlim([startTime t+eventHeight]);
xlabel('y (px)');
ylabel('x (px)');
zlabel('t (us)');
