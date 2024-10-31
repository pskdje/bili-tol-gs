#!/bin/env python
"""批量查询哔哩哔哩主播开播状态
依赖: requests
注意: 你可能需要重写 b 函数来使开播提示可在你的平台上使用。
提示: 默认可以使用 notifi.py 文件来显示通知，需要存在 start 函数。具体可查看本文件的第 47~56 行。
"""

import sys
import time
import argparse
import subprocess
import requests
from traceback import print_exc

room_status: dict = {}

def get_status_info_by_uids(uids: list|tuple)-> None|dict:
    """批量查询直播间状态"""
    try:
        r = requests.post(
            "https://api.live.bilibili.com/room/v1/Room/get_status_info_by_uids",
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML; like Gecko) Chrome/110.0.0.0 Safari/537.36 Edge/110.0.1587.66",
            },
            json={ "uids" : uids }
        )
    except requests.ConnectTimeout:
        print("\r连接超时", " "*4)
        return None
    except requests.Timeout:
        print("\r超时", " "*8)
        return None
    except requests.exceptions.ConnectionError as e:
        print("\r连接错误:", e)
        return None
    if r.status_code != 200:
        print("\nHTTP status:", r.status_code)
        print(r.text)
        return None
    try:
        return r.json()
    except requests.exceptions.JSONDecodeError as e:
        print("\n解析JSON失败:", e)
        print(r.text)
        return None

def b(d):
    """认为开播时执行本函数"""
    try:
        import notifi
        notifi.start(d)
        return
    except ModuleNotFoundError:
        pass
    except:
        print("\r执行外部通知组件时出现错误")
        print_exc()
        print("现执行默认通知组件")
    try:# Android Termux
        s = subprocess.run(
            ["termux-notification", "-t", "哔哩哔哩直播开播提醒", "-c", f"您关注的主播 {d['uname']} 开始直播 {d['title']}", "--icon", "notifications_active"],
            timeout=8)
    except subprocess.TimeoutExpired:
        print("\r通知发送超时")
    except OSError as e:
        print(e)
    else:
        if s.returncode != 0:
            print("\r通知非零退出:", s.returncode)
            print(s.args)

def c(u, o):
    d = get_status_info_by_uids(u)
    if d == None:
        print("\r无数据", " "*4)
        return 2
    if o.show_change:
        print(d)
    try:
        c = d["code"]
        if c == 65530:# 未知问题
            print("\r",end="")
            print(c, d["message"])# route_exception
            print(d)
            return 0
        if c != 0:
            print("\r似乎不成功:", c, d["message"], d["msg"])
            return 3
        if isinstance(d["data"], list):
            print("\r这些用户似乎没有直播间")
            print(d["data"])
            return 4
        for k,v in d["data"].items():
            s = v["live_status"]
            if o.show_live_status:
                print("主播", k, "开播状态", s)
            if k not in room_status:
                room_status[k] = s
                if s == 1:
                    print("\r主播", v["uname"], "正在直播:", v["title"])
            if room_status[k] == s:
                continue
            if s == 1:
                room_status[k] = 1
                print("\r主播", v["uname"], "开始直播:", v["title"])
                b(v)
            else:
                room_status[k] = s
    except KeyError as e:
        print(e)
        return 1
    return 0

def m():
    p = argparse.ArgumentParser(
        description="哔哩哔哩开播检测",
        fromfile_prefix_chars="+@"
    )
    p.add_argument("uids", help="用户UID", action="extend", nargs="+", type=int)
    p.add_argument("-l", "--show-live-status", help="显示开播状态", action="store_true")
    p.add_argument("-s", "--show-change", help="显示获取信息", action="store_true")
    n = p.parse_args()
    u = n.uids
    while True:
        if c(u, n) != 0:
            break
        if not (n.show_change or n.show_live_status):
            sys.stdout.write("\rT:" + str(int(time.time())))
            sys.stdout.flush()
        time.sleep(5)

if __name__ == "__main__":
    try:
        m()
    except KeyboardInterrupt:
        print("\n关闭")
