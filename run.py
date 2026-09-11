import os
import sys
import socket
import uvicorn

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    local_ip = get_local_ip()
    print("[INFO] Iniciando o RoboCode Challenge...")
    print(f"[INFO] Acesso neste computador: http://127.0.0.1:8000")
    print(f"[INFO] Acesso de OUTROS computadores na mesma rede Wi-Fi/Laboratorio: http://{local_ip}:8000")
    print(f"[INFO] Documentacao da API (Swagger): http://127.0.0.1:8000/docs")
    print("=" * 70)

    # host="0.0.0.0" permite conexões de outros computadores da rede local
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
