# utils.py

import requests

from api.services.telegram import logging
from apps.general.models import DevSetting


def get_address(lat, lng):
    try:
        api_key = DevSetting.get_value('ggAPIKey')
        base_url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'latlng': f'{lat},{lng}',
            'key': api_key,
        }

        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        logging(f'Call google API => {str(data)}', f'{lat},{lng}')

        if data['status'] == 'OK':
            address = data['results'][0]['formatted_address']
            return address
        else:
            return None

    except requests.exceptions.RequestException as e:
        logging(f"Error making HTTP request to Google Map API {e}")
        return None