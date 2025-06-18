import sys
import os
import uuid
from glob import glob
from datetime import datetime

class HttpServer:
    def __init__(self):
        self.types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.png': 'image/png',
            '.txt': 'text/plain',
            '.html': 'text/html'
        }

    def response(self, kode=404, message='Not Found', messagebody=bytes(), headers={}):
        tanggal = datetime.now().strftime('%c')
        resp = [
            f"HTTP/1.0 {kode} {message}\r\n",
            f"Date: {tanggal}\r\n",
            "Connection: close\r\n",
            "Server: myserver/1.0\r\n",
            f"Content-Length: {len(messagebody)}\r\n"
        ]
        for kk in headers:
            resp.append(f"{kk}: {headers[kk]}\r\n")
        resp.append("\r\n")

        response_headers = ''.join(resp).encode()
        if type(messagebody) is str:
            messagebody = messagebody.encode()

        return response_headers + messagebody

    def proses(self, data):
        if type(data) is bytes:
            data = data.decode(errors='ignore')

        try:
            headers_part, _, body_part = data.partition('\r\n\r\n')
            requests = headers_part.split("\r\n")
            baris = requests[0]
            all_headers = [n for n in requests[1:] if n != '']

            method, path, *_ = baris.split(" ")
            method = method.upper().strip()
            object_address = path.strip()

            if method == 'GET':
                return self.http_get(object_address, all_headers)

            elif method == 'POST':
                content_length = 0
                for h in all_headers:
                    if h.lower().startswith("content-length:"):
                        content_length = int(h.split(":", 1)[1].strip())
                        break

                # Ambil body dari data mentah (bytes)
                raw_data = data.encode()
                header_end = raw_data.find(b'\r\n\r\n')
                body = raw_data[header_end + 4 : header_end + 4 + content_length]

                return self.http_post(object_address, all_headers, body)

            else:
                return self.response(400, 'Bad Request', 'Unsupported HTTP Method', {})

        except Exception as e:
            return self.response(400, 'Bad Request', f'Error parsing request: {str(e)}', {})

    def http_get(self, object_address, headers):
        thedir = './'

        if object_address == '/':
            return self.response(200, 'OK', 'Ini Adalah Web Server Percobaan', {})

        elif object_address == '/list':
            files = os.listdir(thedir)
            files = [f for f in files if os.path.isfile(os.path.join(thedir, f))]
            content = "\n".join(files)
            return self.response(200, 'OK', content, {'Content-type': 'text/plain'})

        elif object_address == '/video':
            return self.response(302, 'Found', '', {'Location': 'https://youtu.be/katoxpnTf04'})

        elif object_address == '/santai':
            return self.response(200, 'OK', 'santai saja', {})

        else:
            file_path = object_address.lstrip('/')
            full_path = os.path.join(thedir, file_path)

            if not os.path.isfile(full_path):
                return self.response(404, 'Not Found', '', {})

            with open(full_path, 'rb') as f:
                isi = f.read()

            fext = os.path.splitext(full_path)[1]
            content_type = self.types.get(fext, 'application/octet-stream')
            return self.response(200, 'OK', isi, {'Content-type': content_type})

    def http_post(self, object_address, headers, body: bytes):
        if object_address == '/upload':
            filename = ''
            for h in headers:
                if h.lower().startswith('filename:'):
                    filename = h.split(":", 1)[1].strip()
                    break
            if not filename:
                filename = f'upload_{uuid.uuid4().hex}.bin'

            with open(filename, 'wb') as f:
                f.write(body)

            return self.response(201, 'Created', f'File {filename} uploaded successfully', {})

        elif object_address == '/delete':
            filename = ''
            for h in headers:
                if h.lower().startswith('filename:'):
                    filename = h.split(":", 1)[1].strip()
                    break
            if not filename:
                return self.response(400, 'Bad Request', 'Filename header missing', {})

            if os.path.exists(filename):
                os.remove(filename)
                return self.response(200, 'OK', f'File {filename} deleted', {})
            else:
                return self.response(404, 'Not Found', 'File not found', {})
        
        else:
            return self.response(404, 'Not Found', 'Invalid POST path', {})
