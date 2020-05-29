from datetime import datetime
from py.xml import html
import pytest


def pytest_configure(config):
    # 添加网站地址与项目名称
    config._metadata["项目名称"] = "基于Pytest豆瓣网站自动化测试"
    config._metadata['网站地址'] = 'https://accounts.douban.com/'
    config._metadata.pop("Platform")
    config._metadata.pop("Plugins")
    config._metadata.pop("Packages")


@pytest.hookimpl(optionalhook=True)
def pytest_html_report_title(report):
    report.title = "豆瓣网自动化测试示例（基于Pytest）"


@pytest.hookimpl(optionalhook=True)
def pytest_html_results_summary(prefix, summary, postfix):
    prefix.extend([html.p("测试人: 姜子轩")])


@pytest.hookimpl(optionalhook=True)
def pytest_html_results_table_header(cells):
    cells.insert(2, html.th('模块'))
    cells.insert(3, html.th('描述'))
    cells.insert(4, html.th('时间', class_='sortable time', col='time'))
    cells.pop()


@pytest.hookimpl(optionalhook=True)
def pytest_html_results_table_row(report, cells):
    cells.insert(2, html.td(report.module))
    cells.insert(3, html.td(report.description))
    cells.insert(4, html.td(datetime.utcnow(), class_='col-time'))
    cells.pop()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    report.description = str(item.function.__doc__)
    report.module = str(item.module.__doc__)
