import csv


def load_simulation_events(filename):
    with open(filename, "r") as f:
        reader = csv.reader(f)
        _ = next(reader)  # skip header

        data = []
        rider_id = 0
        for row in reader:
            timestamp = float(row[0])
            source_floor = int(row[1])
            destination_floor = int(row[2])

            if timestamp < 0:
                raise Exception("Error in simulation file {} - timestamp can't be negative".format(filename))

            if source_floor < 0 or destination_floor < 0:
                raise Exception("Error in simulation file {} - source/destination floor can't be negative"
                                .format(filename))

            data_to_append = dict(timestamp=timestamp, source_floor=source_floor, destination_floor=destination_floor)
            data_to_append["rider_id"] = rider_id
            data.append(data_to_append)
            rider_id += 1

    return data
