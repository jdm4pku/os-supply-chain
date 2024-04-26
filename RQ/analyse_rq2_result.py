
import os,sys
print(os.getcwd())
sys.path.append(os.getcwd())
import os
import json
from utils.json import load_file
from utils.logger import get_logger
from download_file.download_repomd import download_repo_metadata
from group.group_label import __repomd_get_group_file,get_groups_info,merge_groups
from pkg.pkg import __repomd_get_primary_file,get_pkgs_info,merge_pkgs


def write_json_file(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


logger = get_logger(__name__)
def parser_result(os_arch_ver,override=False):
    metas = load_file('./os_urls.json')
    for os_name,os_arch,os_ver in os_arch_ver:
        logger.info(f"-------{os_name}-{os_arch}-{os_ver}------")
        all_groups = None
        all_pkgs = None
        for os_k,os_url in metas[os_name].items():
            os_path,os_files =download_repo_metadata(os_url.format(arch=os_arch, ver=os_ver), "./data/", override)
            group_file = __repomd_get_group_file(os_path)
            if group_file:
                os_groups, os_cate, os_env, os_langp = get_groups_info(os.path.join(os_path, group_file).replace('\\', '/'))
                all_groups = merge_groups(all_groups,os_groups)
        for os_k, os_url in metas[os_name].items():
            os_path,os_files =download_repo_metadata(os_url.format(arch=os_arch, ver=os_ver), "./data/", override)
            primary_file = __repomd_get_primary_file(os_path)
            if primary_file:
                os_pkgs = get_pkgs_info(os.path.join(os_path, primary_file).replace('\\', '/'))
                all_pkgs = merge_pkgs(all_pkgs,os_pkgs)
        # 第一问
        root_dir = "results/RQ2/0-cluster"
        input_path = os.path.join(root_dir,f"{os_name}_{os_arch}_{os_ver}/result.json")
        output = []
        with open(input_path, 'r') as file:
            json_content = json.load(file)
        sorted_items = sorted(json_content.items(), key=lambda x: x[1], reverse=True)
        group_result = []
        for item in sorted_items:
            group_name = item[0]
            cluster_result = item[1]
            pkg_list = {}
            for pkg_name in all_groups[group_name]['packagelist']:
                if pkg_name in all_pkgs:
                    pkg_list[pkg_name] = all_pkgs[pkg_name]["description"]
            one_group_result = {
                "group_name":group_name,
                "cluster_result":cluster_result,
                "pkg":pkg_list
            }
            group_result.append(one_group_result)
        write_dir = f"results/RQ2/0-cluster/{os_name}_{os_arch}_{os_ver}"
        write_path = os.path.join(write_dir,"detail_result.json")
        write_json_file(write_path,group_result)
        # 第二问
        root_dir = "results/RQ2/1-relevant"
        input_path = os.path.join(root_dir,f"{os_name}_{os_arch}_{os_ver}/result.json")
        output = []
        with open(input_path, 'r') as file:
            json_content = json.load(file)
        sorted_items = sorted(json_content.items(), key=lambda x: x[1], reverse=True)
        group_result = []
        for item in sorted_items:
            group_name = item[0]
            relevant_result = item[1]
            group_descrption = all_groups[group_name]["description"][0]
            pkg_list = {}
            for pkg_name in all_groups[group_name]['packagelist']:
                if pkg_name in all_pkgs:
                    pkg_list[pkg_name] = all_pkgs[pkg_name]["description"]
            one_group_result = {
                "group_name":group_name,
                "group_description":group_descrption,
                "relevant_result":relevant_result,
                "pkg":pkg_list
            }
            group_result.append(one_group_result)
        write_dir = f"results/RQ2/1-relevant/{os_name}_{os_arch}_{os_ver}"
        write_path = os.path.join(write_dir,"detail_result.json")
        write_json_file(write_path,group_result)

        


if __name__=="__main__":
    os_versions = [
        ("fedora", "x86_64", "38"),
        ('fedora', 'aarch64', '38'),
        ('centos', 'x86_64', '7'),
    ]
    parser_result(os_versions)
    
            
        