"""
dos-indexd-lambda
This lambda proxies requests to the necessary indexd endpoints
and converts them to GA4GH messages.

"""

import logging

from chalice import Chalice, Response
import requests
import yaml

SWAGGER_URL = "https://raw.githubusercontent.com/david4096/data-object-schemas/client_headers/openapi/data_object_service.swagger.yaml"  # NOQA
INDEXD_URL = "https://dev.planx-pla.net/index"
DOWNLOAD_URL = "https://dev.planx-pla.net/user/data/download"

app = Chalice(app_name='dos-indexd-lambda', debug=True)
app.log.setLevel(logging.DEBUG)

# Converter Functions


def indexd_to_ga4gh(indexd):
    """
    Accepts a signpost/gdc entry and returns a GA4GH DataObject as a
    dictionary.


    {
        "baseid": "c57e0a80-f3bd-46b6-8fbb-68dc3f34257a",
        "created_date": "Mon, 22 Jan 2018 18:34:12 GMT",
        "did": "c8215adc-d77a-4cb1-b1e4-8dd96d7e8821",
        "file_name": "testdata.txt",
        "form": "object",
        "hashes": {
            "md5": "73d643ec3f4beb9020eef0beed440ad0"
        },
        "metadata": {},
        "rev": "5582aee1",
        "size": 9,
        "updated_date": "Mon, 22 Jan 2018 18:34:12 GMT",
        "urls": [
            "s3://cdistest-gen3data/testdata.txt"
        ],
        "version": null
    }


    :param indexd: A dictionary representing a GDC index response
    :return: ga4gh formatted dictionary
    """
    # TODO rest of fields
    # TODO convert time
    data_object = {
        "id": indexd['did'],
        "name": indexd['file_name'],
        'created': indexd['created_date'],
        'updated': indexd['updated_date'],
        "size": indexd['size'],
        "version": indexd['rev']
    }

    # parse out checksums
    data_object['checksums'] = []
    for k in indexd['hashes']:
        data_object['checksums'].append(
            {'checksum': indexd['hashes'][k], 'type': k})

    # parse out the urls
    data_object['urls'] = []
    for url in indexd['urls']:
        data_object['urls'].append({
            'url': url,
            'system_metadata': indexd,
            'user_metadata': indexd['metadata']})

    return data_object


def dos_list_request_to_indexd(dos_list):
    """
    Takes a DOS ListDataObjects request and converts it into a request against
    indexd index.
    :param gdc:
    :return:
    """
    mreq = {}
    mreq['limit'] = dos_list.get('page_size', None)
    mreq['start'] = dos_list.get('page_token', None)
    return mreq


def gdc_to_dos_list_response(gdcr):
    """
    Takes a GDC list response and converts it to GA4GH.
    :param gdc:
    :return:
    """
    mres = {}
    mres['data_objects'] = []
    for id_ in gdcr.get('ids', []):
        mres['data_objects'].append({'id': id_})
    if len(gdcr.get('ids', [])) > 0:
        mres['next_page_token'] = gdcr['ids'][-1:][0]
    return mres


def not_found_response(data_object_id, e):
    """
    Creates a not found response to be returned using the exception
    and requested data object ID.

    :param data_object_id:
    :param e:
    :return:
    """
    not_found_msg = 'Data Object with data_object_id {} ' \
                    'was not found. {} '.format(data_object_id, str(e))
    return Response({'msg': not_found_msg},
                    status_code=404)


# Paths


@app.route('/swagger.json', cors=True)
def swagger():
    """
    Downloads the swagger from a reputable source and injects our change `api`.

    :return:
    """
    req = requests.get(SWAGGER_URL)
    swagger_dict = yaml.load(req.content)
    swagger_dict['basePath'] = '/api/ga4gh/dos/v1'
    return swagger_dict


@app.route(
    '/ga4gh/dos/v1/dataobjects/{data_object_id}',
    methods=['GET'], cors=True)
def get_data_object(data_object_id):
    """
    This endpoint returns DataObjects by their identifier by proxying the
    request to indexd.
    :param data_object_id:
    :return:
    """
    # Try to get fence session from the header.
    authorization = app.current_request.headers.get('Authorization', None)
    download_url = None
    # FIXME this has been changed
    if authorization:
        try:
            response = requests.get(
                "{}/{}".format(DOWNLOAD_URL, data_object_id),
                headers={'Authorization': authorization})
            download_url = response.json()['url']
        except Exception as e:
            # the fence token probably wasn't good
            download_url = str(e)
    req = requests.get(
        "{}/index/{}".format(INDEXD_URL, data_object_id))
    if req.status_code == 200:
        data_object = indexd_to_ga4gh(req.json())
    else:
        return not_found_response(data_object_id, req.get('message', ""))
    if download_url:
        data_object['urls'].append({'url': download_url})
    return {'data_object': data_object}


@app.route('/ga4gh/dos/v1/dataobjects/list', methods=['POST'], cors=True)
def list_data_objects():
    """
    This endpoint translates DOS List requests into requests against indexd
    and converts the responses into GA4GH messages.

    :return:
    """
    req_body = app.current_request.json_body
    if req_body:
        page_token = req_body.get('page_token', None)
        page_size = req_body.get('page_size', None)
    else:
        page_token = "0"
        page_size = 100
    if req_body and (page_token or page_size):
        gdc_req = dos_list_request_to_indexd(req_body)
    else:
        gdc_req = {}
    response = requests.get("{}/index/".format(INDEXD_URL), params=gdc_req)
    if response.status_code != 200:
        return Response(
            {'msg': 'The request was malformed {}'.format(
                response.json().get('message', ""))})
    list_response = response.json()
    return gdc_to_dos_list_response(list_response)


@app.route(
    '/ga4gh/dos/v1/dataobjects/{data_object_id}/versions',
    methods=['GET'], cors=True)
def get_data_object_versions(data_object_id):
    req = requests.get(
        "{}/index/{}".format(INDEXD_URL, data_object_id))
    return req.json()


@app.route('/')
def index():
    message = "<h1>Welcome to the DOS lambda, " \
              "send requests to /ga4gh/dos/v1/</h1>"
    return Response(body=message,
                    status_code=200,
                    headers={'Content-Type': 'text/html'})
