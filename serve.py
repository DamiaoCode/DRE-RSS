#!/usr/bin/env python3
"""
Servidor local simples para testar a interface web dos procedimentos ativos
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

def main():
    # Configurar o diretório atual
    current_dir = Path(__file__).parent
    os.chdir(current_dir)
    
    # Configurar o servidor
    PORT = 8000
    
    # Criar o servidor
    Handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🌐 Servidor iniciado em http://localhost:{PORT}")
        print(f"📁 Servindo arquivos do diretório: {current_dir}")
        print(f"🔗 Abrindo navegador automaticamente...")
        print(f"⏹️  Pressione Ctrl+C para parar o servidor")
        
        # Abrir o navegador automaticamente
        webbrowser.open(f'http://localhost:{PORT}')
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n🛑 Servidor parado")
            httpd.shutdown()

if __name__ == "__main__":
    main() 