# coding: utf-8
from depen_analyze.utils import js_util, chrome_driver, private_analyzer
from depen_analyze.get_data import js_data
from depen_analyze.analyze import js_analyze

import requests


def test_js_data_format(domain):
    priv_analyzer = private_analyzer.PrivateAnalyzer()


def print_initiators(driver, domain):
    driver = chrome_driver.get_driver("../resources/chromedriver")
    har = js_util.get_har_log(driver, "baidu.com")
    initiators = js_util.get_initiators(har)
    print(initiators)


def test_get_resources(driver, domain):
    print(js_util.get_linked_js(driver, domain))


def test_get_js(src, dest, start, end):
    js_data.get_js_data(src, dest, start=start, end=end)


def test_get_xssed():
    resp = requests.get("http://www.xssed.com/archive/page=1/")
    domains = js_util.get_xssed_domains(resp.text)
    print(domains)


def test_get_js_relia(src, dest, start):
    # js_analyze.get_all_ns(src, dest, start)
    js_analyze.get_all_cdn(src, dest, start)
    js_analyze.get_all_https(src, dest, start)
    js_analyze.get_trans(src, dest, start)
    js_analyze.get_eval_docwrite(src, dest, start)
    # reli_analyzer = js_analyze.JsReliabilityAnalyzer()
    # reli_analyzer.analyze(all_js_src="./result/loading/xssed_js/all_js.json",js_score_src="./result/loading/xssed_js/js_score.json", dest="./result/loading/analyze/xssed_js_reliability.json")


if __name__ == "__main__":
    # driver = chrome_driver.get_driver("../resources/chromedriver")
    # test_get_resources(driver, "baidu.com")
    # har = js_util.get_har_log(driver, "baidu.com")
    # initiators = js_util.get_initiators(har)
    # degree_dict = js_util.get_js_degree(har)
    # print(initiators[10])
    # test_get_js(start = 901, end = 20000, src="./data/domain_rank.json", dest="./result/js/china_2w/")
    # test_get_xssed()
    test_get_js_relia(
        src="./result/js/malicious/all_js.json",
        dest="./result/js/malicious/analyze/",
        start=1,
    )
