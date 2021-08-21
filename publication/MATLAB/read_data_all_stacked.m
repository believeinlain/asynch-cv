
%% Define parameters
files = [
    "june_12_run_01.json"
    "june_12_run_02.json"
    "june_12_run_03.json"
    "june_12_run_05.json"
    "june_12_run_06.json"
];
num_files = length(files);

clf;

%% Read data
for k=1:num_files
    text = importdata(files(k));
    data = jsondecode(text{1});
    fn = fieldnames(data);

    % Compute analysis results


    ratio_target = [];
    ratio_nontarget = [];

    dot_ratio_target = [];
    dot_ratio_nontarget = [];

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

    % Plot histograms
    figure(1);
    hold on;
    histogram(ratio_target);
    title('target ratio distribution');
    set(gca,'YScale','log');
    figure(2);
    hold on;
    histogram(ratio_nontarget);
    title('non-target ratio distribution');
    set(gca,'YScale','log');

    figure(3);
    hold on;
    histogram(dot_ratio_target);
    title('target dot-ratio distribution');
    set(gca,'YScale','log');
    figure(4);
    hold on;
    histogram(dot_ratio_nontarget);
    title('non-target dot-ratio distribution');
    set(gca,'YScale','log');
end
    