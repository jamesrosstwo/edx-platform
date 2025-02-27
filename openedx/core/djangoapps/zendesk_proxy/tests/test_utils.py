"""
Tests of Zendesk interaction utility functions
"""

from __future__ import absolute_import

import json
from collections import OrderedDict

from django.test.utils import override_settings

import ddt
from mock import MagicMock, patch
from openedx.core.djangoapps.zendesk_proxy.utils import create_zendesk_ticket, get_zendesk_group_by_name
from openedx.core.lib.api.test_utils import ApiTestCase


@ddt.ddt
@override_settings(
    ZENDESK_URL="https://www.superrealurlsthataredefinitelynotfake.com",
    ZENDESK_OAUTH_ACCESS_TOKEN="abcdefghijklmnopqrstuvwxyz1234567890"
)
class TestUtils(ApiTestCase):
    def setUp(self):
        self.request_data = {
            'email': 'JohnQStudent@example.com',
            'name': 'John Q. Student',
            'subject': 'Python Unit Test Help Request',
            'body': "Help! I'm trapped in a unit test factory and I can't get out!",
        }
        return super(TestUtils, self).setUp()

    @override_settings(
        ZENDESK_URL=None,
        ZENDESK_OAUTH_ACCESS_TOKEN=None
    )
    def test_missing_settings(self):
        status_code = create_zendesk_ticket(
            requester_name=self.request_data['name'],
            requester_email=self.request_data['email'],
            subject=self.request_data['subject'],
            body=self.request_data['body'],
        )

        self.assertEqual(status_code, 503)

    @ddt.data(201, 400, 401, 403, 404, 500)
    def test_zendesk_status_codes(self, mock_code):
        with patch('requests.post', return_value=MagicMock(status_code=mock_code)):
            status_code = create_zendesk_ticket(
                requester_name=self.request_data['name'],
                requester_email=self.request_data['email'],
                subject=self.request_data['subject'],
                body=self.request_data['body'],
            )

            self.assertEqual(status_code, mock_code)

    def test_unexpected_error_pinging_zendesk(self):
        with patch('requests.post', side_effect=Exception("WHAMMY")):
            status_code = create_zendesk_ticket(
                requester_name=self.request_data['name'],
                requester_email=self.request_data['email'],
                subject=self.request_data['subject'],
                body=self.request_data['body'],
            )
            self.assertEqual(status_code, 500)

    def test_financial_assistant_ticket(self):
        """ Test Financial Assistent request ticket. """
        ticket_creation_response_data = {
            "ticket": {
                "id": 35436,
                "subject": "My printer is on fire!",
            }
        }
        response_text = json.dumps(ticket_creation_response_data)
        with patch('requests.post', return_value=MagicMock(status_code=200, text=response_text)):
            with patch('requests.put', return_value=MagicMock(status_code=200)):
                with patch('openedx.core.djangoapps.zendesk_proxy.utils.get_zendesk_group_by_name', return_value=2):
                    status_code = create_zendesk_ticket(
                        requester_name=self.request_data['name'],
                        requester_email=self.request_data['email'],
                        subject=self.request_data['subject'],
                        body=self.request_data['body'],
                        group='Financial Assistant',
                        additional_info=OrderedDict(
                            (
                                ('Username', 'test'),
                                ('Full Name', 'Legal Name'),
                                ('Course ID', 'course_key'),
                                ('Annual Household Income', 'Income'),
                                ('Country', 'Country'),
                            )
                        ),
                    )
                    self.assertEqual(status_code, 200)

    def test_get_zendesk_group_by_name(self):
        """ Tests the functionality of the get zendesk group. """
        response_data = {
            "groups": [
                {
                    "name": "DJs",
                    "created_at": "2009-05-13T00:07:08Z",
                    "updated_at": "2011-07-22T00:11:12Z",
                    "id": 211
                }
            ]
        }

        response_text = json.dumps(response_data)
        with patch('requests.get', return_value=MagicMock(status_code=200, text=response_text)):
            group_id = get_zendesk_group_by_name('DJs')
        self.assertEqual(group_id, 211)
