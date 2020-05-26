'''
This script uses metamodel apis and rest navigation to generate openapi json files
for apis available on vcenter.
'''
from __future__ import print_function
from lib import RestUrlProcessing
from lib import ApiUrlProcessing
from lib import dictionary_processing as dict_processing
from lib import establish_connection as connection
from lib import utils
from vmware.vapi.core import ApplicationContext
from vmware.vapi.lib.constants import SHOW_UNRELEASED_APIS
from vmware.vapi.lib.connect import get_requests_connector
import os
import sys
import threading
import timeit
import warnings
import requests
import six

from lib.rest_endpoint.rest_deprecation_handler import RestDeprecationHandler
from lib.rest_endpoint.rest_navigation_handler import RestNavigationHandler

warnings.filterwarnings("ignore")


GENERATE_UNIQUE_OP_IDS = False
GENERATE_METAMODEL = False
API_SERVER_HOST = '<vcenter>'
TAG_SEPARATOR = '/'
SPECIFICATION = '3'
MIXED = False


def main():
    # Get user input.
    metadata_api_url, rest_navigation_url, output_dir, verify, show_unreleased_apis, GENERATE_METAMODEL, SPECIFICATION, GENERATE_UNIQUE_OP_IDS, TAG_SEPARATOR, MIXED = connection.get_input_params()
    # Maps enumeration id to enumeration info
    enumeration_dict = {}
    # Maps structure_id to structure_info
    structure_dict = {}
    # Maps service_id to service_info
    service_dict = {}
    # Maps service url to service id
    service_urls_map = {}

    rest_navigation_handler = RestNavigationHandler(rest_navigation_url)

    start = timeit.default_timer()
    print('Trying to connect ' + metadata_api_url)
    session = requests.session()
    session.verify = False
    connector = get_requests_connector(session, url=metadata_api_url)
    if show_unreleased_apis:
        connector.set_application_context(
            ApplicationContext({SHOW_UNRELEASED_APIS: "True"}))
    print('Connected to ' + metadata_api_url)
    component_svc = connection.get_component_service(connector)
    dict_processing.populate_dicts(
        component_svc,
        enumeration_dict,
        structure_dict,
        service_dict,
        service_urls_map,
        rest_navigation_url,
        GENERATE_METAMODEL)

    # if show_unreleased_apis:
    #     service_urls_map = dict_processing.get_service_urls_from_rest_navigation(
    #         rest_navigation_url, verify)

    http_error_map = utils.HttpErrorMap(component_svc)

    deprecation_handler = None
    if MIXED:
        # package_dict_api holds list of all service urls which come under /api
        # package_dict_deprecated holds a list of all service urls which come under /rest, but are
        # deprecated with /api
        # replacement_map contains information about the deprecated /rest to /api mappings
        package_dict_api, package_dict, package_dict_deprecated, replacement_map = dict_processing.add_service_urls_using_metamodel(
            service_urls_map, service_dict, rest_navigation_handler, MIXED)

        utils.combine_dicts_with_list_values(package_dict, package_dict_deprecated)

        deprecation_handler = RestDeprecationHandler(replacement_map)
    else:
        # package_dict_api holds list of all service urls which come under /api
        package_dict_api, package_dict = dict_processing.add_service_urls_using_metamodel(
            service_urls_map, service_dict, rest_navigation_handler, MIXED)

    rest = RestUrlProcessing()
    api = ApiUrlProcessing()

    threads = []
    for package, service_urls in six.iteritems(package_dict):
        worker = threading.Thread(
            target=rest.process_service_urls,
            args=(
                package,
                service_urls,
                output_dir,
                structure_dict,
                enumeration_dict,
                service_dict,
                service_urls_map,
                http_error_map,
                rest_navigation_handler,
                show_unreleased_apis,
                SPECIFICATION,
                GENERATE_UNIQUE_OP_IDS,
                deprecation_handler))
        worker.daemon = True
        worker.start()
        threads.append(worker)

    for package, service_urls in six.iteritems(package_dict_api):
        worker = threading.Thread(
            target=api.process_service_urls,
            args=(
                package,
                service_urls,
                output_dir,
                structure_dict,
                enumeration_dict,
                service_dict,
                service_urls_map,
                http_error_map,
                show_unreleased_apis,
                SPECIFICATION,
                GENERATE_UNIQUE_OP_IDS))
        worker.daemon = True
        worker.start()
        threads.append(worker)
    for worker in threads:
        worker.join()

    # api.json contains list of packages which is used by UI to dynamically
    # populate dropdown.
    api_files_list = []
    for name in list(package_dict.keys()):
        api_files_list.append("rest_" + name)

    for name in list(package_dict_api.keys()):
        api_files_list.append("api_" + name)

    api_files = {'files': api_files_list}
    utils.write_json_data_to_file(
        output_dir +
        os.path.sep +
        'api.json',
        api_files)
    stop = timeit.default_timer()
    print('Generated swagger files at ' + output_dir + ' for ' +
          metadata_api_url + ' in ' + str(stop - start) + ' seconds')


if __name__ == '__main__':
    main()
