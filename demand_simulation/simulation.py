import csv

def LoadSimulationEvents(filename, max_floor):
    with open(filename, "r") as f:
        reader = csv.reader(f)
        headers = next(reader)  # skip header

        data = []
        rider_id = 0
        for row in reader:
            timestamp = float(row[0])
            source_floor = int(row[1])
            destination_floor = int(row[2])

            if timestamp < 0:
                raise Exception("Error in simulation file {} - timestamp can't be negative".format(filename))

            if source_floor < 0 or destination_floor < 0:
                raise Exception("Error in simulation file {} - source/destination floor can't be negative".format(filename))

            if source_floor > max_floor or destination_floor > max_floor:
                raise Exception("Error in simulation file {} - source/destination floor can't be exceed max floor {}"
                                .format(filename, max_floor))

            data_to_append = {"timestamp": timestamp,
                              "source_floor": source_floor,
                              "destination_floor": destination_floor}
            data_to_append["rider_id"] = rider_id
            data.append(data_to_append)
            rider_id += 1

    return data