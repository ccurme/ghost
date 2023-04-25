import os

from flask import Flask, request
from twilio.rest import Client

from utils import initialize_agent, load_settings

app = Flask(__name__)
AGENT_CACHE = {}
VERBOSE_PROMPT = os.environ.get("VERBOSE_PROMPT", "False").lower() in ("true", "1")


def _make_twilio_client():
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    return Client(account_sid, auth_token)


@app.route("/sms", methods=["POST"])
def sms():
    twilio_client = _make_twilio_client()
    incoming_message = request.values["Body"]
    chat_partner_phone_number = request.values["From"]
    ai_settings, contacts = load_settings()
    number_to_contact = {contact.pop("phone_number"): contact for contact in contacts}
    if chat_partner_phone_number not in number_to_contact:
        return "Unknown number."
    else:
        if chat_partner_phone_number in AGENT_CACHE:
            agent_executor = AGENT_CACHE[chat_partner_phone_number]
        else:
            agent_executor = initialize_agent(
                ai_settings, number_to_contact[chat_partner_phone_number]
            )
            agent_executor.agent.llm_chain.verbose = VERBOSE_PROMPT
            AGENT_CACHE[chat_partner_phone_number] = agent_executor
        response = agent_executor.run(incoming_message)

        message = twilio_client.messages.create(
            body=response,
            from_=ai_settings["ai_phone_number"],
            to=chat_partner_phone_number,
        )

        return message.sid
