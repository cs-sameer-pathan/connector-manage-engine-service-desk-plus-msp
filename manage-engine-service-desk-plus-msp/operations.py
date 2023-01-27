""" Copyright start
  Copyright (C) 2008 - 2023 Fortinet Inc.
  All rights reserved.
  FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE
  Copyright end """
import requests
import json
from .constants import *
from connectors.core.connector import get_logger, ConnectorError

logger = get_logger('manage-engine-service-desk-plus-msp')


class ManageEngine:
    def __init__(self, config):
        self.server_url = config.get('server_url')
        if self.server_url.startswith('https://') or self.server_url.startswith('http://'):
            self.server_url = self.server_url.strip('/')
        else:
            self.server_url = 'http://{0}'.format(self.server_url)
        self.token = config.get('token')
        self.verify_ssl = config.get('verify_ssl')

    def make_api_call(self, config, method, endpoint=None, params=None, data=None, json1=None, files=None):
        if endpoint:
            url = '{0}{1}'.format(self.server_url, endpoint)
        else:
            url = self.server_url
        logger.info('Request URL {0}'.format(url))
        headers = {
            'Accept': 'application/vnd.manageengine.sdp.v3+json',
            'authtoken': self.token
        }
        try:
            response = requests.request(method=method, url=url,
                                        params=params, headers=headers, data=data, verify=self.verify_ssl)
            if response.ok:
                logger.warn(response.json())
                return response.json()
            elif response.status_code == 401:
                logger.info('Unauthorized: Invalid credentials')
                raise ConnectorError('Unauthorized: Invalid credentials')
            else:
                logger.info(
                    'Fail To request API {0} response is : {1} with reason: {2}'.format(str(url), str(response.content),
                                                                                        str(response.reason)))
                raise ConnectorError(
                    'Fail To request API {0} response is :{1} with reason: {2}'.format(str(url), str(response.content),
                                                                                       str(response.reason)))
        except requests.exceptions.SSLError as e:
            logger.exception('{0}'.format(e))
            raise ConnectorError('{0}'.format('SSL certificate validation failed'))
        except requests.exceptions.ConnectionError as e:
            if 'Max retries exceeded with url' in str(e):
                logger.exception('Failed to establish a new connection. Invalid URL')
                raise ConnectorError('Failed to establish a new connection. Invalid URL')
            else:
                logger.exception('{0}'.format(e))
                raise ConnectorError('{0}'.format('The request timed out while trying to connect to the remote server'))
        except Exception as e:
            if 'timed out' in str(e):
                logger.exception('Failed to establish a new connection. Invalid URL')
                raise ConnectorError('Failed to establish a new connection. Invalid URL')
            else:
                logger.exception('{0}'.format(e))
                raise ConnectorError('{0}'.format(e))


def build_payload(params):
    result = dict()
    for key, value in params.items():
        if value != '' and value is not None:
            result[key] = value
    return result


def check_health(config):
    obj = ManageEngine(config)
    try:
        if obj.make_api_call(config, method='GET', endpoint=USER_ENDPOINT):
            return True
    except Exception as Err:
        logger.exception('Error occured while connecting server: {0}'.format(str(Err)))
        raise ConnectorError('Error occured while connecting server: {0}'.format(Err))


def add_request(config, params):
    obj = ManageEngine(config)
    try:
        payload = {}
        status = params.pop("status", '')
        if status:
            payload.update({"status": {"name": status}})
        urgency = params.pop("urgency", '')
        if urgency:
            payload.update({"urgency": {"name": urgency}})
        priority = params.pop("priority", '')
        if priority:
            payload.update({"priority": {"name": priority}})
        requester = params.pop("requester", '')
        if requester:
            payload.update({"requester": requester})
        request_type = params.pop("request_type", '')
        if request_type:
            payload["request_type"] = {"name": request_type}
        group = params.pop("group", "")
        if group:
            payload["group"] = {"name": group}
        other_fields = params.pop('other_fields', '')
        payload.update(build_payload(params))
        if other_fields:
            payload.update(other_fields)
        input_data = json.dumps({"request": payload})
        data = {"input_data": input_data}
        logger.info("payload data>>")
        logger.info(input_data)
        return obj.make_api_call(config, method='POST', endpoint=REQUEST_ENDPOINT, data=data)
    except Exception as Err:
        logger.error('Exception occurred: {0}'.format(Err))
        raise ConnectorError(Err)


