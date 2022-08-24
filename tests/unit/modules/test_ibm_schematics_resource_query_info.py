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

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os

from .common import DetailedResponseMock
from plugins.modules import ibm_schematics_resource_query_info
from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import patch
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils  import ModuleTestCase, AnsibleFailJson, AnsibleExitJson, set_module_args
try:
    from ibm_cloud_sdk_core import ApiException
except ImportError:
    pass


class TestResourceQueryRecordModuleInfo(ModuleTestCase):
    """
    Test class for ResourceQueryRecord module testing.
    """

    def test_read_ibm_schematics_resource_query_success(self):
        """Test the "read" path - successful."""
        datasource = {
            'query_id': 'testString',
        }

        patcher = patch('plugins.modules.ibm_schematics_resource_query_info.SchematicsV1.get_resources_query')
        mock = patcher.start()
        mock.return_value = DetailedResponseMock(datasource)

        set_module_args({
            'query_id': 'testString',
        })

        with self.assertRaises(AnsibleExitJson) as result:
            os.environ['SCHEMATICS_AUTH_TYPE'] = 'noAuth'
            os.environ['IC_API_KEY'] = 'noAuthAPIKey'
            ibm_schematics_resource_query_info.main()

        assert result.exception.args[0]['msg'] == datasource

        mock.assert_called_once_with(
            query_id='testString',
        )

        patcher.stop()

    def test_read_ibm_schematics_resource_query_failed(self):
        """Test the "read" path - failed."""
        patcher = patch('plugins.modules.ibm_schematics_resource_query_info.SchematicsV1.get_resources_query')
        mock = patcher.start()
        mock.side_effect = ApiException(400, message='Read ibm_schematics_resource_query error')

        set_module_args({
            'query_id': 'testString',
        })

        with self.assertRaises(AnsibleFailJson) as result:
            os.environ['SCHEMATICS_AUTH_TYPE'] = 'noAuth'
            os.environ['IC_API_KEY'] = 'noAuthAPIKey'
            ibm_schematics_resource_query_info.main()

        assert result.exception.args[0]['msg'] == 'Read ibm_schematics_resource_query error'

        mock.assert_called_once_with(
            query_id='testString',
        )

        patcher.stop()