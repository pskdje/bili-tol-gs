"""哔哩哔哩直播信息流推送到Minecraft"""

import blw
import time
import json
import signal
import asyncio
import argparse
import websockets
import websockets.asyncio.server
import mcws_cmd_handle as MCH
from blw import log,GetDataError,CookiesAgent,BiliLiveWS
from typing import Any
from mcws import MinecraftWS
from urllib.parse import urlparse

type ServerConnection=websockets.asyncio.server.ServerConnection

sess_list:set["MCWSP"]=set()

class BLM(MCH.BLM_to_MCWS):
    """为此定制实现"""

    no_run_enable_cmd=True

    def __init__(self):
        """初始化信息流"""
        super().__init__()
        self.connection:set[ServerConnection]=set()
        """连接到此直播间的客户端列表"""
        self.ws_close_count:int=0
        """信息流WS客户端异常关闭计数"""
        self.blmws=None
        """信息流WS客户端容纳"""

    def error(self,d=None,**v):
        super().error(d,
            connection=self.connection,
            ws_close_count=self.ws_close_count,
            blmws=self.blmws,
            BLM=self,
            **v
        )

    def p(self,*t:Any):
        """加时间和直播间ID输出信息"""
        print(f"[{time.strftime(blw.TIMEFORMAT)}]","直播间",self.roomid,"-",*t)

    def push_msg(self,msg:str):
        """推送信息到指定会话"""
        d=self.create_commandRequest(f"say {msg}")
        websockets.broadcast(self.connection,json.dumps(d))

    async def mcws_join_event(self,ws:ServerConnection):
        self.connection.add(ws)
        self.p(ws.remote_address,"加入")
        d=self.create_commandRequest(f"say 已加入直播间{MCH.TRMI}{self.roomid}{MCH.MF_r}的信息流")
        await ws.send(json.dumps(d))
    async def mcws_exit_event(self,ws:ServerConnection):
        self.connection.discard(ws)
        self.p(ws.remote_address,"退出")

    async def close(self):
        """关闭该直播间和连接到该直播间的会话"""
        log.debug(f"关闭直播间{self.roomid}",stack_info=False)
        conn=self.connection.copy()
        for c in conn:
            await c.close()
        self.connection.clear()
        if self.blmws:
            self.blmws.cancel()
            self.p("结束")
            self.blmws=None
        self.close_hpst()

    async def run_client(self,host:str,token:str):
        """启动WS客户端"""
        self.p("启动")
        try:
            await self.ws_client(f"wss://{host}/sub",token)
        except websockets.ConnectionClosedError:
            log.warning("WS被关闭",exc_info=True)
            self.ws_close_count+=1
            if self.ws_close_count<3:
                if self.start_blm()=="GetDataError":
                    await self.close()
        except asyncio.CancelledError:
            await self.close()
            raise
        except:
            self.error()
            await self.close()

    def start_blm(self):
        """启动信息流\n
        若从此处启动请保证填入roomid变量"""
        log.debug(f"启动直播间{self.roomid}的信息流")
        try:
            self.get_room_init()
            w=self.get_ws_info()
        except GetDataError as e:
            log.debug(f"直播间{self.roomid}的信息流启动失败",exc_info=True)
            self.p(f"信息流启动失败")
            self.p(str(e))
            return "GetDataError"
        self.blmws=asyncio.create_task(self.run_client(w.wss_host,w.token))
        log.debug(f"直播间{self.roomid}的信息流启动完成")

    def start(self,roomid:int,args:list[str]):
        """使用指定直播间启动信息流"""
        log.info(f"开始直播间{roomid}的信息流")
        self.pararg(args+["--pack-error-no-exit",str(roomid)])
        return self.start_blm()

