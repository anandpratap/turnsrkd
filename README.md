# turnsrkd

## Usage

- Make sure that the directory is added to the PYTHONPATH
- Set the OVERTURNS2D and ADOVERTURN2D environment variables to the path of the corresponding executable

```
import os
from turnsrkd import driver, visualizer

run_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'basic')

turns = driver.TurnsRKD()
turns.set_rundir(run_dir)
turns.set_configfile_name('unsteady')
turns.set_debug_params()
# or alternatively can set the parameters as 
# params = {'NSTEPS': 100, 'DT': 0.2}
# turns.set_input_params(params)
turns.run()


adturns = driver.AdTurnsRKD()
adturns.set_rundir(run_dir)
adturns.set_configfile_name('unsteady')
adturns.set_debug_params()
adturns.run()


visturns = visualizer.TurnsViz(run_dir)
visturns.plot_cp()
visturns.plot_cf()
visturns.plot_res()
visturns.show()
```