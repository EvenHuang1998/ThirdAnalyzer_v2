#coding: utf-8
from tqdm import tqdm
import tldextract
import requests
import json
import os

from depen_analyze.utils import data_reader, js_util, private_analyzer, chrome_driver
from depen_analyze.constant import count, path, time_const

def get_js_data(src: str = path.SRC_PATH, dest = path.DEST_JS_PATH, step_size = count.STEP_SIZE, start = 0, end = count.DOMAIN_CNT):
    '''获取所有的js相关基础信息,并存储为json格式'''
    
    if not os.path.exists(dest):
        os.makedirs(dest)
    
    priv_analyzer = private_analyzer.PrivateAnalyzer()
    rank_data = data_reader.load_data(src)
    driver = chrome_driver.get_driver()
    driver.set_page_load_timeout(time_const.DRIVER_LOADING_TIME)
    all_js = {}
    with tqdm(total = len(rank_data)) as pbar:
        pbar.set_description("get js data")
        for rank, domain in rank_data.items():
            pbar.update(1)
            if int(rank) < start: 
                continue
            if int(rank) > end:
                break
            domain_js_info = {
                "rank": rank,
                "private": [],
                "third": []
            }

            status, js_urls = js_util.get_linked_js(driver, domain)
            # print(status)
            if status == "fail":
                driver = chrome_driver.get_driver()
                driver.set_page_load_timeout(time_const.DRIVER_LOADING_TIME)
            ext = tldextract.extract(domain)
            domain_name = ext.registered_domain
            for js_url in js_urls:
                if priv_analyzer.is_other_private(domain_name, js_url):
                    domain_js_info["private"].append(js_url)
                else:
                    domain_js_info["third"].append(js_url)
            all_js[domain] = domain_js_info
            if int(rank)%step_size == 0:
                filename = "{path}top_{rank}.json".format(path = dest, rank = rank)
                with open(filename, "w") as f:
                    json.dump(all_js, f, indent = 2)
                all_js = {}
 
def get_all_xssed_domains(dest = path.SRC_XSS_PATH, target_xssed_domain_size = count.XSSED_DOMAIN_SIZE):
    if not os.path.exists(dest):
        os.makedirs(dest)
    all_pages_size = 1530
    all_xssed_domains = []
    xssed_cnt = 0
    page_cnt = 1
    with tqdm(total=target_xssed_domain_size) as pbar:
        pbar.set_description("get xssed domains")
        while page_cnt <= all_pages_size and xssed_cnt < target_xssed_domain_size:
            resp = requests.get("http://www.xssed.com/archive/page={page}/".format(page=page_cnt))
            
            domains = js_util.get_xssed_domains(resp.text)
            xssed_cnt += len(domains)
            page_cnt += 1
            all_xssed_domains += domains
            pbar.update(len(domains))
    with open(dest+"xssed_domains.json", "w") as f:
        json.dump({"domains":all_xssed_domains}, f, indent=2)

def get_all_bank_domains(src=path.SRC_BANK_CHINESE_PATH, dest=path.SRC_BANK_PATH):
    if not os.path.exists(dest):
        os.makedirs(dest)
    with open(src, "r") as f:
        bank_chinese = json.load(f)
    
    all_bank_domains = {
        "bank_domains": []
    }

    with tqdm(total = len(bank_chinese["bank_chinese"])) as pbar:
        pbar.set_description("get bank domains")
        for bank_name in bank_chinese["bank_chinese"]:
            bank_domain = js_util.get_bank_domain(bank_name)
            if not bank_domain: continue
            all_bank_domains["bank_domains"].append(bank_domain)
            pbar.update(1)
    
    with open(dest+"bank_domain.json", "w") as f:
        json.dump(all_bank_domains, f, indent=2)

if __name__ == "__main__":
    get_js_data(src="./data/domains/bank_domains.json",
                dest="./result/loading/bank_js/")
