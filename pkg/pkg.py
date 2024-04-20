import os,sys
print(os.getcwd())
sys.path.append(os.getcwd())
from utils.json import load_file
from download_file.download_repomd import download_repo_metadata
from utils.xml import XMLParser
import pandas as pd 

def __repomd_get_primary_file(os_path, repomd_path='repodata/repomd.xml'):
    repo_cont = XMLParser.parsefile(os.path.join(os_path, repomd_path).replace("\\", "/"))
    for i in repo_cont['repomd']['data']:
        if i['@type'] == 'primary':
            return i['location']['@href']
    return None

def get_pkgs_info(xml_file):
    if not os.path.exists(xml_file):
        print(f"{xml_file} may be exists!")
        return {}
    xml_root = XMLParser.gz_parsefile(xml_file, 0)
    if xml_root is None:
        return None
    os_pkgs = None
    if 'package' in xml_root['metadata']:
        os_pkgs = {}
        for i in xml_root['metadata']['package']:
            pkg_content = {}
            pkg_content['@type'] = i['@type']
            pkg_content['name'] = i['name']
            pkg_content['arch'] = i['arch']
            pkg_content['version_@epoch'] = i['version']['@epoch']
            pkg_content['version_@ver'] = i['version']['@ver']
            pkg_content['version_@rel'] = i['version']['@rel']
            pkg_content['checksum_@type'] = i['checksum']['@type']
            pkg_content['checksum_@pkgid'] = i['checksum']['@pkgid']
            pkg_content['summary'] = i['summary']
            pkg_content['description'] = i['description']
            pkg_content['packager'] = i['packager']
            pkg_content['url'] = i['url']
            pkg_content['time_@file'] = i['time']['@file']
            pkg_content['time_@build'] = i['time']['@build']
            pkg_content['size_@package'] = i['size']['@package']
            pkg_content['size_@installed'] = i['size']['@installed']
            pkg_content['size_@archive'] = i['size']['@archive']
            pkg_content['location_@href'] = i['location']['@href']
            # pkg_content['format_rpm:license'] = i['format']['rpm:license']
            # pkg_content['format_rpm:vendor'] = i['format']['rpm:vendor']
            # pkg_content['format_rpm:group'] = i['format']['rpm:group']
            # pkg_content['format_rpm:buildhost'] = i['format']['rpm:buildhost']
            # pkg_content['format_rpm:sourcerpm'] = i['format']['rpm:sourcerpm']
            # pkg_content['format_rpm:header-range_@start'] = i['format']['rpm:header-range']['@start']
            # pkg_content['format_rpm:header-range_@end'] = i['format']['rpm:header-range']['@end']
            os_pkgs[pkg_content['name']] = pkg_content
        return os_pkgs

def save_pkgs(os_pkgs,os_path,os_k):
    if not os.path.exists(os_path):
        os.mkdir(os_path)
    pkg_path = os.path.join(os_path,f"{os_k}.csv")
    # headers = ['@type','name','arch','version_@epoch','version_@ver','version_@rel','checksum_@pkgid','summary','description','packager','url','time_@file','time_@build','size_@package','size_@installed','size_@archive','location_@href','format_rpm:license','format_rpm:vendor','format_rpm:group','format_rpm:buildhost','format_rpm:sourcerpm','format_rpm:header-range_@start','format_rpm:header-range_@end']
    headers = ['@type','name','arch','version_@epoch','version_@ver','version_@rel','checksum_@pkgid','summary','description','packager','url','time_@file','time_@build','size_@package','size_@installed','size_@archive','location_@href']
    data = []
    if os_pkgs==None:
        return
    for item in os_pkgs.values():
        row = []
        row.append(item['@type'])
        row.append(item['name'])
        row.append(item['arch'])
        row.append(item['version_@epoch'])
        row.append(item['version_@ver'])
        row.append(item['version_@rel'])
        row.append(item['checksum_@pkgid'])
        row.append(item['summary'])
        row.append(item['description'])
        row.append(item['packager'])
        row.append(item['url'])
        row.append(item['time_@file'])
        row.append(item['time_@build'])
        row.append(item['size_@package'])
        row.append(item['size_@installed'])
        row.append(item['size_@archive'])
        row.append(item['location_@href'])
        # row.append(item['format_rpm:license'])
        # row.append(item['format_rpm:vendor'])
        # row.append(item['format_rpm:group'])
        # row.append(item['format_rpm:buildhost'])
        # row.append(item['format_rpm:sourcerpm'])
        # row.append(item['format_rpm:header-range_@start'])
        # row.append(item['format_rpm:header-range_@end'])
        data.append(row)
    df = pd.DataFrame(data,columns=headers)
    df.to_csv(pkg_path,index=False)

def merge_pkgs(all_pkgs,os_pkgs):
    if all_pkgs == None:
        all_pkgs = os_pkgs
    elif os_pkgs==None:
        return all_pkgs
    else:
        for key,item in os_pkgs.items():
            if key in all_pkgs:
                pass
            else:
                all_pkgs[key] = os_pkgs[key]
    return all_pkgs

def get_os_pkgs(os_versions,override):
    metas = load_file('./os_urls.json')
    for os_name,os_arch,os_ver in os_versions:
        all_pkgs = None
        save_path = f"./format/pkg/eachOS/{os_name}_{os_arch}_{os_ver}"
        for os_k, os_url in metas[os_name].items():
            os_path,os_files = download_repo_metadata(os_url.format(arch=os_arch, ver=os_ver), "./data/", override)
            primary_file = __repomd_get_primary_file(os_path)
            if primary_file:
                print(os_k,"=======YES========")
                os_pkgs = get_pkgs_info(os.path.join(os_path, primary_file).replace('\\', '/'))
                save_pkgs(os_pkgs,save_path,os_k)
                all_pkgs = merge_pkgs(all_pkgs,os_pkgs)
            else:
                print(os_k, "=======NO========")
        save_pkgs(all_pkgs,save_path,"merge")



def get_os_pkgs(os_versions,override):
    metas = load_file('./os_urls.json')
    for os_name,os_arch,os_ver in os_versions:
        all_pkgs = None
        for os_k, os_url in metas[os_name].items():
            os_path,os_files = download_repo_metadata(os_url.format(arch=os_arch, ver=os_ver), "./data/", override)
            primary_file = __repomd_get_primary_file(os_path)
            if primary_file:
                print(os_k,"=======YES========")
                os_pkgs = get_pkgs_info(os.path.join(os_path, primary_file).replace('\\', '/'))
                os_path = f"./format/pkg/eachOS/{os_name}_{os_arch}_{os_ver}"
                save_pkgs(os_pkgs,os_path,os_k)
                all_pkgs = merge_pkgs(all_pkgs,os_pkgs)
            else:
                print(os_k, "=======NO========")
        save_pkgs(all_pkgs,os_path,"merge")

if __name__== "__main__":
    os_versions = [
        # ("fedora", "x86_64", "38"),
        # ('fedora', 'aarch64', '38'),
        ('centos', 'x86_64', '7'),
    ]
    get_os_pkgs(os_versions,False)
    pass