# Copyright © 2019 Province of British Columbia
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
"""Utils for keycloak administration"""

import os

from keycloak import KeycloakAdmin
from keycloak import KeycloakOpenID


KEYCLOAK_ADMIN = KeycloakAdmin(server_url=os.getenv('KEYCLOAK_BASE_URL') + '/auth/',
                               username=os.getenv('KEYCLOAK_ADMIN_CLIENTID'),
                               password=os.getenv('KEYCLOAK_ADMIN_SECRET'),
                               realm_name=os.getenv('KEYCLOAK_REALMNAME'),
                               client_id=os.getenv('KEYCLOAK_ADMIN_CLIENTID'),
                               client_secret_key=os.getenv('KEYCLOAK_ADMIN_SECRET'),
                               verify=True)


# Configure client
KEYCLOAK_OPENID = KeycloakOpenID(server_url=os.getenv('KEYCLOAK_BASE_URL') + '/auth/',
                                 realm_name=os.getenv('KEYCLOAK_REALMNAME'),
                                 client_id=os.getenv('KEYCLOAK_AUTH_AUDIENCE'),
                                 client_secret_key=os.getenv('KEYCLOAK_AUTH_CLIENT_SECRET'),
                                 verify=True)


class KeycloakService:
    """For Keycloak services."""
    def __init__(self):
        super()

    # Add user to Keycloak
    def add_user(self, user_request):
        """Add user to Keycloak"""

        # New user default to enabled.
        enabled = user_request.get('enabled')
        if enabled is None:
            enabled = True

        # Add user and set password
        try:
            KEYCLOAK_ADMIN.create_user({'email': user_request.get('email'),
                                        'username': user_request.get('username'),
                                        'enabled': enabled,
                                        'firstName': user_request.get('firstname'),
                                        'lastName': user_request.get('lastname'),
                                        'credentials': [{'value': user_request.get('password'), 'type': 'password'}],
                                        'groups': user_request.get('user_type'),
                                        'attributes': {'corp_type': user_request.get('corp_type'), 'source': user_request.get('source')}})

            user_id = KEYCLOAK_ADMIN.get_user_id(user_request.get('username'))

            # Set user groups
            if user_request.get('user_type'):
                for user_type in user_request.get('user_type'):
                    group = KEYCLOAK_ADMIN.get_group_by_path(user_type, True)
                    if group:
                        KEYCLOAK_ADMIN.group_user_add(user_id, group['id'])

            user = self.get_user_by_username(user_request.get('username'))

            return user
        except Exception as err:
            raise err

    def get_user_by_username(self, username):
        """ Get user from Keycloak by username"""
        try:
            # Get user id
            user_id_keycloak = KEYCLOAK_ADMIN.get_user_id(username)
            # Get User
            user = KEYCLOAK_ADMIN.get_user(user_id_keycloak)
            return user
        except Exception as err:
            raise err

    def delete_user_by_username(self, username):
        """Delete user from Keycloak by username"""
        try:
            user_id_keycloak = KEYCLOAK_ADMIN.get_user_id(username)
            # Get User
            response = KEYCLOAK_ADMIN.delete_user(user_id_keycloak)
            return response
        except Exception as err:
            raise err

    def get_token(self, username, password):
        """Get user access token by username and password"""
        return KEYCLOAK_OPENID.token(username, password)

    def refresh_token(self, refresh_token):
        """Refresh user token"""
        return KEYCLOAK_OPENID.refresh_token(refresh_token, ['refresh_token'])
