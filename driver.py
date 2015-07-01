import tempfile as tempf
import subprocess as sp
import os
import re
from utils import bcolors
SUCCESS = 0


class TurnsRKD(object):
    def __init__(self):
        self.executable_path = os.environ['OVERTURNS2D']
        self.configfile_name = 'unsteady'
        self.logfile_name = 'stdout.log'
        self.rundir = '/tmp/TurnsRKD_test'
        pass

    def set_rundir(self, rundir=tempf.mkdtemp(prefix='turns_')):
        self.rundir = rundir
        os.chdir(self.rundir)
        pass

    def set_debug(self, value=True):
        self.debug = value

    def set_debug_params(self):
        debug_params = {'NSTEPS': 2, 'NREST': 1, 'NPNORM': 1, 'DT': 0.2}
        self.set_inputs_params(debug_params)

    def set_inputs_params(self, params_dict):
        if not isinstance(params_dict, dict):
            raise ValueError('A dict should be supplied to the set_inputs_params function')

        for key, value in params_dict.iteritems():
            self.set_input_param(key, value)

    def set_input_param(self, key, value):
        print 'Setting %s to %s....' % (key, str(value)),
        with open(self.configfile_name, 'r') as f:
            lines = f.read()
        pattern = "(?i)" + key + '\s*=\s*\d*\.*\d*,'
        lines = re.sub(pattern, "%s = %s," % (key.upper(), str(value)), lines)
        f = open(self.configfile_name, 'w')
        f.write(lines)
        f.close()
        print 'Done!'
        return SUCCESS

    def set_executable_path(self):
        pass

    def set_configfile_name(self, filename):
        self.configfile_name = filename

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
        sp.call('%s < %s  > %s' % (self.executable_path, self.configfile_name, self.logfile_name), shell=True)
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
        with open(self.configfile_name, 'r') as f:
            for line in f:
                for key in ['IREAD', 'NSTEPS', 'NREST', 'NPNORM', 'DT', 'ALFA', 'FSMACH', 'ITURB']:
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


class AdTurnsRKD(TurnsRKD):
    def __init__(self):
        TurnsRKD.__init__(self)
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
