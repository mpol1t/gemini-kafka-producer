FROM python:latest as builder

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc zlib1g-dev
RUN pip install --upgrade pip && pip install -r requirements.txt
RUN pip install pyinstaller
RUN pyinstaller --onefile main.py

FROM gcr.io/distroless/base-debian11

WORKDIR /app

COPY --from=builder /app/dist/main /app/main
COPY --from=builder /lib/x86_64-linux-gnu/libz.so.1 /lib/x86_64-linux-gnu/

USER nonroot:nonroot

ENTRYPOINT ["/app/main"]