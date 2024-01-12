import json
from typing import List
from llama_cpp import Llama
from langchain.prompts import PromptTemplate
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from support_ticket import SupportTicket
from zendesk_service import ZendeskService


class SupportAgent:
    def __init__(self):
        # Initialize the SupportAgent with default parameters
        self.llm = Llama(
            model_path="/Users/michele/Documents/Arbeit/Projektarbeit/support-agent/llama.cpp/models/7B/ggml-model-q4_1.gguf",
            temperature=0.6,
            max_tokens=2000,
            n_ctx=2048,
            top_p=0.8,
            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
            verbose=True,
            repeat_penalty=0.8,
        )
        self.zendesk_service = ZendeskService()
        self.history = []
        self.template = """
           <s>[INST]<<SYS>>
            Du bist Supportio, ein qualifizierter Kunden-Support Mitarbeiter.
            Deine Aufgabe ist es,Support-Tickets zu klassifizieren.
            Du antwortest immer mit eienem Wort.
            Analysiere das Support-Ticket 
            Schritt für Schritt, um eine präzise Antwort zu geben.

            Antworte mit:

            RESEND_TICKET
            wenn das Support-Ticket die folgenden Worte oder ähnliche Sätze enthält:

            "Neu Senden"
            "Neue Tickets"
            "Ich finde meine Tickets nicht"
            "Wo finde ich meine Tickets"
            "Keine E-Mail erhalten"
            "Ich komme nicht mehr an die Bestätigungs-Mail mit den Tickets"
            "Email fach geleert"
            "Email wiederherstellen"

            DELETE_ACCOUNT
            wenn das Support-Ticket die folgenden Worte oder ähnliche Sätze enthält:

            "Account löschen"
            "Ich möchte meinen Account löschen"
            "Daten löschen"
            "Ich würde gerne meine Daten löschen"
            "Wie kann ich meine Daten löschen"
            "DSGVO"
            "Daten löschen lassen"
            "Daten entfernen"

            Hier sind einige Beispiele:

            Klassifiziere nun folgendes Support-Ticket in einem Wort
            Sehr geehrte Damen und Herren,
            Ich habe für folgende Events im Hans Bunte Areal Tickets gekauft,\n 
            ich komme nicht mehr an die Bestätigungs Mail mit den Tickets.\n 
            Die Mails wurden von meinem Postfach gelöscht da dieses voll war.\n 
            Gibt es Möglichkeiten diese wieder zu bekommen, bei der Buchung/kauf wurde\n 
            diese Mail verwendet zudem auch per PayPal mit dieser Mail bezahlt. RESEND_TICKET

            Klassifiziere nun folgendes Support-Ticket in einem Wort
            Hallo,\n 
            Ich würde gerne meine Daten die bei Ticket i/O löschen.\n 
            Wie kann ich meine Daten entfernen lassen? DELETE_ACCOUNT

            <</SYS>>

            Klassifiziere nun folgendes Support-Ticket in einem Wort [/INST] 
            {support_ticket} 
        """

    def solve_tickets(self):
        support_tickets = self.zendesk_service.get_tickets(count=50)
        classified_tickets = self.__classify_tickets(support_tickets)
        self.__generate_answers(classified_tickets)

    def __classify_tickets(
        self, support_tickets: List[SupportTicket]
    ) -> List[SupportTicket]:
        prompt = PromptTemplate.from_template(template=self.template)
        for support_ticket in support_tickets:
            support_ticket_template = prompt.format(
                support_ticket=support_ticket.description
            )
            output = self.llm(support_ticket_template, echo=False)
            ticket_classification = output["choices"][0]["text"].strip()
            support_ticket.classification = ticket_classification
        return support_tickets

    def __generate_answers(self, classified_tickets):
        for classified_ticket in classified_tickets:
            self.__solve_classifyed_tickt(classified_ticket)
        self.generate_export()

    def generate_history_entry(self, support_ticket, llama_output):
        interaction = {
            f"{support_ticket.ticket_id}": {
                "support_ticket": support_ticket.as_dict(),
                "llama_output": llama_output,
            }
        }
        self.history.append(interaction)
        return interaction

    def __solve_classifyed_tickt(self, support_ticket):
        classification_map = {
            "RESEND_TICKET": 8140353174289,
            "DELETE_ACCOUNT": 8147065642385,
        }
        classification = support_ticket.classification
        if classification in classification_map:
            macro_id = classification_map[classification]
            mail_template = self.zendesk_service.utilize_mail_template(
                macro_id=macro_id
            )
            mail_template_body = mail_template.text
            payload = self.__generate_response_body(macro_template=mail_template_body)
            self.zendesk_service.reply_to_customer(
                ticket_id=support_ticket.ticket_id, payload=payload
            )

    def __generate_response_body(self, macro_template):
        get_body = json.loads(macro_template)
        answer = {
            "ticket": {
                "comment": {
                    "html_body": get_body["result"]["ticket"]["comment"]["html_body"],
                    "public": False,
                }
            }
        }
        return answer

    def generate_export(self):
        with open("history.json", "w") as outfile:
            outfile.write(json.dumps(self.history))
