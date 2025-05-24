import socket
import json
import base64
import os
import logging
from multiprocessing import Pool, Manager
import multiprocessing
import signal

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 6666
FILES_DIR = 'files_process'  # direktori penyimpanan file
MAX_WORKERS = 5  # jumlah process worker pool

if not os.path.exists(FILES_DIR):
    os.makedirs(FILES_DIR)

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

def process_command(command_str):
    try:
        parts = command_str.strip().split(' ', 2)
        cmd = parts[0].upper()
        if cmd == 'LIST':
            files = os.listdir(FILES_DIR)
            return json.dumps({'status': 'OK', 'data': files}) + "\r\n\r\n"

        elif cmd == 'GET':
            if len(parts) < 2:
                return json.dumps({'status': 'ERROR', 'data': 'Filename missing'}) + "\r\n\r\n"
            filename = parts[1]
            filepath = os.path.join(FILES_DIR, filename)
            if not os.path.exists(filepath):
                return json.dumps({'status': 'ERROR', 'data': 'File not found'}) + "\r\n\r\n"
            with open(filepath, 'rb') as f:
                encoded = base64.b64encode(f.read()).decode()
            return json.dumps({'status': 'OK', 'data_file': encoded}) + "\r\n\r\n"

        elif cmd == 'UPLOAD':
            if len(parts) < 3:
                return json.dumps({'status': 'ERROR', 'data': 'Invalid UPLOAD command'}) + "\r\n\r\n"
            filename = parts[1]
            encoded_data = parts[2]
            data = base64.b64decode(encoded_data)
            with open(os.path.join(FILES_DIR, filename), 'wb') as f:
                f.write(data)
            return json.dumps({'status': 'OK', 'data': f'File "{filename}" uploaded successfully'}) + "\r\n\r\n"

        elif cmd == 'DELETE':
            if len(parts) < 2:
                return json.dumps({'status': 'ERROR', 'data': 'Filename missing'}) + "\r\n\r\n"
            filename = parts[1]
            filepath = os.path.join(FILES_DIR, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                return json.dumps({'status': 'OK', 'data': f'File "{filename}" deleted'}) + "\r\n\r\n"
            else:
                return json.dumps({'status': 'ERROR', 'data': 'File not found'}) + "\r\n\r\n"

        else:
            return json.dumps({'status': 'ERROR', 'data': 'Unknown command'}) + "\r\n\r\n"
    except Exception as e:
        return json.dumps({'status': 'ERROR', 'data': str(e)}) + "\r\n\r\n"

def handle_client(conn_fd, addr):
    """Fungsi worker proses untuk handle satu client connection."""
    try:
        conn = socket.socket(fileno=conn_fd)
        logging.info(f"Client connected: {addr}")
        buffer = ''
        while True:
            data = conn.recv(1024)
            if not data:
                break
            buffer += data.decode()
            if '\r\n\r\n' in buffer:
                commands = buffer.split('\r\n\r\n')
                for command_str in commands[:-1]:
                    response = process_command(command_str)
                    conn.sendall(response.encode())
                buffer = commands[-1]
    except Exception as e:
        logging.error(f"Error handling client {addr}: {e}")
    finally:
        conn.close()
        logging.info(f"Client disconnected: {addr}")

def accept_connections(listener, pool):
    """Menerima koneksi dan delegasi ke pool process."""
    while True:
        try:
            conn, addr = listener.accept()
            # Kirim file descriptor socket ke worker process pool
            pool.apply_async(handle_client, args=(conn.fileno(), addr))
            # close socket di proses utama, tanggung jawab worker
            conn.close()
        except KeyboardInterrupt:
            logging.info("Server shutting down...")
            break
        except Exception as e:
            logging.error(f"Error accepting connection: {e}")

def main():
    multiprocessing.set_start_method('spawn')  # supaya multiprocessing stabil

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.bind((SERVER_HOST, SERVER_PORT))
        server_sock.listen()
        logging.info(f"Server running on {SERVER_HOST}:{SERVER_PORT}")

        with Pool(processes=MAX_WORKERS) as pool:
            accept_connections(server_sock, pool)

if __name__ == '__main__':
    main()
