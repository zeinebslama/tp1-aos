FROM python:3.11-slim

WORKDIR /code
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY soap ./soap

EXPOSE 8000
CMD ["uvicorn", "soap.rest_api:app", "--host", "0.0.0.0", "--port", "8000"]