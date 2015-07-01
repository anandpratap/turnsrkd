import os
import numpy as np
import matplotlib.pyplot as plt


class TurnsViz(object):
    def __init__(self, rundir):
        self.rundir = rundir
        os.chdir(self.rundir)

    def plot_cp(self):
        fig = plt.figure()
        x = np.loadtxt('cp.dat')[:, 0]
        cp = np.loadtxt('cp.dat')[:, 1]
        plt.plot(x, cp, 'rx-')
        return fig

    def plot_res(self):
        fig = plt.figure()
        plt.semilogy(np.loadtxt('fort.71')[:, 2:4], 'rx-')
        return fig

    def plot_cf(self):
        fig = plt.figure()
        x = np.loadtxt('cf_new.dat')[:, 0]
        cf = np.loadtxt('cf_new.dat')[:, 1]
        plt.plot(x, cf, 'rx-')
        return fig

    def show(self):
        plt.show()
