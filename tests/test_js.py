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
    # js_analyze.get_all_cdn(src, dest, start)
    js_analyze.get_all_https(src, dest, 501)
    js_analyze.get_trans(src, dest, start)
    js_analyze.get_eval_docwrite(src, dest, start)
    # reli_analyzer = js_analyze.JsReliabilityAnalyzer()
    # reli_analyzer.analyze(all_js_src="./result/loading/xssed_js/all_js.json",js_score_src="./result/loading/xssed_js/js_score.json", dest="./result/loading/analyze/xssed_js_reliability.json")

def test_get_dependence():
    info = {
        "rank": 1,
        "has_cycle": False,
        "weights": {}
    }
    driver = chrome_driver.get_driver()
    har=js_util.get_har_log(driver, "baidu.com")
    initiators=js_util.get_initiators(har)
    for item_ in initiators:
        for url in item_:
            if not url.endswith(".js"):
                root_url = url
                break
    root_node = js_util.Node(root_url)
    edges = js_util.get_edges(initiators)
    visited = [False] * len(edges)
    has_cycle = False
    node_set = set([root_url])

    js_util.build_tree(root_node, edges, visited, node_set)
    weights = js_util.get_node_weight(root_node)
    weights = dict(sorted(weights.items(), key=lambda x: x[1], reverse=True))
    info["has_cycle"] = has_cycle
    info["weights"] = weights

    return info

if __name__ == "__main__":
    # driver = chrome_driver.get_driver("../resources/chromedriver")
    # test_get_resources(driver, "baidu.com")
    # har = js_util.get_har_log(driver, "baidu.com")
    # initiators = js_util.get_initiators(har)
    # degree_dict = js_util.get_js_degree(har)
    # print(initiators[10])
    test_get_js(start = 1, end = 20000, src="./data/domains/global_top2w/formated_website_rank.json", dest="./result/js/global_2w/")
    # test_get_xssed()
    # test_get_js_relia(
    #     src="./result/js/china_1k/all_js.json",
    #     dest="./result/js/china_1k/analyze/",
    #     start=1,
    # )
    # print(test_get_dependence())
