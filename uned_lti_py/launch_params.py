from collections import defaultdict
import sys
import json

# List of the standard launch parameters for an LTI launch
LAUNCH_DATA_PARAMETERS = [
    'context_id',
    'context_label',
    'context_title',
    'context_type',
    'launch_presentation_css_url',
    'launch_presentation_document_target',
    'launch_presentation_height',
    'launch_presentation_locale',
    'launch_presentation_return_url',
    'launch_presentation_width',
    'lis_course_section_sourcedid',
    'lis_outcome_service_url',
    'lis_person_contact_email_primary',
    'lis_person_name_family',
    'lis_person_name_full',
    'lis_person_name_given',
    'lis_person_sourcedid',
    'lis_result_sourcedid',
    'lti_message_type',
    'lti_version',
    'oauth_callback',
    'oauth_consumer_key',
    'oauth_nonce',
    'oauth_signature',
    'oauth_signature_method',
    'oauth_timestamp',
    'oauth_version',
    'resource_link_description',
    'resource_link_id',
    'resource_link_title',
    'roles',
    'tool_consumer_info_product_family_code',
    'tool_consumer_info_version',
    'tool_consumer_instance_contact_email',
    'tool_consumer_instance_description',
    'tool_consumer_instance_guid',
    'tool_consumer_instance_name',
    'tool_consumer_instance_url',
    'user_id',
    'user_image'
]

class LaunchParamsMixin(object):
    def __init__(self):
        super(LaunchParamsMixin, self).__init__()

        self.launch_params = {}
        for param in LAUNCH_DATA_PARAMETERS:
            self.launch_params[param] = None

        # We only support oauth 1.0 for now
        self.oauth_version = '1.0'

        # These dictionaries return a 'None' object when accessing a key that
        # is not in the dictionary.
        self.custom_params = {}
        self.ext_params = {}
        self.params = {}
        
    def process_params(self, params):
        '''
        Populates the launch data from a dictionary. Only cares about keys in
        the LAUNCH_DATA_PARAMETERS list, or that start with 'custom_' or
        'ext_'.
        '''
        for key, val in params.items():
            if key in LAUNCH_DATA_PARAMETERS and val != 'None':
                self.launch_params[key] = val
            elif 'custom_' in key:
                self.custom_params[key] = val
            elif 'ext_' in key:
                self.ext_params[key] = val

    def get_custom_param(self, key):
        return self.custom_params['custom_' + key]

    def get_ext_param(self, key):
        return self.ext_params['ext_' + key]

    def get_launch_param(self, key):
        return self.launch_params[key]

    def to_json_params(self, excluded = ''):
        '''
        Create a new dictionary with all launch data in JSON format. 
        Custom / Extension keys will be included, not excluded keys.
        '''
        json_params = {}
        params = dict(self.custom_params.items() + self.ext_params.items() + self.launch_params.items())
        for key in params.keys():
            if (len(excluded) == 0 or not key.startswith(excluded)) and params[key] != None:
               try:
                  value = json.loads(params[key])
                  json_params[key] = value
               except Exception:
                  try:
                     value = json.loads('"' + params[key] + '"')
                     json_params[key] = value
                  except Exception, e:
                     print('[Exception]' + key + ':' + str(e))
                     pass
        return json_params