import json
import unittest
from unittest.mock import Mock, patch
from supportagent.support_agent import SupportAgent
from supportagent.support_ticket import SupportTicket


class TestSupportAgent(unittest.TestCase):
    def setUp(self):
        # Create a SupportAgent instance for testing
        self.support_agent = SupportAgent()

    def test_classify_tickets(self):
        # Create a list of mock SupportTicket objects
        support_tickets = [
            SupportTicket(
                ticket_id=1,
                customer_email="test@example.com",
                status="open",
                subject="Test subject",
                description="Test description",
                classification=None,
            ),
            SupportTicket(
                ticket_id=2,
                customer_email="test2@example.com",
                status="open",
                subject="Test subject 2",
                description="Test description 2",
                classification=None,
            ),
        ]

        # Mock the Llama class's response
        llama_output = {"choices": [{"text": "RESEND_TICKET"}]}
        self.support_agent.llm = Mock(return_value=llama_output)

        # Call the classify_tickets method
        classified_tickets = self.support_agent._SupportAgent__classify_tickets(
            support_tickets
        )

        # Ensure that the classification is set correctly
        self.assertEqual(classified_tickets[0].classification, "RESEND_TICKET")
        self.assertEqual(classified_tickets[1].classification, "RESEND_TICKET")

    def test_generate_response_body(self):
        # Create a mock macro template with valid JSON format
        macro_template = '{"result": {"ticket": {"comment": {"html_body": "Test body", "public": false}}}}'

        # Call the __generate_response_body method with the mocked template
        with patch("support_agent.json.loads", return_value=json.loads(macro_template)):
            response_body = self.support_agent._SupportAgent__generate_response_body(
                macro_template
            )

        # Ensure that the response body is generated correctly
        expected_body = {
            "result": {
                "ticket": {"comment": {"html_body": "Test body", "public": False}}
            }
        }
        self.assertEqual(response_body, expected_body)

    def test_map_classification(self):
        # Create a mock SupportTicket with a classification
        support_ticket = SupportTicket(
            ticket_id=1,
            customer_email="test@example.com",
            status="open",
            subject="Test subject",
            description="Test description",
            classification="RESEND_TICKET",
        )

        # Mock the ZendeskService methods
        self.support_agent.zendesk_service.utilize_mail_template = Mock()
        self.support_agent.zendesk_service.reply_to_customer = Mock()

        # Mock the behavior of __generate_response_body to return a valid JSON string
        with patch(
            "support_agent.SupportAgent._SupportAgent__generate_response_body",
            return_value='{"result": {"ticket": {"comment": {"html_body": "Test body", "public": false}}}}',
        ):
            # Call the __map_classification method
            self.support_agent._SupportAgent__map_classification(support_ticket)

        # Ensure that the ZendeskService methods were called correctly
        self.support_agent.zendesk_service.utilize_mail_template.assert_called_with(
            macro_id=8140353174289
        )
        # Ensure that the payload is a JSON string in the expected call
        self.support_agent.zendesk_service.reply_to_customer.assert_called_with(
            ticket_id=support_ticket.ticket_id,
            payload='{"result": {"ticket": {"comment": {"html_body": "Test body", "public": false}}}}',
        )

    def test_generate_export(self):
        # Create a list of mock interaction data
        interactions = [
            {
                "1": {
                    "support_ticket": {
                        "ticket_id": 120052,
                        "customer_email": "test@example.com",
                        "status": "open",
                        "subject": "Test subject",
                        "description": "Test description",
                        "classification": "RESEND_TICKET",
                    },
                    "llama_output": {
                        "id": "cmpl-c4cdeb89-3fac-4a54-a3f2-2873a9aa4b7a",
                        "object": "text_completion",
                        "created": 1696518220,
                        "model": "/Users/michele/Documents/Arbeit/Projektarbeit/support-agent/llama.cpp/models/7B/ggml-model-q4_1.gguf",
                        "choices": [
                            {
                                "text": " ",
                                "index": 0,
                                "logprobs": "null",
                                "finish_reason": "length",
                            }
                        ],
                        "usage": {
                            "prompt_tokens": 684,
                            "completion_tokens": 128,
                            "total_tokens": 812,
                        },
                    },
                }
            },
            {
                "2": {
                    "support_ticket": {
                        "ticket_id": 120052,
                        "customer_email": "test@example.com",
                        "status": "open",
                        "subject": "Test subject2",
                        "classification": "RESEND_TICKET",
                    },
                    "llama_output": {
                        "id": "cmpl-c4cdeb89-3fac-4a54-a3f2-2873a9aa4b7a",
                        "object": "text_completion",
                        "created": 1696518220,
                        "model": "/Users/michele/Documents/Arbeit/Projektarbeit/support-agent/llama.cpp/models/7B/ggml-model-q4_1.gguf",
                        "choices": [
                            {
                                "text": "",
                                "index": 0,
                                "logprobs": "null",
                                "finish_reason": "length",
                            }
                        ],
                        "usage": {
                            "prompt_tokens": 684,
                            "completion_tokens": 128,
                            "total_tokens": 812,
                        },
                    },
                }
            },
        ]

        # Set the history attribute with mock data
        self.support_agent.history = interactions

        # Call the __generate_export method
        self.support_agent._SupportAgent__generate_export()

        # Ensure that the export file is created and written
        with open("/test/test_history.json", "r") as outfile:
            exported_data = json.load(outfile)

        self.assertEqual(exported_data, interactions)


if __name__ == "__main__":
    unittest.main()
