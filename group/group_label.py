
import os,sys
print(os.getcwd())
sys.path.append(os.getcwd())
import os
import json
import pandas as pd
from utils.json import load_file
from utils.xml import XMLParser
from utils.logger import get_logger
from download_file.download_repomd import download_repo_metadata

logger = get_logger(__name__)

def __repomd_get_group_file(os_path, repomd_path='repodata/repomd.xml'):
    repo_cont = XMLParser.parsefile(os.path.join(os_path, repomd_path).replace("\\", "/"))
    for i in repo_cont['repomd']['data']:
        if i['@type'] == 'group':
            return i['location']['@href']
    return None

def __get_descrip(des_list):
    if des_list is None:
        return ["", ""]
    if type(des_list) is str:
        return [des_list, ""]
    if type(des_list) is list:
        engstr = ""
        chstr = ""
        for des_i in des_list:
            if type(des_i) is str:
                engstr += des_i
            elif type(des_i) is dict:
                if des_i["@xml:lang"] == "zh_CN":
                    chstr += des_i["#text"]
            else:
                print("=======des_i error=========")
                print(des_i)
        return [engstr, chstr]
    print("=======des_list error=========")
    print(des_list)
    return None


def __get_name(name_list):
    # if name_list is None:
    #     return ["", ""]
    if type(name_list) is str:
        return [name_list, ""]
    if type(name_list) is list:
        engstr = ""
        chstr = ""
        for name_i in name_list:
            if type(name_i) is str:
                engstr += name_i
            elif type(name_i) is dict:
                if name_i["@xml:lang"] == "zh_CN":
                    chstr += name_i["#text"]
            else:
                print("=======name_i error=========")
                print(name_i)
        return [engstr, chstr]
    print("=======name_list error=========")
    print(name_list)
    return None


def __get_group_packs(pack_dict):
    if pack_dict is None:
        return {}
    # if type(pack_dict) is str:
    if not(type(pack_dict) is dict and "packagereq" in list(pack_dict.keys())):
    # if not(type(pack_dict) is dict and len(pack_dict.keys()) == 1 and "packagereq" in list(pack_dict.keys())):
        print("==========packagereq key error==========")
        print(pack_dict)
    pack_ret = {}
    # print(type(pack_dict["packagereq"]))
    if type(pack_dict["packagereq"]) is dict:
        pack_ret[pack_dict["packagereq"]['#text']] = pack_dict["packagereq"]['@type']
        return pack_ret
    if type(pack_dict["packagereq"]) is list:
        # print("==========")
        # print(pack_dict["packagereq"][0])
        for pack_i in pack_dict["packagereq"]:
            if '#text' in pack_i:
                if '@type' in pack_i:
                    pack_ret[pack_i['#text']] = pack_i['@type']
                else: # 用来处理anolis中的一个特殊情况
                    """
                    {'@type': 'mandatory', '#text': 'adwaita-qt'}
                    {'@variant': 'BaseOS', '#text': 'atlas-devel'}
                    """
                    pack_ret[pack_i['#text']] = "mandory"
            else:
                pack_ret[pack_i] = "mandory"
        return pack_ret
    if type(pack_dict["packagereq"]) is str:
        name = pack_dict["packagereq"]
        pack_ret[name] = "mandory"
        return pack_ret
    print("==========packagereq value error==========")
    # exit()
    print(pack_dict["packagereq"])
    return None

def __get_groups(grouplist, group_val, init_groupdict=None):
    if type(grouplist['groupid']) is str:
        if init_groupdict is None:
            return {grouplist['groupid']: group_val}
        else:
            init_groupdict[grouplist['groupid']] = group_val
    elif type(grouplist['groupid']) is list:
        if init_groupdict is None:
            return {g: group_val for g in grouplist['groupid']}
        else:
            for g in grouplist['groupid']:
                if type(g) is str:
                    init_groupdict[g] = group_val
                elif type(g) is dict and '#text' in g.keys():
                    init_groupdict[g['#text']] = group_val
                else:
                    print('========item of group list error=========')
                    print(g)
    else:
        print("==========grouplist error==========")
        print(grouplist)
    return init_groupdict


