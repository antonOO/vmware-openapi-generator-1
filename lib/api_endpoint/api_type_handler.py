from lib import utils
from lib.type_handler_common import TypeHandlerCommon


class ApiTypeHandler(TypeHandlerCommon):

    def __init__(self, show_unreleased_apis):
        TypeHandlerCommon.__init__(self, show_unreleased_apis)

    def visit_generic(
            self,
            generic_instantiation,
            new_prop,
            type_dict,
            structure_svc,
            enum_svc,
            ref_path):
        if generic_instantiation.generic_type == 'OPTIONAL':
            new_prop['required'] = False
            self.visit_type_category(
                generic_instantiation.element_type,
                new_prop,
                type_dict,
                structure_svc,
                enum_svc,
                ref_path)
        elif generic_instantiation.generic_type == 'LIST':
            new_prop['type'] = 'array'
            self.visit_type_category(
                generic_instantiation.element_type,
                new_prop,
                type_dict,
                structure_svc,
                enum_svc,
                ref_path)
        elif generic_instantiation.generic_type == 'SET':
            new_prop['type'] = 'array'
            new_prop['uniqueItems'] = True
            self.visit_type_category(
                generic_instantiation.element_type,
                new_prop,
                type_dict,
                structure_svc,
                enum_svc,
                ref_path)
        elif generic_instantiation.generic_type == 'MAP':
            # Have static key/value pair object maping for /rest paths
            # while use additionalProperties for /api paths
            new_type = {'type': 'object', 'additionalProperties': {}}

            if generic_instantiation.map_value_type.category == 'USER_DEFINED':
                new_type['additionalProperties'] = {
                    '$ref': ref_path + generic_instantiation.map_value_type.user_defined_type.resource_id}
                res_type = generic_instantiation.map_value_type.user_defined_type.resource_type
                res_id = generic_instantiation.map_value_type.user_defined_type.resource_id
                self.check_type(
                    res_type,
                    res_id,
                    type_dict,
                    structure_svc,
                    enum_svc,
                    ref_path)

            elif generic_instantiation.map_value_type.category == 'BUILTIN':
                new_type['additionalProperties'] = {
                    'type': utils.metamodel_to_swagger_type_converter(
                        generic_instantiation.map_value_type.builtin_type)[0]}

            elif generic_instantiation.map_value_type.category == 'GENERIC':
                temp_new_type = {}
                self.visit_generic(
                    generic_instantiation.map_value_type.generic_instantiation,
                    temp_new_type,
                    type_dict,
                    structure_svc,
                    enum_svc,
                    ref_path)
                new_type['additionalProperties'] = temp_new_type

            new_prop.update(new_type)

            if 'additionalProperties' in new_type:
                if not new_type['additionalProperties'].get('required', True):
                    del new_type['additionalProperties']['required']

            if '$ref' in new_prop:
                del new_prop['$ref']
