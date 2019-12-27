import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm


def erf(x_pred, x_true, r, y, indexs_pred, indexs_true):
    return len(set(indexs_pred[:int(r * x_pred.shape[0])]).intersection(set(indexs_true[:int(y * x_pred.shape[0])])))


def erfmax(x_pred, x_true, r, y, indexs_pred, indexs_true):
    return (int(min(r, y) * x_pred.shape[0]))


def nefr(*i):
    return erf(*i) / erfmax(*i)


def nefrcurve(points_, p, t, min_sample=-3, reverse_sort=False):
    xs = np.logspace(min_sample, 0, points_, base=10)
    ys = np.logspace(min_sample, 0, points_, base=10)

    indexs_pred = np.argsort(p)
    indexs_true = np.argsort(t)
    if reverse_sort:
        indexs_pred = indexs_pred[::-1]
        indexs_true = indexs_true[::-1]

    xx, yy = np.meshgrid(xs, ys)
    zz = np.zeros(xx.shape)
    for i in tqdm(range(points_)):
        for j in range(points_):
            zz[i, j] = nefr(p, t, xx[i, j], yy[i, j], indexs_pred, indexs_true)

    return xx, yy, zz


class RegressionDetectionSurface:

    def __init__(self, percent_min=-3):
        self.min = percent_min
        self.nefr = None
        self.stratify = False

    def compute(self, trues, preds, stratify=None, samples=30):
        self.stratify = stratify is not None
        if self.stratify:
            self.nefr = nefrcurve(samples, preds, trues, self.min)
        else:
            x, y, z = [], [], []
            u, indices = np.unique(stratify, return_inverse=True)
            for i in u.shape:
                locs = np.argwhere(indices == i).flatten()
                preds_strat = preds[locs]
                trues_strat = trues[locs]

                x_2, y_2, z_2 = nefrcurve(30, preds_strat, trues_strat)
                x.append(x_2)
                y.append(y_2)
                z.append(z_2)
            self.nefr = (x, y, z)

        return self.nefr

    def plot(self, save_file=None, levels=10, title="RDS", cmap='Blues', figsize=(8, 5)):
        plt.figure(figsize=figsize)
        plt.xscale("log")
        plt.yscale("log")
        plt.xlabel("Screen top x%")
        plt.ylabel("True top x%")
        plt.contourf(np.stack(self.nefr[0]).mean(0) if self.stratify else self.nefr[0],
                     np.stack(self.nefr[1]).mean(0) if self.stratify else self.nefr[1],
                     np.stack(self.nefr[2]).mean(0) if self.stratify else self.nefr[2],
                     vmin=0,
                     vmax=1,
                     cmap=cmap,
                     levels=levels)

        plt.colorbar()
        plt.title(title)

        if save_file is None:
            plt.show()
        else:
            plt.savefig(save_file, bbox_inches='tight', dpi=300)
