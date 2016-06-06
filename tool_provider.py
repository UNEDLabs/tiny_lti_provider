from flask import Flask, render_template, session, request,\
        make_response, send_from_directory
        
from uned_lti_py import ToolProvider, ToolConfig

from time import time
import os
import json

app = Flask(__name__, static_url_path='', template_folder='./tools')

# Tool provider configuration parameters 
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
oauth_creds = { 'test': 'secret', 'simple': 'supersecret' }
assessment_creds = { 'test': 'test.html', 'simple': 'simple.html' }
port = 5000

@app.route('/', methods = ['GET'])
def index():
    return render_template('index.html')

@app.route('/lti_tool', methods = ['POST'])
def lti_tool():
    # check auth
    key = request.form.get('oauth_consumer_key')
    if key:
        secret = oauth_creds.get(key)
        if secret:
            tool_provider = ToolProvider(key, secret, request.form)
        else:
            tool_provider = ToolProvider(None, None, request.form)
            tool_provider.lti_msg = 'Your consumer didn\'t use a recognized key'
            tool_provider.lti_errorlog = 'You did it wrong!'
            return render_template('error.html', 
                    message = 'Consumer key wasn\'t recognized',
                    params = request.form)
    else:
        return render_template('error.html', message = 'No consumer key')

    if not tool_provider.is_valid_request(request):
        return render_template('error.html', 
                message = 'The OAuth signature was invalid',
                params = request.form)

    if time() - int(tool_provider.get_launch_param('oauth_timestamp')) > 60*60:
        return render_template('error.html', message = 'Your request is too old.')

    # tools should be checking the OAuth nonce
    if was_nonce_used_in_last_x_minutes(tool_provider.get_launch_param('oauth_nonce'), 60):
        return render_template('error.html', message = 'Why are you reusing the nonce?')

    session['launch_params'] = tool_provider.to_json_params()
    lti_params = tool_provider.to_json_params(excluded='oauth')  # JSON with LTI params (excluding oauth params)
    if tool_provider.is_outcome_service():
        return render_template(assessment_creds[key], lti_params = json.dumps(lti_params))
    else:
        return render_template(assessment_creds[key], lti_params = json.dumps(lti_params), 
		    launch_presentation_return_url = tool_provider.get_launch_param('launch_presentation_return_url'))

@app.route('/assessment', methods = ['POST'])
def assessment():
    if session['launch_params']:
        key = session['launch_params']['oauth_consumer_key']
    else:
        return render_template('error.html', message = 'The tool never launched')

    tool_provider = ToolProvider(key, oauth_creds[key], session['launch_params'])

    if not tool_provider.is_outcome_service():
        return render_template('error.html', message = 'The tool wasn\'t launch as an outcome service.')

    # Post the given score to the ToolConsumer
    response = tool_provider.post_replace_result(request.form.get('score'))
    if response.is_success():
        score = request.form.get('score')
        tool_provider.lti_message = 'Message shown when arriving back at Tool Consumer.'
        return render_template('simple_finished.html',
                score = score, 
                launch_presentation_return_url = tool_provider.get_launch_param('launch_presentation_return_url'))
    else:
        tool_provider.lti_errormsg = 'The Tool Consumer failed to add the score.'
        return render_template('error.html', message = response.description, return_url = tool_provider.launch_presentation_return_url)

@app.route('/tool_config.xml', methods = ['GET'])
def tool_config():
    host = request.scheme + '://' + request.host
    secure_host = 'https://' + request.host
    url = host + '/lti_tool'
    secure_url = secure_host + '/lti_tool'
    lti_tool_config = ToolConfig(
        title='Example Flask Tool Provider',
        launch_url=url,
        secure_launch_url=secure_url)
    lti_tool_config.description = 'This example LTI Tool Provider supports LIS Outcome pass-back'
    resp = make_response(lti_tool_config.to_xml(), 200)
    resp.headers['Content-Type'] = 'text/xml' 
    return resp

def was_nonce_used_in_last_x_minutes(nonce, minutes):
    return False
	
if __name__ == '__main__':
    #if 'DEBUG' in os.environ:
    app.debug = True
    app.run(host="0.0.0.0", port=port)
