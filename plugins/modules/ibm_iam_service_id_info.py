# coding: utf-8

# (C) Copyright IBM Corp. 2022.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = r'''
---
module: ibm_iam_service_id_info
short_description: Manage ibm_iam_service_id info.
author: IBM SDK Generator
version_added: "0.1"
description:
    - This module retrieves one or more ibm_iam_service_id(s).
requirements:
    - "IamIdentityV1"
options:
    include_history:
        description:
            - Defines if the entity history is included in the response.
        type: bool
    id:
        description:
            - Unique ID of the service ID.
        type: str
    include_activity:
        description:
            - Defines if the entity's activity is included in the response. Retrieving activity data is an expensive operation, so please only request this when needed.
        type: bool
'''

EXAMPLES = r'''
Examples coming soon.
'''


from ansible.module_utils.basic import AnsibleModule
from ibm_cloud_sdk_core import ApiException
from ibm_platform_services import IamIdentityV1

from ..module_utils.auth import get_authenticator


def run_module():
    module_args = dict(
        include_history=dict(
            type='bool',
            required=False),
        id=dict(
            type='str',
            required=False),
        include_activity=dict(
            type='bool',
            required=False),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    include_history = module.params["include_history"]
    id = module.params["id"]
    include_activity = module.params["include_activity"]

    authenticator = get_authenticator(service_name='iam_identity')
    if authenticator is None:
        module.fail_json(msg='Cannot create the authenticator.')

    sdk = IamIdentityV1(
        authenticator=authenticator,
    )

    if id:
        # read
        try:
            response = sdk.get_service_id(
                id=id,
                include_history=include_history,
                include_activity=include_activity
            )
            module.exit_json(msg=response.get_result())
        except ApiException as ex:
            module.fail_json(msg=ex.message)


def main():
    run_module()


if __name__ == '__main__':
    main()