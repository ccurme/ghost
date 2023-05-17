# Ghost
Create an AI replica of yourself that is accessible via SMS.

Ghost allows you to chat with (1) a LLM that is fine-tuned on your text messages, or (2) [Langchain agent](https://python.langchain.com/en/latest/use_cases/personal_assistants.html) with a custom prompt that implements retrieval-augmented generation over a set of personal facts. For fine-tuning, Ghost provides functionality to sample and review text conversations from your iPhone, granting oversight of the training data. See [fine tuning README](ghost/fine_tuning/README.md) for details.

## Configuration
Ghost requires two configuration files to tailor your chat responses:
1. Describe your background, writing style, or mannerisms by modifying [prompt_prefix.md](ghost/settings/prompt_prefix.md), or setting the `PROMPT_PREFIX_PATH=/path/to/prompt_prefix.md` environment variable.
1. Provide structured information such as your SMS-enabled Twilio phone number, chatbot name, and aliases in [contacts.json](ghost/settings/contacts.json). If using the Langchain agent, this configuration file also houses an array of facts that is indexed and retrieved over when generating responses. You can also point to this configuration file by setting the `CONTACTS_PATH=/path/to/contacts.json` environment variable.

The [contacts.json](ghost/settings/contacts.json) file specifies other important information such as allowed senders for incoming messages, and information about the senders that helps Ghost tailor its responses. See [settings/README.md](ghost/settings/README.md) for more detail.

## Usage
Ghost currently uses OpenAI LLMs and embeddings, so you will need to provide an [API key](https://platform.openai.com/account/api-keys). You will also need a [Twilio](https://www.twilio.com/console) account ID, auth token, and SMS-enabled phone number.

Start server:
```
TWILIO_ACCOUNT_SID=... TWILIO_AUTH_TOKEN=... OPENAI_API_KEY=... URL=... flask run
```

Ghost has three endpoints:
* `/llm_reply`: configuring a Twilio SMS webhook to this endpoint will produce replies for inbound messages from known contacts (those in [contacts.json](ghost/settings/contacts.json)).
* `/llm_send`: this endpoint will send an unsolicited message to a known contact following a given input prompt (requires authentication).
* `/login`: this endpoint can produce a token for use with `/llm_send`.

## Testing
See [Makefile](Makefile) for testing, test coverage and linting.
### Unit tests:
```
make unit_tests
```
### Integration tests:
```
OPENAI_API_KEY=... make integration_tests
```
