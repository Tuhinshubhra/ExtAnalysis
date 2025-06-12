FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt ./
RUN pip install --user --no-warn-script-location --no-cache-dir -r requirements.txt

FROM python:3.11-slim
LABEL name="ExtAnalysis"
LABEL creator="Tuhinshubhra"
LABEL desc="Browser Extension Analysis Framework"
WORKDIR /app
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY . .

EXPOSE 13337
ENTRYPOINT ["python3", "extanalysis.py"]
