#coding: utf-8
from tqdm import tqdm
import json
import os

from depen_analyze.utils import data_reader, ca_util
from depen_analyze.constant import count

def get_ca_data(src:str = "./data/domain_rank.json", dest: str = "./result/infra/ca/", step_size = count.STEP_SIZE, start = 0, end = count.DOMAIN_CNT, step_save = False):
    '''
        获取所有的ca相关基础信息,并存储为json格式
        数据格式如下：
        {
            "example.com":{
                "rank": 1,
                "san": [],
                "issuer": ""
            }
        }
    '''
    if not os.path.exists(dest):
        os.makedirs(dest)

    ctx = ca_util.ssl_ctx()
    rank_data = data_reader.load_data(src)

    all_ca = {}
    all_ca_set = {}

    all_ca_set_filename = "{path}all_ca_set.json"
    try:
        with open(all_ca_set_filename, "r") as f:
            ca_set = json.load(f)
            all_ca_set = set(ca_set["ca_set"])
    except:
        pass

    with tqdm(total = count.DOMAIN_CNT) as pbar:
        pbar.set_description("get ca data")
        for rank, domain in rank_data.items():
            pbar.update(1)
            if int(rank) < start:
                continue
            if int(rank) > end:
                break

            support_https, hostname = ca_util.is_support_https(domain)
            if not support_https:
                continue
            ca = ca_util.get_ca(ctx, hostname)
            if ca:
                all_ca[domain] = ca_util.format_ca(ca)
                all_ca[domain]["rank"] = rank
            
            
            if step_save:
                if int(rank)%step_size == 0:
                    filename = "{path}top_{rank}.json".format(path=dest, rank=rank)
                    with open(filename, "w") as f:
                        json.dump(all_ca, f, indent=2)
                    all_ca = {}
        if not step_save:
            filename = "{path}all_ca.json".format(path=dest)
            with open(filename, "w") as f:
                json.dump(all_ca, f, indent=2)
            with open(all_ca_set_filename, "w") as f:
                json.dump({
                    "all_ca": list(all_ca_set)
                }, f, indent=2)
            return all_ca