class MCWSP(BiliLiveWS,MinecraftWS):
    """运行实现"""

    def __init__(self):
        """初始化MCWSP的必要变量"""
        BiliLiveWS.__init__(self)
        self.livecm:dict[int,BLM]={}
        """房间号映射信息流"""
        self.sess:dict[ServerConnection,int]={}
        """会话映射房间号"""

    def __repr__(self):
        return object.__repr__(self)

    def error(self,d=None,**v):
        return super().error(d,
            livecm=self.livecm,
            sess=self.sess,
            MCWSP=self,
            **v
        )

    async def run_blm(self,roomid:int):
        """根据roomid启动信息流客户端"""
        log.info(f"启动blm，直播间{roomid}")
        s=BLM()
        s.uid=self.uid
        s.wbi_imgKey=self.wbi_imgKey
        s.wbi_subKey=self.wbi_subKey
        s.cookies.update(self.cookies)
        if "buvid3" not in s.cookies:
            try:
                b=s.set_buvid3_4()
            except GetDataError:
                self.error()
                return
            self.cookies["buvid3"]=b["b_3"]
            self.cookies["buvid4"]=b["b_4"]
        r=s.start(roomid,[f"@{self.args.blm_args}"]if self.args.blm_args else[])
        if isinstance(r,str):
            return
        self.livecm[roomid]=s
        return s

    async def mcws_join_event(self,ws:ServerConnection):
        log.info(f"{ws.remote_address} 加入服务器")
        async def send(msg):
            """发送提示"""
            return await ws.send(json.dumps(self.create_commandRequest(f"say {msg}")))
        async def close(msg):
            """发送关闭提示并关闭连接"""
            self.p(f"{ws.remote_address} 加入服务器失败:",msg)
            await send(f"{MCH.MF_o}{MCH.MC_m}加入失败:{MCH.MF_r} {msg}")
            await asyncio.sleep(1)
            await ws.send(json.dumps(self.create_close_command()))
            await ws.close()
        p=urlparse(ws.request.path).path.split("/",2)
        if len(p)<2:
            await send(f"请在URL的后面接上直播间ID，详细信息请查看文档。")
            return await close("未加入直播间")
        try:
            r=int(p[1])
        except:
            return await close("无效的直播间ID")
        if r not in self.livecm:
            await send("连接直播间…")
            b=await self.run_blm(r)
            if b is None:
                return await close(f"连接直播间{MCH.TRMI} {r} {MCH.MF_r}信息流失败")
        await self.livecm[r].mcws_join_event(ws)
        self.sess[ws]=r
    async def mcws_exit_event(self,ws:ServerConnection):
        log.info(f"{ws.remote_address} 退出服务器")
        if ws not in self.sess:return
        r=self.sess[ws]
        m=self.livecm[r]
        await m.mcws_exit_event(ws)
        del self.sess[ws]
        if len(m.connection)<1:
            await m.close()
            del self.livecm[r]

    def close(self):
        """关闭关联的信息流客户端，关闭MCWS服务器"""
        log.info(f"关闭 {self}")
        for l in self.livecm.values():
            asyncio.create_task(l.close(),name="关闭任务")
        self.mcws_close()

    async def main(self,port:int=19134):
        """启动并运行服务器循环"""
        log.debug("启动服务器")
        s=await self.MCWS(port)
        self.p(f"MCWS在 {port} 端口运行")
        try:
            await s.serve_forever()
        except(KeyboardInterrupt,asyncio.CancelledError):
            pass
        finally:
            for i in self.livecm.values():
                await i.close()

    def pararg(self):
        """处理参数"""
        p=argparse.ArgumentParser(description="直播信息流推送")
        p.add_argument("-c","--cookie",default={},type=self.get_Cookie,help="提供将在blm使用的cookie",metavar="Cookie")
        p.add_argument("-d","--debug",action="store_true",help="启用调试模式")
        p.add_argument("-p","--port",help="监听哪个端口",type=int,default=19134)
        p.add_argument("-a","--blm-args",help="提供blm的参数",metavar="FILE")
        return p.parse_args()

    def start(self):
        """启动MCWSP"""
        a=self.pararg()
        self.args=a
        if a.debug:
            blw.DEBUG=True
            blw.set_log()
        if isinstance(a.cookie,CookiesAgent):
            for ck,cv in a.cookie.items():
                self.cookies.set(ck,cv,domain=".bilibili.com")
        self.get_login_nav()
        try:
            asyncio.run(self.main(a.port))
        except KeyboardInterrupt:
            pass

def stop(sign,stack):
    """停止注册的处理会话"""
    log.info("触发 SIGINT 信号，关闭已注册的会话。")
    print("执行全局退出任务，关闭已注册的会话。")
    for s in sess_list:
        s.close()

if __name__=="__main__":
    signal.signal(signal.SIGINT,stop)
    c=MCWSP()
    sess_list.add(c)
    c.start()
