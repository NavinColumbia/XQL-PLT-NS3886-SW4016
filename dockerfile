

FROM python:3.9-slim


WORKDIR /app


COPY . /app


COPY ./tests /app/tests


RUN useradd -m myuser && \
    chown -R myuser:myuser /app && \
    chmod +x run.sh && \
    chmod +w /app/lexer_output && \
    chmod +w /app/parser_output


USER myuser

VOLUME [ "/app/lexer_output" ]
VOLUME [ "/app/parser_output" ]


ENTRYPOINT ["./run.sh"]

