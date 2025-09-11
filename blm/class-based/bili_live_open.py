"""直播开放平台互动框架
文档: https://open-live.bilibili.com/document/
"""

from blw import log,from_list_add_args,ArgsParser,GetDataError,WSClientError
from blm import BiliLiveExp
import json,asyncio,re,argparse,math
import time,hashlib,hmac,uuid
from pathlib import Path
import requests,websockets

class LiveOpenAPI(BiliLiveExp):
    """直播开放平台接口"""

    BLOHS:str="https://live-open.biliapi.com"
    """直播开放平台origin"""
    accessKeyId:str=""
    """直播开放平台 access key id"""
    accessKeySecret:str=""
    """直播开放平台 access key secret"""
    appID:int=0
    """直播开放平台项目id"""
    gameID:str=""
    """直播开放平台游戏id"""
    UA="blo/0.0.0"

    def error(self,d=None,**v):
        return super().error(d,
            BiliLiveOpenOrigin=self.BLOHS,
            accessKeyId=self.accessKeyId,
            accessKeySecret=self.accessKeySecret,
            appID=self.appID,
            gameID=self.gameID,
            **v
        )

    def create_headers(self,body:str)->dict[str,str]:
        """创建开放平台需要的请求头"""
        hd={
            "x-bili-accesskeyid":self.accessKeyId,
            "x-bili-content-md5":hashlib.md5(str(body).encode()).hexdigest(),
            "x-bili-signature-method":"HMAC-SHA256",
            "x-bili-signature-nonce":uuid.uuid4().hex,
            "x-bili-signature-version":"1.0",
            "x-bili-timestamp":str(int(time.time())),
        }
        ht=""
        for k,v in hd.items():
            ht+=f"{k}:{v}\n"
        ht=ht.rstrip("\n")
        hd["Authorization"]=hmac.new(self.accessKeySecret.encode(),ht.encode(),digestmod=hashlib.sha256).hexdigest()
        hd["Accept"]=hd["Content-Type"]="application/json"
        return hd

    def post_openAPI_data(self,tip:str,url:str,body:dict)->dict:
        """发送数据"""
        b=json.dumps(body)
        return self.get_rest_data(tip,url,b,headers=self.create_headers(b))["data"]

    def liveOpenStart(self,code:str):
        """请求开始游戏"""
        d=self.post_openAPI_data("开始游戏",f"{self.BLOHS}/v2/app/start",{"code":code,"app_id":self.appID})
        self.gameID=str(d["game_info"]["game_id"])
        ai=d["anchor_info"]
        self.roomid=int(ai["room_id"])
        self.up_uid=int(ai["uid"])
        return d

    def liveOpenEnd(self,game_id:str=None):
        """请求结束游戏"""
        gi=game_id
        if gi is None:
            gi=self.gameID
        return self.post_openAPI_data("结束游戏",f"{self.BLOHS}/v2/app/end",{"app_id":self.appID,"game_id":gi})

    def liveOpenHeartbeat(self,game_id:str=None):
        """进行心跳上报"""
        gi=game_id
        if gi is None:
            gi=self.gameID
        return self.post_openAPI_data("游戏心跳",f"{self.BLOHS}/v2/app/heartbeat",{"game_id":gi})

    def liveOpenBatchHeartbeat(self,game_ids:list|tuple):
        """进行批量心跳上报"""
        return self.post_openAPI_data("批量游戏心跳",f"{self.BLOHS}/v2/app/batchHeartbeat",{"game_ids":game_ids})

class LiveOpenClient(BiliLiveExp):
    """直播开放平台信息流客户端"""

    def join_room_pack(self,token:str="",uid:int=0):
        """直播开放平台专用加入直播间数据包"""
        if token[0]=="{" and token[-1]=="}":
            return self.create_pack(7,token)
        else:
            return super().join_room_pack(token,uid)

    def run_open_client(self,url:str,auth:str):
        """启动客户端"""
        try:
            asyncio.run(self.ws_client(url,auth),debug=True if self.debug else None)
        except websockets.ConnectionClosedError as e:
            log.warning("连接关闭: "+str(e))
            self.error()
            self.close_hpst("连接关闭")
            raise WSClientError("连接关闭: "+str(e))
        except WSClientError:
            raise
        except TimeoutError:
            log.warning("超时")
            self.error()
            raise WSClientError("内部超时")
        except OSError:
            log.critical("出现OS异常!")
            self.error()
            raise WSClientError("出现OS异常，详细信息见异常记录。")
        except Exception:
            log.critical("出现异常")
            self.error(f"ws_client出现错误")
            self.close_hpst("异常")
            raise WSClientError("出现异常")
        except KeyboardInterrupt:
            log.info("中断键按下，停止运行")
            self.close_hpst("中断键按下")
            log.debug(f"数据包计数: {self.pack_count}")
            raise

