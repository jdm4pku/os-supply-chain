import os,sys
print(os.getcwd())
sys.path.append(os.getcwd())
import solv
import random
import numpy as np
import networkx as nx
from tqdm import tqdm
from itertools import repeat
from solv import XSolvable, Pool
from typing import Set,Tuple
from utils.json import load_file
from utils.xml import XMLParser
from utils.logger import get_logger
from download_file.download_repomd import download_repo_metadata
from dep.repo import Repo
from dep.repo import load_stub


logger = get_logger(__name__)

def setup_pool(arch, repos=()):
    pool = solv.Pool()
    pool.setarch(arch)
    pool.set_loadcallback(load_stub)
    for repo in repos:
        repo.baseurl = repo.baseurl.format(arch=arch)
    for repo in repos:
        assert repo.load(pool)
        if "override" in repo.name:
            repo.handle.priority = 99
    addedprovides = pool.addfileprovides_queue()
    if addedprovides:
        for repo in repos:
            repo.updateaddedprovides(addedprovides)
    pool.createwhatprovides()
    return pool



def find_direct_deps(pool: Pool, pkg: XSolvable) -> Tuple[Set[XSolvable], Set[str]]:
    unsatisfied = set()
    deps = set()
    for dep in pkg.lookup_deparray(solv.SOLVABLE_REQUIRES):
        _provides_pkgs = pool.whatprovides(dep)
        if len(_provides_pkgs) == 0:
            logger.info("No package provides %s required by %s", dep, pkg)
            unsatisfied.add(dep)
        else:
            deps.add(_provides_pkgs.pop())
    return deps, unsatisfied


def get_os_dep(os_arch_ver,override=False):
    metas = load_file('./os_urls.json')
    for os_name,os_arch,os_ver in os_arch_ver:
        _distro_name = f"{os_name}_{os_arch}_{os_ver}"
        repo_objs = []
        for os_k,os_url in metas[os_name].items():
            os_path,os_files = download_repo_metadata(os_url.format(arch=os_arch, ver=os_ver), "./data/", override)
            _repo = Repo(os_k,os_path)
            repo_objs.append(_repo)
        pool = setup_pool(os_arch,repo_objs)
        dg = nx.DiGraph()
        unsatisfied = set()
        for pkg in tqdm(pool.solvables):
            dg.add_node(pkg)
            _deps, _uns = find_direct_deps(pool, pkg)
            if len(_deps) == 0:
                continue
            dg.add_edges_from(zip(repeat(pkg), _deps))
            unsatisfied.update(_uns)
        print(f"{_distro_name}: Number of unsatisfied dependencies: {len(unsatisfied)}, {len(unsatisfied) / dg.number_of_edges() * 100:.2f}%, {[str(x) for x in random.sample(list(unsatisfied), 3 if len(unsatisfied) > 3 else len(unsatisfied))]}")
        print(f"{_distro_name}: Edges: {dg.number_of_edges()}, Nodes: {dg.number_of_nodes()}")
        # describe the distribution of in-degree
        _in_degrees = np.array([dg.in_degree(n) for n in dg.nodes])
        print(f"{_distro_name}: In-degree: mean: {np.mean(_in_degrees):.1f} 25%: {np.percentile(_in_degrees, 25)}, 50%: {np.percentile(_in_degrees, 50)}, 75%: {np.percentile(_in_degrees, 75)}, 100%: {np.percentile(_in_degrees, 100)} std: {np.std(_in_degrees):.1f}")
        # describe the distribution of out-degree
        _out_degrees = np.array([dg.out_degree(n) for n in dg.nodes])
        print(f"{_distro_name}: Out-degree: mean: {np.mean(_out_degrees):.1f} 25%: {np.percentile(_out_degrees, 25)}, 50%: {np.percentile(_out_degrees, 50)}, 75%: {np.percentile(_out_degrees, 75)}, 100%: {np.percentile(_out_degrees, 100)} std: {np.std(_out_degrees):.1f}")
        nx.write_graphml(dg, f"./out_data/{_distro_name}.graphml")
        print(f"{_distro_name}: Written to {os.path.abspath(f'{_distro_name}.graphml')}")
        


            





if __name__=="__main__":
    os_versions = [
        ("fedora", "x86_64", "38"),
        # ('fedora', 'aarch64', '38'),
        # ('centos', 'x86_64', '7'),
    ]
    get_os_dep(os_versions,False)
    pass