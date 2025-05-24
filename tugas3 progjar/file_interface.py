import os
import json
import base64
from glob import glob

class FileInterface:
    def __init__(self):
        os.makedirs('files/', exist_ok=True)
        os.chdir('files/')

    def list(self, params=[]):
        try:
            filelist = glob('*.*')
            return dict(status='OK', data=filelist)
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def get(self, params=[]):
        try:
            filename = params[0]
            if filename == '':
                return dict(status='ERROR', data='Filename is empty')
            with open(filename, 'rb') as fp:
                isifile = base64.b64encode(fp.read()).decode()
            return dict(status='OK', data_namafile=filename, data_file=isifile)
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def upload(self, params=[]):
        try:
            filename = params[0]
            filedata_base64 = params[1]
            filedata = base64.b64decode(filedata_base64.encode())
            with open(filename, 'wb') as fp:
                fp.write(filedata)
            return dict(status='OK', data='File uploaded')
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def delete(self, params=[]):
        try:
            filename = params[0]
            if os.path.exists(filename):
                os.remove(filename)
                return dict(status='OK', data='File deleted')
            else:
                return dict(status='ERROR', data='File not found')
        except Exception as e:
            return dict(status='ERROR', data=str(e))


if __name__ == '__main__':
    f = FileInterface()
    print(f.list())
    print(f.get(['contoh_upload.txt']))
    # Contoh simpan
    print(f.upload(['contoh_upload.txt', base64.b64encode(b"Hello world").decode()]))
    print(f.list())
    # Contoh hapus
    print(f.delete(['contoh_upload.txt']))
    print(f.list())
