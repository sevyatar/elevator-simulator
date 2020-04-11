import random
import csv
import os

SIM_DIR = 'demand_simulation/random_scenario'

def generate_random_free_for_all(sim_filename):
    max_floor = random.randint(5,100)
    number_of_events = random.randint(1,1000)

    with open(os.path.join(SIM_DIR, 'free_for_all', sim_filename), 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(('timestamp', 'source_floor', 'destination_floor'))

        current_ts = 0
        for _ in range(number_of_events):
            new_ts = current_ts + random.randint(0, 60)
            source_floor = random.randint(1, max_floor)
            destination_floor = random.randint(1, max_floor)
            if source_floor == destination_floor:
                continue

            csv_writer.writerow((new_ts, source_floor, destination_floor))
            current_ts = new_ts


def generate_random_office_building(sim_filename):
    GROUND_FLOOR = 1

    max_floor = random.randint(5,100)
    number_of_employees = random.randint(50,1000)
    employee_floors = {employee_id : random.randint(2,max_floor) for employee_id in range(number_of_employees)}

    # For an office building, we split the day according to:
    # - first 2 hours of the day : people coming into the office
    # - last 2 hours of the day : people leaving the office
    # - everything else : people go randomly between their floor and ground floor
    # Note : I'm assuming there's no movement between floors that doesn't involve the ground floor
    ONE_HOUR = 60 * 60 * 24
    start_of_day_ts = 0
    end_of_day_ts = ONE_HOUR * 8
    end_of_inbound_ts = ONE_HOUR * 2
    start_of_outbound_ts = end_of_day_ts - (ONE_HOUR * 2)

    events_list = []
    # Every employee gets to the building at some point, leaves the building at some point,
    # and potentially gets out of the building a few times during the day
    for employee_id, employee_floor in employee_floors.items():
        # Employee arriving in the morning
        building_arrival_ts = random.randint(start_of_day_ts, end_of_inbound_ts)
        events_list.append((building_arrival_ts, GROUND_FLOOR, employee_floor))

        # Employee departing when the day is done
        building_departure_ts = random.randint(start_of_outbound_ts, end_of_day_ts)
        events_list.append((building_departure_ts, employee_floor, GROUND_FLOOR))

        # Potentially leaving the building for lunch (80% chance)
        if random.random() < 0.8:
            lunch_start = random.randint(end_of_inbound_ts, start_of_outbound_ts)
            events_list.append((lunch_start, employee_floor, GROUND_FLOOR))

            lunch_end = random.randint(lunch_start, start_of_outbound_ts)
            events_list.append((lunch_end, GROUND_FLOOR, employee_floor))

    # Write sorted events to CSV file
    with open(os.path.join(SIM_DIR, 'office_building', sim_filename), 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(('timestamp', 'source_floor', 'destination_floor'))

        sorted_events_list = sorted(events_list, key=lambda event: event[0])
        for event in sorted_events_list:
            csv_writer.writerow((event[0], event[1], event[2]))


if "__main__" == __name__:
    random.seed(1)

    for i in range(1, 100):
        # generate_random_free_for_all("sim_{}.csv".format(i))
        generate_random_office_building("sim_{}.csv".format(i))
