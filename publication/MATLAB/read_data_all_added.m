
%% Define parameters
% files = [
%     "june_12_run_02.json"
%     "june_12_run_03.json"
%     "june_12_run_05.json"
%     "june_12_run_06.json"
% ];
files = [
    "june_26_run_03.json"
    "june_26_run_06.json"
    "june_26_run_09.json"
    "june_26_run_21.json"
];
% files = [
%     "april_12_run_00.json"
%     "april_12_run_01.json"
%     "april_12_run_02.json"
%     "april_12_run_03.json"
%     "april_12_run_04.json"
%     "april_12_run_05.json"
%     "april_12_run_06.json"
% ];
num_files = length(files);

ratio_target = [];
ratio_nontarget = [];

dot_ratio_target = [];
dot_ratio_nontarget = [];

for k=1:num_files
    text = importdata("data/"+files(k));
    data = jsondecode(text{1});
    fn = fieldnames(data);

    % Compute analysis results

    for c=1:numel(fn)
        cluster = struct2table(data.(fn{c}));
        n = length(cluster.frame);

        long_v = [cluster.long_v_x, cluster.long_v_y];
        short_v = [cluster.short_v_x, cluster.short_v_y];
        diff_v = long_v - short_v;

        ratio = zeros(n, 0);
        ratio_sq = zeros(n, 0);
        dot_ratio = zeros(n, 0); 
        target_count = 0;
        for ii = 1:n
            if cluster.is_target(ii)
                target_count = target_count + 1;
            end
            ratio(ii) = norm(long_v(ii,:))/norm(diff_v(ii,:));
            dot_ratio(ii) = dot(long_v(ii,:), short_v(ii,:))/ ...
                sqrt(dot(long_v(ii,:), long_v(ii,:)) ...
                    * dot(short_v(ii,:), short_v(ii,:)));
        end

        if target_count/n > 0.5
            ratio_target = [ratio_target ratio];
            dot_ratio_target = [dot_ratio_target dot_ratio];
        else
            ratio_nontarget = [ratio_nontarget ratio];
            dot_ratio_nontarget = [dot_ratio_nontarget dot_ratio];
        end
    end
end

%% Plot histograms

close all;

threshold = [0.85 0.9 0.95];

% figure();
% histogram(ratio_target);
% title('target ratio distribution');
% set(gca,'YScale','log');
% yl = ylim;
% ylim([0.9 yl(2)]);

figure();
h = histogram(ratio_nontarget);
title('non-target ratio distribution');
set(gca,'YScale','log');

y = h.BinCounts;
edges = h.BinEdges;
% interpolate between edges
x = edges + (edges(2)-edges(1))/2;
x(end) = [];

total = sum(y);
current = 0;
bin = 1;
for ii = 1:length(threshold)
    while current < threshold(ii)*total
        current = current + y(bin);
        bin = bin + 1;
    end
    xline(x(bin), '--r', ...
        num2str(threshold(ii)*100)+"%: "+num2str(x(bin)));
end

plotRatioData(ratio_nontarget);
title('non-target ratio fit');
% xlim([0 80]);
% ylim([-1 2.5]);

plotRatioData(dot_ratio_target);
title('target dot-ratio fit');

figure();
title('target dot-ratio distribution');
h = histogram(dot_ratio_target, 'BinMethod', 'fd');
set(gca,'YScale','log');

y = h.BinCounts;
edges = h.BinEdges;
% interpolate between edges
x = edges + (edges(2)-edges(1))/2;
x(end) = [];

total = sum(y);
current = 0;
bin = h.NumBins;
for ii = 1:length(threshold)
    while current < threshold(ii)*total
        current = current + y(bin);
        bin = bin - 1;
    end
    xline(x(bin), '--r', ...
        num2str(threshold(ii)*100)+"%: "+num2str(x(bin)));
end

% total = sum(y);
% current = 0;
% bin = h.NumBins;
% for ii = 1:length(threshold)
%     while current < threshold(ii)*total
%         current = current + y(bin);
%         bin = bin - 1;
%     end
%     if bin > 0 
%         xline(x(bin), '--r', ...
%             num2str(threshold(ii)*100)+"%: "+num2str(x(bin)));
%     end
% end

% figure();
% histogram(dot_ratio_nontarget, 100);
% title('non-target dot-ratio distribution');
% set(gca,'YScale','log');
% yl = ylim;
% ylim([0.9 yl(2)]);
    