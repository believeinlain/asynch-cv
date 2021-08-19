
%% import data
opts = delimitedTextImportOptions("NumVariables", 2);

% Specify range and delimiter
opts.DataLines = [1, Inf];
opts.Delimiter = ",";

% Specify column names and types
opts.VariableNames = ["factor", "roc"];
opts.VariableTypes = ["double", "double"];

% Specify file level properties
opts.ExtraColumnsRule = "ignore";
opts.EmptyLineRule = "read";

june12 = readtable("data\june_12.txt", opts);
june26 = readtable("data\june_26.txt", opts);
april12 = readtable("data\april_12.txt", opts);

clear opts

%% plot data
% hold on;
figure();
plot(june12.factor, june12.roc);
title('Collection 1');
xlabel('Scaling Factor');
ylabel('Area Under ROC');
figure();
plot(june26.factor, june26.roc);
title('Collection 2');
xlabel('Scaling Factor');
ylabel('Area Under ROC');
figure();
plot(april12.factor, april12.roc);
title('Collection 3');
xlabel('Scaling Factor');
ylabel('Area Under ROC');