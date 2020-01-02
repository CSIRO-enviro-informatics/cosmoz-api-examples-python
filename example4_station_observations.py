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
This example gets some Sensor Observations from a given Cosmoz station
"""

from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlencode
from datetime import datetime, timezone
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
# Add request query params
query_params = {
    "processing_level": PROCESSING_LEVEL,
    "startdate": start_date_str,
    "enddate": end_date_str,
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

count = payload['meta']['count']
site = payload['meta']['site_no']
print("Showing {} Observations for station {}.".format(str(count), str(site)))
for i, o in enumerate(payload['observations']):
    print("Observation {} of {}:".format(i+1, count))
    for k, v in o.items():
        print("\t{}: {}".format(str(k), str(v)))
