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


import os

from ibm_cloud_sdk_core import ApiException

from ansible.modules.cloud.ibm import ibm_resource_key
from ibm_platform_services import *  # pylint: disable=wildcard-import,unused-wildcard-import
from units.compat.mock import patch
from units.modules.utils import ModuleTestCase, AnsibleFailJson, AnsibleExitJson, set_module_args

from .common import DetailedResponseMock


def post_process_result(expected: dict, result: dict) -> dict:
    """Removes implicitly added items by Ansible.

    Args:
        expected: the expected results
        result: the actual ressult
    Returns:
        A cleaned dictionary.
    """

    new_result = {}

    for res_key, res_value in result.items():
        try:
            mock_value = expected[res_key]
        except KeyError:
            # If this key not presented in the expected dictionary and its value is None
            # we can ignore it, since it supposed to be an implicitly added item by Ansible.
            if res_value is None:
                continue

            new_result[res_key] = res_value
        else:
            # We need to recursively check nested dictionaries as well.
            if isinstance(res_value, dict):
                new_result[res_key] = post_process_result(mock_value, res_value)
            # Just like lists.
            elif isinstance(res_value, list) and len(res_value) > 0:
                # We use an inner function for recursive list processing.
                def process_list(m: list, r: list) -> list:
                    # Create a new list that we will return at the end of this function.
                    # We will check, process then add each elements one by one.
                    new_list = []
                    for mock_elem, res_elem in zip(m, r):
                        # If both items are dict use the outer function to process them.
                        if isinstance(mock_elem, dict) and isinstance(res_elem, dict):
                            new_list.append(post_process_result(mock_elem, res_elem))
                        # If both items are list, use this function to process them.
                        elif isinstance(mock_elem, list) and isinstance(res_elem, list):
                            new_list.append(process_list(mock_elem, res_elem))
                        # Otherwise just add it to the new list, but only if both items have
                        # the same type. Otherwise do nothing, since it's and invalid scenario.
                        elif isinstance(mock_elem, type(res_elem)):
                            new_list.append(res_elem)

                    return new_list

                new_result[res_key] = process_list(mock_value, res_value)
            # This should be a simple value, so let's use it as is.
            else:
                new_result[res_key] = res_value

    return new_result


