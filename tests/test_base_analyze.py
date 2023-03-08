# coding: utf-8

from depen_analyze.analyze import base_analyze

def test_js_analyze():
    js_analyzer = base_analyze.js_analyzer()
    js_analyzer.third_js_ratio()

if __name__ == "__main__":
    test_js_analyze()