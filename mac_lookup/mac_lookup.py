import argparse
import json
import os
import re
import requests
from prettytable import PrettyTable

__version__ = '1.0'


class MacAddressIO(object):
    """Class to gather details regarding a MAC address from api.macaddress.io"""

    def __init__(self, mac, data):
        """
        Convert responses from the macaddress.io API into an object

        Parameters
        ----------
        mac : str
            The MAC address tied to the subsequent data in this object
        data : dict
            A dictionary representation of the data returned by the macaddress.io API
        """
        self.mac = mac
        {setattr(self, k.lower(), v) for k, v in data.items()}

    @staticmethod
    def __validate_api_key_exists(api_key):
        """
        Validates the existence of an API key

        Parameters
        ----------
        api_key : str
            The API key to be used for authentication against the API

        Raises
        -------
        ValueError
            Raises a value error if the API key is not provided
        """
        if not api_key:
            raise ValueError('API key was was not provided.')

    @staticmethod
    def validate_hex_only(mac):
        """
        Validates that the MAC address contains only hexadecimal characters and/or delimiters

        Parameters
        ----------
        mac : str
            The MAC to validate

        Raises
        -------
        ValueError
            Raises a value error if the MAC address provided does not contain only hexadecimal characters
        """
        if not re.fullmatch(r"^[0-9A-F:.]+$", mac):
            raise ValueError(f'MAC Address ({mac}) did not pass hex-only validation.')

    @staticmethod
    def validate_mac_length(mac):
        """
        Validates that the MAC address matches length requirements (can include delimiters)

        Parameters
        ----------
        mac : str
            The MAC to validate

        Raises
        -------
        ValueError
            Raises a value error if the MAC address provided does not match length requirements (can include delimiters)
        """
        if len(mac) not in [12, 17]:
            raise ValueError(f'MAC address ({mac}) did not pass length validation.')

    @staticmethod
    def validate_mac(mac):
        """
        Runs a provided MAC address through validations for length and content.

        Parameters
        ----------
        mac : str
            The MAC to validate
        """
        validation_checks = [MacAddressIO.validate_mac_length, MacAddressIO.validate_hex_only]
        [check(mac) for check in validation_checks]

    @staticmethod
    def make_request(mac, api_key):
        """
        Performs a GET request to the macaddress.io API

        Parameters
        ----------
        mac : str
            The MAC to query the API with
        api_key : str
            The API key to be used for authentication against the API

        Returns
        -------
        MacAddressIO
            An object that contains the top level keys from the API response
        """
        url = 'https://api.macaddress.io/v1/'
        headers = {'x-Authentication-Token': api_key}
        params = {'output': 'json', 'search': mac}
        try:
            response = requests.get(url, params=params, headers=headers)
            if response.status_code == 200:
                data = json.loads(response.text)
                return MacAddressIO(mac, data.get('vendorDetails'))
            else:
                raise ValueError(
                    f'There was a problem gathering details for {mac}. Response: {response.status_code}')
        except requests.exceptions.RequestException as err:
            raise SystemExit(err)

    @staticmethod
    def get_mac_details(mac_addresses, api_key):
        """
        Validates provided mac addresses

        Parameters
        ----------
        mac_addresses : str
            The MAC address, or a comma separated list of mac addresses to use in the API queries
        api_key : str
            The API key to be used for authentication against the API

        Returns
        -------
        list
            A list of MacAddressIO objects containing information from the macaddress.io API response
        """
        MacAddressIO.__validate_api_key_exists(api_key)
        mac_results = []
        for mac in set(mac_addresses.split(',')):
            mac = mac.strip()
            MacAddressIO.validate_mac(mac)
            mac_results.append(MacAddressIO.make_request(mac, api_key))
        return mac_results


if __name__ == '__main__':
    # Parse arguments for use later on in the script
    parser = argparse.ArgumentParser(description='Gathers company name from https://macaddress.io')
    parser.add_argument('-m',
                        '--mac',
                        required=True,
                        type=str.upper, help='The MAC address, or a comma separated list of mac addresses to query.')
    args = parser.parse_args()

    # Get API Key
    API_KEY = os.getenv('API_KEY', None)

    try:
        # Gather any results by querying the API
        results = MacAddressIO.get_mac_details(args.mac, API_KEY)

        # If there are any results, create a readable table and print it.
        # Otherwise, notify the user that there are no results
        if results:
            table = PrettyTable(['MAC', 'Company'])
            for result in results:
                table.add_row([result.mac, result.companyname])
            print(table)
        else:
            print('No results found.')
    except ValueError as e:
        # Catch and display any raised ValueError exceptions. These occur during validation of input
        print(e)
    except SystemExit as e:
        # Catch any raised SystemExit exceptions. These occur when there is an issue with communicating to the API
        print('Exception caught while making requests to the api.macaddress.io API')
        print(e)