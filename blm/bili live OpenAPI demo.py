# bili live open API demo
r"""
[文档](https://open-live.bilibili.com/document/)
需要：项目id,主播身份码,开发者access_key_id,开发者access_key_seceret
项目id需要创建项目后在“项目概览>基本信息”里查看
主播身份码需要访问[幻星互动](https://play-live.bilibili.com/)在右下角“身份码”标签获取
开发者access_key_id和access_key_seceret通过申请邮件或个人资料获取，可能需要自己加密
gameid由start获得

===下面图表受到字体影响，无法做到合适===
两个key合称"key"

客户端        OpenAPI服务器         信息流服务器
  |                 |                   |
  |  发送start请求   |                   |
  |  需要key、项目id |                   |
  |  和主播身份码    |                   |
  |---------------->|-----\             | #0
  |                 |     |签名验证      |
  | 返回信息流地址和  |<---/              |
  | 验证信息         |-----获取信息------>|
  |<----------------|<-----返回信息------| #0
  |                 |                   |
  |   定期请求心跳   |                   |
  | 需要key和gameid  |                   |
  |----20秒一次----->|                   | #1
  |<-响应心跳成功信息-|                   | #1
  |                 |                   |
  |-------建立ws连接-------------------->| #2(0)
  |-------发送start获得的验证信息-------->| #2(1)
  |<---返回成功信息，通常为`{"code":0}`---| #2(1)
  |--------每隔30秒发送心跳包------------>| #2(2)
  |<-------心跳包回复，附带人气值---------| #2(2)
  |<-----------持续推送数据包------------| #2(0)
  |                  |                  |
  |<---------任意目标关闭ws连接---------->|
  |<------------或项目手动关闭----------->| #2(0)
  |    发送end请求    |                  |
  |  需要key、项目id  |                  |
  |  和gameid        |                  |
  |----------------->|                  | #3
  |<--返回成功信息----|                  | #3

"""# 应使用class

import os,json,pathlib
import time,hashlib,uuid,hmac
import logging,asyncio,zlib
import requests
import websockets

def get_access_key()->dict[str,str]:
    """从文件读取密钥"""
    with open("bili_live_open_key.txt","rt")as f:
        d=f.read(1024)
        kl=d.split("\n")
        return {"kid":kl[0],"kse":kl[1]}

def create_head(kid:str,kse:str,b:str)->dict[str,str]:
    """头部生成"""
    hd={
        "x-bili-accesskeyid":kid,
        "x-bili-content-md5":hashlib.md5(str(b).encode()).hexdigest(),
        "x-bili-signature-method":"HMAC-SHA256",
        "x-bili-signature-nonce":uuid.uuid4().hex,
        "x-bili-signature-version":"1.0",
        "x-bili-timestamp":str(int(time.time())),
    }
    i=0
    t=""
    for k,v in hd.items():
        i+=1
        t+=f"{k}:{v}"+("\n"if i<len(hd)else"")
    hd["Authorization"]=hmac.new(kse.encode(),t.encode(),digestmod=hashlib.sha256).hexdigest()
    hd["Content-Type"]=hd["Accept"]="application/json"
    hd["User-Agent"]=UA
    return hd

def get_start(kid:str,kse:str,appid:int,code:str)->dict:
    j=json.dumps({"code":code,"app_id":appid})
    r=requests.post("https://live-open.biliapi.com/v2/app/start",
        data=j,
        headers=create_head(kid,kse,j)
    )
    if r.status_code!=200:
        print(r.status_code)
        return
    d=r.json()
    #print("start:",d)
    if d["code"]!=0:
        print(d["code"],d["message"])
        return
    return d["data"]

def get_end(kid:str,kse:str,appid:int,gameid:str)->None:
    j=json.dumps({"app_id":appid,"game_id":gameid})
    r=requests.post("https://live-open.biliapi.com/v2/app/end",
        data=j,
        headers=create_head(kid,kse,j)
    )
    if r.status_code!=200:
        print(r.status_code)
        return
    d=r.json()
    #print("end:",d)
    if d["code"]!=0:
        print(d["code"],d["message"])
        return

def get_heart(kid:str,kse:str,gameid:str):
    j=json.dumps({"game_id":gameid})
    r=requests.post("https://live-open.biliapi.com/v2/app/heartbeat",
        data=j,
        headers=create_head(kid,kse,j)
    )
    if r.status_code!=200:
        print(r.status_code)
        return
    d=r.json()
    #print("heart:",d)
    if d["code"]!=0:
        print(d["code"],d["message"])
        return

# 项目
UA="blo/0.0.0"# 用户代理常量
wslog=logging.getLogger("websockets.client")# 日志
sequence:int=0
hpst=None
fi=0
class LoggerAdapter(logging.LoggerAdapter):
    def process(self,msg,kwargs):
        try:
            websocket=kwargs["extra"]["websocket"]
        except:
            return msg,kwargs
        return f"{websocket.id} {msg}",kwargs
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
def joinroom(ad):# 与项目有相同的地方，甚至信息流服务器都是一样的
    """加入直播间"""
    return setdata(7,ad)
def hp():# 返回需要发送的心跳包
    return setdata(2,"")
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
async def live(url:str,ab:str):
    global hpst
    async with websockets.connect(url,logger=LoggerAdapter(wslog,{"websocket":""}),user_agent_header=UA)as ws:
        await ws.send(joinroom(ab))
        hpst=asyncio.create_task(hps(ws),name="循环发送心跳包")
        async for msg in ws:# 此处匹配结构不好用，不要照抄
            #print("<",msg)
            if msg[7]==1 and msg[11]==8:# 认证包
                print("认证返回:",msg[16:])
            elif msg[7]==1 and msg[11]==3:# 心跳包
                print("人气值:",fatchhpmsg(msg[-4:]))
            elif msg[7]==0 and msg[11]==5:# 普通包未压缩
                save(fetchmsgdata(msg))
            elif msg[7]==2 and msg[11]==5:# 普通包使用zlib压缩时使用zlib解压
                save(fetchmsgdata(zlib.decompress(msg[16:])))
            else:
                print(msg)

async def ghs(kid:str,kse:str,gameid:str)->None:
    while True:
        await asyncio.sleep(20)
        get_heart(kid,kse,gameid)

async def start(kid:str,kse:str,appid:int,code:str)->None:
    s=get_start(kid,kse,appid,code)
    if s is None:return
    gameid=s["game_info"]["game_id"]
    rh=asyncio.create_task(ghs(kid,kse,gameid))
    wsi=s["websocket_info"]
    try:
        await live(wsi["wss_link"][0],wsi["auth_body"])
    finally:
        get_end(kid,kse,appid,gameid)

def main():
    k=get_access_key()
    try:
        asyncio.run(start(k["kid"],k["kse"],1732359181754,"DXNSNEEKL9MO1"))
    except KeyboardInterrupt:
        print("exit")

if __name__=="__main__":
    main()
