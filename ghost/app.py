from copy import deepcopy
import json
import logging
import os
from typing import Optional

from flask import Flask, Request, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from langchain.schema import BaseModel
from twilio.request_validator import RequestValidator
from twilio.rest import Client

from agent_utils import initialize_agent
from fine_tuning.inference import initialize_chain
from unsolicited_message import generate_unsolicited_message
from utils import load_settings


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
jwt = JWTManager(app)
URL = os.environ.get("URL")

LOGLEVEL = 25  # Above info
logging.basicConfig(level=LOGLEVEL)
logger = logging.getLogger(__name__)

MODEL_CACHE = {}
VERBOSE_PROMPT = os.environ.get("VERBOSE_PROMPT", "False").lower() in ("true", "1")


def _make_twilio_client():
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    return Client(account_sid, auth_token)


def _validate_twilio_request(request: Request) -> bool:
    """Validate that post request is from Twilio."""
    validator = RequestValidator(os.environ.get("TWILIO_AUTH_TOKEN"))
    twilio_signature = request.headers.get("X-Twilio-Signature", "")
    return validator.validate(URL, request.values, twilio_signature)


def _validate_number_and_get_model(
    chat_partner_phone_number: str, ai_settings: dict, contacts: dict
) -> Optional[BaseModel]:
    """Validate phone number for chat partner and retrieve or initialize model."""
    if chat_partner_phone_number not in contacts:
        return None
    else:
        if chat_partner_phone_number in MODEL_CACHE:
            model = MODEL_CACHE[chat_partner_phone_number]
        else:
            if ai_settings["fine_tuned_model_name"]:
                model = initialize_chain(
                    ai_settings, contacts[chat_partner_phone_number]
                )
                model.verbose = VERBOSE_PROMPT
            else:
                model = initialize_agent(
                    ai_settings, contacts[chat_partner_phone_number]
                )
                model.agent.llm_chain.verbose = VERBOSE_PROMPT
            MODEL_CACHE[chat_partner_phone_number] = model

        return model


@app.route("/llm_reply", methods=["POST"])
def llm_reply():
    """Receive message and send response."""
    if not _validate_twilio_request(request):
        return "Invalid request."
    twilio_client = _make_twilio_client()
    incoming_message = request.values["Body"]
    chat_partner_phone_number = request.values["From"]
    logger.log(LOGLEVEL, f"Received {chat_partner_phone_number}: {incoming_message}")
    ai_settings, contacts = load_settings()
    contacts = {
        contact.pop("phone_number"): contact for contact in deepcopy(contacts)
    }  # key contacts by phone number
    model = _validate_number_and_get_model(
        chat_partner_phone_number, ai_settings, contacts
    )
    if model is None:
        logger.log(LOGLEVEL, f"Number not in contacts: {chat_partner_phone_number}")
        return "Unknown number."
    else:
        response = model.run(incoming_message)

        twliio_message = twilio_client.messages.create(
            body=response,
            from_=ai_settings["ai_phone_number"],
            to=chat_partner_phone_number,
        )
        logger.log(LOGLEVEL, f"Sent {chat_partner_phone_number}: {response}")

        return twliio_message.sid


@app.route("/llm_send", methods=["POST"])
@jwt_required()
def llm_send():
    """Send message."""
    twilio_client = _make_twilio_client()
    prompt = request.values["prompt"]
    chat_partner_phone_number = request.values["to"]

    ai_settings, contacts = load_settings()
    contacts = {contact.pop("phone_number"): contact for contact in contacts}
    model = _validate_number_and_get_model(
        chat_partner_phone_number, ai_settings, contacts
    )
    if model is None:
        return "Unknown number."
    else:
        contact_settings = contacts[chat_partner_phone_number]
        message = generate_unsolicited_message(
            prompt,
            model,
            ai_settings,
            contact_settings,
            temperature=0.7,
        )

        twliio_message = twilio_client.messages.create(
            body=message,
            from_=ai_settings["ai_phone_number"],
            to=chat_partner_phone_number,
        )
        logger.log(LOGLEVEL, f"Sent {chat_partner_phone_number}: {message}")

    return twliio_message.sid


@app.route("/llm_memory", methods=["POST"])
@jwt_required()
def llm_memory():
    """Return conversation histories."""
    buffers = {
        contact_number: model.memory.load_memory_variables({})["chat_history"]
        for contact_number, model in MODEL_CACHE.items()
    }

    return json.dumps(buffers, indent=2)


@app.route("/login", methods=["POST"])
def login():
    secret_key = request.values["secret_key"]
    if secret_key == app.config["SECRET_KEY"]:
        access_token = create_access_token(identity=123)
        return {"access_token": access_token}
    else:
        return {}
