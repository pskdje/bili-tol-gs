# bilibili live

import sys
import os
import json
import pathlib
import logging
import requests
import asyncio
import websockets
import zlib

class LoggerAdapter(logging.LoggerAdapter):
    def process(self,msg,kwargs):
        try:
            websocket=kwargs["extra"]["websocket"]
        except:
            return msg,kwargs
        return f"{websocket.id} {msg}",kwargs

UA="Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0"# 用户代理常量
wslog=logging.getLogger("websockets.client")# 日志
sequence:int=0
hpst=None
fi=0

def setdata(t:int,data:str):
    global sequence
    d=str(data).encode()
    db=b""
    db+=bytes.fromhex("{:0>8X}".format(16+len(d)))# 数据包总长度
    db+=b"\0\x10"# 数据包头部长度
    db+=b"\0\x01"# 协议版本
    db+=b"\0\0\0"+bytes.fromhex("0"+str(t))# 操作码
    db+=bytes.fromhex("{:0>8X}".format(sequence))# sequence
    db+=d
    sequence+=1
    #print(">",db)
    return db

def joinroom(roomid:int,token:str):
    """加入直播间\n
需要提供正确的roomid才可正确获取信息(例:3号直播间需要输入23058而不是3)可使用 http://api.live.bilibili.com/room/v1/Room/room_init 接口获取真实信息
    """
    return setdata(7,json.dumps({"roomid":roomid,"key":token},separators=(",",":")))

def hp():# 返回需要发送的心跳包
    return setdata(2,"")

def main(roomid):
    print("直播间id:",roomid)
    try:# 获取信息流的地址
        r=requests.get("https://api.live.bilibili.com/xlive/web-room/v1/index/getDanmuInfo?id="+str(roomid),headers={"Origin":"https://live.bilibili.com","Referer":"https://live.bilibili.com/"+str(roomid),"User-Agent":UA})
    except:
        raise
    else:
        d=r.json()
        assert d["code"]==0,"code not 0"
        u=d["data"]["host_list"][0]
        asyncio.run(live(roomid,f"""ws://{u["host"]}:{u["ws_port"]}/sub""",d["data"]["token"]))# 路径需要为"/sub"才可获取信息流

def fetchmsgdata(msg:bytes):# 获取并返回解析后的普通包列表
    data=msg.split(b"\0\x10\0\0\0\0\0\x05\0\0\0\0")[1:]
    packlist=[]
    for item in data:
        if item[-4]==0:
            packlist.append(json.loads(item[:-4]))
        else:
            packlist.append(json.loads(item))
    return packlist

def fatchhpmsg(data:bytes):# 获取并返回解析后的心跳包内容(人气值)
    return int.from_bytes(data,"big")

def save(obj):
    global fi
    fpa=pathlib.Path("bili live msg data")
    if not os.path.exists(fpa):
        os.mkdir(fpa)
    with open(fpa/(str(fi)+".json"),"w",encoding="utf-8")as f:
        f.write(json.dumps(obj,ensure_ascii=False,indent="\t",sort_keys=False))
    fi+=1

async def hps(ws):# 循环发送心跳包
    while not ws.closed:
        await ws.send(hp())
        await asyncio.sleep(30)

async def live(roomid:int,url:str,token:str):
    global hpst
    async with websockets.connect(url,logger=LoggerAdapter(wslog,{"websocket":""}),user_agent_header=UA)as ws:
        await ws.send(joinroom(roomid,token))
        hpst=asyncio.create_task(hps(ws),name="循环发送心跳包")
        async for msg in ws:
            #print("<",msg)
            if msg[7]==1 and msg[11]==3:# 心跳包
                print("人气值:",fatchhpmsg(msg[-4:]))
            if msg[7]==0:# 普通包未压缩
                save(fetchmsgdata(msg))
            if msg[7]==2:# 普通包使用zlib压缩时使用zlib解压
                save(fetchmsgdata(zlib.decompress(msg[16:])))

if __name__=="__main__":
    try:
        if len(sys.argv)==2:
            roomid=int(sys.argv[1])
        else:
            roomid=23058
    except(KeyError,ValueError):
        print("args error")
        sys.exit(1)
    try:
        main(roomid)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        # 当处于调试模式时再次抛出异常
        if __debug__:
            print(e)
        else:
            raise
