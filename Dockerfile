FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
LABEL name="ExtAnalysis"
LABEL creator="Tuhinshubhra"
LABEL desc="Browser Extension Analysis Framework"
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .

EXPOSE 13337
ENTRYPOINT ["python3", "extanalysis.py"]
