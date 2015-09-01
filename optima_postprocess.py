import numpy as np
from mpi4py import MPI
from driver import AdTurnsRKD, SensTurnsRKD
import subprocess as sp
import os
import scipy.io as io
class JacobianCalc(object):
    def __init__(self):
        self.solution_dir = ""
        self.OBJINP_STR = ""
        self.copytree = ""
        self.points_index = []

    def generaterundir(self):
        n = len(self.points_index)
        print "Generating directories"
        for idx, point in enumerate(self.points_index):
            print "\r Processing adjoint for point %i"%point,
            adjoint_dir = os.path.join(self.solution_dir, "jac_adjoint_%i"%point)
            os.mkdir(adjoint_dir)
            os.chdir(adjoint_dir)
            for f in self.copytree:
                file_ = os.path.join(self.solution_dir, f)
                sp.call("cp " + file_ + " " + adjoint_dir, shell=True)
                
            f = open("obj.inp", "w")
            f.write(self.OBJINP_STR%point)
            f.close()
            os.chdir(self.solution_dir)
        print "\n"

    def run(self):
        n = len(self.points_index)
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        size = comm.Get_size()
        comm.barrier()
        if rank == 0:
            self.generaterundir()
        comm.barrier()
        global_range = range(n)
        local_range = range(rank,n,size)
        for idx, val in enumerate(local_range):
            current_adjoint_rundir = os.path.join(self.solution_dir, "jac_adjoint_%i"%self.points_index[val])
            adturns = AdTurnsRKD(nspec=1, rundir = current_adjoint_rundir)
            if self.DEBUG:
                adturns.set_debug_params()
            else:
                adturns.set_input_params(self.adjoint_params)
            print "Running adjoint for points %i from process %i"%(self.points_index[val], rank)
            adturns.run()
        comm.barrier()
        if rank == 0:
            nj, nk = adturns.get_grid_dimensions()
            nt = nj*nk
            jac_map = np.zeros([n, nt])
            F_map = np.zeros([n])
            for idx, val in enumerate(global_range):
                current_adjoint_rundir = os.path.join(self.solution_dir, "jac_adjoint_%i"%self.points_index[val])
                sensturns = SensTurnsRKD(nspec=1, rundir = current_adjoint_rundir)
                sens = sensturns.get_beta_sensitivity()
                jac_map[idx, :] = np.reshape(sens, [1, nt])
                F_map[idx] = np.loadtxt('fort.747')
            beta_map = np.reshape(sensturns.read_beta("beta.opt"), [nt, 1])
            io.savemat(os.path.join(self.solution_dir, "map.mat"),  {'jac_map':jac_map, 'beta_map':beta_map, 'F_map': F_map, 'nj':nj, 'nk':nk})
        
            
if __name__ == "__main__":
    pass
