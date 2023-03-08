#coding: utf-8#coding: utf-8
import dns.resolver
import subprocess
import tldextract
import platform
import signal
import whois
import time
import json
import re
import os

from depen_analyze.constant import count

'''本文件基础数据获取函数，包括：
 - 提取sld
 - 获取soa
 - 判断soa是否在san中
 - 处理过的whois查询
 - shell命令执行
'''

def extract_sld(url):
    '''提取url的sld'''
    try:
        ext = tldextract.extract(url)
        sld = ext.registered_domain
    except:
        print("url{0}提取sld失败".format(sld))
        sld = ""
    finally:
        return sld

def get_soa(domain):
    '''提取域名domain的soa信息'''
    try:
        answer = dns.resolver.resolve(domain, "SOA")
        rname = str(answer[0].rname)
        mname = str(answer[0].mname)
        return [rname, mname]
    except:
        # print("domain {0} 获取SOA失败".format(domain))
        return []

def is_sld_in_san(sld, san_list):
    '''判断某个sld是否在san列表中'''
    regrex = ".*" + sld
    for san in san_list:
        if re.match(regrex, san):
            return True
    return False

def whois_query(url):
    '''返回url的whois信息'''
    try:
        w = whois.whois(url)
        if "org" in w:
            org = w["org"].upper()
        elif "organization" in w:
            org = w["organization"].upper()
        elif "registrant_name" in w:
            org = w["registrant_name"].upper()
        elif "registrant_organization" in w:
            org = w["registrant_organization"].upper()
        elif "registrant_org" in w:
            org = w["registrant_org"].upper()
        elif "tech_org" in w:
            org = w["tech_org"].upper()
        elif "PRIVACY" in org or "REDACTED" in org:
            org = ""
        else:
            org = ""
    except:
        return ""

def execute(cmd, timeout=1000, cwd=None):
    '''执行os命令,返回是否执行成功和执行结果'''

    is_linux = platform.system() == "Linux"

    if not cwd:
        cwd = os.getcwd()
    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        bufsize=32768,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        preexec_fn=os.setsid if is_linux else None,
    )

    t_beginning = time.time()

    # cycle times
    time_gap = 0.01

    str_std_output = ""
    while True:

        str_out = str(process.stdout.read().decode())

        str_std_output = str_std_output + str_out

        if process.poll() is not None:
            break
        seconds_passed = time.time() - t_beginning

        if timeout and seconds_passed > timeout:

            if is_linux:
                os.kill(process.pid, signal.SIGTERM)
            else:
                process.terminate()
            return False, process.stdout.readlines()
        time.sleep(time_gap)
    # str_std_output = str_std_output.strip()
    # print(str_std_output)
    # std_output_lines_last = []
    # std_output_lines = str_std_output.split("\n")
    # for i in std_output_lines:
    #     std_output_lines_last.append(i)

    if process.returncode != 0 or "Traceback" in str_std_output:
        return False, str_std_output

    return True, str_std_output

def combine_results(src, dest, total = count.DOMAIN_CNT, step_size = count.STEP_SIZE):
    '''将分批存储的数据整合成单独的文件'''
    start_index = 1
    end_index = total//step_size
    combined_result = {}
    for i in range(start_index, end_index + 1):
        filename = "{src_path}top_{rank}.json".format(src_path = src, rank = i*step_size)
        try:
            with open(filename, "r") as f:
                result = json.load(f)
        except:
            result = {}
        for k,v in result.items():
            combined_result[k] = v
    with open(dest, "w") as f:
        json.dump(combined_result, f, indent = 2)

def get_ip(url):
    '''获取url对应的ip地址列表'''
    ext = tldextract.extract(url)
    hostname = ext.fqdn
    try:
        answer = dns.resolver.resolve(hostname, "A")
        return [str(ip) for ip in answer]
    except:
        return []
    
def notify(content: str) -> None:
    os.system(
        'osascript -e \'display notification "{content}" with title "第三方测量"\''.format(content=content)
    )
