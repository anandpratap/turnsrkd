import os
import glob
import shutil
import subprocess as sp
import numpy as np
from numpy.linalg import norm
import scipy.sparse.linalg as slinalg
from multiprocessing import Pool
from itertools import repeat, izip



from driver import TurnsRKD, AdTurnsRKD, SensTurnsRKD
from template import POINTWISE_OBJINP
BASE_DIR_NFILES = 6
BASE_DIR_NAME = "base_dir"

class Optima(object):
    def __init__(self, rundir):
        self.rundir = rundir
        self.iteration_number = 0
        os.chdir(self.rundir)
        self.base_dir = os.path.join(self.rundir, BASE_DIR_NAME)
        self.check_rundir()
        self.check_restart()
        self.DEBUG = False
        self.step_type = 'sd'
        self.base_stepsize = 0.2
        self.maxstep = 1
        self.objf = 0.0
        self.sens_norm = 0.0
        self.nspec = 1 #asitav

    def check_rundir(self):
        # check for folder named base_dir, inside the folder check for fort.1 bc.inp atleast
        # Also number of files in the case_dir should be 5
        
        if os.path.isdir(self.base_dir):
            print "Base dir found!"
        else:
            raise ValueError("Base directory not found!!")
        base_files = glob.glob(os.path.join(self.base_dir, '*'))
        nbase_files = len(base_files)
        if nbase_files != BASE_DIR_NFILES:
            raise ValueError("Something wrong with the base directory, number of files do not match, change the value in optima if you think you are 100% right!!")
        for f in ['fort.1', 'bc.inp', 'obj.inp']:
            if not os.path.isfile(os.path.join(self.base_dir, f)):
                raise ValueError("File %s does not exist in the base directory!"%f)
        
        print "Everything seem to be just fine, Optima checking done!"

    def check_restart(self):
        iter_dirs = glob.glob("iteration_*")
        niter = len(iter_dirs)
        if niter > 0:
            self.iteration_number = niter
            print "Old iteration directories found, will be restarting from iteration", niter - 1

    def update(self, beta, sens):
        if self.step_type == 'sd':
            stepsize = self.base_stepsize
            beta = beta - sens/abs(sens).max()*stepsize
            print "Updated beta using steepest descent!"
        else:
            raise ValueError("Step type not defined!")
            
        return beta
            
    def step(self):
        # create iteration directory
        current_rundir = os.path.join(self.rundir, "iteration_%i"%self.iteration_number)
        # copy files from base_dir
        shutil.copytree(self.base_dir, current_rundir)
        
        # create solver instance
        turns = TurnsRKD(nspec=self.nspec, rundir = current_rundir )
        if self.DEBUG:
            turns.set_debug_params()
        else:
            turns.set_input_params(self.solver_params)
            
        turns.run()
 
        if self.step_type == 'sd':
            current_adjoint_rundir = os.path.join(current_rundir, "adjoint_0")
            os.mkdir(current_adjoint_rundir)
            for f in self.adjoint_copytree:
                cmd = 'cp ' + os.path.join(current_rundir, f) +' '+ current_adjoint_rundir + '/.'
                sp.call(cmd, shell=True)

            #for TS
            if(self.nspec > 1):
                print "Copy all the *_TS* files"
                cmd = 'cp ' + os.path.join(current_rundir, 'fort_TS*.[8,9]') +' '+ current_adjoint_rundir + '/.'
                sp.call(cmd, shell=True)
                cmd = 'cp ' + os.path.join(current_rundir, 'SA_TS*.dat') +' '+ current_adjoint_rundir + '/.'
                sp.call(cmd, shell=True)
                cmd = 'cp ' + os.path.join(current_rundir, 'production_TS*.dat') +' '+ current_adjoint_rundir + '/.'
                sp.call(cmd, shell=True)
                cmd = 'cp ' + os.path.join(current_rundir, 'destruction_TS*.dat') +' '+ current_adjoint_rundir + '/.'
                sp.call(cmd, shell=True)

            adturns = AdTurnsRKD(nspec=self.nspec, rundir = current_adjoint_rundir)
            if self.DEBUG:
                adturns.set_debug_params()
            else:
                adturns.set_input_params(self.adjoint_params)
            
            adturns.run()
            sensturns = SensTurnsRKD(nspec=self.nspec, rundir = current_adjoint_rundir)
            sens = sensturns.get_beta_sensitivity()
            beta = sensturns.read_beta("beta.opt")
            beta = self.update(beta, sens)
        elif self.step_type == 'gn':
            # Gauss Newton
            points = self.points
            npoints = len(self.points)
            for p in points:
                current_adjoint_rundir = os.path.join(current_rundir, "adjoint_%i"%p)
                os.mkdir(current_adjoint_rundir)
                for f in self.adjoint_copytree:
                    cmd = 'cp ' + os.path.join(current_rundir, f) +' '+ current_adjoint_rundir + '/.'
                    sp.call(cmd, shell=True)
                os.chdir(current_adjoint_rundir)
                # change the obj_inp
                os.chdir("../")
            # pool and run the adjoints
            pool = Pool(npoints)
            pool.map(run_pointwise_adjoint, izip(points, repeat(current_rundir), repeat(self.adjoint_params), repeat(self.DEBUG)))
            # build jac
            nj, nk = turns.get_grid_dimensions()
            nt = nj*nk
            jac = np.zeros([npoints, nt])
            F = np.zeros([npoints,1])
            for pidx, p in enumerate(points):
                current_adjoint_rundir = os.path.join(current_rundir, "adjoint_%i"%p)
                sensturns = SensTurnsRKD(nspec=self.nspec, rundir = current_adjoint_rundir)
                sens = sensturns.get_beta_sensitivity()
                jac[pidx, :] = np.reshape(sens, [1, nt])
                F[pidx] = np.loadtxt("fort.747")

            lam = self.lam
            beta = sensturns.read_beta("beta.opt")
            dbeta = slinalg.cg(jac.T.dot(jac) + lam*np.eye(nt), -jac.T.dot(F))
            beta = beta + np.reshape(dbeta[0], [nj, nk])
        else:
            raise ValueError("Step type not defined!")
            
        
        sensturns.write_beta(beta, os.path.join(self.base_dir, "beta.opt"))
        print "Updated beta in the base directory!!"
        self.iteration_number += 1
        try:
            self.objf = np.loadtxt("fort.747")[-1]
        except:
            self.objf = np.loadtxt("fort.747")
        self.sens_norm = norm(sens)

        
    def run(self):
        for i in range(self.maxstep):
            print "Starting iteration ", self.iteration_number
            self.step()
            print "Ending iteration ", self.iteration_number
            print "Objective function: ", self.objf
            print "Sensitivity Norm: ", self.sens_norm
            log = open(os.path.join(self.rundir,'optima.log'), 'ab+')
            log.write('%i %10.14f %10.14f'%(self.iteration_number, self.objf, self.sens_norm))
            log.write('\n')
            log.close()
            # write log file
            os.chdir(self.rundir)

if __name__ == "__main__":
    pass

DEBUG = True
def run_pointwise_adjoint((p, current_rundir, adjoint_params, debug)):
    current_adjoint_rundir = os.path.join(current_rundir, "adjoint_%i"%p)
    adturns = AdTurnsRKD(nspec=self.nspec, rundir = current_adjoint_rundir)
    
    # setup obj.inp
    f = open("obj.inp", "w")
    f.write(POINTWISE_OBJINP%p)
    f.close()

    if debug:
        adturns.set_debug_params()
    else:
        adturns.set_input_params(adjoint_params)
    adturns.run()




