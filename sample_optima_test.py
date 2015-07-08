from optima import Optima

opt = Optima(rundir = "/home/anandps/Dropbox/research/summer_2015/naca_4412/inverse_test")
opt.DEBUG = False
opt.maxstep = 20
opt.base_stepsize = 0.2


opt.adjoint_copytree = ['bc.inp', 'obj.inp', 'beta.opt', 'cp_benchmark.dat', 'cf.dat', 'fort.9', 
                        'fort.8', 'fort.1', 'SA.dat', 'production.dat', 'unsteady', 'fort.747', 'cp.dat']

opt.solver_params = {'DT':0.5, 'NSTEPS':100000, 'NREST':1000, 'NPNORM': 1000, 'ALFA': 13.87, 'FSMACH': 0.09, 'REY': 1.52E6}
opt.adjoint_params = {'DT':0.5, 'NSTEPS':100000, 'NREST':1000, 'NPNORM': 1000, 'ALFA': 13.87, 'FSMACH': 0.09, 'REY': 1.52E6}


# run
opt.run()
