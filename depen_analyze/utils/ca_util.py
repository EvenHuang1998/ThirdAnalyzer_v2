#coding: utf-8
import requests
import certifi
import socket
import urllib3
import ssl

from depen_analyze.utils import base_util

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def https_visit(domain):
    '''获取https协议访问domain对应的url'''
    got_answer, hostname = False, ""
    www_hostname = "www," + domain
    domain_hostname = domain
    www_url = "https://" + www_hostname
    domain_url = "https://" + domain_hostname
    try:
        requests.get(www_url, timeout=5, verify=False)
        got_answer = True
        hostname = www_hostname
    except:
        pass
    if not got_answer:
        try:
            requests.get(domain_url, timeout=5, verify=False)
            got_answer = True
            hostname = domain_hostname
        except:
            pass
    return hostname

def is_support_https(domain):
    '''判断domain是否支持https'''
    hostname = https_visit(domain)
    return hostname != "", hostname

def ssl_ctx():
    '''返回ssl句柄'''
    sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
    sslctx.verify_mode = ssl.CERT_REQUIRED
    sslctx.check_hostname = False
    sslctx.load_verify_locations(certifi.where())
    return sslctx

def get_ca(context, hostname):
    '''获取域名对应hostname的ca证书信息'''
    try:
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                ca = ssock.getpeercert()
        return ca
    except:
        return None

def format_ca(ca):
    '''按照目标ca格式进行格式化'''
    formatted_ca = dict()

    issuer = ""
    if "issuer" in ca:
        for issue in ca["issuer"]:
            if issue[0][0] == "organizationName":
                issuer = issue[0][1]
                break
    formatted_ca["issuer"] = issuer

    san_list = list()
    if "subjectAltName" in ca:
        for _, san in ca["subjectAltName"]:
            san_list.append(san)
    formatted_ca["san"] = san_list

    ca_url_list = list()
    if "caIssuers" in ca:
        for ca_url in ca["caIssuers"]:
            ca_url_list.append(ca_url)
    formatted_ca["ca_url"] = ca_url_list

    return formatted_ca

def get_san(ca):
    san_list = list()
    if "subjectAltName" in ca:
        for _, san in ca["subjectAltName"]:
            san_list.append(san)
    return san_list

def support_ocsp_staping(hostname):
    '''返回ocsp stapling的结果'''
    cmd = 'echo "" | openssl s_client -connect ' + hostname + ":443 -status"
    status, ca = base_util.execute(cmd)
    return (status and "OCSP Response Status: successful" in "".join(ca))