class TestResourceKeyPostModule(ModuleTestCase):
    """
    Test class for ResourceKeyPost module testing.
    """

    def test_read_ibm_resource_key_failed(self):
        """Test the inner "read" path in this module with a server error response."""

        patcher = patch('ansible.modules.cloud.ibm.ibm_resource_key.ResourceControllerV2.get_resource_key')
        mock = patcher.start()
        mock.side_effect = ApiException(500, message='Something went wrong...')

        set_module_args({
            'id': 'testString',
        })

        with self.assertRaises(AnsibleFailJson) as result:
            os.environ['RESOURCE_CONTROLLER_AUTH_TYPE'] = 'noAuth'
            ibm_resource_key.main()

        assert result.exception.args[0]['msg'] == 'Something went wrong...'

        mock_data = dict(
            id='testString',
        )

        mock.assert_called_once()
        processed_result = post_process_result(mock_data, mock.call_args.kwargs)
        assert mock_data == processed_result

        patcher.stop()

    def test_create_ibm_resource_key_success(self):
        """Test the "create" path - successful."""
        resource_key_post_parameters_model = {
            'serviceid_crn': 'crn:v1:bluemix:public:iam-identity::a/9fceaa56d1ab84893af6b9eec5ab81bb::serviceid:ServiceId-fe4c29b5-db13-410a-bacc-b5779a03d393',
            'foo': 'testString',
        }

        resource = {
            'name': 'my-key',
            'source': '25eba2a9-beef-450b-82cf-f5ad5e36c6dd',
            'parameters': resource_key_post_parameters_model,
            'role': 'Writer',
        }

        patcher = patch('ansible.modules.cloud.ibm.ibm_resource_key.ResourceControllerV2.create_resource_key')
        mock = patcher.start()
        mock.return_value = DetailedResponseMock(resource)

        get_resource_key_patcher = patch('ansible.modules.cloud.ibm.ibm_resource_key.ResourceControllerV2.get_resource_key')
        get_resource_key_mock = get_resource_key_patcher.start()

        set_module_args({
            'name': 'my-key',
            'source': '25eba2a9-beef-450b-82cf-f5ad5e36c6dd',
            'parameters': resource_key_post_parameters_model,
            'role': 'Writer',
        })

        with self.assertRaises(AnsibleExitJson) as result:
            os.environ['RESOURCE_CONTROLLER_AUTH_TYPE'] = 'noAuth'
            ibm_resource_key.main()

        assert result.exception.args[0]['changed'] is True
        assert result.exception.args[0]['msg'] == resource

        mock_data = dict(
            name='my-key',
            source='25eba2a9-beef-450b-82cf-f5ad5e36c6dd',
            parameters=resource_key_post_parameters_model,
            role='Writer',
        )

        mock.assert_called_once()
        processed_result = post_process_result(mock_data, mock.call_args.kwargs)
        assert mock_data == processed_result

        get_resource_key_mock.assert_not_called()

        get_resource_key_patcher.stop()
        patcher.stop()

    def test_create_ibm_resource_key_failed(self):
        """Test the "create" path - failed."""

        get_resource_key_patcher = patch('ansible.modules.cloud.ibm.ibm_resource_key.ResourceControllerV2.get_resource_key')
        get_resource_key_mock = get_resource_key_patcher.start()

        patcher = patch('ansible.modules.cloud.ibm.ibm_resource_key.ResourceControllerV2.create_resource_key')
        mock = patcher.start()
        mock.side_effect = ApiException(400, message='Create ibm_resource_key error')

        resource_key_post_parameters_model = {
            'serviceid_crn': 'crn:v1:bluemix:public:iam-identity::a/9fceaa56d1ab84893af6b9eec5ab81bb::serviceid:ServiceId-fe4c29b5-db13-410a-bacc-b5779a03d393',
            'foo': 'testString',
        }

        set_module_args({
            'name': 'my-key',
            'source': '25eba2a9-beef-450b-82cf-f5ad5e36c6dd',
            'parameters': resource_key_post_parameters_model,
            'role': 'Writer',
        })

        with self.assertRaises(AnsibleFailJson) as result:
            os.environ['RESOURCE_CONTROLLER_AUTH_TYPE'] = 'noAuth'
            ibm_resource_key.main()

        assert result.exception.args[0]['msg'] == 'Create ibm_resource_key error'

        mock_data = dict(
            name='my-key',
            source='25eba2a9-beef-450b-82cf-f5ad5e36c6dd',
            parameters=resource_key_post_parameters_model,
            role='Writer',
        )

        mock.assert_called_once()
        processed_result = post_process_result(mock_data, mock.call_args.kwargs)
        assert mock_data == processed_result

        get_resource_key_mock.assert_not_called()

        get_resource_key_patcher.stop()
        patcher.stop()

    def test_update_ibm_resource_key_success(self):
        """Test the "update" path - successful."""
        resource = {
            'id': 'testString',
            'name': 'my-new-key-name',
        }

        patcher = patch('ansible.modules.cloud.ibm.ibm_resource_key.ResourceControllerV2.update_resource_key')
        mock = patcher.start()
        mock.return_value = DetailedResponseMock(resource)

        get_resource_key_patcher = patch('ansible.modules.cloud.ibm.ibm_resource_key.ResourceControllerV2.get_resource_key')
        get_resource_key_mock = get_resource_key_patcher.start()
        get_resource_key_mock.return_value = DetailedResponseMock(resource)

        set_module_args({
            'id': 'testString',
            'name': 'my-new-key-name',
        })

        with self.assertRaises(AnsibleExitJson) as result:
            os.environ['RESOURCE_CONTROLLER_AUTH_TYPE'] = 'noAuth'
            ibm_resource_key.main()

        assert result.exception.args[0]['changed'] is True
        assert result.exception.args[0]['msg'] == resource

        mock_data = dict(
            id='testString',
            name='my-new-key-name',
        )

        mock.assert_called_once()
        processed_result = post_process_result(mock_data, mock.call_args.kwargs)
        assert mock_data == processed_result

        get_resource_key_mock_data = dict(
            id='testString',
        )
        # Set the variables that belong to the "read" path to `None`
        # since we test the "delete" path here.
        for param in get_resource_key_mock_data:
            get_resource_key_mock_data[param] = mock_data.get(param, None)

        get_resource_key_mock.assert_called_once()
        get_resource_key_processed_result = post_process_result(get_resource_key_mock_data, get_resource_key_mock.call_args.kwargs)
        assert get_resource_key_mock_data == get_resource_key_processed_result
        get_resource_key_patcher.stop()
        patcher.stop()

    def test_update_ibm_resource_key_failed(self):
        """Test the "update" path - failed."""
        resource = {
            'id': 'testString',
            'name': 'my-new-key-name',
        }

        patcher = patch('ansible.modules.cloud.ibm.ibm_resource_key.ResourceControllerV2.update_resource_key')
        mock = patcher.start()
        mock.side_effect = ApiException(400, message='Update ibm_resource_key error')

        get_resource_key_patcher = patch('ansible.modules.cloud.ibm.ibm_resource_key.ResourceControllerV2.get_resource_key')
        get_resource_key_mock = get_resource_key_patcher.start()
        get_resource_key_mock.return_value = DetailedResponseMock(resource)

        set_module_args({
            'id': 'testString',
            'name': 'my-new-key-name',
        })

        with self.assertRaises(AnsibleFailJson) as result:
            os.environ['RESOURCE_CONTROLLER_AUTH_TYPE'] = 'noAuth'
            ibm_resource_key.main()

        assert result.exception.args[0]['msg'] == 'Update ibm_resource_key error'

        mock_data = dict(
            id='testString',
            name='my-new-key-name',
        )

        mock.assert_called_once()
        processed_result = post_process_result(mock_data, mock.call_args.kwargs)
        assert mock_data == processed_result

        get_resource_key_mock_data = dict(
            id='testString',
        )
        # Set the variables that belong to the "read" path to `None`
        # since we test the "delete" path here.
        for param in get_resource_key_mock_data:
            get_resource_key_mock_data[param] = mock_data.get(param, None)

        get_resource_key_mock.assert_called_once()
        get_resource_key_processed_result = post_process_result(get_resource_key_mock_data, get_resource_key_mock.call_args.kwargs)
        assert get_resource_key_mock_data == get_resource_key_processed_result

        get_resource_key_patcher.stop()
        patcher.stop()

    def test_delete_ibm_resource_key_success(self):
        """Test the "delete" path - successfull."""
        patcher = patch('ansible.modules.cloud.ibm.ibm_resource_key.ResourceControllerV2.delete_resource_key')
        mock = patcher.start()
        mock.return_value = DetailedResponseMock()

        get_resource_key_patcher = patch('ansible.modules.cloud.ibm.ibm_resource_key.ResourceControllerV2.get_resource_key')
        get_resource_key_mock = get_resource_key_patcher.start()
        get_resource_key_mock.return_value = DetailedResponseMock()

        args = {
            'id': 'testString',
            'state': 'absent',
        }

        set_module_args(args)

        with self.assertRaises(AnsibleExitJson) as result:
            os.environ['RESOURCE_CONTROLLER_AUTH_TYPE'] = 'noAuth'
            ibm_resource_key.main()

        assert result.exception.args[0]['changed'] is True
        assert result.exception.args[0]['msg']['id'] == 'testString'
        assert result.exception.args[0]['msg']['status'] == 'deleted'

        mock_data = dict(
            id='testString',
        )

        mock.assert_called_once()
        processed_result = post_process_result(mock_data, mock.call_args.kwargs)
        assert mock_data == processed_result

        get_resource_key_mock_data = dict(
            id='testString',
        )
        # Set the variables that belong to the "read" path to `None`
        # since we test the "delete" path here.
        for param in get_resource_key_mock_data:
            get_resource_key_mock_data[param] = mock_data.get(param, None)

        get_resource_key_mock.assert_called_once()
        get_resource_key_processed_result = post_process_result(get_resource_key_mock_data, get_resource_key_mock.call_args.kwargs)
        assert get_resource_key_mock_data == get_resource_key_processed_result

        get_resource_key_patcher.stop()
        patcher.stop()

    def test_delete_ibm_resource_key_not_exists(self):
        """Test the "delete" path - not exists."""
        patcher = patch('ansible.modules.cloud.ibm.ibm_resource_key.ResourceControllerV2.delete_resource_key')
        mock = patcher.start()
        mock.return_value = DetailedResponseMock()

        get_resource_key_patcher = patch('ansible.modules.cloud.ibm.ibm_resource_key.ResourceControllerV2.get_resource_key')
        get_resource_key_mock = get_resource_key_patcher.start()
        get_resource_key_mock.side_effect = ApiException(404)

        args = {
            'id': 'testString',
            'state': 'absent',
        }

        set_module_args(args)

        with self.assertRaises(AnsibleExitJson) as result:
            os.environ['RESOURCE_CONTROLLER_AUTH_TYPE'] = 'noAuth'
            ibm_resource_key.main()

        assert result.exception.args[0]['changed'] is False
        assert result.exception.args[0]['msg']['id'] == 'testString'
        assert result.exception.args[0]['msg']['status'] == 'not_found'

        mock_data = dict(
            id='testString',
        )

        mock.assert_not_called()

        get_resource_key_mock_data = dict(
            id='testString',
        )
        # Set the variables that belong to the "read" path to `None`
        # since we test the "delete" path here.
        for param in get_resource_key_mock_data:
            get_resource_key_mock_data[param] = mock_data.get(param, None)

        get_resource_key_mock.assert_called_once()
        get_resource_key_processed_result = post_process_result(get_resource_key_mock_data, get_resource_key_mock.call_args.kwargs)
        assert get_resource_key_mock_data == get_resource_key_processed_result

        get_resource_key_patcher.stop()
        patcher.stop()

    def test_delete_ibm_resource_key_failed(self):
        """Test the "delete" path - failed."""
        patcher = patch('ansible.modules.cloud.ibm.ibm_resource_key.ResourceControllerV2.delete_resource_key')
        mock = patcher.start()
        mock.side_effect = ApiException(400, message='Delete ibm_resource_key error')

        get_resource_key_patcher = patch('ansible.modules.cloud.ibm.ibm_resource_key.ResourceControllerV2.get_resource_key')
        get_resource_key_mock = get_resource_key_patcher.start()
        get_resource_key_mock.return_value = DetailedResponseMock()

        set_module_args({
            'id': 'testString',
            'state': 'absent',
        })

        with self.assertRaises(AnsibleFailJson) as result:
            os.environ['RESOURCE_CONTROLLER_AUTH_TYPE'] = 'noAuth'
            ibm_resource_key.main()

        assert result.exception.args[0]['msg'] == 'Delete ibm_resource_key error'

        mock_data = dict(
            id='testString',
        )

        mock.assert_called_once()
        processed_result = post_process_result(mock_data, mock.call_args.kwargs)
        assert mock_data == processed_result

        get_resource_key_mock_data = dict(
            id='testString',
        )
        # Set the variables that belong to the "read" path to `None`
        # since we test the "delete" path here.
        for param in get_resource_key_mock_data:
            get_resource_key_mock_data[param] = mock_data.get(param, None)

        get_resource_key_mock.assert_called_once()
        get_resource_key_processed_result = post_process_result(get_resource_key_mock_data, get_resource_key_mock.call_args.kwargs)
        assert get_resource_key_mock_data == get_resource_key_processed_result

        get_resource_key_patcher.stop()
        patcher.stop()
