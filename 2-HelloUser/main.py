# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import Flask, render_template, request

app = Flask(__name__)


# Disable browser caching so changes in each step are always shown
@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/', methods=['GET'])
def say_hello():
    user_email = request.headers.get('X-Goog-Authenticated-User-Email')
    user_id = request.headers.get('X-Goog-Authenticated-User-ID')

    page = render_template('index.html',
        email=user_email,
        id=user_id)
    return page

@app.route('/privacy', methods=['GET'])
def show_policy():
    page = render_template('privacy.html')
    return page


if __name__ == '__main__':
    # This is used when running locally, only to verify it does not have
    # significant errors. It cannot demonstrate restricting access using
    # Identity-Aware Proxy when run locally, only when deployed.
    #
    # When deploying to Google App Engine, a webserver process such as
    # Gunicorn will serve the app. This can be configured by adding an
    # `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
