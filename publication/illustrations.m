close all;

addpath 'C:\dev\PyAedatTools\frames';
load('frame299.mat');
% load('frame50.mat');

x = 237; y = 141; r = 4; timeFrame = 100000; % boat frame299
% x = 309; y = 152; r = 4; timeFrame = 100000; % boat frame50
% x = 158; y = 82; r = 4; timeFrame = 50000; % overactive pixel frame50

xLim = [x-r x+r];
yLim = [y-r y+r];
eventBuffer = rot90(flip(eventBuffer));
polarityBuffer = rot90(flip(polarityBuffer));
slice = eventBuffer(yLim(1):yLim(2), xLim(1):xLim(2), :);
pslice = polarityBuffer(yLim(1):yLim(2), xLim(1):xLim(2), :);

% calculate region colors
oneDHue = reshape(regionHue.',1,[]);
regionRGB = arrayfun(@(h) hsv2rgb([double((h~=-1)*h)/360.0 (h~=-1)*1.0 (h~=-1)*0.5+0.5]), regionHue,'UniformOutput',false);
regionRGBMatrix = cell2mat(arrayfun(@(x)permute(x{:},[3 1 2]),regionRGB,'UniformOutput',false));
sliceRGBMatrix = rot90(flip(regionRGB));
colorSlice = sliceRGBMatrix(yLim(1):yLim(2), xLim(1):xLim(2));

figure(1);
t = plotEvents(xLim, yLim, timeFrame, slice, pslice, colorSlice);
highlight_r = 3; highlight_dt = 100000;
plotcube([highlight_r highlight_r highlight_dt], ...
    [x-(highlight_r-1)/2 y-(highlight_r-1)/2 double(t-highlight_dt)], 0.5, [1 0 0]);

% draw an event at x,y to represent the event being considered
% plotcube([0.9 0.9 3000], double([x y t])+[0.05, 0.05, 2.0], 0.8, [1.0 1.0 1.0]);

set(gca,'YTickLabel',xLim(1):2:xLim(2));
set(gca,'XTickLabel',yLim(1):2:yLim(2));
view(45, 73);

% figure(2);
% SAE = rot90(flip(SAE));
% SAEslice = SAE(yLim(1):yLim(2), xLim(1):xLim(2));
% plotSurface(xLim, yLim, timeFrame, SAEslice, pslice, colorSlice);
% plotcube([3.01 3.01 50.01], [237 139 8950], 0.5, [1 0 0]);

% draw frame from buffer
figure(3);
image(rot90(flip(regionRGBMatrix)),'CDataMapping','scaled');
rectangle('Position', [x-r-0.5 y-r+0.5 2*r+1 2*r+1], 'EdgeColor', 'r');
xlabel('x');
ylabel('y');
% rectangle('Position', [x-highlight_r/2 y-highlight_r/2 highlight_r highlight_r], 'EdgeColor', 'r');
