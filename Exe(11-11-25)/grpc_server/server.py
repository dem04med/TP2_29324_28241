import grpc
from concurrent import futures
from lxml import etree
from pymongo import MongoClient
import os

import data_service_pb2 as pb2
import data_service_pb2_grpc as pb2_grpc

XML_FILE = "sales_data.xml"

MONGO_HOST = os.environ.get("MONGO_HOST", "localhost")
MONGO_USER = os.environ.get("MONGO_USER", "root")
MONGO_PASS = os.environ.get("MONGO_PASS", "secret")
MONGO_DB = os.environ.get("MONGO_DB", "salesdb")


class DataService(pb2_grpc.DataServiceServicer):

    # ---------- LIGAR AO MONGO ----------
    def connect_mongo(self):
        uri = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:27017/"
        client = MongoClient(uri)
        return client[MONGO_DB]

    # ---------- DEVOLVE O XML COMPLETO ----------
    def GetXML(self, request, context):
        with open(XML_FILE, "r", encoding="utf-8") as f:
            xml_data = f.read()
        return pb2.XMLResponse(xml_data=xml_data)

    # ---------- CONSULTA XPATH ----------
    def QueryXPath(self, request, context):
        expression = request.expression

        try:
            tree = etree.parse(XML_FILE)
            results = tree.xpath(expression)

            str_results = []
            for r in results:
                if isinstance(r, etree._Element):
                    str_results.append(etree.tostring(r, pretty_print=True).decode())
                else:
                    str_results.append(str(r))

            return pb2.XPathResponse(results=str_results)

        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return pb2.XPathResponse(results=[])

    # ---------- INSERIR XML → MONGODB ----------
    def InsertToDB(self, request, context):
        try:
            tree = etree.parse(XML_FILE)
            sales = tree.xpath("//sale")

            db = self.connect_mongo()
            collection = db["sales"]

            docs = []

            for s in sales:
                doc = {
                    "id": int(s.get("id")),
                    "date": s.findtext("date"),
                    "warehouse": s.findtext("warehouse"),
                    "client_type": s.findtext("client_type"),
                    "product_line": s.findtext("product_line"),
                    "quantity": int(s.findtext("quantity")),
                    "unit_price": float(s.findtext("unit_price")),
                    "total": float(s.findtext("total")),
                    "payment": s.findtext("payment")
                }
                docs.append(doc)

            # Inserção em massa (muito mais rápido)
            if docs:
                collection.insert_many(docs)

            return pb2.InsertResponse(
                success=True,
                message="Dados importados com sucesso para o MongoDB!"
            )

        except Exception as e:
            return pb2.InsertResponse(
                success=False,
                message=f"Erro ao inserir no MongoDB: {str(e)}"
            )



def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_DataServiceServicer_to_server(DataService(), server)
    server.add_insecure_port("[::]:50051")
    print(" Servidor gRPC + MongoDB a correr na porta 50051...")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
