function t = plotEvents(xLim, yLim, timeFrame, slice, pslice, colorSlice)

timeStamps = nonzeros(reshape(slice, [numel(slice) 1]));
t = max(timeStamps);
startTime = t - timeFrame;
dim = size(slice);

eventHeight = 3000;

for i=1:dim(1)
    for j=1:dim(2)
        for k=1:dim(3)
            if slice(i, j, k) ~= 0
                cubeShape = [0.90 0.90 eventHeight-1];
                centerX = double(xLim(1))+double(i)-0.95;
                centerY = double(yLim(1))+double(j)-0.95;
                centerT = double(slice(i, j, k)+1);
                cubeCenter = [centerX centerY centerT];
                cubeAlpha = 0.8;
                cubeColor = cell2mat(colorSlice(i, j));
                if i==ceil(dim(1)/2) && j==ceil(dim(2)/2) && k==dim(3)
                    cubeColor = [1.0 1.0 1.0];
                end
%                 if pslice(i, j, k) ~= 1
%                     cubeColor = cubeColor.*0.5;
%                 end
                plotcube(cubeShape, cubeCenter, cubeAlpha, cubeColor);
            end
        end
    end
end

xlim([xLim(1) xLim(2)+1]);
ylim([yLim(1) yLim(2)+1]);
zlim([startTime t+eventHeight]);
xlabel('y');
ylabel('x');
zlabel('t (us)');
