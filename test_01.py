"""登陆模块"""
import json
import random
import time
import pytest
import requests
import logging

from Login import users

logging.basicConfig(level=logging.INFO)
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko)"}


class VisitStat:
    __stat_param = {"platform": "douban"}
    __login_start_time = 0
    __login_end_time = 0

    @staticmethod
    def __random_string(string_length=15):
        letters = 'zyxwvutsrqponmlkjihgfedcba123456789'
        return ''.join(random.sample(letters, string_length))

    @staticmethod
    def __visit_stat(request_param):
        url = "https://www.douban.com/stat.html"
        response = requests.get(url, headers=headers, data=request_param)
        logging.info("visit_stat,param: %s", request_param)
        return response

    def visit_login_start(self):
        param = self.__stat_param.copy()
        param["action"] = "login_start"
        self.__login_start_time = int(time.time()*1000)
        param["login_start_time"] = str(self.__login_start_time)
        param["login_browser"] = '{"browser":"chrome","ver":"81.0.4044.138"}'
        param["callback"] = "jsonp_" + self.__random_string()

        return self.__visit_stat(param)

    def visit_login_click(self):
        param = self.__stat_param.copy()
        param["action"] = "login_click"
        param["login_click_time"] = str(time.time() * 1000)
        param["callback"] = "jsonp_" + self.__random_string()
        return self.__visit_stat(param)

    def visit_login_error(self, message):
        param = self.__stat_param.copy()
        param["login_error"] = message
        param["callback"] = "jsonp_" + self.__random_string()
        return self.__visit_stat(param)

    def visit_login_success(self):
        param = self.__stat_param.copy()
        param["action"] = "login_success"
        param["callback"] = "jsonp_" + self.__random_string()
        return self.__visit_stat(param)

    def visit_login_success_duration(self):
        param = self.__stat_param.copy()
        self.__login_end_time = int(time.time()* 1000)
        param["login_end_time"] = str(self.__login_end_time)
        param["login_success_duration"] = str(self.__login_end_time - self.__login_start_time)
        param["callback"] = "jsonp_" + self.__random_string()
        return self.__visit_stat(param)


def visit_passport_login():
    url = "https://accounts.douban.com/passport/login"
    response = requests.get(url, headers=headers)
    logging.info("visit_passport_login,cookie: %s", response.cookies)
    return response


def visit_login_basic(request_param, cookies):
    url = "https://accounts.douban.com/j/mobile/login/basic"
    response = requests.post(url, headers=headers, data=request_param, cookies=cookies)
    logging.info("visit_passport_login,content: %s", response.content.decode('utf-8'))
    return response


@pytest.fixture()
def error_account():
    login_basic_param = {'name': users.accounts["error_account"]["name"],
                         'password': users.accounts["error_account"]["password"],
                         'remember': 'false', 'ck': '', 'ticket': ''}
    return login_basic_param

@pytest.fixture()
def right_account():
    login_basic_param = {'name': users.accounts["right_account"]["name"],
                         'password': users.accounts["right_account"]["password"],
                         'remember': 'false', 'ck': '', 'ticket': ''}
    return login_basic_param


def test_check_arg_error(error_account):
    """缺少页面访问cookie参数，返回参数错误"""
    # 模拟请求登陆
    login_basic = visit_login_basic(error_account, {})
    assert login_basic.status_code == 200
    # 验证错误code
    content = json.loads(login_basic.content)
    assert content["message"] == "parameter_missing"


def test_check_login_error(error_account):
    """用户名、密码错误时，提示相关错误"""
    visit_stat = VisitStat()

    # 模拟第一次url访问，获取cookie
    login = visit_passport_login()
    assert login.status_code == 200
    # 模拟开始登陆 stat
    assert visit_stat.visit_login_start().status_code == 200
    # 模拟点击按钮事件 stat
    assert visit_stat.visit_login_click().status_code == 200
    # 模拟请求登陆
    login_basic = visit_login_basic(error_account, login.cookies)
    assert login_basic.status_code == 200
    # 验证错误code
    content = json.loads(login_basic.content)
    assert content["message"] == "unmatch_name_password"
    # 模拟请求失败 stat
    assert visit_stat.visit_login_error(content["message"]).status_code == 200


def test_check_login_right(right_account):
    """正常用户名登陆成功"""
    visit_stat = VisitStat()

    # 模拟第一次url访问，获取cookie
    login = visit_passport_login()
    assert login.status_code == 200
    # 模拟开始登陆 stat
    assert visit_stat.visit_login_start().status_code == 200
    # 模拟点击按钮事件 stat
    assert visit_stat.visit_login_click().status_code == 200
    # 模拟请求登陆
    login_basic = visit_login_basic(right_account, login.cookies)
    assert login_basic.status_code == 200
    # 验证错误code
    content = json.loads(login_basic.content)
    assert content["message"] == "success"
    # 模拟登陆成功 stat
    assert visit_stat.visit_login_success().status_code == 200
    # 模拟登陆时长 stat
    assert visit_stat.visit_login_success_duration().status_code == 200
