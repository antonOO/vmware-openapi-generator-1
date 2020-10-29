# Copyright 2020 VMware, Inc.
# SPDX-License-Identifier: MIT

from lib import utils


class ApiMetamodel2Spec():

    def get_path(
            self,
            operation_info,
            http_method,
            url,
            service_name,
            type_dict,
            structure_dict,
            enum_dict,
            operation_id,
            error_map,
            show_unreleased_apis):
        pass

    def handle_request_mapping(
            self,
            url,
            method_type,
            service_name,
            operation_name,
            params_metadata,
            content_type,
            type_dict,
            structure_svc,
            enum_svc,
            show_unreleased_apis,
            spec):
        if method_type in ('post', 'put', 'patch'):
            return self.process_put_post_patch_request(
                url,
                service_name,
                operation_name,
                params_metadata,
                content_type,
                type_dict,
                structure_svc,
                enum_svc,
                show_unreleased_apis,
                spec)
        if method_type == 'get':
            return self.process_get_request(
                url,
                params_metadata,
                type_dict,
                structure_svc,
                enum_svc,
                show_unreleased_apis,
                spec)
        if method_type == 'delete':
            return self.process_delete_request(
                url,
                params_metadata,
                type_dict,
                structure_svc,
                enum_svc,
                show_unreleased_apis,
                spec)

    def process_put_post_patch_request(
            self,
            url,
            service_name,
            operation_name,
            params,
            content_type,
            type_dict,
            structure_svc,
            enum_svc,
            show_unreleased_apis,
            spec):
        """
        Handles http post/put/patch request.
        todo: handle query, formData and header parameters
        """
        # Path
        path_param_list, other_param_list, new_url = utils.extract_path_parameters(
            params, url)
        par_array = []
        for field_info in path_param_list:
            parx = spec.convert_field_info_to_swagger_parameter(
                'path', field_info, type_dict, structure_svc, enum_svc, show_unreleased_apis)
            par_array.append(parx)

        # Body
        body_param_list, other_param_list = utils.extract_body_parameters(
            other_param_list)

        if body_param_list:
            parx = spec.wrap_body_params(
                service_name,
                operation_name,
                content_type,
                body_param_list,
                type_dict,
                structure_svc,
                enum_svc,
                show_unreleased_apis)
            if parx is not None:
                if isinstance(parx, list):
                    par_array.extend(parx)
                else:
                    par_array.append(parx)

        # Query
        query_param_list, other_param_list = utils.extract_query_parameters(
            other_param_list)
        for query_param in query_param_list:
            parx = spec.convert_field_info_to_swagger_parameter(
                'query', query_param, type_dict, structure_svc, enum_svc, show_unreleased_apis)
            par_array.append(parx)

        # process query parameters
        for field_info in other_param_list:
            # See documentation of method flatten_query_param_spec to understand
            # handling of all the query parameters; filter as well as non
            # filter
            flattened_params = spec.flatten_query_param_spec(
                field_info, type_dict, structure_svc, enum_svc, show_unreleased_apis)
            if flattened_params is not None:
                par_array = par_array + flattened_params

        return par_array, new_url

    def process_get_request(
            self,
            url,
            params,
            type_dict,
            structure_svc,
            enum_svc,
            show_unreleased_apis,
            spec):
        param_array = []
        path_param_list, other_params_list, new_url = utils.extract_path_parameters(
            params, url)

        for field_info in path_param_list:
            parameter_obj = spec.convert_field_info_to_swagger_parameter(
                'path', field_info, type_dict, structure_svc, enum_svc, show_unreleased_apis)
            param_array.append(parameter_obj)

        query_param_list, other_params_list = utils.extract_query_parameters(
            other_params_list)
        # Query
        for query_param in query_param_list:
            parameter_obj = spec.convert_field_info_to_swagger_parameter(
                'query', query_param, type_dict, structure_svc, enum_svc, show_unreleased_apis)
            param_array.append(parameter_obj)

        # process query parameters
        for field_info in other_params_list:
            # See documentation of method flatten_query_param_spec to understand
            # handling of all the query parameters; filter as well as non
            # filter
            flattened_params = spec.flatten_query_param_spec(
                field_info, type_dict, structure_svc, enum_svc, show_unreleased_apis)
            if flattened_params is not None:
                param_array = param_array + flattened_params
        return param_array, new_url

    def process_delete_request(
            self,
            url,
            params,
            type_dict,
            structure_svc,
            enum_svc,
            show_unreleased_apis,
            spec):
        path_param_list, other_params, new_url = utils.extract_path_parameters(
            params, url)
        param_array = []
        for field_info in path_param_list:
            parx = spec.convert_field_info_to_swagger_parameter(
                'path', field_info, type_dict, structure_svc, enum_svc, show_unreleased_apis)
            param_array.append(parx)
        for field_info in other_params:
            parx = spec.convert_field_info_to_swagger_parameter(
                'query', field_info, type_dict, structure_svc, enum_svc, show_unreleased_apis)
            param_array.append(parx)
        return param_array, new_url

    def post_process_path(self, path_obj):
        pass
