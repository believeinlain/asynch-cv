
import numpy as np
import sklearn.metrics
import matplotlib.pyplot as plt

root = 'output'

factors = [*range(0, 1010, 10)]

# runs = [
#     'june_12_run_02',
#     'june_12_run_03',
#     'june_12_run_05',
#     'june_12_run_06'
# ]

# runs = [
#     'june_26_run_03',
#     'june_26_run_06',
#     'june_26_run_09',
#     'june_26_run_21'
# ]

runs = [
    'april_12_run_00',
    'april_12_run_01',
    'april_12_run_02',
    'april_12_run_03',
    'april_12_run_04',
    'april_12_run_05',
    'april_12_run_06',
]

# roc_array = []

# for f in factors:
 
#     total_truth_array = np.array([])
#     total_conf_array = np.array([])

#     for run in runs:
#         path = f'output/{f:03}/{run}/results/'
#         truth_array = np.loadtxt(path+'metrics_truth_array.txt')
#         conf_array = np.loadtxt(path+'metrics_conf_array.txt')
#         total_truth_array = np.concatenate((total_truth_array, truth_array))
#         total_conf_array = np.concatenate((total_conf_array, conf_array))
    
#     roc = sklearn.metrics.roc_auc_score(
#         total_truth_array, total_conf_array
#     )

#     print(f'{f:3}, {roc:.4}')
#     roc_array.append(roc)

# plt.plot(factors, roc_array)
# plt.legend(['area under ROC'])
# plt.xlabel('dot-ratio coefficient') 
# plt.show()

f = 0

total_truth_array = np.array([])
total_conf_array = np.array([])

for run in runs:
    path = f'output/{f:03}/{run}/results/'
    truth_array = np.loadtxt(path+'metrics_truth_array.txt')
    conf_array = np.loadtxt(path+'metrics_conf_array.txt')
    total_truth_array = np.concatenate((total_truth_array, truth_array))
    total_conf_array = np.concatenate((total_conf_array, conf_array))

fpr, tpr, _ = sklearn.metrics.roc_curve(
    total_truth_array, total_conf_array
)

disp = sklearn.metrics.RocCurveDisplay(fpr=fpr, tpr=tpr)
disp.plot()
disp.ax_.set_title(f'Collection 3 ROC at Scaling Factor 0')
plt.show()
