FROM python:3.12
LABEL org.opencontainers.image.source="https://github.com/pkorpine/ylerobo"
RUN apt update && apt install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install poetry && poetry config virtualenvs.create false

ENV YLEROBO_DB="/app/ylerobo.db"
ENV YLEDL_PARAMS="--destdir /app/storage"

COPY . /app/
RUN cd app && poetry install --no-dev

EXPOSE 8000
ENTRYPOINT ["/app/ylerobo.sh"]
CMD ["serve"]
