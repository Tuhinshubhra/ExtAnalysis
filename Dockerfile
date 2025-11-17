FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
LABEL name="ExtAnalysis"
LABEL creator="Tuhinshubhra"
LABEL desc="Browser Extension Analysis Framework"

# Create a non-root user for security
RUN groupadd -r extanalysis && useradd -r -g extanalysis extanalysis

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .

# Change ownership of the app directory to the non-root user
RUN chown -R extanalysis:extanalysis /app

# Switch to non-root user
USER extanalysis

EXPOSE 13337
ENTRYPOINT ["python3", "extanalysis.py"]
