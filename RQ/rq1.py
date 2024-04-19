import os,sys
print(os.getcwd())
sys.path.append(os.getcwd())
import os,sys
import json
from utils.json import load_file
from download_file.download_repomd import download_repo_metadata
from group.group_label import __repomd_get_group_file,get_groups_info,save_groups,merge_groups
from pkg.pkg import __repomd_get_primary_file,get_pkgs_info,save_pkgs,merge_pkgs

"""
37,38,39 --> fedora1
7-36 --> fedora 2
1-6 fedora 3
"""

def write_json(data,path):
    with open(path,'w') as f:
        json.dump(data,f,indent=4)

def get_pkg2group(all_groups):
    pkg2group = {}
    if all_groups == None:
        return pkg2group
    for item in all_groups.values():
        group = ".".join(item["name"])
        for pkg,pkg_opt in item["packagelist"].items():
            if pkg in pkg2group:
                if group not in pkg2group[pkg]:
                    pkg2group[pkg][group] = pkg_opt
                else:
                    continue
            else:
                pkg2group[pkg] = {group:pkg_opt}
    return pkg2group

def count_pkg_in_group(all_groups):
    pkg2group = get_pkg2group(all_groups)
    return len(pkg2group)


def rq1_count_analysis(os_arch_ver,override=False):
    metas = load_file('./os_urls_rq1.json')
    group_counts_res = {
        "x86_64":[],
        "aarch64":[]
    }
    inpkg_counts_res = {
        "x86_64":[],
        "aarch64":[]
    }
    tolpkg_counts_res = {
        "x86_64":[],
        "aarch64":[]
    }
    for os_name,os_arch,os_ver in os_arch_ver:
        all_groups = None
        all_pkgs = None
        rq1_result_dir = f"/home/jindongming/project/1-OsSupplyChain/os-supply-chain/results/RQ1/{os_name}"
        if not os.path.exists(rq1_result_dir):
            os.mkdir(rq1_result_dir)
        group_path = f"./format/group/eachOS/{os_name}_{os_arch}_{os_ver}"
        pkgs_path = f"./format/pkg/eachOS/{os_name}_{os_arch}_{os_ver}"
        for os_k,os_url in metas[os_name].items():
            os_path,os_files =download_repo_metadata(os_url.format(arch=os_arch, ver=os_ver), "./rq1-data/", override)
            if os_path==None:
                continue
            group_file = __repomd_get_group_file(os_path)
            primary_file = __repomd_get_primary_file(os_path)
            if group_file:
                os_groups, os_cate, os_env, os_langp = get_groups_info(os.path.join(os_path, group_file).replace('\\', '/'))
                save_groups(os_groups,group_path,os_k)
                all_groups = merge_groups(all_groups,os_groups)
            if primary_file:
                os_pkgs = get_pkgs_info(os.path.join(os_path, primary_file).replace('\\', '/'))
                save_pkgs(os_pkgs,pkgs_path,os_k)
                all_pkgs = merge_pkgs(all_pkgs,os_pkgs)
        save_groups(all_groups,group_path,"merge")
        save_pkgs(all_pkgs,pkgs_path,"merge")
        group_count = len(all_groups)
        inpkg_count = count_pkg_in_group(all_groups)
        pkg_count = len(all_pkgs)
        group_counts_res[os_arch].append(group_count)
        inpkg_counts_res[os_arch].append(inpkg_count)
        tolpkg_counts_res[os_arch].append(pkg_count)
    group_counts_path = os.path.join(rq1_result_dir,"groupcount.json")
    inpkg_counts_path = os.path.join(rq1_result_dir,"inpkgcount.json")
    tolpkg_counts_path = os.path.join(rq1_result_dir,"tolpkgcount.json")
    write_json(group_counts_res,group_counts_path)
    write_json(inpkg_counts_res,inpkg_counts_path)
    write_json(tolpkg_counts_res,tolpkg_counts_path)


