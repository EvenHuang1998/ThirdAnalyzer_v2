# coding: utf-8
from collections import defaultdict
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse
from time import sleep
import jsbeautifier
import tldextract
import requests
import difflib
import json
import re

from depen_analyze.utils import ns_util, ca_util
from depen_analyze.constant import key

def get_linked_js(driver, domain):
    '''获取访问domain的过程中请求的所有JS脚本'''
    try:
        js_urls = []
        # url = "http://www." + domain
        url = "http://"+domain
        driver.get(url)
        # js_entries = driver.execute_script(
        #     "return window.performance.getEntriesByType('resource').filter(entry=>entry.name.substring(entry.name.length-2,entry.name.length)=='js');"
        # )
        resources = driver.execute_script("return window.performance.getEntriesByType('resource')")
        for entry in resources:
            parsed_url = urlparse(entry["name"])
            full_url = parsed_url.scheme+"://"+parsed_url.netloc+parsed_url.path
            if full_url.endswith(".js"):
                js_urls.append(full_url)
        return "success", js_urls
    except:
        return "fail", []

def get_all_resources(driver, domain):
    '''获取访问domain时请求的所有资源'''
    resources = []
    try:
        url = "http://www." + domain
        driver.get(url)
        #sleep(2)
        cmd = "var performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {}; var network = performance.getEntries() || {}; return network;"
        result = driver.execute_script(cmd)
        for item in result:
            if "name" in item:
                resources.append(item["name"])
    except:
        pass
    finally:
        return resources


def get_har_log(driver, domain):
    '''获取访问domain时形成的har文件'''
    try:
        url = "http://www." + domain
        driver.get(url)
        sleep(2)
        har_log = driver.get_log("performance")
        return har_log
    except:
        return []

def get_initiators(har_log):
    '''从har文件中分析得出initiator列表的信息'''
    '''输出结果是一个列表，'''
    initiators = list()
    for ini_item in har_log:
        try:
            json_obj = json.loads(ini_item["message"])
        except:
            continue
        if "initiator" in json_obj["message"]["params"] and json_obj["message"]["params"]["initiator"]["type"] != "other":
            ini_list = []
            target_url = json_obj["message"]["params"]["request"]["url"]
            if not "stack" in json_obj["message"]["params"]["initiator"]:
                ini_list.append(json_obj["message"]["params"]["initiator"]["url"])
                ini_list.append(target_url)
                if not json_obj["message"]["params"]["initiator"]["url"].endswith(".js") and not target_url.endswith(".js"):
                    continue
                if len(ini_list)!=1:
                    initiators.append(ini_list)
            else:
                for frame in json_obj["message"]["params"]["initiator"]["stack"]["callFrames"]:
                    if frame["functionName"] != "":
                        ini_list.append(frame["url"])
                if len(ini_list)!=1:
                    initiators.append(list(set(ini_list)))

    return initiators

'''
下面的函数为获取js主机可靠度的工具函数
'''
def get_js_degree(har_log):
    '''从har文件中分析得出每个js的度信息'''
    degree_dict = defaultdict(int)
    initiators = get_initiators(har_log)

    for item in initiators:
        if "stack" in item and "callFrames" in item["stack"]:
            for url_item in item["stack"]["callFrames"]:
                degree_dict[url_item["url"]] += 1
    return degree_dict

def get_js_ns(priv_analyzer, js_url):
    private, third = [], []

    ext = tldextract.extract(js_url)
    domain = ext.registered_domain
    ns_urls = ns_util.get_ns(domain)
    ns_entities = ns_util.divide_ns_entity(ns_urls)
    for entity in ns_entities:
        if priv_analyzer.is_other_private(domain, entity):
            private.append(entity)
        else:
            third.append(entity)

    # entity_size = len(private) + len(third)
    # if entity_size == 0:
    #     return 0
    # return (entity_size - 1) / entity_size
    return private, third

def get_js_cdn(obtainer, extractor, js_url):
    cdns = []
    ext = tldextract.extract(js_url)
    domain = ext.registered_domain
    urls = obtainer.get_urls(domain)
    for link in urls:
        cdns += extractor.get_cdns(link)

    cdns = list(set(cdns))
    # cdn_size = len(cdns)
    # return cdn_size / (cdn_size+1)
    return cdns