class LiveOpen(LiveOpenAPI,LiveOpenClient):
    """直播开放平台框架"""

    bloghp:asyncio.Task=None
    """循环发送开放平台心跳任务容纳"""

    def error(self,d=None,**v):
        return super().error(d,
            bloghp=self.bloghp,
            **v
        )

    def load_liveopen_config(self,arg:str):
        """加载配置数据"""
        d=None
        try:
            d=json.loads(arg)
        except:
            pass
        if len(arg)<2048 and Path(arg).is_file():
            try:
                with open(arg,"r")as f:
                    d=json.load(f)
            except:
                pass
        if len(arg)<1024 and re.match(r"^https?://",arg):
            try:
                d=requests.get(arg).json()
            except:
                pass
        if not d:
            raise ValueError("输入的配置参数无效")
        return d

    def build_argparser(self,
        desc:str="哔哩哔哩直播开放平台信息流处理\n允许使用@来引入参数文件",
        epil:str=""
    )->ArgsParser:
        """构造命令行参数解析
        desc: 放在前面的描述
        epil: 放在后面的说明
        """
        log.debug(f"构造命令行参数解析，参数信息：\ndesc = `{desc}`\nepil = `{epil}`")
        parser=ArgsParser(
            usage="%(prog)s [options] code",
            description=desc,
            epilog=epil,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            fromfile_prefix_chars="@"
        )
        parser.add_argument("code",help="主播身份码",default="")
        parser.add_argument("-d","--debug",help="开启调试模式",action="store_true")
        parser.add_argument("--roomid",help="直播间ID，通常不需要提供",type=int,default=0)
        parser.add_argument("--cookie",help="使用Cookie登录(若需使用其它功能)",type=self.get_Cookie,metavar="Cookie|FILE")
        parser.add_argument("--BLO-config",help="直播开放平台专用配置",type=self.load_liveopen_config,metavar="data|path|URL")
        parser.add_argument("--no-print-enable",help="不打印不支持的信息",action="store_true")
        parser.add_argument("--pack-error-no-exit",help="数据包处理异常时不退出",action="store_false")
        dbg=parser.add_argument_group("调试功能")
        dbg.add_argument("-u","--save-unknow-datapack",help="保存未知的数据包",action="store_true")
        dbg.add_argument("-C","--print-pack-count",help="打印数据包计数",action="store_true")
        dbg.add_argument("-c","--count-cmd",help="对某个cmd进行计数",action="append",metavar="CMD",default=[])
        dbg.add_argument("-s","--save-cmd",help="保存某个cmd数据包",action="append",metavar="CMD",default=[])
        cmd=parser.add_argument_group("关闭某个cmd的显示")
        from_list_add_args(cmd,self.cmd_args)
        return parser

    async def loop_liveopen_hp(self,game_id:str=None):
        """循环发送开放平台心跳"""
        gi=game_id
        if gi is None:
            gi=self.gameID
        try:
            while True:
                self.liveOpenHeartbeat(gi)
                await asyncio.sleep(20)
        except(websockets.ConnectionClosedOK):
            pass
        except(KeyboardInterrupt,asyncio.CancelledError):
            raise
        except:
            self.error()

    async def loop_liveopen_hps(self,game_ids:list[str]):
        """循环批量发送开放平台心跳(未测试)"""
        max_len=200
        gids=[]
        for i in range(0,math.ceil(len(game_ids)/max_len),max_len):
            gids.append(game_ids[i,i+max_len])
        try:
            while True:
                for gi in gids:
                    self.liveOpenBatchHeartbeat(gi)
                await asyncio.sleep(20)
        except(websockets.ConnectionClosedOK):
            pass
        except(KeyboardInterrupt,asyncio.CancelledError):
            raise
        except:
            self.error()

    def on_conn_ws_server(s):
        super().on_conn_ws_server()
        s.bloghp=asyncio.create_task(s.loop_liveopen_hp(),name="循环发送开放平台心跳")

    def start(self):
        log.info("使用直播开放平台启动")
        a=self.pararg()
        BLOC:dict|None=a.BLO_config
        if BLOC:
            self.accessKeyId=BLOC.get("accessKeyId","")
            self.accessKeySecret=BLOC.get("accessKeySecret","")
            self.appID=BLOC.get("appID",0)
        else:
            self.p("警告：未检出直播开放平台专用配置文件")
        self.p("正在启动…")
        try:
            d=self.liveOpenStart(a.code)
        except GetDataError as e:
            self.p("启动失败:",e)
            return
        try:
            wi=d["websocket_info"]
            self.run_open_client(wi["wss_link"][0],wi["auth_body"])
        except WSClientError as e:
            self.p(e)
        finally:
            self.p("正在退出…")
            if self.bloghp:
                self.bloghp.cancel()
            self.liveOpenEnd()

if __name__=="__main__":
    try:
        LiveOpen().start()
    except KeyboardInterrupt:
        pass
