import os
from turnsrkd import driver, visualizer

rundir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'basic')

turns = driver.TurnsRKD(rundir)
turns.set_configfile_name('unsteady')
turns.set_debug_params()
# or alternatively can set the parameters as 
# params = {'NSTEPS': 100, 'DT': 0.2}
# turns.set_input_params(params)
turns.run()


adturns = driver.AdTurnsRKD(rundir)
adturns.set_configfile_name('unsteady')
adturns.set_debug_params()
adturns.run()


visturns = visualizer.TurnsViz(rundir)
visturns.plot_cp()
visturns.plot_cf()
visturns.plot_res()
visturns.show()
