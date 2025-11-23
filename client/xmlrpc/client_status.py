#!/usr/bin/env python3
"""
Cliente para verificar status do servidor XML-RPC
Uso: python client_status.py
"""

import xmlrpc.client

def main():
    try:
        # Conectar ao servidor XML-RPC
        server = xmlrpc.client.ServerProxy('http://localhost:8000')
        
        # Ping
        ping_result = server.ping()
        print(f"Ping: {ping_result}")
        
        # Status
        status_result = server.get_server_status()
        print(f"Status: {status_result['status']}")
        print(f"Database: {status_result['database']}")
        
        print("\n✓ Servidor XML-RPC operacional")
        
    except Exception as e:
        print(f"✗ Erro ao conectar ao servidor: {e}")
        print("\nVerifique se o servidor está a correr:")
        print("  docker-compose up -d")

if __name__ == '__main__':
    main()
