import csv
from datetime import datetime

def get_total_dist(walk_dist, transit_dist):
    return float(walk_dist) + float(transit_dist)
        

def get_fare(num_transfers):
    return str(2.40 * (int(num_transfers) + 1))

# CSV files resulting from OTP processing
csv_files = [
    '../results/results_1.csv',
    '../results/results_2.csv',
    '../results/results_3.csv',
    '../results/results_4.csv',
    '../results/results_5.csv',
    '../results/results_6.csv',
    '../results/results_7.csv',
    '../results/results_8.csv',
    '../results/results_9.csv',
    '../results/results_10.csv',
	'../results/results_11.csv',
	'../results/results_12.csv',
	'../results/results_13.csv',
	'../results/results_14.csv',
	'../results/results_15.csv'
]

# Output file where we combine all the results
output_file = open('../results/results_full.csv', 'a')
output_csv = csv.writer(output_file)

for csv_file in csv_files:
    with open(csv_file, newline='') as f:
        reader = csv.reader(f)
        bad_lines = 0 # How many lines have blank values
        for index, line in enumerate(reader):
            # Unpack the line to get all the row values
            [
                trip_id,
                departure_time,
                arrival_time,
                total_time,
                walk_time,
                transfer_wait_time,
                initial_wait_time,
                transit_time,
                walk_dist,
                transit_dist,
                total_dist,
                num_transfers,
                fare
            ] = line
            try:
                if walk_time == total_time:
                    fare = 0
                else:
                    fare = get_fare(num_transfers)
                # Re-pack the row into a list
                line = [
                    trip_id,
                    departure_time,
                    arrival_time,
                    total_time,
                    walk_time,
                    transfer_wait_time,
                    initial_wait_time,
                    transit_time,
                    walk_dist,
                    transit_dist,
                    total_dist,
                    num_transfers,
                    fare
                ]
                output_csv.writerow(line)
            except ValueError:
                # Blank rows will throw errors when type converting in get_fare
                bad_lines += 1

            if index % 10000 == 0:
                # To check progress while the script is running
                print(f'{index} lines written. {(index / 19803420) * 100}% Done')
        print('Lines containing blank values: ' + str(bad_lines))
            
print("Done")
