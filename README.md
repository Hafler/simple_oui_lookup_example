# MAC Address Lookup

This tool will allow you to look up a MAC address by querying api.maccaddress.io

## Getting Started

### Prerequisites

  * Docker (https://docs.docker.com/get-docker/)
  * Macaddress.io API key (https://macaddress.io/api)

### Installation

  1. Pull down this repository
  2. Navigate to the local repository on your system
  2. Build the docker container:
  ```
  docker build . -t mac_lookup:latest
  ```

### Usage

#### Basic Usage
```
usage: mac_lookup.py [-h] -m MAC

Gathers company name from https://macaddress.io

optional arguments:
  -h, --help         show this help message and exit
  -m MAC, --mac MAC  The MAC address, or a comma separated list of mac
                     addresses to query.
```


#### General Usage
You can simply run the container by using the docker command. For example:
```
docker run -e API_KEY=<API_KEY_HERE> mac_lookup:latest -m '44:38:39:FF:EF:53'
+-------------------+-----------------------+
|        MAC        |        Company        |
+-------------------+-----------------------+
| 44:38:39:FF:EF:53 | Cumulus Networks, Inc |
+-------------------+-----------------------+
```

#### Library Usage
You may choose to use the python library (mac_lookup.py) outside of the container like so:
```python
from mac_lookup.mac_lookup import MacAddressIO
mac_info = MacAddressIO.get_mac_details('44:38:39:FF:EF:53', '<API_KEY_HERE>')
for item in mac_info:
    print(vars(item))

# Results:
# {'mac': '44:38:39:FF:EF:53', 'oui': '443839', 'isprivate': False, 'companyname': 'Cumulus Networks, Inc', 'companyaddress': '650 Castro Street, suite 120-245 Mountain View CA 94041 US', 'countrycode': 'US'}
```

#### Usage Notes
* Multiple MAC addresses can be provided in comma-separated format without spaces.
Example: -m 44:38:39:FF:EF:53,44:38:39:FF:EF:54
* If the same MAC address is provided multiple times, only a single result for that MAC will be queried/returned
* MAC addresses are validated based on length and content (0-9/A-F)
```
