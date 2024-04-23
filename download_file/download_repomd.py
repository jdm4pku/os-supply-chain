import re
import os
from typing import Tuple, Any, List

import requests
from download_file.remote_file import RemoteFile
from utils.download import dir_name


def download_repo_metadata(url: str, path=None, override=False) -> tuple[Any, list[Any]]:

    _base_url = url
    if 'repomd.xml' in url:
        _base_url = os.path.dirname(url)
    if 'repodata' in url:
        _base_url = os.path.dirname(url)
    _hash = dir_name(_base_url)
    if not path:
        path = "./data/CACHEDIR/"
        if not os.path.exists(path):
            os.makedirs(path)
    _repo_path = os.path.join(path, _hash, 'repodata').replace("\\", "/")
    _repomd_url = os.path.join(_base_url, 'repodata', 'repomd.xml').replace("\\", "/")
    if not os.path.exists(_repo_path):
        os.makedirs(_repo_path)

    _primary, _filelists = None, None
    with RemoteFile(_repomd_url, path=os.path.join(_repo_path, 'repomd.xml').replace("\\", "/"), override=override) as f:
        if f==None:
            return None,None
        _hrefs = re.findall(r'<location href="(.+?)"', f.read().decode('utf-8'))
        for href in _hrefs:
            if href.endswith('primary.xml.gz'):
                _primary = href
            elif href.endswith('filelists.xml.gz'):
                _filelists = href

    if not _primary or not _filelists:
        os.remove(os.path.join(_repo_path, 'repomd.xml').replace("\\", "/"))
        return None,None
        # raise Exception(
        #     "Can't find primary.xml.gz or filelists.xml.gz in {}".format(os.path.join(_repo_path, 'repomd.xml').replace("\\", "/")))

    for url in _hrefs:
        if url.endswith('.xml') or url.endswith('.gz') or url.endswith('.xz') or url.endswith('.bz2'):
            try:
                with RemoteFile(os.path.join(_base_url, url).replace("\\", "/"), path=os.path.join(_repo_path, os.path.basename(url)).replace("\\", "/"), override=override) as f:
                    pass
            except requests.HTTPError as e:
                print(f"Can't download {url}: {e}")

    return os.path.dirname(_repo_path), _hrefs