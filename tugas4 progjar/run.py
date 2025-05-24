import subprocess
import time
import csv
import os
from threading import Thread
from stresstest import run_stresstest

# Path file server
SERVER_THREAD = "server_multithread/file_server_thread.py"
SERVER_PROCESS = "server_multiprocess/file_server_process.py"

# CSV output file
CSV_FILE = "experiment_results.csv"

# Konfigurasi eksperimen
OPERATIONS = ["upload", "download"]
VOLUMES = [10, 50, 100]  # MB
CLIENT_WORKERS = [1, 5, 50]
SERVER_WORKERS = [1, 5, 50]

def run_server(mode, workers):
    """Jalankan server dengan mode dan jumlah worker tertentu"""
    if mode == "thread":
        cmd = ["python", SERVER_THREAD, str(workers)]
    else:
        cmd = ["python", SERVER_PROCESS, str(workers)]

    # Jalankan server sebagai subprocess
    return subprocess.Popen(cmd)

def stop_server(process):
    process.terminate()
    process.wait()

def main():
    # Pastikan CSV file ada header
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Nomor", "Server Mode", "Operasi", "Volume (MB)",
                "Client Worker Pool", "Server Worker Pool",
                "Waktu Total (s)", "Throughput (bytes/s)",
                "Client Sukses", "Client Gagal", "Server Sukses", "Server Gagal"
            ])

    nomor = 1
    for server_mode in ["thread", "process"]:
        for server_workers in SERVER_WORKERS:
            # Jalankan server dengan jumlah worker tertentu
            print(f"\nMenjalankan server {server_mode} dengan {server_workers} worker")
            server_proc = run_server(server_mode, server_workers)
            time.sleep(2)  # Tunggu server start

            for op in OPERATIONS:
                for vol in VOLUMES:
                    for client_workers in CLIENT_WORKERS:
                        print(f"Stress test: Server={server_mode}, ServerWorkers={server_workers}, Op={op}, Volume={vol}MB, ClientWorkers={client_workers}")

                        # Run stress test, sesuaikan multiprocessing jika server process
                        use_mp = True if server_mode == "process" else False

                        result = run_stresstest(op, vol, client_workers, use_multiprocessing=use_mp)

                        # Catat hasil ke CSV
                        with open(CSV_FILE, "a", newline="") as f:
                            writer = csv.writer(f)
                            writer.writerow([
                                nomor, server_mode, op, vol,
                                client_workers, server_workers,
                                f"{result['total_time']:.2f}",
                                f"{result['avg_throughput']:.2f}",
                                result['total_success'],
                                result['total_fail'],
                                "N/A",  # Server sukses/gagal bisa diisi dari log server
                                "N/A"
                            ])
                        nomor += 1

            # Stop server setelah kombinasi selesai
            stop_server(server_proc)
            time.sleep(1)

if __name__ == "__main__":
    main()
