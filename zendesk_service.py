import os
from typing import List
import requests
import json
from dotenv import find_dotenv, load_dotenv
from support_ticket import SupportTicket


class ZendeskService:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.base_url = "https://ticketio.zendesk.com/api/v2/"
        self.headers = {
            "Content-Type": "application/json",
        }
        self.auth = (f'{os.environ.get("USERNAME")}/token', os.environ.get("API_TOKEN"))

    def get_tickets(self, count: int):
        try:
            params = {
                "query": f"type:ticket group:1. Level Customer Support status:open count:{count}",
                "sort_by": "created_at",
                "sort_order": "asc",
            }
            response = requests.get(
                self.base_url + "tickets",
                params=params,
                auth=self.auth,
                headers=self.headers,
            )

            support_tickets = self.__generate_support_tickets(json.loads(response.text))
            return support_tickets
        except Exception as e:
            print(e)
            raise

    def reply_to_customer(self, ticket_id, payload):
        response = requests.put(
            self.base_url + f"tickets/{ticket_id}",
            auth=self.auth,
            headers=self.headers,
            json=payload,
        )
        return response

    def __generate_support_tickets(self, json_response) -> List[SupportTicket]:
        support_tickets = []

        if isinstance(json_response, dict) and "listName" in json_response:
            for ticket_data in json_response["tickets"]:
                support_ticket = self.__create_support_ticket_from_data(ticket_data)
                support_tickets.append(support_ticket)
        else:
            support_ticket_data = json_response["ticket"]
            support_ticket = self.__create_support_ticket_from_data(support_ticket_data)
            support_tickets.append(support_ticket)

        return support_tickets

    def __create_support_ticket_from_data(self, ticket_data) -> SupportTicket:
        customer_email = ""
        if ticket_data["via"]["channel"] == "email":
            customer_email = ticket_data["via"]["source"]["from"]["address"]

        return SupportTicket(
            ticket_id=ticket_data["id"],
            customer_email=customer_email,
            status=ticket_data["status"],
            subject=ticket_data["subject"],
            description=ticket_data["description"],
            classification=None,
        )

    def get_macros(self):
        response = requests.get(
            self.base_url + "macros/active",
            auth=self.auth,
            headers=self.headers,
        )
        with open("macros.json", "w") as outfile:
            outfile.write(response.text)

    def utilize_mail_template(self, macro_id):
        try:
            response = requests.get(
                self.base_url + f"macros/{macro_id}/apply",
                auth=self.auth,
                headers=self.headers,
            )
            return response
        except Exception as e:
            print(e)
            raise Exception
