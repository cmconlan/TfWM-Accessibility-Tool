# Modelling and OTP

The Modelling process involves calculating a trip itinerary using [Open Trip Planner](https://www.opentripplanner.org/)(OTP) for
all possible trips - all combinations of output area, demographics, time and point of interest types. This results
in around 19 million unique trips, each of which contains starting point (OA centroid) location, destination location (POI lat and longitude) 
and time values which are provided as input to Open Trip Planner to produce an itinerary.
OTP may produce several values for each trip:
 - `departure_time`,
 - `arrival_time`,
 - `total_time`,
 - `walk_time`,
 - `transfer_wait_time`,
 - `initial_wait_time`,
 - `transit_time`,
 - `walk_dist`,
 - `transit_dist`,
 - `total_dist`,
 - `num_transfers`,
 - `fare` *Note: OTP does not inherently contain fare information, so this output is 0 and is calculated during the results aggregation.*

OTP may not produce valid outputs for some trips - when the source and destination are too close, for example.

The full ETL to Modelling pipeline was not possible on University Systems due to lack of support for Postgres, 
so the `sql/create_model_otp_trips.csv` was used on a VM with Postgres installed to create and export all possible trips.

## Running OTP processing locally with CSV data

### Setup
1. Set the relevant environment variables in `src/.env`. Use the `.env-template` file to fill in your specific details, then rename the file to .env:
```
...
# The OTP process is done in parallel on multiple processes. This var sets how many processes are used
NUM_PROCESSES=
# The number of instances of OTP Servers. Processes are assigned an OTP server.
NUM_OTPS=
# The base port of OTP servers e.g if 2 OTPs are running on 8080 and 8082, the base port is 8080
OTP_PORT=
# The host where the OTP server instances are running. Typically this is set to localhost
OTP_HOST=
```
2. Prepare the `/data` and `/results` directories - `/data` should contain the OTP trip enumerations to be fed as input to OTP, while
`/results` will produce the output of each process in a separate results `csv` file. The input and output files can be set in `run_otp_processing.py`.

3. Start up OTP using `run.sh` - this script contains the setup for two OTP servers, but feel free to add more. Remember to include an
ampersand after all Java commands (except potentially the last one) to enable the servers to run in the background.
OTP servers also use two ports, one for HTTP and one for HTTPS. Make sure the HTTP ports between servers differ by 1 only e,g
8080, 8081, 8082... etc.
For more information on starting up OTP, see [OTP Basic Tutorial](http://docs.opentripplanner.org/en/latest/Basic-Tutorial/)

4. Start the processing with `(venv) $ python run_otp_processing.py`. You can monitor CPU usage with `top` on Linux. Note that computation
time for 19 million rows with 10 processes and 2 OTPs took around a day on the University compute nodes.

Once all processes are done, the results can be found in separate CSVs under `/results`
