import unittest
from supportagent.support_ticket import SupportTicket


class TestSupportTicket(unittest.TestCase):
    def test_support_ticket_as_dict(self):
        # Create a SupportTicket instance for testing
        ticket = SupportTicket(
            ticket_id=1,
            customer_email="test@example.com",
            status="open",
            subject="Test subject",
            description="Test description",
            classification="RESEND_TICKET",
        )

        # Call the as_dict method
        ticket_dict = ticket.as_dict()

        # Ensure that the dictionary representation is correct
        expected_dict = {
            "ticket_id": 1,
            "customer_email": "test@example.com",
            "status": "open",
            "subject": "Test subject",
            "description": "Test description",
            "classification": "RESEND_TICKET",
        }
        self.assertEqual(ticket_dict, expected_dict)
