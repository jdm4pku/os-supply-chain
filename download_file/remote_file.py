import os
import requests

class RemoteFile:
    def __init__(self, url, path, chunk_size=8192, override=False,flag=False):
        self.url = url
        self.chunksize = chunk_size
        self.override = override
        self.path = os.path.abspath(path)
        self.flag = flag
        if override and os.path.exists(self.path):
            os.remove(self.path)

    def __enter__(self):
        if os.path.exists(self.path):
            self.f = open(self.path, 'rb')
            return self.f
        # print(f"Downloading {self.url} to {self.path}...")
        try: 
            with requests.get(self.url, stream=True) as r:
                r.raise_for_status()
                print(os.path.exists(self.path[:-10]))
                if self.flag and (not os.path.exists(self.path[:-10])):
                    os.makedirs(self.path[:-10])
                self.f = open(self.path, 'wb+')
                for chunk in r.iter_content(chunk_size=self.chunksize):
                    if chunk:  # filter out keep-alive new chunks
                        self.f.write(chunk)
            self.f.seek(0)
            return self.f
        except requests.exceptions.HTTPError as err:
            print(f"{self.url} does not exist!")
            self.f=None
            return None

    def __exit__(self, exc_type, exc_value, traceback):
        if not (self.f==None):
            self.f.close()
        if exc_type is not None:
            print(f"Error occurred: {exc_type} - {exc_value}")