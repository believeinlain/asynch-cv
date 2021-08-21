
%% Read data
text = importdata('june_12_run_03.json');
data = jsondecode(text{1});
cluster = struct2table(data.x16884); 
n = length(cluster.frame);

%% Compute analysis results
long_v = [cluster.long_v_x, cluster.long_v_y];
short_v = [cluster.short_v_x, cluster.short_v_y];
diff_v = long_v - short_v;

ratio = zeros(n, 0);
ratio_sq = zeros(n, 0);
dot_ratio = zeros(n, 0); 
for ii = 1:n
    ratio_sq(ii) = norm(long_v(ii,:))^2/norm(diff_v(ii,:));
    ratio(ii) = norm(long_v(ii,:))/norm(diff_v(ii,:));
    dot_ratio(ii) = dot(long_v(ii,:), short_v(ii,:))/ ...
        sqrt(dot(long_v(ii,:), long_v(ii,:)) ...
            * dot(short_v(ii,:), short_v(ii,:)));
end

%% Plot data
tiledlayout(3,1,'TileSpacing','Compact');
nexttile;
plot(cluster.frame, ratio);
legend('|v|/|v-u|');
title('cid=16884 (boat)');

nexttile;
plot(cluster.frame, ratio_sq);
legend('|v|^2/|v-u|');

nexttile
plot(cluster.frame, dot_ratio);
legend('dot(v,u)/sqrt(dot(v,v)*dot(u,u))');

xlim([0 n]);
xlabel('frame #')