def update_request(config, params):
    obj = ManageEngine(config)
    try:
        payload = {}
        request_id = params.pop('request_id')
        status = params.pop("status", '')
        if status:
            payload.update({"status": {"name": status}})
        urgency = params.pop("urgency", '')
        if urgency:
            payload.update({"urgency": {"name": urgency}})
        priority = params.pop("priority", '')
        if priority:
            payload.update({"priority": {"name": priority}})
        other_fields = params.pop('other_fields', '')
        payload.update(build_payload(params))
        if other_fields:
            payload.update(other_fields)
        input_data = json.dumps({"request": payload})
        data = {"input_data": input_data}
        return obj.make_api_call(config, method='PUT', endpoint=REQUEST_ENDPOINT + "/" + str(request_id), data=data)
    except Exception as Err:
        logger.error('Exception occurred: {0}'.format(Err))
        raise ConnectorError(Err)


def add_resolution(config, params):
    obj = ManageEngine(config)
    try:
        input_data = {
            "resolution": {
                "content": params.get("resolution")
            }}
        return obj.make_api_call(config, method='POST', endpoint=REQUEST_ENDPOINT + "/" + str(params.get('request_id')) + '/resolutions', data={"input_data": json.dumps(input_data)})
    except Exception as Err:
        logger.error('Exception occurred: {0}'.format(Err))
        raise ConnectorError(Err)


def add_note(config, params):
    obj = ManageEngine(config)
    try:
        request_id = params.pop('request_id')
        payload = build_payload(params)
        data = json.dumps({"note": payload})
        return obj.make_api_call(config, method='POST', endpoint=REQUEST_ENDPOINT + "/" + str(request_id) + '/notes', data={"input_data": data})
    except Exception as Err:
        logger.error('Exception occurred: {0}'.format(Err))
        raise ConnectorError(Err)


def get_request(config, params):
    obj = ManageEngine(config)
    try:
        request_id = str(params.get('request_id'))
        return obj.make_api_call(config, method='GET', endpoint=REQUEST_ENDPOINT + "/" + request_id)
    except Exception as Err:
        logger.error('Exception occurred: {0}'.format(Err))
        raise ConnectorError(Err)


def get_all_open_requests(config, params):
    obj = ManageEngine(config)
    try:
        start = params.pop("from", 1)
        limit = params.pop("limit", '')
        sort_order = params.pop('sort_order', '')
        sort_field = params.pop('sort_field', '')
        other_fields = params.pop("other_fields", '')
        params["status.name"] = "Open"
        if other_fields:
            params.update(other_fields)
        payload = build_payload(params)
        list_info = {
            "start_index": start,
            "get_total_count": True,
            "search_fields": payload
        }
        if limit:
            list_info["row_count"] = limit
        if sort_order:
            list_info["sort_order"] = SORT_ORDER.get(sort_order)
        if sort_field:
            list_info["sort_field"] = sort_field
        input_data = json.dumps({"list_info": list_info})
        response = obj.make_api_call(config, method='GET', endpoint=REQUEST_ENDPOINT, params={"input_data": input_data})
        return response
    except Exception as Err:
        logger.error('Exception occurred: {0}'.format(Err))
        raise ConnectorError(Err)


def get_all_users(config, params):
    obj = ManageEngine(config)
    try:
        start_index = params.pop('start_index', 1)
        size = params.pop('size', '')
        sort_field = params.pop('sort_field', '')
        sort_order = params.pop('sort_order', '')
        fields_required = params.pop('fields_required', '')
        other_fields = params.pop('other_fields', '')
        if other_fields:
            params.update(other_fields)
        payload = build_payload(params)
        list_info = {
            "start_index": start_index,
            "search_fields": payload
        }
        if size:
            list_info["row_count"] = size
        if sort_field:
            list_info.update({"sort_field": sort_field})
        if sort_order:
            list_info.update({"sort_order": SORT_ORDER.get(sort_order)})
        input_data = {
            "list_info": list_info
        }
        if fields_required:
            input_data["fields_required"] = fields_required.split(",")
        params = {"input_data": json.dumps(input_data)}
        return obj.make_api_call(config, method='GET', endpoint=USER_ENDPOINT, params=params)
    except Exception as Err:
        logger.error('Exception occurred: {0}'.format(Err))
        raise ConnectorError(Err)


def get_all_sites(config, params):
    obj = ManageEngine(config)
    try:
        response = obj.make_api_call(config, method='GET', endpoint=SITE_ENDPOINT)
        return response
    except Exception as Err:
        logger.error('Exception occurred: {0}'.format(Err))
        raise ConnectorError(Err)


