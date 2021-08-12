
import numpy as np
import sklearn.metrics
import matplotlib.pyplot as plt

root = 'output'

factors = [
    0,
    1,
    10,
    100,
    200,
    210,
    220,
    250,
    260,
    300,
    400,
    500,
    1000
]

runs = [
    'june_12_run_02',
    'june_12_run_03',
    'june_12_run_05',
    'june_12_run_06'
]

ap_array = []
roc_array = []

for f in factors:

    total_truth_array = np.array([])
    total_conf_array = np.array([])

    for run in runs:
        path = f'output/{str(f)}/{run}/results/'
        truth_array = np.loadtxt(path+'metrics_truth_array.txt')
        conf_array = np.loadtxt(path+'metrics_conf_array.txt')
        total_truth_array = np.concatenate((total_truth_array, truth_array))
        total_conf_array = np.concatenate((total_conf_array, conf_array))
    
    ap = sklearn.metrics.average_precision_score(
        total_truth_array, total_conf_array
    )
    roc = sklearn.metrics.roc_auc_score(
        total_truth_array, total_conf_array
    )

    print(f'{f:3}, {ap:.4}, {roc:.4}')
    ap_array.append(ap)
    roc_array.append(roc)

plt.plot(
    factors, ap_array, 'b', 
    factors, roc_array, 'r'
)
plt.legend(['average precision', 'area under ROC'])
plt.xlabel('dot-ratio coefficient') 
plt.show()
