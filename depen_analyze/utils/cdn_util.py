# coding: utf-8
from selenium.webdriver.common.by import By
import dns.resolver
import tldextract
import requests

from depen_analyze.utils import chrome_driver, private_analyzer, base_util
from depen_analyze.constant import path

def read_cdn_map(src = path.CDN_MAP_PATH):
    '''
        读取cdnMap
    '''
    cdn_map_dict=dict()
    with open(src, "r") as f:
        for line in f:
            line = line.strip().split(",")
            cdn, cname_list = line[0], line[1].split(' ')
            cdn_map_dict[cdn] = cname_list
    return cdn_map_dict
class InternalUrlObtainer:
    '''
        获取访问domain时可能得到的所有内部url, 使得cname的获取更加全面
    '''
    def __init__(self):
        self.driver = chrome_driver.get_driver()
        self.priv_analyer = private_analyzer.PrivateAnalyzer()

    def get_domain_url(self, domain):
        '''
            获取domain对应网页的url
        '''
        url = ""
        try:
            requests.get("http://www."+domain, timeout=5)
            url = "http://www."+domain
        except:
            pass
        try:
            requests.get("http://"+domain, timeout=5)
            url = "http://"+domain
        except:
            pass
        return url

    def get_urls(self, domain):
        domain_url = self.get_domain_url(domain)
        if not domain_url:
            return []
        link_set = set([domain_url])
        try:
            self.driver.get(domain_url)
            # sleep(5)
            for url in self.driver.find_elements(by=By.XPATH, value="//*[@href]"):
                link = url.get_attribute("href")
                if not link.startswith("javascript") and self.priv_analyer.is_other_private(domain_url, link):
                    link_set.add(link)
        except:
            pass
        return list(link_set)
    
class CdnExtractor:
    def __init__(self, cdn_map_path = path.CDN_MAP_PATH):
        self.cdn_map_dict = read_cdn_map(cdn_map_path)
    
    def recursively_get_cname(self, link):
        '''
            递归获取某个link对应的全部CNAME信息
        '''
        ext = tldextract.extract(link)
        pre_cname = ext.fqdn # TODO
        cnames = []
        while True:
            try:
                answer = dns.resolver.resolve(pre_cname, "CNAME")
                cname = str(answer[0])
                if pre_cname == cname:
                    break
                else:
                    cnames.append(cname)
                    pre_cname = cname
            except:
                break
        return cnames

    def map_cname_list_to_cdn(self, cname_list):
        '''
            根据cname列表映射得到cdn列表信息
        '''
        cdn_list = []
        for cname in cname_list:
            cname_sld = base_util.extract_sld(cname)
            for cdn, cnames in self.cdn_map_dict.items():
                if cname_sld in cnames:
                    cdn_list.append(cdn)
        return  cdn_list
    
    def get_cdns(self, link):
        cnames = self.recursively_get_cname(link)
        cdns = self.map_cname_list_to_cdn(cnames)
        return cdns