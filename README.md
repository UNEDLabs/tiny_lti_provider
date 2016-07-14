# Python LTI provider

`uned_lti_py` is a simple LTI Tool Provider that is a fork of [ims_lti_py](https://github.com/tophatmonocle/ims_lti_py).
Besides, it presents a TP example based on (https://github.com/tophatmonocle/lti_tool_provider_example_flask).

## Tool Provider example

Edit the file tool_provider.py in order to config your Tool Provider:

 * port: connection port
 * app.secret_key:  app key
 * oauth_creds: id/password pair, e.g. "{ 'test': 'secret', 'simple': 'supersecret' }"
 * assessment_creds: id/tool pair, e.g. "{ 'test': 'test.html', 'simple': 'simple.html' }"

Launch:

```
python tool_provider.py
``` 

The Tool Provider includes two tools:
 * Test LTI Tool (tool/test.html). It shows all LTI params provided by LTI consumer.
 * Simple LTI Assessment Tool (tool/simple.html). It uses the username and send a score to LTI consumer. 

## Usage in Moodle

Moodle allows you to include a "External Tool" based on LTI. The main settings are:
 * Launch URL: http://yourdomain:port/lti_tool  
 * Consumer key: oauth id, e.g. 'test'
 * Shared secret: oauth password, e.g. 'secret'
 * Custom parameters: any custom parameter that your tool needs
 * Accept grades from the tool: whether your tool returns score

## Dependencies

 * [Flask](https://github.com/mitsuhiko/flask)
 * [lxml](https://github.com/lxml/lxml)
 * [python-oauth2](https://github.com/simplegeo/python-oauth2)

## Authors

ims_lti_py (original):
* Anson MacKeracher (https://github.com/amackera)
* Jero Sutlovic (https://github.com/jsutlovic)

uned_lti_py:
* Felix J. Garcia (https://github.com/felixgarcia)
* Luis de la Torre (https://github.com/Ravenink)

## Acknowledgment
Este trabajo es resultado de la estancia 19937/EE/15 financiada por la Fundación Séneca-Agencia de Ciencia y Tecnología de la Región de Murcia con cargo al Programa “Jiménez de la Espada” de Movilidad Investigadora, Cooperación e Internacionalización.
