from launch_params import LaunchParamsMixin
from request_validator import RequestValidatorMixin
from outcome_request import OutcomeRequest
from collections import defaultdict
from urllib import urlencode
from urlparse import urlsplit, urlunsplit
from json import dumps

try:
    from urlparse import parse_qsl
except ImportError:
    # fall back for Python 2.5
    from cgi import parse_qsl  # NOQA


accessors = [
    'consumer_key',
    'consumer_secret',
    'outcome_requests',
    'lti_errormsg',
    'lti_errorlog',
    'lti_msg',
    'lti_log'
]


class ToolProvider(LaunchParamsMixin, RequestValidatorMixin, object):
    '''
    Implements the LTI Tool Provider.
    '''

    def __init__(self, consumer_key, consumer_secret, params={}):
        '''
        Create new ToolProvider.
        '''
        # Initialize all class accessors to None
        for param in accessors:
            setattr(self, param, None)

        # These are hyper important class members that we init first
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

        # Call superclass initializers
        super(ToolProvider, self).__init__()

        self.outcome_requests = []
        self.params = params
        self.process_params(params)

    def is_launch_request(self):
        '''
        Check if the request was an LTI Launch Request.
        '''
        return self.get_launch_param('lti_message_type') == 'basic-lti-launch-request'

    def is_outcome_service(self):
        '''
        Check if the Tool Launch expects an Outcome Result.
        '''
        return (self.get_launch_param('lis_outcome_service_url') and
                self.get_launch_param('lis_result_sourcedid'))

    def username(self, default=None):
        '''
        Return the full, given, or family name if set.
        '''
        if self.get_launch_param('lis_person_name_given'):
            return self.get_launch_param('lis_person_name_given')
        elif self.get_launch_param('lis_person_name_family'):
            return self.get_launch_param('lis_person_name_family')
        elif self.get_launch_param('lis_person_name_full'):
            return self.get_launch_param('lis_person_name_full')
        else:
            return default

    def post_replace_result(self, score, outcome_opts=defaultdict(lambda:None), result_data=None):
        '''
        POSTs the given score to the Tool Consumer with a replaceResult.

        Returns OutcomeResponse object and stores it in self.outcome_request

        OPTIONAL:
            result_data must be a dictionary
            Note: ONLY ONE of these values can be in the dict at a time,
            due to the Canvas specification.

            'text' : str text
            'url' : str url
        '''
        return self.new_request(outcome_opts).post_replace_result(score, result_data)

    def post_delete_result(self,outcome_opts=defaultdict(lambda:None)):
        '''
        POSTs a delete request to the Tool Consumer.
        '''
        return self.new_request(outcome_opts).post_delete_result()

    def post_read_result(self,outcome_opts=defaultdict(lambda:None)):
        '''
        POSTs the given score to the Tool Consumer with a replaceResult, the
        returned OutcomeResponse will have the score.
        '''
        return self.new_request(outcome_opts).post_read_result()

    def last_outcome_request(self):
        '''
        Returns the most recent OutcomeRequest.
        '''
        return self.outcome_requests[-1]

    def last_outcome_success(self):
        '''
        Convenience method for determining the success of the last
        OutcomeRequest.
        '''
        return all((self.last_outcome_request,
                    self.last_outcome_request.was_outcome_post_successful()))

    def build_return_url(self):
        '''
        If the Tool Consumer sent a return URL, add any set messages to the
        URL.
        '''
        if not self.get_launch_param('launch_presentation_return_url'):
            return None

        lti_message_fields = ['lti_errormsg', 'lti_errorlog',
                              'lti_msg', 'lti_log']

        messages = dict([(key, self.get_launch_param(key))
                         for key in lti_message_fields
                         if self.get_launch_param(key) != None])

        # Disassemble original return URL and reassemble with our options added
        original = urlsplit(self.get_launch_param('launch_presentation_return_url'))

        combined = messages.copy()
        combined.update(dict(parse_qsl(original.query)))

        combined_query = urlencode(combined)

        return urlunsplit((
            original.scheme,
            original.netloc,
            original.path,
            combined_query,
            original.fragment
        ))

    def new_request(self, defaults):
        opts = dict(defaults)
        opts.update({
            'consumer_key': self.consumer_key,
            'consumer_secret': self.consumer_secret,
            'lis_outcome_service_url': self.get_launch_param('lis_outcome_service_url'),
            'lis_result_sourcedid': dumps(self.get_launch_param('lis_result_sourcedid'))
        })
        self.outcome_requests.append(OutcomeRequest(opts=opts))
        self.last_outcome_request = self.outcome_requests[-1]
        return self.last_outcome_request
