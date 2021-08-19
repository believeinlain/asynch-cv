
ang = -pi:0.01:pi;
mag = 0:0.01:2;

[X, Y] = meshgrid(ang, mag);
Z = X;

long_v = [1 0];
for a = 1:length(ang)
    for m = 1:length(mag)
        short_v = [mag(m)*cos(ang(a)) mag(m)*sin(ang(a))];
        diff_v = long_v - short_v;
        ratio(m, a) = min(1/norm(diff_v), 50);
        dot_ratio(m, a) = dot(long_v, short_v) / ...
            sqrt(dot(long_v, long_v)*dot(short_v, short_v));
    end
end

figure;
surf(X,Y,ratio,'EdgeColor','none');
xlim([-pi pi]);
xlabel('angle offset (rad)');
ylabel('magnitude multiple (relative)');

figure;
surf(X,Y,dot_ratio,'EdgeColor','none');
xlim([-pi pi]);
xlabel('angle offset (rad)');
ylabel('magnitude multiple (relative)');