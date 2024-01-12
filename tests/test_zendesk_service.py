import json
import unittest
from unittest.mock import Mock, patch
from supportagent.support_ticket import SupportTicket
from supportagent.zendesk_service import ZendeskService


class TestZendeskService(unittest.TestCase):
    @patch("requests.get")
    def test_get_tickets(self, mock_get):
        # Mock the response from the Zendesk API
        mock_response = Mock()
        mock_response.text = json.dumps(
            {
                "tickets": [
                    {
                        "ticket_id": 1,
                        "status": "open",
                        "subject": "Test subject 1",
                        "description": "Test description 1",
                        "via": {
                            "channel": "email",
                            "source": {"from": {"address": "test1@example.com"}},
                        },
                    },
                    {
                        "ticket_id": 2,
                        "status": "open",
                        "subject": "Test subject 2",
                        "description": "Test description 2",
                        "via": {
                            "channel": "email",
                            "source": {"from": {"address": "test2@example.com"}},
                        },
                    },
                ]
            }
        )
        mock_get.return_value = mock_response

        # Create an instance of ZendeskService and call the method
        zendesk_service = ZendeskService()
        tickets = zendesk_service.get_tickets()

        # Assert that the method returns a list of SupportTicket objects
        self.assertIsInstance(tickets, list)
        self.assertEqual(len(tickets), 2)
        self.assertIsInstance(tickets[0], SupportTicket)
        self.assertIsInstance(tickets[1], SupportTicket)

    @patch("requests.put")
    def test_reply_to_customer(self, mock_put):
        # Mock the response from the Zendesk API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_put.return_value = mock_response

        # Create an instance of ZendeskService and call the method
        zendesk_service = ZendeskService()
        ticket_id = 123
        payload = {"ticket": {"comment": {"html_body": "Test reply"}}}
        response = zendesk_service.reply_to_customer(ticket_id, payload)

        # Assert that the method returns a response with status code 200
        self.assertEqual(response.status_code, 200)

    @patch("requests.get")
    def test_utilize_mail_template(self, mock_get):
        # Mock the response from the Zendesk API
        mock_response = Mock()
        mock_response.text = json.dumps({"text": "Test mail template"})
        mock_get.return_value = mock_response

        # Create an instance of ZendeskService and call the method
        zendesk_service = ZendeskService()
        macro_id = 456
        response = zendesk_service.utilize_mail_template(macro_id)

        # Assert that the method returns a response with the expected text
        self.assertEqual(response.text, "Test mail template")


if __name__ == "__main__":
    unittest.main()