def close_request(config, params):
    obj = ManageEngine(config)
    try:
        request_id = str(params.get('request_id'))
        closure_info = {
            "requester_ack_resolution": params.get("requester_ack_resolution"),
        }
        if params.get("requester_ack_comments"):
            closure_info["requester_ack_comments"] = params.get("requester_ack_comments")
        if params.get("closure_comments"):
            closure_info["closure_comments"] = params.get("closure_comments")
        if params.get("closure_code"):
            closure_info["closure_code"] = {
                "name": params.get("closure_code")
            }
        input_data = {
            'request': {
                "closure_info": closure_info,
                "is_fcr": params.get("is_fcr")
                    }
            }
        return obj.make_api_call(config, method='PUT', endpoint=REQUEST_ENDPOINT + "/" + request_id + '/close', data={"input_data":  json.dumps(input_data)})
    except Exception as Err:
        logger.error('Exception occurred: {0}'.format(Err))
        raise ConnectorError(Err)


def delete_request(config, params):
    obj = ManageEngine(config)
    try:
        request_id = str(params.get('request_id'))
        return obj.make_api_call(config, method='DELETE', endpoint=REQUEST_ENDPOINT + "/" +request_id + "/move_to_trash")
    except Exception as Err:
        logger.error('Exception occurred: {0}'.format(Err))
        raise ConnectorError(Err)


def delete_request_from_trash(config, params):
    obj = ManageEngine(config)
    try:
        request_id = str(params.get('request_id'))
        return obj.make_api_call(config, method='DELETE', endpoint=REQUEST_ENDPOINT + "/" + request_id)
    except Exception as Err:
        logger.error('Exception occurred: {0}'.format(Err))
        raise ConnectorError(Err)


def get_all_accounts(config, params):
    obj = ManageEngine(config)
    endpoint = ACCOUNT_ENDPOINT
    try:
        params = {
            "format": "json",
            "TECHNICIAN_KEY": obj.token
        }
        if endpoint:
            url = '{0}{1}'.format(obj.server_url, endpoint)
        else:
            url = obj.server_url
        logger.info('Request URL {0}'.format(url))
        try:
            response = requests.request(method="GET", url=url,
                                        params=params, verify=obj.verify_ssl)
            if response.ok:
                logger.warn(response.json())
                return response.json()
            elif response.status_code == 401:
                logger.info('Unauthorized: Invalid credentials')
                raise ConnectorError('Unauthorized: Invalid credentials')
            else:
                logger.info(
                    'Fail To request API {0} response is : {1} with reason: {2}'.format(str(url), str(response.content), str(response.reason)))
                raise ConnectorError(
                    'Fail To request API {0} response is :{1} with reason: {2}'.format(str(url), str(response.content), str(response.reason)))
        except requests.exceptions.SSLError as e:
            logger.exception('{0}'.format(e))
            raise ConnectorError('{0}'.format('SSL certificate validation failed'))
        except requests.exceptions.ConnectionError as e:
            if 'Max retries exceeded with url' in str(e):
                logger.exception('Failed to establish a new connection. Invalid URL')
                raise ConnectorError('Failed to establish a new connection. Invalid URL')
            else:
                logger.exception('{0}'.format(e))
                raise ConnectorError(
                    '{0}'.format('The request timed out while trying to connect to the remote server'))
        except Exception as e:
            if 'timed out' in str(e):
                logger.exception('Failed to establish a new connection. Invalid URL')
                raise ConnectorError('Failed to establish a new connection. Invalid URL')
            else:
                logger.exception('{0}'.format(e))
                raise ConnectorError('{0}'.format(e))

    except Exception as Err:
        logger.error('Exception occurred: {0}'.format(Err))
        raise ConnectorError(Err)


def get_all_accounts(config, params):
    obj = ManageEngine(config)
    endpoint = ACCOUNT_ENDPOINT
    params = {
        "format": "json",
        "TECHNICIAN_KEY": obj.token
    }
    response = obj.make_api_call(config=config, method="GET", endpoint=endpoint, params=params)
    return response


operations = {
    'add_request': add_request,
    'add_resolution': add_resolution,
    'add_note': add_note,
    'get_request': get_request,
    'get_all_open_requests': get_all_open_requests,
    'get_all_sites': get_all_sites,
    'update_request': update_request,
    'close_request': close_request,
    'delete_request': delete_request,
    'delete_request_from_trash': delete_request_from_trash,
    'get_all_user': get_all_users,
    'get_all_accounts': get_all_accounts
}
