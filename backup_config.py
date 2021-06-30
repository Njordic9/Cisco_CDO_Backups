#!/.pyenv/versions/3.7.2/bin/python
"""Module docstring."""
import json
import os
import sys
import ssl
import requests
import urllib3
import csv
import pysnooper
from requests.auth import HTTPBasicAuth

ssl._create_default_https_context = ssl._create_unverified_context

urllib3.disable_warnings()  # Suppresses warnings from unsigned Cert warning.

SERVER = "https://<CDO_URL>"
NUM_DEVICES_TO_RETRIEVE_PER_QUERY = 50

token = "<insert API Token>"

def device_count():
    """GET REST API Agent to retrieve AUTH Token.
    Returns:
        [str] -- [Post returns JSON, which is converted to str and returned.]
    """
    apipath = "/targets/devices"
    url = SERVER + apipath
    params = {
        'q': '(deviceType:ASA)',
        'agg': 'count'}
    headers = {
        'Accept': "application/json",
        'Content-Type': "application/json",
        'Authorization': "bearer {}".format(token)}
    response = requests.get(url, verify=False, stream=True, headers=headers, params=params)
    getstatuscode = response.status_code
    getresponse = response.json()
    if getstatuscode == 200:
        return getresponse
    else:
        response.raise_for_status()

def device_config(i):
    """Polls CDO for ASA Device Configruations.
    Returns:
        [str] -- [Post returns JSON, which is converted to str and returned.]
    """
    apipath = "/targets/devices"
    url = SERVER + apipath
    params = {
        'q': '(deviceType:ASA)',
        'resolve': '[targets/devices.{name,deviceConfig}]',
        'sort': 'name:desc',
        'limit': NUM_DEVICES_TO_RETRIEVE_PER_QUERY,
        'offset': i}
    headers = {
        'Accept': "application/json",
        'Content-Type': "application/json",
        'Authorization': "bearer {}".format(token)}
    response = requests.get(url, verify=False, stream=True, headers=headers, params=params)
    getstatuscode = response.status_code
    getresponse = response.json()
    if getstatuscode == 200:
        return getresponse
    else:
        response.raise_for_status()


# @pysnooper.snoop()
def main():
    # token = getcsrftoken(uname, passwd)
    output_dir = "<File_Destination>/CDO/Backups"
    try:
        count_resp = device_count()
        print(count_resp)
        d_count = count_resp['aggregationQueryResult']
        for i in range(0, d_count, NUM_DEVICES_TO_RETRIEVE_PER_QUERY):
            d_configs = device_config(i)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            for device_json in d_configs:
                config_file = open(os.path.join(output_dir, device_json['name'] + '.config.txt'), "w")
                if device_json['deviceConfig'] is not None:
                    config_file.write(device_json['deviceConfig'])
                config_file.close()
    except Exception as e:
        print("ERROR: {}".format(e))


if __name__ == '__main__':
    main()
