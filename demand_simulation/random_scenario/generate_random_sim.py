import yaml
import random
import csv
import os

import main

SIM_DIR = 'demand_simulation/random_scenario'

def generate_random_free_for_all(sim_filename):
    with open(main.CONFIGURATION_FILE, 'rb') as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)

    max_floor = conf["ELEVATOR"]["MAX_FLOOR"]
    number_of_events = random.randint(1,1000)

    with open(os.path.join(SIM_DIR, 'free_for_all', sim_filename), 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(('timestamp', 'source_floor', 'destination_floor'))

        current_ts = 0
        for i in range(number_of_events):
            new_ts = current_ts + random.randint(0, 60)
            source_floor = random.randint(1, max_floor)
            destination_floor = random.randint(1, max_floor)
            if source_floor == destination_floor:
                continue

            csv_writer.writerow((new_ts, source_floor, destination_floor))
            current_ts = new_ts

if "__main__" == __name__:
    random.seed(1)

    for i in range(1, 100):
        generate_random_free_for_all("sim_{}.csv".format(i))
