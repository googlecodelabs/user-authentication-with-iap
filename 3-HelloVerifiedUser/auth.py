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

from flask import request
from jose import jwt
import os
import requests

KEYS = None     # Cached public keys for verification
AUDIENCE = None # Cached value requiring information from metadata server


# Google publishes the public keys needed to verify a JWT. Save them in KEYS.
def keys():
    global KEYS

    if KEYS is None:
        resp = requests.get('https://www.gstatic.com/iap/verify/public_key')
        KEYS = resp.json()

    return KEYS


# Returns the JWT "audience" that should be in the assertion
def audience():
    global AUDIENCE

    if AUDIENCE is None:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT', None)

        endpoint = 'http://metadata.google.internal'
        path = '/computeMetadata/v1/project/numeric-project-id'
        response = requests.get(
            '{}/{}'.format(endpoint, path),
            headers = {'Metadata-Flavor': 'Google'}
        )
        project_number = response.json()

        AUDIENCE = '/projects/{}/apps/{}'.format(project_number, project_id)

    return AUDIENCE


# Return the authenticated user's email address and persistent user ID if
# available from Cloud Identity Aware Proxy (IAP). If IAP is not active,
# returns None.
#
# Raises an exception if IAP header exists, but JWT token is invalid, which
# would indicates bypass of IAP or inability to fetch KEYS.
def user():
    # Requests coming through IAP have special headers
    assertion = request.headers.get('X-Goog-IAP-JWT-Assertion')
    if assertion is None:   # Request did not come through IAP
        return None, None

    info = jwt.decode(
        assertion,
        keys(),
        algorithms=['ES256'],
        audience=audience()
    )

    return info['email'], info['sub']
