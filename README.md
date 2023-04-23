# Ghost
Create an AI replica of yourself that is accessible via SMS.

### Start server:
```
TWILIO_ACCOUNT_SID=... TWILIO_AUTH_TOKEN=... OPENAI_API_KEY=... flask run
```

## Testing
See [Makefile](Makefile) for testing, test coverage and linting.
### Unit tests:
```
make unit_tests
```
### Integration tests:
Ghost currently uses OpenAI LLMs and embeddings, so you will need to provide an API key:
```
OPENAI_API_KEY=... make integration_tests
```
