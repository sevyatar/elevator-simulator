Intro
----
This is an elevator simulator that aims to find the best scheduling algorithm for elevators.  

Elevator Types
--------------

The elevator simulator can deal with 3 different types of elevators: 
1. `Naive Elevator`:
This elevator has 1 button outside, and the rider chooses his destination floor once he walks into the elevator.

2. `Up-Down Button Elevator`:
This elevator has 2 buttons outside - an up and a down button. The rider chooses his destination floor once he walks into the elevator.


3. `Destination-First Elevator`:
In this elevator, the rider inputs his destination floor before getting into the elevator.

For every elevator type, the simulator can handle any number of elevators that work simultaneously.

Adding an algorithm
-------------------
To add an algorithm, simply add a new class to the `algo` directory, in the relevant sub-dir according to the elevator type.
Make sure to implement the relevant interface from `algo/algo_interface.py`

Running all simulations
-----------------------
1. Generate random simulation scenarios
`python demand_simulation_data/random_scenario/generate_random_sim.py`
2. Run the simulation (runs all algorithms, on a specific type of demand pattern, to change the pattern - edit run_all_simulations.py : run_multiple_simulations)
`python run_all_simulations.py`
3. Compare algorithm results
`simulation_results/compare_simulation_results.py` 

Running and visualizing single simulation
-----------------------------------------
1. `python run_single_simulations.py`
2. Load `monitoring/visualize/visualize.html` into a browser (tested on Chrome)

Final Notes
-----------
- at this stage, we're assuming that the elevator has infinite passenger capacity.