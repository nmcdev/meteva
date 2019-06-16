

import sklearn
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt


def contingency_table(ob, fo, figsize=(9, 4), x_label=None, y_label=None, title='contingency table', fontsize=20,

                      fontproperties='KaiTi', col_labels=['yes', 'no', 'Total'], row_labels=['yes', 'no', 'Total']):

    cm = confusion_matrix(ob, fo)
    tn, fp, fn, tp = cm.ravel()
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, frameon=True, xticks=[], yticks=[])
    table_vals = [[tn, fn, tn + fn], [fp, tp, fp + tp], [tn + fp, fn + tp, tn + fp + fn + tp]]
    my_table = plt.table(cellText=table_vals,
                         rowLabels=row_labels, colLabels=col_labels,
                         loc='center')
    my_table.set_fontsize(10)
    my_table.scale(0.7, 3.5)
    plt.text(0.05, 0.5, y_label, fontsize=fontsize, rotation=90)
    plt.text(0.5, 0.9, x_label, fontsize=fontsize)
    plt.title(title, fontproperties=fontproperties, fontsize=25)
    plt.show()