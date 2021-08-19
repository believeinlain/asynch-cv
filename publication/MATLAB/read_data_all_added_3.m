%% Define parameters
% files = [
%     "june_12_run_02.json"
%     "june_12_run_03.json"
%     "june_12_run_05.json"
%     "june_12_run_06.json"
% ];
% files = [
%     "june_26_run_03.json"
%     "june_26_run_06.json"
%     "june_26_run_09.json"
%     "june_26_run_21.json"
% ];
files = [
    "april_12_run_00.json"
    "april_12_run_01.json"
    "april_12_run_02.json"
    "april_12_run_03.json"
    "april_12_run_04.json"
    "april_12_run_05.json"
    "april_12_run_06.json"
];
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


%% Plot ratio histograms

% figure();
% histogram(ratio_nontarget, 'BinMethod', 'fd');
[counts_nt, edges_nt] = histcounts(ratio_nontarget, 'BinMethod', 'fd');
numbins_nt = length(counts_nt);
% interpolate between edges
x_nt = edges_nt + (edges_nt(2)-edges_nt(1))/2;
x_nt(end) = [];
y_nt = counts_nt;

% figure();
% histogram(ratio_target, 'BinMethod', 'fd');
[counts_t, edges_t] = histcounts(ratio_target, 'BinMethod', 'fd');
numbins_t = length(counts_t);
% interpolate between edges
x_t = edges_t + (edges_t(2)-edges_t(1))/2;
x_t(end) = [];
y_t = counts_t;

edges = sort([edges_nt edges_t]);
cum_nt = zeros(length(edges), 0);
cum_t = zeros(length(edges), 0);

for ii = 1:length(edges)
    cum_nt(ii) = sum(counts_nt(x_nt < edges(ii)));
    cum_t(ii) = sum(counts_t(x_t < edges(ii)));
end

total_nt = sum(counts_nt);
total_t = sum(counts_t);
total = total_nt + total_t;

norm_cum_nt = cum_nt ./ total_nt;
norm_cum_t = cum_t ./ total_t;

% % Set up fittype and options.
% ft = fittype( 'smoothingspline' );
% opts = fitoptions( 'Method', 'SmoothingSpline' );
% opts.SmoothingParam = 0.01;
% 
% % Fit model to data.
% fitresult = fit( edges', norm_cum_t', ft, opts );
% y = fitresult(edges');

% figure();
% h = plot( fitresult, edges', cum_t' );

figure();
hold on;
% plot(edges, norm_cum_nt);
% plot(edges, norm_cum_t);
plot(edges, norm_cum_nt - norm_cum_t);

%% Plot dot-ratio histograms

% figure();
% histogram(dot_ratio_nontarget, 'BinMethod', 'fd');
[counts_nt, edges_nt] = histcounts(dot_ratio_nontarget, 'BinMethod', 'fd');
numbins_nt = length(counts_nt);
% interpolate between edges
x_nt = edges_nt + (edges_nt(2)-edges_nt(1))/2;
x_nt(end) = [];
y_nt = counts_nt;

% figure();
% histogram(dot_ratio_target, 'BinMethod', 'fd');
[counts_t, edges_t] = histcounts(dot_ratio_target, 'BinMethod', 'fd');
numbins_t = length(counts_t);
% interpolate between edges
x_t = edges_t + (edges_t(2)-edges_t(1))/2;
x_t(end) = [];
y_t = counts_t;

edges = sort([edges_nt edges_t]);
cum_nt = zeros(length(edges), 0);
cum_t = zeros(length(edges), 0);

for ii = 1:length(edges)
    cum_nt(ii) = sum(counts_nt(x_nt < edges(ii)));
    cum_t(ii) = sum(counts_t(x_t < edges(ii)));
end

total_nt = sum(counts_nt);
total_t = sum(counts_t);
total = total_nt + total_t;

norm_cum_nt = cum_nt ./ total_nt;
norm_cum_t = cum_t ./ total_t;

figure();
hold on;
plot(edges, norm_cum_nt - norm_cum_t);
