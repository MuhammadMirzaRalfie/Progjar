from socket import *
import socket
from concurrent.futures import ProcessPoolExecutor
from http import HttpServer

httpserver = HttpServer()

def ProcessTheClient(connection, address):
    try:
        data = b""
        # Terima data hingga header selesai (\r\n\r\n)
        while True:
            chunk = connection.recv(4096)
            if not chunk:
                break
            data += chunk
            if b"\r\n\r\n" in data:
                break  # header selesai

        # Decode header
        try:
            header_data = data.decode(errors='ignore')
        except:
            connection.close()
            return

        header_end = header_data.find('\r\n\r\n')
        headers = header_data[:header_end].split("\r\n")
        body = data[header_end + 4:]

        # Cari Content-Length jika ada
        content_length = 0
        for h in headers:
            if h.lower().startswith('content-length'):
                try:
                    content_length = int(h.split(":")[1].strip())
                except:
                    content_length = 0

        # Terima body sampai sesuai Content-Length
        while len(body) < content_length:
            body += connection.recv(4096)

        # Gabungkan full request
        full_request = header_data[:header_end + 4] + body.decode(errors='ignore', errors='ignore')

        # Proses ke httpserver
        response = httpserver.proses(full_request)

        # Kirim response
        connection.sendall(response + b"\r\n\r\n")

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        connection.close()

def Server():
    the_clients = []
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.bind(('0.0.0.0', 8889))  # Ganti port jika diperlukan
    my_socket.listen(20)
    print("Server listening on port 8889 (ProcessPool)...")

    with ProcessPoolExecutor(10) as executor:  # 10 worker process
        while True:
            connection, client_address = my_socket.accept()
            print(f"Connection from {client_address}")
            p = executor.submit(ProcessTheClient, connection, client_address)
            the_clients.append(p)

def main():
    Server()

if __name__ == "__main__":
    main()
