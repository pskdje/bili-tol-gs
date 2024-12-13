# 开始直播和结束直播

import requests
import argparse

head={
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.6",
    "DNT": "1",
    "Origin": "https://live.bilibili.com/",
    "Referer": "https://live.bilibili.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
}
cookie={}

def get_cookie(path):
    c={}
    with open(path)as f:
        d=f.read(16384)
    for i in d.split(";"):
        k,v=i.strip().split("=",1)
        c[k]=v
    return c

def start(roomid,area,csrf):
    body={
        "room_id": roomid,
        "area_v2": area,
        "platform": "web_link",
        "csrf_token": csrf,
        "csrf": csrf,
        "visit_id": "",
    }
    r=requests.post("https://api.live.bilibili.com/room/v1/Room/startLive",headers=head,cookies=cookie,data=body)
    return r.json()

def stop(roomid,csrf):
    body={
        "room_id": roomid,
        "platform": "web_link",
        "csrf_token": csrf,
        "csrf": csrf,
        "vist_id": "",
    }
    r=requests.post("https://api.live.bilibili.com/room/v1/Room/stopLive",headers=head,cookies=cookie,data=body)
    return r.json()

def end_data(live_key):
    r=requests.get("https://api.live.bilibili.com/xlive/app-blink/v1/live/StopLiveData",params={"live_key":live_key},headers=head,cookies=cookie)
    return r.json()

def main():
    global cookie
    p=argparse.ArgumentParser(description="开始和结束直播")
    p.add_argument("cookie",help="Cookie文件")
    p.add_argument("area",help="分区ID",type=int)
    p.add_argument("roomid",help="房间号",type=int)
    a=p.parse_args()
    roomid=a.roomid
    print("分区ID:",a.area,",房间号:",roomid)
    c=get_cookie(a.cookie)
    cookie={
        "SESSDATA":c['SESSDATA'],
        "bili_jct":c['bili_jct'],
        "bili_ticket":c['bili_ticket'],
        "buvid3":c['buvid3'],
        "buvid4":c['buvid4'],
        "b_nut":c['b_nut'],
    }
    sa=start(roomid,a.area,c["bili_jct"])
    if sa["code"]!=0:
        print(sa)
        return
    liveid=sa["data"]["live_key"]
    print("推流地址:",sa["data"]["rtmp"]["addr"])
    print("推流参数:",sa["data"]["rtmp"]["code"])
    input("按下回车继续执行关闭部分")
    so=stop(roomid,c["bili_jct"])
    if so["code"]!=0:
        print(so)
        return
    print("状态是否改变:",so["data"]["change"])
    sd=end_data(liveid)
    if sd["code"]!=0:
        print(sd)
        return
    print(sd["data"])

if __name__=="__main__":
    main()
