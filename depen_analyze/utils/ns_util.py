#coding: utf-8
from collections import defaultdict
import dns.resolver

from depen_analyze.utils import base_util

def get_ns(domain):
    '''获取domain的ns'''
    try:
        answer = dns.resolver.resolve(domain, "NS")
    except:
        answer = ""
    finally:
        return list(map(lambda item: str(item),answer))

def divide_ns_entity(ns_list):
    '''将ns列表根据提供商进行划分'''
    try:
        divider = NsDivider(ns_list)
        divider.divide()
        return divider.ns_entity
    except:
        return []

def get_ns_provider(ns_url):
    '''获取ns提供商'''
    org = base_util.whois_query(ns_url)
    if not org or org == "whois_error":
        if "awsdns" in ns_url:
            org = "AMAZON TECHNOLOGIES, INC."
        elif "dnsv" in ns_url or "dnspod" in ns_url:
            org = "DNSPOD"
        elif (
            "alidns" in ns_url
            or "taobao" in ns_url
            or "alibabadns" in ns_url
            or "aliyun" in ns_url
        ):
            org = "ALIBABA"
        elif "akam" in ns_url:
            org = "AKAMAI TECHNOLOGIES, INC."
        elif "cloudflare" in ns_url:
            org = "CLOUDFLARE"
        else:
            org = base_util.extract_sld(ns_url)
    return org

class NsDivider:
    '''将ns列表根据提供商划分为几块'''
    def __init__(self, arr_):
        self.arr = arr_
        self.parent = [i for i in range(len(arr_))]
        self.ns_entity = set()
        self.ns_entity_num = len(arr_)
        self.ns_info = defaultdict(dict)

    def __get_ns_info(self):
        for ns in self.arr:
            ns_tld = base_util.extract_sld(ns)
            self.ns_info[ns]["tld"] = ns_tld
            (
                self.ns_info[ns]["rname"],
                self.ns_info[ns]["mname"],
            ) = base_util.get_soa(ns_tld)

    def belong_to_same_entity(self, ns1, ns2):
        tld1 = self.ns_info[ns1]["tld"]
        tld2 = self.ns_info[ns2]["tld"]
        if tld1 and tld2 and tld1 == tld2:
            return True
        rname1, mname1 = self.ns_info[ns1]["rname"], self.ns_info[ns1]["mname"]
        rname2, mname2 = self.ns_info[ns2]["rname"], self.ns_info[ns2]["mname"]
        if rname1 and rname2 and rname1 == rname2:
            return True
        if mname1 and mname2 and mname1 == mname2:
            return True
        return False

    def find(self, i):
        root = i
        while root != self.parent[root]:
            root = self.parent[root]
        while i != root:
            parent_ = self.parent[i]
            self.parent[i] = root
            i = parent_
        return root

    def union(self, i, j):
        root_i, root_j = self.find(i), self.find(j)
        if self.belong_to_same_entity(self.arr[i], self.arr[j]) and root_i != root_j:
            if root_i <= root_j:
                self.parent[j] = self.parent[i]
            else:
                self.parent[i] = self.parent[j]

    def divide(self):
        n = len(self.arr)
        self.__get_ns_info()
        for i in range(n):
            for j in range(i + 1, n):
                self.union(i, j)
        for p_index in set(self.parent):
            self.ns_entity.add(self.arr[p_index])
        self.ns_entity_num = len(set(self.parent))
