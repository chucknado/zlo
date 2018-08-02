import os
import time
from urllib.parse import urlparse

import requests
from modules.auth import get_auth


def get_resource_list(url, list_name=None, paginate=True):
    """
    Returns a list of HC resources specified by the url basename (such as .../articles.json)
    :param url: A full endpoint url, such as 'https://support.zendesk.com/api/v2/help_center/articles.json'
    :param list_name: The list name in the response per the docs
    :param paginate: Whether the endpoint has pagination (i.e., a 'next_page' property). Example: missing translations
    :return: List of resources, or False if the request failed
    """
    o = urlparse(url)
    if list_name:
        resource = list_name
    else:
        resource = os.path.splitext(os.path.basename(o.path))[0]    # e.g., 'articles'
    record_list = {resource: []}
    while url:
        response = requests.get(url, auth=get_auth())
        if response.status_code == 429:
            print('Rate limited! Please wait.')
            time.sleep(int(response.headers['retry-after']))
            response = requests.get(url, auth=get_auth())
        if response.status_code != 200:
            print('Error with status code {}'.format(response.status_code))
            print(response.text)
            return False
        data = response.json()
        if data[resource]:  # guard against empty record list
            record_list[resource].extend(data[resource])
        if paginate:
            url = data['next_page']
        else:
            break
    return record_list[resource]


def get_resource(url):
    """
    Returns a single HC resource
    :param url: A full endpoint url, such as 'https://support.zendesk.com/api/v2/help_center/articles/2342572.json'
    :return: Dict of a resource, or False if the request failed.
    """
    resource = None
    response = requests.get(url, auth=get_auth())
    if response.status_code == 429:
        print('Rate limited! Please wait.')
        time.sleep(int(response.headers['retry-after']))
        response = requests.get(url, auth=get_auth())
    if response.status_code != 200:
        print('Failed to get record with error {}:'.format(response.status_code))
        print(response.text)
        return False
    for k, v in response.json().items():
        resource = v
    if type(resource) is dict:
        return resource
    return None


def post_resource(url, data, status=201):
    """
    :param url: Any post endpoint.
    :param data: A dictionary representing the JSON payload, formatted as per docs.
    :param status: HTTP status. Normally 201 but some POST requests return 200
    :return: Python data, or False if the request failed.
    """
    resource = None
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=data, auth=get_auth(), headers=headers)
    if response.status_code == 429:
        print('Rate limited! Please wait.')
        time.sleep(int(response.headers['retry-after']))
        response = requests.post(url, json=data, auth=get_auth(), headers=headers)
    if response.status_code != status:
        print('Failed to create record with error {}:'.format(response.status_code))
        print(response.text)
        return False
    for k, v in response.json().items():
        resource = v
    if type(resource) is dict:
        return resource
    return None


def put_resource(url, data):
    """
    :param url:
    :param data:
    :return: Python data, or False if the request failed.
    """
    resource = None
    headers = {'Content-Type': 'application/json'}
    response = requests.put(url, json=data, auth=get_auth(), headers=headers)
    if response.status_code == 429:
        print('Rate limited! Please wait.')
        time.sleep(int(response.headers['retry-after']))
        response = requests.post(url, json=data, auth=get_auth(), headers=headers)
    if response.status_code != 200:
        print('Failed to update record with error {}:'.format(response.status_code))
        print(response.text)
        return False
    for k, v in response.json().items():
        resource = v
    if type(resource) is dict:
        return resource
    return None


def delete_resource(url):
    """
    Runs a DELETE request on any Delete endpoint in the Zendesk API
    :param url: A full endpoint url, such as 'https://support.zendesk.com/api/v2/help_center/articles/2342572.json'
    :return: If successful, a 204 status code. If not, None
    """
    response = requests.delete(url, auth=get_auth())
    if response.status_code == 429:
        print('Rate limited! Please wait.')
        time.sleep(int(response.headers['retry-after']))
        response = requests.delete(url, auth=get_auth())
    if response.status_code != 204:
        print('Failed to delete record with error {}'.format(response.status_code))
        print(response.text)
        return False
    return None
