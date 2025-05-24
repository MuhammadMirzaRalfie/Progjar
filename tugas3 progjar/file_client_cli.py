import socket
import json
import base64
import logging
import os

server_address = ('127.0.0.1', 6666)

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(server_address)
        logging.warning(f"connecting to {server_address}")
        
        # Kirim perintah dengan akhir \r\n\r\n agar server tahu akhir pesan
        sock.sendall((command_str + "\r\n\r\n").encode())

        data_received = ""
        while True:
            data = sock.recv(1024)
            if not data:
                break
            data_received += data.decode()
            if "\r\n\r\n" in data_received:
                break

        # Bersihkan akhiran \r\n\r\n sebelum parse JSON
        data_received = data_received.strip().replace("\r\n\r\n", "")
        hasil = json.loads(data_received)
        return hasil
    except json.JSONDecodeError:
        logging.warning("Gagal decode JSON dari server.")
        print("❌ Respon server tidak valid.")
        return False
    except Exception as e:
        logging.warning(f"error during data receiving: {e}")
        print(f"❌ Terjadi kesalahan: {e}")
        return False
    finally:
        sock.close()

def remote_list():
    hasil = send_command("LIST")
    if hasil and hasil['status'] == 'OK':
        print("\n📄 Daftar file di server:")
        for nmfile in hasil['data']:
            print(f" - {nmfile}")
    else:
        print("❌ Gagal mendapatkan daftar file.")

def remote_get():
    filename = input("Masukkan nama file yang ingin diambil: ").strip()
    hasil = send_command(f"GET {filename}")
    if hasil and hasil['status'] == 'OK':
        try:
            content = base64.b64decode(hasil['data_file'])
            with open(filename, 'wb') as f:
                f.write(content)
            print(f"✅ File berhasil disimpan sebagai '{filename}'")
        except Exception as e:
            print(f"❌ Gagal menyimpan file: {e}")
    else:
        print("❌ Gagal mengambil file:", hasil['data'] if hasil else "Unknown error")

def remote_upload():
    filepath = input("Masukkan path file lokal yang ingin di-upload: ").strip()
    if not os.path.exists(filepath):
        print("❌ File tidak ditemukan.")
        return
    try:
        with open(filepath, 'rb') as f:
            filedata = f.read()
        encoded = base64.b64encode(filedata).decode('utf-8')
        filename = os.path.basename(filepath)
        command_str = f"UPLOAD {filename} {encoded}"
        hasil = send_command(command_str)
        if hasil and hasil['status'] == 'OK':
            print(f"✅ File '{filename}' berhasil di-upload ke server.")
        else:
            print("❌ Gagal upload:", hasil['data'] if hasil else "Unknown error")
    except Exception as e:
        print(f"❌ Error saat upload: {e}")

def remote_delete():
    filename = input("Masukkan nama file yang ingin dihapus dari server: ").strip()
    hasil = send_command(f"DELETE {filename}")
    if hasil and hasil['status'] == 'OK':
        print(f"✅ File '{filename}' berhasil dihapus dari server.")
    else:
        print("❌ Gagal hapus:", hasil['data'] if hasil else "Unknown error")

def main_menu():
    while True:
        print("\n=== Menu File Client ===")
        print("1. Lihat daftar file di server")
        print("2. Ambil file dari server")
        print("3. Upload file ke server")
        print("4. Hapus file di server")
        print("5. Keluar")
        try:
            pilihan = input("Pilih menu (1-5): ").strip()
        except KeyboardInterrupt:
            print("\n👋 Program dihentikan oleh pengguna.")
            break

        if pilihan == '1':
            remote_list()
        elif pilihan == '2':
            remote_get()
        elif pilihan == '3':
            remote_upload()
        elif pilihan == '4':
            remote_delete()
        elif pilihan == '5':
            print("👋 Keluar dari program.")
            break
        else:
            print("❗ Pilihan tidak valid. Silakan coba lagi.")

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    main_menu()
