FROM python:3.13-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Compilar protobuf para gRPC
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. xml_service.proto

EXPOSE 8000
CMD ["python", "xmlrpc_server.py"]
