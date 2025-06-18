import socket
import os

def send_request(request_bytes):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', 8885))  # Ubah jika IP/server berbeda
        s.sendall(request_bytes)
        response = b""
        while True:
            data = s.recv(4096)
            if not data:
                break
            response += data
        return response.decode(errors='ignore')

def list_files():
    request = "GET /list HTTP/1.0\r\n\r\n".encode()
    response = send_request(request)
    print("=== LIST FILES ===")
    print(response)

def upload_file(filename):
    if not os.path.exists(filename):
        print(f"File {filename} tidak ditemukan.")
        return

    with open(filename, 'rb') as f:
        content = f.read()

    headers = (
        f"POST /upload HTTP/1.0\r\n"
        f"Filename: {filename}\r\n"
        f"Content-Length: {len(content)}\r\n"
        f"\r\n"
    ).encode()

    request = headers + content
    response = send_request(request)
    print("=== UPLOAD ===")
    print(response)

def delete_file(filename):
    headers = (
        f"POST /delete HTTP/1.0\r\n"
        f"Filename: {filename}\r\n"
        f"Content-Length: 0\r\n"
        f"\r\n"
    ).encode()

    response = send_request(headers)
    print("=== DELETE ===")
    print(response)

if __name__ == '__main__':
    print("Pilih operasi:")
    print("1. List file di server")
    print("2. Upload file ke server")
    print("3. Hapus file dari server")
    pilihan = input("Masukkan pilihan (1/2/3): ")

    if pilihan == '1':
        list_files()
    elif pilihan == '2':
        filename = input("Masukkan nama file yang ingin diupload: ")
        upload_file(filename)
    elif pilihan == '3':
        filename = input("Masukkan nama file yang ingin dihapus: ")
        delete_file(filename)
    else:
        print("Pilihan tidak valid.")
