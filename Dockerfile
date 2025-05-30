FROM python:3.13.0-slim
RUN apt-get update && apt-get install -y git && apt-get clean
RUN pip install poetry


WORKDIR /app
# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# remove ssh key after dependency installation
# RUN rm /root/.ssh/id_rsa

COPY ./mcp_server_for_kagent/ mcp_server_for_kagent/
ENV PYTHONUNBUFFERED=1

EXPOSE 4337
CMD ["uvicorn", "mcp_server_for_kagent.main:app", "--host", "0.0.0.0", "--port", "4337", "--workers", "1", "--log-level", "debug"]
