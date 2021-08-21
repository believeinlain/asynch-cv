load('buffer.mat')
flat = squeeze(sum(event,3));
L = logical(flat>0);
imshow(L);