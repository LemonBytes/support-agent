class SupportTicket:
    def __init__(
        self, ticket_id, customer_email, status, subject, description, classification
    ):
        self.ticket_id = ticket_id
        self.customer_email = customer_email
        self.status = status
        self.subject = subject
        self.description = description
        self.classification = classification

    def as_dict(self):
        return {
            "ticket_id": self.ticket_id,
            "customer_email": self.customer_email,
            "status": self.status,
            "subject": self.subject,
            "description": self.description,
            "classification": self.classification,
        }
