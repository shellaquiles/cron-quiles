#!/usr/bin/env python3
"""
Servidor HTTP simple para probar el sitio localmente.
Uso: python serve.py
"""

import http.server
import socketserver
import os
import sys

PORT = 8042

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Agregar headers CORS para desarrollo local
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def log_message(self, format, *args):
        # Log más limpio
        sys.stderr.write("%s - - [%s] %s\n" %
                        (self.address_string(),
                         self.log_date_time_string(),
                         format%args))

def free_port(port):
    import subprocess
    import time
    try:
        # Intentar liberar el puerto matando el proceso que lo usa (Linux/macOS)
        subprocess.run(f"fuser -k {port}/tcp", shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        subprocess.run(f"lsof -ti:{port} | xargs kill -9", shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        time.sleep(0.5) # Esperar a que el sistema operativo libere el socket
    except Exception:
        pass

def main():
    # Cambiar al directorio del script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Intentar liberar el puerto antes de iniciar
    free_port(PORT)

    Handler = MyHTTPRequestHandler
    
    # Habilitar la reutilización de direcciones para evitar el estado TIME_WAIT
    socketserver.TCPServer.allow_reuse_address = True

    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"🚀 Servidor iniciado en http://localhost:{PORT}")
            print(f"📁 Sirviendo archivos desde: {os.getcwd()}")
            print(f"\n🌐 Abre en tu navegador: http://localhost:{PORT}/index.html")
            print(f"\n⏹️  Presiona Ctrl+C para detener el servidor\n")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Servidor detenido")
        sys.exit(0)
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Error: El puerto {PORT} ya está en uso.")
            print(f"   Intenta con otro puerto o cierra el proceso que lo está usando.")
        else:
            print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
