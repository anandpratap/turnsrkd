import os
from turns_driver import driver, visualizer

run_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'basic')

turns = driver.TurnsRKD()
turns.set_rundir(run_dir)
turns.set_configfile_name('unsteady')
turns.set_debug_config()
turns.run()


adturns = driver.AdTurnsRKD()
adturns.set_rundir(run_dir)
adturns.set_configfile_name('unsteady')
adturns.set_debug_config()
adturns.run()


visturns = visualizer.TurnsViz(run_dir)
visturns.plot_cp()
visturns.plot_cf()
visturns.plot_res()
visturns.show()