def rq1_content_analysis(os_arch_ver,override=False):
    metas = load_file('./os_urls_rq1.json')
    group_add_function = {
        "x86_64":[],
        "aarch64":[]
    }
    group_delete_function = {
        "x86_64":[],
        "aarch64":[]
    }
    inpkg_add_function = {
        "x86_64":[],
        "aarch64":[]
    }
    inpkg_delete_function = {
        "x86_64":[],
        "aarch64":[]
    }
    tolpkg_add_function = {
        "x86_64":[],
        "aarch64":[]
    }
    tolpkg_delete_function = {
        "x86_64":[],
        "aarch64":[]
    }
    for os_name,os_arch,os_ver in os_arch_ver:
        all_groups = None
        all_pkgs = None
        rq1_result_dir = f"/home/jindongming/project/1-OsSupplyChain/os-supply-chain/results/RQ1/{os_name}"
        if not os.path.exists(rq1_result_dir):
            os.mkdir(rq1_result_dir)
        pre_tolpkg_x86 = None
        pre_tolpkg_aarch = None
        pre_group_x86 = None
        pre_group_aarch = None
        pre_inpkg_x86 = None
        pre_inpkg_aarch = None
        for os_k,os_url in metas[os_name].items():
            os_path,os_files =download_repo_metadata(os_url.format(arch=os_arch, ver=os_ver), "./rq1-data/", override)
            if os_path==None:
                continue
            group_file = __repomd_get_group_file(os_path)
            primary_file = __repomd_get_primary_file(os_path)
            if group_file:
                os_groups, os_cate, os_env, os_langp = get_groups_info(os.path.join(os_path, group_file).replace('\\', '/'))
                all_groups = merge_groups(all_groups,os_groups)
            if primary_file:
                os_pkgs = get_pkgs_info(os.path.join(os_path, primary_file).replace('\\', '/'))
                all_pkgs = merge_pkgs(all_pkgs,os_pkgs)
        if os_arch == 'x86_64':
            if pre_tolpkg_x86 == None:
                pre_tolpkg_x86 = all_pkgs
            else:
                add_talpkg,delete_talpkg = compute_change_totalpkg(pre_group_x86,all_pkgs)
                tolpkg_add_function['x86_64'].append(add_talpkg)
                tolpkg_delete_function['x86_64'].append(delete_talpkg)
            if pre_inpkg_x86 == None:
                pre_inpkg_x86 = get_pkg2group(all_groups)
            else:
                add_inpkg,delete_inpkg = compute_change_inpkg(pre_inpkg_x86,all_pkgs)
                inpkg_add_function['x86_64'].append(add_inpkg)
                inpkg_delete_function["x86_64"].append(delete_inpkg)
            if pre_group_x86 == None:
                pre_group_x86 = all_groups
            else:
                add_groups,delete_groups = compute_change_inpkg(pre_group_x86,all_groups)
                group_add_function["x86_64"].append(add_groups)
                group_delete_function["x86_64"].append(delete_groups)
        elif os_arch == "aarch64":
            if pre_tolpkg_aarch == None:
                pre_tolpkg_aarch = all_pkgs
            else:
                add_talpkg,delete_talpkg = compute_change_totalpkg(pre_group_aarch,all_pkgs)
                tolpkg_add_function['aarch64'].append(add_talpkg)
                tolpkg_delete_function['aarch64'].append(delete_talpkg)
            if pre_inpkg_aarch == None:
                pre_inpkg_aarch = get_pkg2group(all_groups)
            else:
                add_inpkg,delete_inpkg = compute_change_inpkg(pre_inpkg_aarch,all_groups)
                inpkg_add_function['aarch64'].append(add_inpkg)
                inpkg_delete_function['aarch64'].append(delete_inpkg)
            if pre_group_aarch == None:
                pre_group_aarch = all_groups
            else:
                add_groups,delete_groups = compute_change_inpkg(pre_group_aarch,all_groups)
                group_add_function['aarch64'].append(add_groups)
                group_delete_function['aarch64'].append(delete_groups)



if __name__=="__main__":
    os_name = "fedora"
    os_arch_list = ['x86_64','arch64']
    os_ver_list = [str(i) for i in range(7,40)]
    os_versions = []
    for os_arch in os_arch_list:
        for os_ver in os_ver_list:
            os_versions.append((os_name,os_arch,os_ver))
    rq1_count_analysis(os_versions,True)
    # rq1_content_analysis(os_versions,True)
    pass
    