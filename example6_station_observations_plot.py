#!/bin/python3
# Copyright 2019-2020 CSIRO Land and Water
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This example gets some Sensor Observations from a given Cosmoz station, for a month, aggregated to 512 points,
and plotted using matplotlib
"""

from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlencode
from datetime import datetime, timezone
import matplotlib.pyplot as plt
import numpy as np
import json

COSMOZ_API_URL = "https://esoil.io/cosmoz-data-pipeline/rest/"  # Keep the trailing slash on here

STATION_NUMBER = 21
PROCESSING_LEVEL = 4  # Choose processing level 1, 2, 3, 4, or 0 (for Raw)

# Endpoint to get a station's observations is "pipeline/rest/stations/{id}/observations"
stations_endpoint = urljoin(COSMOZ_API_URL, "stations/")
station_endpoint = urljoin(stations_endpoint, "{}/".format(str(STATION_NUMBER)))
station_obs_endpoint = urljoin(station_endpoint, "observations")

# Time Period Start Date
start_date = datetime(2019, 1, 1, tzinfo=timezone.utc)
start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")  # ISO8601 Format
# Time Period End Date
end_date = datetime(2019, 1, 31, tzinfo=timezone.utc)
end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")  # ISO8601 Format

# Aggregate the whole month into 512 slices
t_delta = end_date - start_date
delta_seconds = (t_delta.days * (60 * 60 * 24)) + t_delta.seconds
# Use 511, because there are 511 steps in 512 slices
step_seconds = delta_seconds // 511  # Integer divide, not floating point
if (step_seconds % 511) != 0:
    step_seconds += 1  # Add one if the total seconds doesn't divide cleanly into 511

# Add request query params
query_params = {
    "processing_level": PROCESSING_LEVEL,
    "startdate": start_date_str,
    "enddate": end_date_str,
    "aggregate": "{}s".format(str(step_seconds))  # Set aggregation to step seconds
}
query_params = urlencode(query_params)
station_obs_url = "{}?{}".format(station_obs_endpoint, query_params)

# Add a header to specifically ask for JSON output
request_headers = {"Accept": "application/json"}

# Construct a GET request, with that URL and those headers
station_obs_request = Request(station_obs_url, method="GET", headers=request_headers)
# Execute the request, and wait for the response.
with urlopen(station_obs_request) as http_response:
    try:
        response = http_response.read()
    except Exception:
        raise RuntimeError("Cannot read HTTP Response")
    try:
        payload = json.loads(response)
    except Exception:
        raise RuntimeError("Invalid JSON response")
print("Got Observations Meta:")
for k, v in payload['meta'].items():
    print("\t{}: {}".format(str(k), str(v)))


count = int(payload['meta']['count'])
observations = payload['observations']

min_soil_moist_filtered_iter = (o['min_soil_moist_filtered'] for o in observations)
max_soil_moist_filtered_iter = (o['max_soil_moist_filtered'] for o in observations)
mean_soil_moist_filtered_iter = (o['mean_soil_moist_filtered'] for o in observations)
x_tick_stride = count // 10
if count % 10 != 0:
    x_tick_stride += 1
all_x_labels = [o['time'] for o in observations]
selected_x_labels = []
selected_x_vals = []
for c in range(0, count, x_tick_stride):
    selected_x_vals.append(c)
    selected_x_labels.append(all_x_labels[c])
selected_x_vals.append(count-1)
selected_x_labels.append(all_x_labels[-1])
min_array = np.fromiter(min_soil_moist_filtered_iter, dtype=np.float)
max_array = np.fromiter(max_soil_moist_filtered_iter, dtype=np.float)
mean_array = np.fromiter(mean_soil_moist_filtered_iter, dtype=np.float)
t = np.arange(count)
fig, ax = plt.subplots(1, dpi=128)
ax.plot(t, mean_array, lw=1, label='soil moisture', color='blue')
ax.set_ylim(0, None)
ax.set_xticks(selected_x_vals)
ax.set_xticklabels(selected_x_labels, rotation=79)
ax.fill_between(t, max_array, min_array, facecolor='blue', alpha=0.5)
ax.set_title("Example of plotting soil moisture vs time for a 1 month period")
ax.legend(loc='upper left')
ax.set_xlabel('date and time')
ax.set_ylabel('volumetric soil moisture m³/m³')
ax.grid()
fig.show()
