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
This example gets a list of stations from the API endpoint
"""

from urllib.request import Request, urlopen
from urllib.parse import urljoin
import json

COSMOZ_API_URL = "https://esoil.io/cosmoz-data-pipeline/rest/"  # Keep the trailing slash on here

# Endpoint to get all stations is "pipeline/rest/stations/"
stations_endpoint = urljoin(COSMOZ_API_URL, "stations")

# Add a header to specifically ask for JSON output
request_headers = {"Accept": "application/json"}

# Construct a GET request, with that URL and those headers
stations_request = Request(stations_endpoint, method="GET", headers=request_headers)

# Execute the request, and wait for the response.
with urlopen(stations_request) as http_response:
    try:
        response = http_response.read()
    except Exception:
        raise RuntimeError("Cannot read HTTP Response")
    try:
        payload = json.loads(response)
    except Exception:
        raise RuntimeError("Invalid JSON response")

count = payload['meta']['count']
print("Found {} stations.".format(str(count)))
for s in payload['stations']:
    print("Site {}: {}".format(str(s['site_no']), s['site_name']))
