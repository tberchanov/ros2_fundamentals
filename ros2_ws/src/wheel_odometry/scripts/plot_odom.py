#!/usr/bin/env python3

"""Wheel odometry (/odom) vs ground truth: path, error, x and y over time, final error."""
import argparse
import csv

import matplotlib.pyplot as plt
import numpy as np


def read_csv(path):
    """Columns t, x, y, yaw as arrays; yaw unwrapped so it can be subtracted and interpolated."""
    with open(path, newline='') as f:
        rows = list(csv.DictReader(f))
    t, x, y, yaw = (np.array([float(r[k]) for r in rows]) for k in ('t', 'x', 'y', 'yaw'))
    return t, x, y, np.unwrap(yaw)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('odom_csv')
    p.add_argument('truth_csv')
    p.add_argument('-o', '--output', default='odom_vs_truth.png')
    a = p.parse_args()

    t, ox, oy, oyaw = read_csv(a.odom_csv)
    tt, tx, ty, tyaw = read_csv(a.truth_csv)
    # Both are stamped in sim time: resample truth at odom's stamps instead of
    # trusting that row i of one file matches row i of the other.
    tx, ty, tyaw = (np.interp(t, tt, v) for v in (tx, ty, tyaw))
    pos_err = np.hypot(tx - ox, ty - oy)
    yaw_err = np.degrees(tyaw - oyaw)

    print(f"{'final':8}{'x':>8}{'y':>8}{'turned deg':>12}")
    for name, x, y, yaw in [('odom', ox, oy, oyaw), ('truth', tx, ty, tyaw)]:
        print(f'{name:8}{x[-1]:8.3f}{y[-1]:8.3f}{np.degrees(yaw[-1] - yaw[0]):12.1f}')
    print(f'\nfinal error (truth - odom): {pos_err[-1]:.3f} m, {yaw_err[-1]:.1f} deg')

    fig, ((ax_xy, ax_err), (ax_x, ax_y)) = plt.subplots(2, 2, figsize=(12, 10))
    ax_xy.plot(ox, oy, label='/odom (wheel odometry)')
    ax_xy.plot(tx, ty, label='/ground_truth (simulator)')
    ax_xy.plot(0, 0, 'ko', label='start')
    ax_xy.set_aspect('equal')
    ax_xy.set(xlabel='x [m]', ylabel='y [m]', title='Path')
    ax_xy.grid(True, alpha=0.3)
    ax_xy.legend()

    st = t - t[0]
    ax_err.plot(st, np.abs(tx - ox) + np.abs(ty - oy), 'C3')
    ax_err.set(xlabel='sim time [s]', ylabel='error [m]',
               title='Error: |x_truth - x_odom| + |y_truth - y_odom|')
    ax_err.grid(True, alpha=0.3)

    for ax, o, tr, name in [(ax_x, ox, tx, 'x'), (ax_y, oy, ty, 'y')]:
        ax.plot(st, o, label=f'{name}_odom')
        ax.plot(st, tr, label=f'{name}_truth')
        ax.set(xlabel='sim time [s]', ylabel=f'{name} [m]', title=f'{name} over time')
        ax.grid(True, alpha=0.3)
        ax.legend()

    fig.savefig(a.output, dpi=120, bbox_inches='tight')
    print(f'\nsaved {a.output}')


if __name__ == '__main__':
    main()