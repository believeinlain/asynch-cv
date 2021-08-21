
%% Define parameters
files = [
    "june_12_run_02.json"
    "june_12_run_03.json"
    "june_12_run_05.json"
    "june_12_run_06.json"
];
% files = [
%     "june_26_run_03.json"
%     "june_26_run_06.json"
%     "june_26_run_09.json"
%     "june_26_run_21.json"
% ];
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

% normalize dot-ratio
dot_ratio_target = (dot_ratio_target + 1)./2;


%% Plot histograms

close all;
% count data points
[counts, edges] = histcounts(ratio_nontarget, 'BinMethod', 'fd');
numbins = length(counts);
% interpolate between edges
x = edges + (edges(2)-edges(1))/2;
x(end) = [];
% accumulate counts
cumcounts = zeros(numbins, 0);
total = 0;
for bin = 1:numbins
    total = total + counts(bin);
    cumcounts(bin) = total;
end
% normalize accumulated counts to represent a fraction
% of total counts
y = cumcounts ./ total;

figure();
[a, b, c] = fitPower(x, y);
hold on;
scatter(x, y);
x_fine = 0:0.1:x(end);
xlim([0 x(find(y>=0.995,1))]);
ylim([0 1]);
ylabel('Fraction of samples captured');
xlabel('Difference ratio value');
plot(x_fine, a*x_fine.^b + c);
legend('Accumulated samples', 'Best fit curve');


% % count data points
% [counts, edges] = histcounts(dot_ratio_target, 'BinMethod', 'fd');
% numbins = length(counts);
% % interpolate between edges
% x = edges + (edges(2)-edges(1))/2;
% x(end) = [];
% % accumulate counts
% cumcounts = zeros(numbins, 0);
% total = 0;
% for bin = numbins:-1:1
%     total = total + counts(bin);
%     cumcounts(bin) = total;
% end
% % normalize accumulated counts to represent a fraction
% % of total counts
% y = cumcounts ./ total;
% 
% figure();
% [a, b, c] = fitPower(x, y);
% hold on;
% scatter(x, y);
% x_fine = x(1):0.001:x(end);
% % x_fine = x;
% xlim([x(find(y<=0.995,1)) 1]);
% ylim([0 1]);
% ylabel('Fraction of samples captured');
% xlabel('Dot-product ratio value');
% plot(x_fine, a*x_fine.^b + c);
% legend('Accumulated samples', 'Best fit curve', 'Location', 'SE');
    