import json
import logging
import shlex

from file_interface import FileInterface


class FileProtocol:
    def __init__(self):
        self.file = FileInterface()

    def proses_string(self, string_datamasuk=''):
        logging.warning(f"string diproses: {string_datamasuk}")
        try:
            tokens = shlex.split(string_datamasuk)  # tetap original case-sensitive
            if not tokens:
                return json.dumps(dict(status='ERROR', data='Empty command'))

            command = tokens[0].lower()
            params = tokens[1:]

            # Khusus untuk UPLOAD: gabungkan semua data base64 menjadi satu string
            if command == 'upload' and len(params) >= 2:
                filename = params[0]
                base64_data = ' '.join(params[1:])  # gabungkan semua bagian base64
                cl = self.file.upload([filename, base64_data])
            elif command == 'delete' and len(params) == 1:
                cl = self.file.delete(params)
            elif command == 'get' and len(params) == 1:
                cl = self.file.get(params)
            elif command == 'list':
                cl = self.file.list()
            else:
                return json.dumps(dict(status='ERROR', data='Perintah atau parameter tidak dikenali'))

            return json.dumps(cl)
        except Exception as e:
            return json.dumps(dict(status='ERROR', data=f'request tidak dikenali: {str(e)}'))


if __name__ == '__main__':
    fp = FileProtocol()
    print(fp.proses_string("LIST"))
    print(fp.proses_string("GET contoh_upload.txt"))
    with open("contoh_upload.txt", "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    print(fp.proses_string(f"UPLOAD contoh_upload.txt {encoded}"))
    print(fp.proses_string("DELETE contoh_upload.txt"))
