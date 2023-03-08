#coding: utf-8
from tqdm import tqdm
import json
import os

from depen_analyze.utils import base_util, data_reader
from depen_analyze.constant import count, path

def get_soa_data(src:str = path.SRC_PATH, dest: str = path.DEST_SOA_PATH):
    if not os.path.exists(dest):
        os.makedirs(dest)

    rank_data = data_reader.load_data(src)

    all_soa = {}
    with tqdm(total = count.DOMAIN_CNT) as pbar:
        pbar.set_description("get soa")
        for rank, domain in rank_data.items():
            pbar.update(1)
            soa = base_util.get_soa(domain)
            if soa:
                all_soa[domain] = soa
    
    filename = "{path}soa.json".format(path = dest)
    with open(filename, "w") as f:
        json.dump(all_soa, f, indent=2)