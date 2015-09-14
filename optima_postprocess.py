import numpy as np
from driver import TurnsRKD, AdTurnsRKD, SensTurnsRKD
import subprocess as sp
import os
import scipy.io as io
import time
PBS_STRING="""
#!/bin/sh
#PBS -S /bin/sh
#PBS -N jac_%i
#PBS -l nodes=1:ppn=1,pmem=2g
#PBS -l walltime=4:00:00
#PBS -A kdur_fluxoe
#PBS -l qos=flux
#PBS -q fluxoe
#PBS -V
#
# echo "I ran on:"
# cat $PBS_NODEFILE
#
# Create a local directory to run from and copy your files to it.
# Let PBS handle your output
export OMPI_MCA_mtl=^mxm
export OMPI_MCA_coll_fca_enable=0
export OMPI_MCA_btl_vader_single_copy_mechanism=none
export OMPI_MCA_btl_sm_use_knem=0
export ADOVERTURNS2D=/scratch/kdur_fluxoe/anandps/turns2d-new/bin/adoverturns2d
#  Include the next three lines always
if [ "x${PBS_NODEFILE}" != "x" ] ; then
   cat $PBS_NODEFILE   # contains a list of the CPUs you were using
fi

#  Change to the directory you submitted from
if [ -n "$PBS_O_WORKDIR" ]; then cd $PBS_O_WORKDIR; fi

# Let PBS handle your output
$ADOVERTURNS2D < unsteady

"""
class JacobianCalc(object):
    def __init__(self):
        self.solution_dir = ""
        self.OBJINP_STR = ""
        self.copytree = ""
        self.points_index = []

    def generate_rundir(self):
        n = len(self.points_index)
        print "Generating directories"
        for idx, point in enumerate(self.points_index):
            print "\r point %i"%point,
            adjoint_dir = os.path.join(self.solution_dir, "jac_adjoint_%i"%point)
            os.mkdir(adjoint_dir)
            os.chdir(adjoint_dir)
            for f in self.copytree:
                file_ = os.path.join(self.solution_dir, f)
                sp.call("cp " + file_ + " " + adjoint_dir, shell=True)
                
            f = open("obj.inp", "w")
            f.write(self.OBJINP_STR%point)
            f.close()
            f = open("run.pbs", "w")
            f.write(PBS_STRING%point)
            f.close()
            os.chdir(self.solution_dir)
        print "\n"
        
    def submit_job(self):
        for idx, point in enumerate(self.points_index):
            current_adjoint_rundir = os.path.join(self.solution_dir, "jac_adjoint_%i"%point)
            os.chdir(current_adjoint_rundir)
            os.system("qsub run.pbs")
            os.chdir(self.solution_dir)
            time.sleep(0.05) 
            print "\r Submitting pbs job for point %i"%point,
        print "\n"

    def collect_jac(self):
        n = len(self.points_index)
        turns = TurnsRKD(nspec=1, rundir = self.solution_dir)
        nj, nk = turns.get_grid_dimensions()
        nt = nj*nk
        jac_map = np.zeros([n, nt])
        F_map = np.zeros([n])
        
        for idx, point in enumerate(self.points_index):
            print "\r Creating jacobian for point %i"%point,
            current_adjoint_rundir = os.path.join(self.solution_dir, "jac_adjoint_%i"%point)
            sensturns = SensTurnsRKD(nspec=1, rundir = current_adjoint_rundir)
            try:
                sens = sensturns.get_beta_sensitivity()
                jac_map[idx, :] = np.reshape(sens, [1, nt])
                F_map[idx] = np.loadtxt('fort.747')
            except:
                print "NOT FOUND SENS"
        print "\n"
        beta_map = np.reshape(sensturns.read_beta("beta.opt"), [nt, 1])
        io.savemat(os.path.join(self.solution_dir, "map.mat"),  {'jac_map':jac_map, 'beta_map':beta_map, 'F_map': F_map, 'nj':nj, 'nk':nk})
        
class JacobianCalcMPI(object):
    # does not work, since subprocess causes some issue with mpi4py
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
