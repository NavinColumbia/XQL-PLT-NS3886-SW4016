

FROM python:3.9-slim


WORKDIR /app


COPY . /app


COPY ./tests /app/tests


RUN chmod +x run.sh


RUN useradd -m myuser
USER myuser

VOLUME [ "/app/lexer_output" ]
VOLUME [ "/app/parser_output" ]


ENTRYPOINT ["./run.sh"]

