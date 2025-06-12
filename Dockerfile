FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt ./
RUN pip install --user --no-warn-script-location --no-cache-dir -r requirements.txt

FROM python:3.11-slim
LABEL name="ExtAnalysis"
LABEL creator="Tuhinshubhra"
LABEL desc="Browser Extension Analysis Framework"
WORKDIR /app
COPY --from=builder /root/.local/lib /root/.local/lib
ENV PYTHONPATH=/root/.local/lib/python3.11/site-packages:$PYTHONPATH
COPY . .

EXPOSE 13337
ENTRYPOINT ["python3", "extanalysis.py"]