def get_groups_info(xml_file):
    # xml_file = "/home/jindongming/project/1-OsSupplyChain/os-supply-chain/rq1-data/anolis_8_PowerTools_x86_64_os/repodata/2b13cd3f9d81647fd31aa16de1b16b582efd9566f8c4334e4561a030f3777c37-comps-PowerTools.x86_64.xml"
    xml_root = XMLParser.parsefile(xml_file)
    if xml_root is None:
        return None, None, None, None
    # if 'comps' in xml_root and type(xml_root['comps']) is dict:
    #     print(xml_root['comps'].keys())
    #     for ks in xml_root['comps'].keys():
    #         print(ks, ": ", len(xml_root['comps'][ks]))
    # else:
    #     return None, None, None, None
    os_groups, os_cate, os_env, os_langp = None, None, None, None
    if xml_root['comps']==None:
        return os_groups, os_cate, os_env, os_langp
    if 'group' in xml_root['comps']:
        os_groups = {}
        gslist = []
        if type(xml_root['comps']['group']) is list:
            gslist = xml_root['comps']['group']
        elif type(xml_root['comps']['group']) is dict:
            gslist = [xml_root['comps']['group']]
        else:
            print("==========groups list error=============")
            print(xml_root['comps']['group'])
        for i in gslist:
            group_contend = {}
            # print("------------------------------\n")
            # print(i)
            # print(f"-----{i['packagelist']}------")
            group_contend['default'] = i['default'] if 'default' in i else "unknown"
            group_contend['description'] = __get_descrip(i['description']) if 'description' in i else ""
            group_contend['name'] = __get_name(i['name']) 
            group_contend['packagelist'] = __get_group_packs(i['packagelist']) if 'packagelist' in i else {}
            group_contend['uservisible'] = i['uservisible'] if 'uservisible' in i else "unknown"
            os_groups[group_contend['name'][0]] = group_contend
    # if 'category' in xml_root['comps']:
    #     os_cate = {}
    #     for i in xml_root['comps']['category']:
    #         cate_contend = {}
    #         cate_contend['description'] = __get_descrip(i['description'])
    #         cate_contend['name'] = __get_name(i['name'])
    #         cate_contend['grouplist'] = __get_groups(i['grouplist'], 'grouplist')
    #         if 'optionlist' in i:
    #             cate_contend['grouplist'] = __get_groups(i['optionlist'], 'optionlist', cate_contend['grouplist'])
    #         os_cate[cate_contend['name'][0]] = cate_contend
    # if 'environment' in xml_root['comps']:
    #     os_env = {}
    #     for i in xml_root['comps']['environment']:
    #         env_contend = {}
    #         if 'description' in i:
    #             env_contend['description'] = __get_descrip(i['description'])
    #         env_contend['name'] = __get_name(i['name'])
    #         if 'grouplist' in i:
    #             env_contend['grouplist'] = __get_groups(i['grouplist'], 'grouplist')
    #         if 'optionlist' in i:
    #             env_contend['grouplist'] = __get_groups(i['optionlist'], 'optionlist', env_contend['grouplist'])
    #         os_env[env_contend['name'][0]] = env_contend
    return os_groups, os_cate, os_env, os_langp

def save_groups(os_groups,os_path,os_k):
    if not os.path.exists(os_path):
        os.mkdir(os_path)
    pkg_path = os.path.join(os_path,f"{os_k}.csv")
    headers = ["name","description","packagelist","default","uservisible"]
    data = []
    if os_groups==None:
        return
    for item in os_groups.values():
        row = []
        row.append(','.join(item["name"]))
        row.append(','.join(item['description']))
        row.append(json.dumps(item['packagelist']))
        row.append(item['default'])
        row.append(item['uservisible'])
        data.append(row)
    df = pd.DataFrame(data, columns=headers)
    df.to_csv(pkg_path,index=False)

def merge_groups(all_groups,os_groups):
    if all_groups==None:
        all_groups = os_groups
    elif os_groups==None:
        return all_groups
    else:
        for key,item in os_groups.items():
            if key in all_groups:
                for pkg,pkg_opt in item["packagelist"].items():
                    # print(all_groups[key])
                    if pkg in all_groups[key]["packagelist"]:
                        continue
                    else:
                        all_groups[key]["packagelist"] = {pkg:pkg_opt}
            else:
                all_groups[key] = os_groups[key]   
    return all_groups

def get_os_groups(os_arch_ver,override=False):
    metas = load_file('./os_urls.json')
    for os_name,os_arch,os_ver in os_arch_ver:
        all_groups = None
        save_path = f"./format/group/eachOS/{os_name}_{os_arch}_{os_ver}"
        for os_k,os_url in metas[os_name].items():
            os_path,os_files =download_repo_metadata(os_url.format(arch=os_arch, ver=os_ver), "./data/", override)
            group_file = __repomd_get_group_file(os_path)
            if group_file:
                os_groups, os_cate, os_env, os_langp = get_groups_info(os.path.join(os_path, group_file).replace('\\', '/'))
                save_groups(os_groups,save_path,os_k)
                all_groups = merge_groups(all_groups,os_groups)
        save_groups(all_groups,save_path,"merge")


if __name__=="__main__":
    os_versions = [
        # ("fedora", "x86_64", "38"),
        # ('fedora', 'aarch64', '38'),
        # ('centos', 'x86_64', '7'),
        ('anolis', 'x86_64', '8.8'),
        ('openCloudOS', 'x86_64', '8'),
    ]
    get_os_groups(os_versions,False)
    pass