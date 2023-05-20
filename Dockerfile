FROM python:3.9

RUN pip install poetry

WORKDIR /ghost

COPY . /ghost

RUN poetry install

WORKDIR /ghost/ghost

ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 5000

CMD ["poetry", "run", "flask", "run"]
