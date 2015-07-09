import tempfile as tempf
import subprocess as sp
import os
import re
from utils import bcolors
import numpy as np
import fortutils as futils

SUCCESS = 0


class TurnsRKD(object):
    def __init__(self, rundir=tempf.mkdtemp(prefix='turns_')):
        self.executable_path = os.environ['OVERTURNS2D']
        self.inputfile_name = 'unsteady'
        self.logfile_name = 'stdout.log'
        self.rundir = rundir
        os.chdir(self.rundir)
        pass

    def set_debug(self, value=True):
        self.debug = value

    def set_debug_params(self):
        debug_params = {'NSTEPS': 2, 'NREST': 1, 'NPNORM': 1, 'DT': 0.2}
        self.set_input_params(debug_params)

    def set_input_params(self, params_dict):
        if not isinstance(params_dict, dict):
            raise ValueError('A dict should be supplied to the set_inputs_params function')

        for key, value in params_dict.iteritems():
            self.set_input_param(key, value)

    def set_input_param(self, key, value):
        print 'Setting %s to %s....' % (key, str(value)),
        with open(self.inputfile_name, 'r') as f:
            lines = f.read()
        pattern = "(?i)" + key + '\s*=\s*\d*\.*\d*,'
        lines = re.sub(pattern, "%s = %s," % (key.upper(), str(value)), lines)
        f = open(self.inputfile_name, 'w')
        f.write(lines)
        f.close()
        print 'Done!'
        return SUCCESS

    def set_executable_path(self):
        pass

    def set_inputfile_name(self, filename):
        self.inputfile_name = filename

    def set_log_level(self):
        pass

    def set_verbatim_level(self):
        pass

    def set_monitoring_level(self):
        pass

    def print_turns(self, msg):
        print msg

    def run(self):
        self.print_startinfo()
        sp.call('%s < %s  > %s' % (self.executable_path, self.inputfile_name, self.logfile_name), shell=True)
        self.print_endinfo()
        return SUCCESS

    def print_startinfo(self):
        print bcolors.BOLD + bcolors.FAIL + '## Starting OVERTURNS2D run via driver TurnsRKD ~~'
        print bcolors.OKBLUE + '## Run dir = ', self.rundir
        print '## Executable path = ', self.executable_path
        print '## Important Parameters include:'
        print '## '
        self.print_params()
        print bcolors.ENDC

    def print_params(self):
        with open(self.inputfile_name, 'r') as f:
            for line in f:
                for key in ['IREAD', 'NSTEPS', 'NREST', 'NPNORM', 'DT', 'ALFA', 'FSMACH', 'REY', 'ITURB']:
                    pattern = "(?i)" + key + '\s*=\s*\d*\.*\d*,'
                    str_ = re.findall(pattern, line)
                    if str_:
                        print '## ' + str_[0]

    def print_endinfo(self):
        print bcolors.BOLD + bcolors.OKGREEN + '## Completed OVERTURNS2D ~~~~~~~~~~'
        print '## Run dir = ', self.rundir
        print '## Executable path = ', self.executable_path
        print '## Important quantities:'
        print '## Convergence:'
        sp.call('tail -n 1 fort.71', shell=True)
        print '## Coefficients:'
        sp.call('tail -n 1 fort.11', shell=True)
        print bcolors.ENDC



    def get_grid_dimensions(self):
        nj, nk = futils.get_grid_dimensions()
        return nj, nk

    def get_grid(self):
        nj, nk = self.get_grid_dimensions()
        x, y = futils.read_grid(nj, nk)
        return x, y

    def get_velocity(self):
        nj, nk = self.get_grid_dimensions()
        x, y, u, v, uv = futils.read_reystress(nj, nk)
        return u, v

    def get_reystress(self):
        nj, nk = self.get_grid_dimensions()
        x, y, u, v, uv = futils.read_reystress(nj, nk)
        return uv

    def get_production(self):
        nj, nk = self.get_grid_dimensions()
        prod = futils.read_production(nj, nk)
        return prod
    
    def get_destruction(self):
        nj, nk = self.get_grid_dimensions()
        dest = futils.read_destruction(nj, nk)
        return dest

    def get_cp(self):
        data = np.loadtxt("cp.dat")
        x = data[:,0]
        cp = data[:,1]
        return x, cp

    def get_cp_benchmark(self):
        data = np.loadtxt("cp_benchmark.dat")
        x = data[:,0]
        cp = data[:,2]
        return x, cp

    def write_beta(self, beta, filename):
        [nj, nk] = np.shape(beta)
        f = open(filename, "w")
        for k in range(nk):
            for j in range(nj):
                f.write("%2.16f\n"%beta[j][k])
        f.close()
        print "Wrote beta to file!"

    def read_beta(self, filename):
        tb = np.loadtxt(filename)
        nj, nk = futils.get_grid_dimensions()
        beta = np.zeros([nj, nk])
        counter = 0
        for k in range(nk):
            for j in range(nj):
                beta[j][k] = tb[counter]
                counter  = counter + 1
        return beta


class AdTurnsRKD(TurnsRKD):
    def __init__(self, rundir=tempf.mkdtemp(prefix='turns_')):
        TurnsRKD.__init__(self, rundir)
        self.executable_path = os.environ['ADOVERTURNS2D']

    def print_startinfo(self):
        print bcolors.BOLD + bcolors.FAIL + '## Starting Adjoint OVERTURNS2D run via driver TurnsRKD ~~'
        print bcolors.OKBLUE + '## Run dir = ', self.rundir
        print '## Executable path = ', self.executable_path
        print '## Important Parameters include:'
        print '## '
        self.print_params()
        print bcolors.ENDC

    def print_endinfo(self):
        print bcolors.BOLD + bcolors.OKGREEN + '## Completed Adjoint OVERTURNS2D ~~~~~~~~~~'
        print '## Run dir = ', self.rundir
        print '## Executable path = ', self.executable_path
        print '## Important quantities:'
        print '## Convergence:'
        sp.call('tail -n 1 fort.171', shell=True)
        print bcolors.ENDC

    def get_saadjoint(self):
        nj, nk = self.get_grid_dimensions()
        psi_sa = futils.read_saadjoint(nj, nk)
        return psi_sa

class SensTurnsRKD(AdTurnsRKD):
    def __init__(self, rundir):
        AdTurnsRKD.__init__(self, rundir)
               

    def get_beta_sensitivity(self):
        prod = self.get_production()
        psi_sa = self.get_saadjoint()
        sens = -prod*psi_sa
        print "Sum of sensitivity: ", sum(sum(sens))
        return sens

    def get_gamma_sensitivity(self):
        dest = self.get_destruction()
        psi_sa = self.get_saadjoint()
        sens = -dest*psi_sa
        print "Sum of sensitivity: ", sum(sum(sens))
        return sens


if __name__ == "__main__":
    # test using naca 4412 test case 
    from pylab import *
    sensturns = SensTurnsRKD(rundir="/home/anandps/Dropbox/research/summer_2015/naca_4412/beta_adjoint_test_225_65")
    sens = sensturns.get_beta_sensitivity()
    x, y = sensturns.get_grid()
    contourf(x, y, sens)
    show()
