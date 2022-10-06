import json
import traceback
from datetime import date

import requests
import time
import random

# -----------------------配置区-----------------------
# 账号


USER = ""
# 密码
PASS = ""


# -----------------------配置区-----------------------


class Upyun:
    def __init__(self):
        self.task_json = None
        self.cookies = None
        self.ip = self.camouflage_ip()
        self.sign_href = "https://console.upyun.com/activity/signin"
        self.task_href = "https://console.upyun.com/activity/tasks"
        self.login_href = "https://console.upyun.com/accounts/signin/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36",
            "origin": "https://www.upyun.com",
            "referer": "https://www.upyun.com/onePiece",
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json; charset=utf-8",
            "Client-Ip": self.ip,
            "X-Forwarded-For": self.ip,
            "x-forwarded-for": self.ip,
            "Remote_Addr": self.ip,
            "x-remote-IP": self.ip,
            "x-remote-ip": self.ip,
            "x-client-ip": self.ip,
            "x-client-IP": self.ip,
            "X-Real-IP": self.ip,
            "client-IP": self.ip,
            "x-originating-IP": self.ip,
            "x-remote-addr": self.ip,
        }

    # 登陆 返回cookie
    def login(self):
        res = None
        success = False
        attempts = 0
        submit = {'username': USER, 'password': PASS}
        while not success and attempts < 10:
            try:
                res = requests.post(self.login_href, data=json.dumps(submit), headers=self.headers)
                success = True
                break
            except:
                # traceback.print_exc()
                time.sleep(1)
                attempts += 1
                print("登陆重试中 第" + str(attempts) + "次")
                if attempts > 10:
                    print("登陆重试次数超过了10次")
        if not success:
            return
        res_txt = res.content.decode()
        res_json = None
        try:
            res_json = json.loads(res_txt)
        except:
            print("登陆错误")
        if "msg" in res_json and res_json['msg']['messages'][0] != "登录成功":
            print("账号密码错误")
            return
        self.cookies = res.cookies

    # 返回任务json
    def get_task(self):
        res = None
        success = False
        attempts = 0
        if self.cookies is None:
            print("未登录，不可获取任务")
            return
        while not success and attempts < 10:
            try:
                res = requests.get(self.task_href, headers=self.headers, cookies=self.cookies)
                success = True
                break
            except:
                # traceback.print_exc()
                time.sleep(1)
                attempts += 1
                print("获取任务重试中 第" + str(attempts) + "次")
                if attempts > 10:
                    print("获取任务次数超过了10次")
        try:
            self.task_json = json.loads(res.content.decode())
        except:
            print("获取任务错误")
            self.task_json = None

    def sign(self):
        res = None
        success = False
        attempts = 0
        if self.cookies is None:
            print("未登录，不可签到")
            return
        while not success and attempts < 10:
            try:
                # 检查今日是否签到
                tomorrow = date.today()
                resi = requests.get(self.sign_href, headers=self.headers, cookies=self.cookies)
                resi_json = json.loads(resi.content.decode())
                if not resi_json['result']:
                    print("获取签到状态失败")
                    return
                flag = False
                for i in resi_json['items']:
                    if i['date'] == str(tomorrow) and i['signin'] is True:
                        flag = True
                        break
                if flag:
                    print("今日已签到,不可再次签到")
                    return
                res = requests.post(self.sign_href, headers=self.headers, cookies=self.cookies)
                success = True
                break
            except:
                # traceback.print_exc()
                time.sleep(1)
                attempts += 1
                print("签到重试中 第" + str(attempts) + "次")
                if attempts > 10:
                    print("签到次数超过了10次")
        try:
            ls = json.loads(res.content.decode())
            if ls['result'] is True:
                print("签到成功")
            else:
                print("签到失败")
        except:
            print("签到错误")

    def task(self):
        res = None
        success1 = False
        attempts1 = 0
        if self.cookies is None:
            print("未登录，完成每日任务")
            return
        self.get_task()
        if self.task_json is None:
            return
        # unlimited为每日任务
        token = "7c4ee7db-d67e-4912-b72b-9e2439352716"  # 根据逆向来看，token定死了,1.js
        # 15930行，2022年10月6日10点13分。官网4.ba3f9c8f847d5fe9d520.js 15610行
        # 限定任务有些很苛刻，消费类型的任务都会失败，免费任务才会成功，如果限定任务你没做完免费任务可以把unlimited替换为limited执行一次，再还原即可
        for i in self.task_json['unlimited']:  # limited unlimited
            while not success1 and attempts1 < 10:
                try:
                    submit = {"event_id": i['event_id'], "accountName": USER}
                    headers = self.headers
                    headers['x-token'] = token
                    res = requests.post(self.task_href, headers=self.headers, cookies=self.cookies,
                                        data=json.dumps(submit))
                    success1 = True
                    break
                except:
                    # traceback.print_exc()
                    time.sleep(1)
                    attempts1 += 1
                    print(i['description'] + " 任务重试中 第" + str(attempts1) + "次")
                    if attempts1 > 10:
                        # 超过进行下一个任务
                        print(i['description'] + " 重试次数超过了10次")
            task = None
            try:
                task = json.loads(res.content.decode())
            except:
                print(i['description'] + " 任务失败")
                continue
            if success1 and 'result' in task and task['result']:
                print(i['description'] + " 任务成功")
            else:
                print(i['description'] + " 任务失败,失败原因 " + task['message'])
            success1 = False
            attempts1 = 0

    def camouflage_ip(self):  # 暂时只能伪装电信ip,伪装其他地区ip更改106.84.
        return "106.84." + str(random.randint(146, 254)) + "." + str(random.randint(1, 254))


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    # 可用方法：.login()   .sign()   .task()    其余不可使用，为内部方法
    up = Upyun()
    up.login()
    up.sign()
    up.task()

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
