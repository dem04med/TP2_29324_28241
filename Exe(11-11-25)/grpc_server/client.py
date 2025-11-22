import grpc
import data_service_pb2 as pb2
import data_service_pb2_grpc as pb2_grpc

def run():
    channel = grpc.insecure_channel("localhost:50051")
    stub = pb2_grpc.DataServiceStub(channel)

    print("=== Inserir XML na base de dados ===")
    insert_result = stub.InsertToDB(pb2.Empty())
    print("Success:", insert_result.success)
    print("Message:", insert_result.message)

    print("\n=== XML Completo ===")
    response = stub.GetXML(pb2.Empty())
    print(response.xml_data[:500] + "...\n")  # não imprimir tudo

    print("\n=== Resultado de XPath ===")
    xpath_expr = "/sales/sale[1]/*"
    res = stub.QueryXPath(pb2.XPathRequest(expression=xpath_expr))

    for r in res.results:
        print("->", r)


if __name__ == "__main__":
    run()