def is_js_support_https(js_url):
    return 1 if js_url.startswith("https://") else 0

def is_support_ocsp(js_url):
    ext = tldextract.extract(js_url)
    hostname = ext.fqdn
    return 1 if ca_util.support_ocsp_staping(hostname) else 0

'''
下面的函数为获取js传输可靠度的工具函数
'''
def get_x_xss_protection(resp):
    headers = resp.headers
    key = "X-XSS-Protection"
    if not key in headers or headers[key] == 0:
        return False
    else:
        return True

def get_content_security_policy(resp):
    headers = resp.headers
    key = "Content-Security-Policy"
    return False if not key in headers else True

def get_x_content_type(resp):
    headers = resp.headers
    key = "X-Content-Type-Options"
    return False if not key in headers else True

'''
下面的函数为检查JS实现可靠度的工具函数
'''
def get_local_storage_score(resp):
    encrypted_js = resp.text
    recoverd_js = jsbeautifier.beautify(encrypted_js)
    reg_exp = "LocalStorage\((.*?)\)"

def get_outdated_js_api(resp):
    encrypted_js = resp.text
    recovered_js = jsbeautifier.beautify(encrypted_js)
    # eval_reg_exp = "eval\((.*?)\)"
    # document_write_reg_exp = "document.write\((.*?)\)"
    pattern1 = re.compile(r'eval\((.*?)\)')
    pattern2 = re.compile(r'document.write\((.*?)\)')
    matches1 = re.findall(pattern1, recovered_js)
    matches2 = re.findall(pattern2, recovered_js)
    return matches1, matches2

'''
下面的函数为检查JS重要性的工具函数
'''
def get_compare_html(driver, url, js_url):
    "输出原始html以及block js_url之后的html"
    driver.get(url, timeout=5)
    html_origin = driver.page_source

    driver.execute_cdp_cmd(
        'Network.setBlockedURLs',
        {"urls": [js_url]}
    )
    driver.get(url)
    # dom = driver.execute_script("return document.documentElement.outerHTML")
    html_blocked = driver.page_source
    return html_origin, html_blocked

def get_html_diff_cnt(html1, html2):
    d = difflib.HtmlDiff()
    diff=d.make_file(html1.splitlines(),html2.splitlines())
    diff_chg_count = len(re.findall(r'<span class="diff_chg">', diff))
    diff_add_count = len(re.findall(r'<span class="diff_add">', diff))
    diff_sub_count = len(re.findall(r'<span class="diff_sub">', diff))
    return diff_chg_count, diff_add_count, diff_sub_count

def get_js_dom_change_score(driver, url, js_url):
    html_origin, html_blcked = get_compare_html(driver, url, js_url)
    diff_chg_count, diff_add_count, diff_sub_count = get_html_diff_cnt(html_origin, html_blcked)
    return (diff_chg_count + diff_add_count+ diff_sub_count)/(diff_chg_count + diff_add_count+ diff_sub_count+1)

'''下面为获取各类域名的代码'''
'''xss domain'''
def get_xssed_domains(resp):
    "从xssed domains中的某一页获取域名信息，以列表的形式返回"
    soup = bs(resp, "html.parser")
    table = soup.find_all(attrs={
        "width":"835",
        "border":"0",
        "align":"center",
        "cellpadding":"0",
        "cellspacing":"0"})[1]
    # domains = [row.find_all("th")[2].text for row in table.find_all("tr")]
    unfixed_domains = []

    try:
        for row in table.find_all("tr"):
            if row.find_all("img"):
                if len(row.find_all("img")) == 2 and row.find_all("img")[1].get("src").endswith("unfixed.gif"):
                    unfixed_domains.append(row.find_all("th")[2].text)
                elif row.find_all("img")[0].get("src").endswith("unfixed.gif"):
                    unfixed_domains.append(row.find_all("th")[2].text)
    except:
        pass

    return unfixed_domains

'''bank domains'''
def get_bank_domain(bank_name):
    params = {
        "api_key": key.SERP_API_KEY,
        "q": bank_name,
        "gl": 'cn',
        'hl': 'zh-cn'
    }
    try:
        api_result = requests.get("https://api.scaleserp.com/search", params, timeout=5)
        return api_result.json()["organic_results"][0]["displayed_link"]
    except:
        return ""
