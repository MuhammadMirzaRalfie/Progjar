import socket
import threading
import logging
import json
import base64
import os
from glob import glob

class FileServer:
    def __init__(self, address=('0.0.0.0', 6666)):
        self.address = address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(self.address)
        self.sock.listen(5)
        self.running = True
        os.makedirs('files', exist_ok=True)

    def start(self):
        logging.warning(f"Server berjalan di {self.address}")
        try:
            while self.running:
                conn, client_addr = self.sock.accept()
                logging.warning(f"Client terhubung dari {client_addr}")
                thread = threading.Thread(target=self.handle_client, args=(conn,))
                thread.daemon = True  # agar thread otomatis tertutup saat main thread keluar
                thread.start()
        except KeyboardInterrupt:
            logging.warning("Server dimatikan oleh user (KeyboardInterrupt)")
        finally:
            self.sock.close()

    def handle_client(self, conn):
        try:
            data = b""
            while True:
                chunk = conn.recv(1024)
                if not chunk:
                    break
                data += chunk
                if b"\r\n\r\n" in data:
                    break

            message = data.decode().strip()
            logging.warning(f"Perintah dari client: {message}")
            response = self.process_command(message)
            response_str = json.dumps(response) + "\r\n\r\n"
            conn.sendall(response_str.encode())
        except Exception as e:
            logging.warning(f"Error saat handle client: {e}")
        finally:
            conn.close()

    def process_command(self, command_str):
        parts = command_str.strip().split(" ", 2)
        cmd = parts[0].upper()

        if cmd == "LIST":
            return self.list_files()
        elif cmd == "GET" and len(parts) >= 2:
            return self.get_file(parts[1])
        elif cmd == "UPLOAD" and len(parts) >= 3:
            return self.upload_file(parts[1], parts[2])
        elif cmd == "DELETE" and len(parts) >= 2:
            return self.delete_file(parts[1])
        else:
            return {"status": "ERROR", "data": "Perintah atau parameter tidak dikenali"}

    def list_files(self):
        try:
            files = os.listdir('files')
            return {"status": "OK", "data": files}
        except Exception as e:
            return {"status": "ERROR", "data": str(e)}

    def get_file(self, filename):
        try:
            path = os.path.join("files", filename)
            if not os.path.exists(path):
                return {"status": "ERROR", "data": "File tidak ditemukan"}
            with open(path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
            return {"status": "OK", "data_file": encoded}
        except Exception as e:
            return {"status": "ERROR", "data": str(e)}

    def upload_file(self, filename, encoded_data):
        try:
            data = base64.b64decode(encoded_data.encode())
            with open(os.path.join("files", filename), "wb") as f:
                f.write(data)
            return {"status": "OK", "data": "File berhasil di-upload"}
        except Exception as e:
            return {"status": "ERROR", "data": str(e)}

    def delete_file(self, filename):
        try:
            path = os.path.join("files", filename)
            if os.path.exists(path):
                os.remove(path)
                return {"status": "OK", "data": "File berhasil dihapus"}
            else:
                return {"status": "ERROR", "data": "File tidak ditemukan"}
        except Exception as e:
            return {"status": "ERROR", "data": str(e)}

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    server = FileServer()
    server.start()
