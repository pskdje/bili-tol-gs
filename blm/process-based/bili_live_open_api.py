#!/usr/bin/env python
"""哔哩哔哩直播开放平台信息流
使用bili_live_ws的连接数据处理
使用的第三方库: requests
还需注意bili_live_ws使用的第三方库
部分平台下可能可以直接运行
"""

import time,hashlib,uuid,hmac,json
import asyncio,requests
import bili_live_ws as blw

UA="bloa/0"
log=blw.log

def __getattr__(name):
    log.debug(f"在blo获取blw的'{name}'",stacklevel=2)
    return getattr(blw,name)

class BiliLiveOpenAPIClient():
    UA=UA
    def __init__(self,key_id:str,key_secert:str,appid:int,code:str):
        log.debug(f"kid:'{key_id}',kse:'{key_secert}',aid:{appid},lac:'{code}'")
        self.kid=key_id
        self.kse=key_secert
        self.appid=appid
        self.code=code
        self.is_run=False
    def _p(self,*a):
        log.info("[print]"+str(a))
        print(*a)
    def _dp(self,*a):
        log.info("[DEBUG print]"+str(a))
        if blw.DEBUG:print(*a)
    def create_head(self,data:str)->dict[str,str]:
        """头部生成"""
        hd={
            "x-bili-accesskeyid":self.kid,
            "x-bili-content-md5":hashlib.md5(str(data).encode()).hexdigest(),
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
        hd["Authorization"]=hmac.new(self.kse.encode(),t.encode(),digestmod=hashlib.sha256).hexdigest()
        hd["Content-Type"]=hd["Accept"]="application/json"
        hd["User-Agent"]=self.UA
        return hd
    def post_api(self,path:str,bObj:dict,name:str)->dict[str,int|str|dict]:
        """发送API请求，接收响应"""
        j=json.dumps(bObj)
        log.debug(f"[req:{name}]{j}")
        try:
            r=requests.post("https://live-open.biliapi.com/"+path,
                data=j,
                headers=self.create_head(j)
            )
        except KeyboardInterrupt:
            self._p(f"获取{name}数据被中断")
            raise
        except:
            blw.error()
            return
        if r.status_code!=200:
            self._p("HTTP",r.status_code)
            return
        log.debug(f"[res:{name}]{r.text}")
        d=r.json()
        if d["code"]!=0:
            self._p(d["code"],d["message"])
        return d
    def get_start(self)->dict:
        self._dp("发送启动请求")
        d=self.post_api("v2/app/start",{"code":self.code,"app_id":self.appid},"start")
        self.start=d
        self.is_run=True
        if d["code"]!=0:return
        self.gameid=d["data"]["game_info"]["game_id"]
        return d["data"]
    def req_end(self)->bool|None:
        self._dp("发送结束请求")
        d=self.post_api("v2/app/end",{"app_id":self.appid,"game_id":self.gameid},"end")
        self.is_run=False
        if d is None:return
        return d["code"]==0
    def req_heart(self)->bool|None:
        if not self.is_run:return
        self._dp("发送心跳请求")
        d=self.post_api("v2/app/heartbeat",{"game_id":self.gameid},"heart")
        if d is None:return
        return d["code"]==0
    async def loop_req_heart(self):
        while self.is_run:
            await asyncio.sleep(20)
            self.req_heart()
    @staticmethod
    def joinroom(d:dict[str,str],NCJR)->str:
        if len(d)==1 and "body"in d:return d["body"]
    async def start(self,opt):
        self._p("启动客户端…")
        s=self.get_start()
        if s is None:return
        lh=asyncio.create_task(self.loop_req_heart(),name="重复发送心跳请求")
        wsi=s["websocket_info"]
        try:
            await blw.bililivemsg(wsi["wss_link"][0],opt,{"body":wsi["auth_body"]})
        except Exception:
            blw.error("哔哩哔哩直播开放运行时出现错误")
        finally:
            self._p("\r关闭客户端…")
            lh.cancel("stop")
            blw.hpst.cancel("stop")
            self.req_end()

blw.create_joinroom_pack_funs.append(BiliLiveOpenAPIClient.joinroom)

def main():
    o=blw.pararg([
        {"name":"--access-key-id","help":"开发者access_key_id"},
        {"name":"--access-key-seceret","help":"开发者access_key_seceret"},
        {"name":"--open-app-id","help":"项目id","type":int},
        {"name":"--live-anchor-code","help":"主播身份码"}
    ])
    if blw.DEBUG:
        print("版本信息:",blw.VERSIONINFO)
        print("命令行参数:",o)
        print("启动时间戳:",blw.starttime)
        blw.set_log()
        blw.set_wslog()
    print("载入数据…")
    log.info("载入数据")
    if o.shielding_words:
        blw.shielding_words(o.shielding_words)
    if o.blocking_rules:
        blw.blocking_rules(o.blocking_rules)
    if o.atirch:
        r_ich=blw.import_cmd_handle()
        blw.idp("导入命令处理的结果:",r_ich)
        del r_ich
    log.info("初始化客户端")
    client=BiliLiveOpenAPIClient(o.access_key_id,o.access_key_seceret,o.open_app_id,o.live_anchor_code)
    log.info("启动客户端")
    try:
        asyncio.run(client.start(o))
    except KeyboardInterrupt:
        print("关闭程序")
        log.info("关闭")

if __name__=="__main__":
    main()
