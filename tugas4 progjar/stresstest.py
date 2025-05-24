import time
import base64
import os
import socket
import threading
from multiprocessing import Pool
import multiprocessing

SERVER_ADDRESS = ('127.0.0.1', 6666)
FILES_DIR = 'stresstest_files'
if not os.path.exists(FILES_DIR):
    os.makedirs(FILES_DIR)

# Fungsi untuk kirim perintah ke server dan menerima respons lengkap
def send_command(command_str):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(SERVER_ADDRESS)
        sock.sendall((command_str + "\r\n\r\n").encode())
        buffer = ""
        while True:
            data = sock.recv(1024)
            if not data:
                break
            buffer += data.decode()
            if "\r\n\r\n" in buffer:
                break
        return buffer.strip()

# Fungsi untuk generate file dummy dengan ukuran tertentu (MB)
def generate_dummy_file(filename, size_mb):
    path = os.path.join(FILES_DIR, filename)
    if not os.path.exists(path):
        with open(path, "wb") as f:
            f.write(os.urandom(size_mb * 1024 * 1024))
    return path

# Operasi upload file
def upload_file_worker(file_size_mb):
    filename = f"upload_test_{file_size_mb}MB.bin"
    filepath = generate_dummy_file(filename, file_size_mb)
    with open(filepath, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    cmd = f"UPLOAD {filename} {encoded}"
    resp = send_command(cmd)
    return resp

# Operasi download file
def download_file_worker(file_size_mb):
    filename = f"upload_test_{file_size_mb}MB.bin"
    cmd = f"GET {filename}"
    resp = send_command(cmd)
    # Kita bisa cek keberhasilan dan decode (optional)
    return resp

def list_files_worker():
    return send_command("LIST")

def worker_task(operation, volume_mb):
    start_time = time.time()
    success = 0
    fail = 0

    try:
        if operation == "upload":
            resp = upload_file_worker(volume_mb)
        elif operation == "download":
            resp = download_file_worker(volume_mb)
        elif operation == "list":
            resp = list_files_worker()
        else:
            resp = "Invalid operation"
            fail += 1

        if '"status": "OK"' in resp:
            success += 1
        else:
            fail += 1
    except Exception:
        fail += 1

    elapsed = time.time() - start_time
    # Throughput = bytes processed / elapsed time, diasumsikan file size jika upload/download
    throughput = (volume_mb * 1024 * 1024) / elapsed if elapsed > 0 else 0

    return {
        'success': success,
        'fail': fail,
        'elapsed': elapsed,
        'throughput': throughput
    }

def run_stresstest(operation, volume_mb, client_workers, use_multiprocessing=False):
    print(f"Running stress test: operation={operation}, volume={volume_mb}MB, workers={client_workers}, multiprocessing={use_multiprocessing}")
    results = []

    if use_multiprocessing:
        with Pool(processes=client_workers) as pool:
            results = pool.starmap(worker_task, [(operation, volume_mb)] * client_workers)
    else:
        threads = []
        results = []

        def thread_func():
            res = worker_task(operation, volume_mb)
            results.append(res)

        for _ in range(client_workers):
            t = threading.Thread(target=thread_func)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

    # Rekap hasil
    total_success = sum(r['success'] for r in results)
    total_fail = sum(r['fail'] for r in results)
    total_elapsed = sum(r['elapsed'] for r in results)
    total_throughput = sum(r['throughput'] for r in results)

    print(f"Success: {total_success}, Fail: {total_fail}, Total time: {total_elapsed:.2f}s, Avg throughput: {total_throughput / client_workers:.2f} bytes/s\n")

    return {
        'operation': operation,
        'volume_mb': volume_mb,
        'client_workers': client_workers,
        'total_success': total_success,
        'total_fail': total_fail,
        'total_time': total_elapsed,
        'avg_throughput': total_throughput / client_workers if client_workers else 0,
    }

if __name__ == "__main__":
    # Contoh menjalankan stress test upload dan download
    volumes = [10, 50, 100]  # MB
    workers_list = [1, 5, 50]

    # Jalankan contoh dengan threading
    for op in ['upload', 'download']:
        for vol in volumes:
            for workers in workers_list:
                run_stresstest(op, vol, workers, use_multiprocessing=False)

    # Jalankan contoh dengan multiprocessing
    for op in ['upload', 'download']:
        for vol in volumes:
            for workers in workers_list:
                run_stresstest(op, vol, workers, use_multiprocessing=True)
