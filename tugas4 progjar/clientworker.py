import socket
import base64
import os
import time
import json

SERVER_ADDRESS = ('127.0.0.1', 6666)

def send_command(command_str):
    """Kirim perintah ke server dan terima respons JSON."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(SERVER_ADDRESS)
            sock.sendall((command_str + "\r\n\r\n").encode())

            data_received = ""
            while True:
                data = sock.recv(1024)
                if not data:
                    break
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break

            return json.loads(data_received.strip())
    except Exception as e:
        return {"status": "ERROR", "data": str(e)}

def upload_file(filename):
    """Upload file ke server"""
    try:
        with open(filename, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        command = f"UPLOAD {os.path.basename(filename)} {encoded}"
        return send_command(command)
    except Exception as e:
        return {"status": "ERROR", "data": str(e)}

def download_file(filename):
    """Download file dari server"""
    try:
        command = f"GET {filename}"
        result = send_command(command)
        if result["status"] == "OK":
            with open(f"downloads/{filename}", "wb") as f:
                f.write(base64.b64decode(result["data_file"]))
        return result
    except Exception as e:
        return {"status": "ERROR", "data": str(e)}

def list_files():
    """Ambil daftar file dari server"""
    return send_command("LIST")

def perform_task(operation, volume_mb):
    """Lakukan operasi sesuai instruksi dan ukur waktu + throughput"""
    filename = f"test_{volume_mb}MB.dat"

    if operation == "upload":
        if not os.path.exists(filename):
            with open(filename, "wb") as f:
                f.write(os.urandom(volume_mb * 1024 * 1024))

        start_time = time.time()
        result = upload_file(filename)
        end_time = time.time()
        size = os.path.getsize(filename)

    elif operation == "download":
        start_time = time.time()
        result = download_file(filename)
        end_time = time.time()
        size = volume_mb * 1024 * 1024  # ukuran file yang di-download

    elif operation == "list":
        start_time = time.time()
        result = list_files()
        end_time = time.time()
        size = 0

    else:
        return {"status": "ERROR", "data": "Unknown operation"}

    total_time = end_time - start_time
    throughput = size / total_time if total_time > 0 else 0

    return {
        "status": result["status"],
        "total_time": total_time,
        "throughput": throughput,
        "message": result.get("data", "")
    }

# Untuk pengujian mandiri
if __name__ == "__main__":
    res = perform_task("upload", 10)
    print(res)
