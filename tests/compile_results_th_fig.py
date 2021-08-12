
import numpy as np
import sklearn.metrics
import matplotlib.pyplot as plt

root = 'output'

thresholds = [
    0,
    140
]

runs = [
    'june_12_run_02',
    'june_12_run_03',
    'june_12_run_05',
    'june_12_run_06'
]

ap_array = []
roc_array = []

for th in thresholds:

    total_truth_array = np.array([])
    total_conf_array = np.array([])

    for run in runs:
        path = f'output/ratio_threshold/{str(th)}/{run}/results/'
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
    precision, recall, _ = sklearn.metrics.precision_recall_curve(
        total_truth_array, total_conf_array
    )
    fpr, tpr, _ = sklearn.metrics.roc_curve(
        total_truth_array, total_conf_array
    )

    # print(f'{th:3}, {ap:.2}, {roc}')
    ap_array.append(ap)
    roc_array.append(roc)

    disp = sklearn.metrics.PrecisionRecallDisplay(precision, recall)
    disp.plot()
    disp.ax_.set_title(f'Average Precision: {ap:0.2f}')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.show()

    disp = sklearn.metrics.RocCurveDisplay(fpr=fpr, tpr=tpr)
    disp.plot()
    disp.ax_.set_title(f'Area Under Curve: {roc:0.2f}')
    plt.show()

plt.plot(
    thresholds, ap_array, 'b', 
    thresholds, roc_array, 'r'
)
plt.legend(['average precision', 'area under ROC'])
plt.xlabel('ratio threshold') 
plt.show()
