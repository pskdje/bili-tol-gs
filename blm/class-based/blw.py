"""哔哩哔哩直播信息流基本功能
包括信息流服务器获取、认证，ws连接功能。
使用的第三方库: requests , websockets
可选的第三方库: brotli
数据包格式参考自: https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/live/message_stream.md 和 直播开放平台
本文件只实现基本功能
本文件自带一个异常保存功能，出现异常时调用error函数即可。
但要注意：它能记录的信息是有限的，并要尽快记录一些信息。因此，你可能需要自行处理一些信息。
"""

import sys,time,json,re,zlib
import errno,logging,traceback
import typing,asyncio,argparse
import struct
import requests
import websockets
from pathlib import Path
from typing import Any,NoReturn
try:
    import brotli
except ImportError:
    brotli=None

__version__:str="0"
DEBUG:bool=False
TIMEFORMAT:str="%Y/%m/%d-%H:%M:%S"
UA:str="Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0"
VERSIONINFO:str=f"""Python/{sys.version.split()[0]}({sys.platform}) blw/{__version__} requests/{requests.__version__} websockets/{websockets.__version__}{" brotli/"+brotli.version if brotli else""}"""
LOGDIRPATH=Path("bili_live_ws_log")
ENCODING:str="utf_8"
starttime:float=time.time()
log=logging.getLogger("bili_live_ms")
log.setLevel(logging.DEBUG)
log.addHandler(logging.NullHandler())
wslog=logging.getLogger("websockets.client")
wslog.setLevel(logging.DEBUG)
is_save_log:bool=False
cumulative_error_count:int=0

def error(v:dict[Any]=None,d:Any=None)->None:
    """记录异常
    v: 额外的变量列表
    d: 额外信息
    """
    global cumulative_error_count
    log.exception("[error函数获得了异常]",stack_info=True,stacklevel=2)
    dp=Path("bili_live_ws_err")
    fp=dp/f"{time.time_ns()}.txt"
    def nsf():# 未成功保存异常时调用
        log.exception(f"未成功保存错误文件，文件路径: {fp.resolve()}",stacklevel=2)
        print("=====错误堆栈=====")
        traceback.print_exc()
        print("="*18)
    try:
        if not dp.is_dir():
            log.info("新建保存错误文件用目录")
            dp.mkdir()
        with open(fp,"w",encoding=ENCODING)as f:
            f.write("哔哩哔哩直播信息流\n时间: ")
            f.write(time.strftime("%Y/%m/%d-%H:%M:%S%z"))
            f.write("\n版本信息: "+VERSIONINFO)
            f.write("\n全局用户代理常量: "+str(UA))
            f.write("\n启动时间戳: "+str(starttime))
            f.write("\n累计错误数: "+str(cumulative_error_count))
            f.write("\n命令行: "+str(sys.orig_argv))
            f.write("\n变量DEBUG的值: "+str(DEBUG))
            f.write("\n\n异常信息:\n")
            f.write("str(exception)= \""+str(sys.exc_info()[1])+"\"\n")
            traceback.print_exc(file=f)
            f.flush()
            f.write("\n额外输入的变量信息:")
            if isinstance(v,dict):
                for vn,vv in v.items():
                    f.write("\n\t"+str(vn)+" := "+repr(vv))
            else:
                f.write("\n无")
            f.write("\n")
            if d is not None:
                f.write("\n[其它信息]:\n\n")
                print(d,file=f)
    except PermissionError as e:
        print("无权限保存异常信息:",e)
        nsf()
    except OSError as e:
        print("无法保存异常信息")
        print("OSError:",e)
        nsf()
    except:
        print("写入异常信息到文件失败！")
        nsf()
    else:
        log.debug(f"错误信息已存储至: {fp.absolute()}")
        if DEBUG:
            print("错误信息已存储至",str(fp))
    cumulative_error_count+=1

def pr(d:Any)->Any:# 打印并返回输入的值。[用于调试]
    print(d)
    return d
def bst(b:bytes,sep:str=" ")->str:# 将字节串处理成16进制内容的字符串
    t=""
    x=0
    e=len(b)
    for i in b:
        t+="%02X"%i
        x+=1
        if x<e: t+=sep
    return t

def res_log(res:requests.Response,stacklevel=2)->None:
    """记录响应数据日志
    res: requests库的响应对象或类似格式的对象
    stacklevel: 日志内要跳过的堆栈数，不可少于2
    """
    sl=stacklevel
    if (not isinstance(sl,int)) or sl<2:
        sl=2
    headers=""
    for k,v in res.headers.items():
        headers+=f"{k}: {v}\n"
    log.debug(f"""[响应]{res.url}\n{res.status_code} {res.reason}\n{headers}\n{res.text}""",stacklevel=sl)

class BLWException(Exception):
    """哔哩哔哩直播信息流根异常"""

class GetDataError(BLWException):
    """获取数据时出现的错误，包括网络错误和无效数据"""

class WSClientError(BLWException):
    """blw ws 客户端异常"""

class SavePack(BLWException):
    """保存数据包"""

def bilipack(op:int,data:str,seq:int=0)->bytes:
    """返回要发送的数据包
    op: 操作码
    data: 数据包内容
    seq: 每次递增
    返回值: 一个数据包字节串
    """
    d=str(data).encode()
    db=b""
    db+=bytes.fromhex("{:0>8X}".format(16+len(d)))# 数据包总长度
    db+=b"\0\x10"b"\0\x01"# 头部长度 和 协议版本
    db+=b"\0\0\0"+bytes.fromhex("0"+str(op))# 操作码
    db+=bytes.fromhex("{:0>8X}".format(seq))# 每次递增
    db+=d # 内容
    return db

def savepack(d:dict)->bool:
    """保存数据包"""
    dp=Path("bili_live_ws_pack")
    fn=f"{time.time_ns()}.json"
    fp=dp/fn
    if not dp.is_dir():
        log.info("新建保存数据包用目录")
        dp.mkdir()
    log.debug(f"数据包文件名: {fn}")
    try:
        with open(fp,"w",encoding=ENCODING)as f:
            f.write(json.dumps(d,ensure_ascii=False,indent="\t",sort_keys=False))
    except:
        error(f"保存数据包时出现错误\n路径: {fp.resolve()}\n数据: {d}")
        log.warning("保存失败，详细信息已保存至错误文件。")
        return False
    return True

class Proto(typing.NamedTuple):
    """ws数据包映射"""
    length:int # 数据包总长度
    headerLength:int # 头部长度
    ver:int # 协议版本
    op:int # 操作码
    seq:int # 每次递增
    body:bytes # 正文
    def __len__(self):
        return len(self.body)
    @classmethod
    def unpack(cls,pk:bytes)->typing.Self:
        """解析服务器下发的数据包"""
        if not isinstance(pk,bytes):
            raise TypeError("需要字节串类型数据包")
        if len(pk)<16:
            raise ValueError("数据包长度不足")
        ui=lambda i:struct.unpack(">i",i)[0]
        uh=lambda i:struct.unpack(">h",i)[0]
        return cls(ui(pk[0:4]),uh(pk[4:6]),uh(pk[6:8]),ui(pk[8:12]),ui(pk[12:16]),pk[16:])

class ArgsParser(argparse.ArgumentParser):
    """参数解析，覆盖部分默认行为"""
    def convert_arg_line_to_args(self,arg_line:str)->list[str]:
        """处理一行参数
        注：查源代码可得知，本方法需要参数输入一行文件，返回可迭代对象
        """
        if not arg_line:
            return []
        if re.fullmatch(r"^\s*#.*$",arg_line):
            return []
        if arg_line[0] in self.prefix_chars:
            lco=arg_line.split("#",1)
            return lco[0].split()
        return [arg_line]

class BiliLiveWS:
    """哔哩哔哩直播信息流主程序框架"""

    UA:str=UA
    """类用户代理常量"""
    sequence:int=0
    """数据包递增"""
    roomid:int=0
    """房间号"""
    hpst:asyncio.Task=None
    """循环发送心跳包任务暂存"""
    args:argparse.Namespace=None
    """命令行参数存储"""
    no_run_enable_cmd:bool=False
    """不运行不支持某个cmd的回退操作"""
    cmd_args:list=[]
    """添加给cmd处理使用的命令行参数"""
    only_count_cmd:list[str]=[]
    """只计数cmd的列表"""

    @property
    def debug(self)->bool:
        """返回blw的全局调试状态"""
        return DEBUG

    def __init__(self):
        """初始化一些必要变量"""
        self.save_cmd:list[str]=[]
        self.count_cmd:list[str]=[]
        self.pack_count:dict[str,int]={}
        self.headers:dict[str,str]={
            "Origin":"https://live.bilibili.com/",
            "User-Agent":self.UA
        }
        self.cookies:dict[str,str]={}
        self.uid:int=0
        self.hpst=None
    def error(self,d:Any=None)->None:
        """记录异常，附带该类的部分变量"""
        error({
            "UA":self.UA,
            "sequence":self.sequence,
            "roomid":self.roomid,
            "hpst":self.hpst,
            "args":self.args,
            "pack_count":self.pack_count,
        },d)
    def p(self,*t:Any)->None:
        """输出文本"""
        print(*t)
    def pct(self,name:str,*data:Any)->None:
        """统一按照一定样式输出cmd处理后文本"""
        self.p(f"[{name}]",*data)

    # 事件，主要在主程序中显示提示
    def on_conn_ws_server(s)->None:
        s.p("连接服务器…")
    def on_conn_ws_server_ok(s)->None:
        s.p("服务器已连接")
    def on_no_packlist(s)->None:
        s.p("数据包处理函数未收到数据包列表")
    def on_no_support_cmd_tip(s,cmd:str)->None:
        s.pct("支持",f"不支持'{cmd}'命令")

    # 错误事件，可自定义提示信息
    def erron_split_pack(s,sou_byte:bytes)->None:
        """分割数据包时出现错误的提示信息，将传入原始字节串"""
        s.p("无法解析数据")

    def get_rest_data(self,tip:str,url:str,data:dict|bytes|None=None,err_code_raise:bool=True)->dict[str,str|int|dict]:
        """获取API数据
        tip: 操作提示，用于生成错误和日志
        url: 请求的URL
        data: 要发送的数据，不为None时将使用POST方法请求
        err_code_raise: 若为真值，响应内容的code不为0时将抛出错误
        返回值: 经过json解析后的响应内容
        """
        if not isinstance(tip,str):
            raise TypeError("tip需要为str")
        rn=tip
        log.debug(f"""[请求]{url}\nheaders: {self.headers}\ncookies: {self.cookies}\ndata: {data}""",stacklevel=2)
        try:
            if data:
                r=requests.post(url,
                    data=data,
                    headers=self.headers,
                    cookies=self.cookies
                )
            else:
                r=requests.get(url,
                    headers=self.headers,
                    cookies=self.cookies
                )
        except KeyboardInterrupt:
            log.info(f"{rn}操作被中断")
            raise
        except:
            log.exception(f"{rn}时出现错误")
            raise GetDataError(f"{rn}失败")
        res_log(r,3)
        if r.status_code!=200:
            raise GetDataError(f"{rn}响应的状态码为{r.status_code}")
        try:
            d=r.json()
        except:
            log.exception(f"{rn}数据解析失败")
            raise GetDataError(f"{rn}json数据解析失败")
        if err_code_raise and d["code"]!=0:
            if "message" in d:
                msg=d["message"]
            elif "msg" in d:
                msg=d["msg"]
            else:
                msg="?"
            log.warning(f"{rn}的code不为0，信息: {d['code']} - {msg}")
            raise GetDataError(f"{rn}的code为{d['code']}，信息: {msg}")
        return d

    def from_list_add_args(self,argobj:argparse.ArgumentParser,arg_list:list[dict]|tuple[dict,...])->list[str]:
        """从列表添加命令行选项
        argobj: 参数解析对象
        arg_list: 一个或多个参数解析方法的列表
        返回值: 一个添加成功参数名称的列表
        """
        add_args=[]
        log.debug("将为参数解析对象添加参数: "+str(argobj))
        def setit(n):# 只可在下面的循环中使用
            ov=ari.get(n)
            if ov is None:
                return
            aro[n]=ov
        if not isinstance(arg_list,(list,tuple)):
            raise TypeError("argobj需要为list或tuple类型")
        for ari in arg_list:
            if not isinstance(ari,dict):
                continue
            arin=ari.get("name")
            if not isinstance(arin,str):
                continue
            if arin[0:2]!="--":
                arin="--"+arin
            aro={}# 参数组
            setit("help")
            setit("action")
            setit("nargs")
            setit("const")
            setit("default")
            setit("type")
            setit("choices")
            setit("required")
            setit("metavar")
            setit("dest")
            log.debug(str(argobj.add_argument(arin,**aro)))
            add_args.append(arin)
        return add_args
    def get_SESSDATA(self,s:str)->str|None:
        """获取登录会话数据"""
        rs=re.compile(r"(?:^|.*;\s*)SESSDATA\s*\=\s*([^;]*).*$")
        p=Path(s)
        if p.is_file():
            if p.stat().st_size>65536:
                raise ValueError("文件过大")
            fts=p.read_text().splitlines()
            for ft in fts:
                rst=rs.search(ft)# 支持使用Cookie头内容或之类的数据
                if(rst):
                    return rst[1]
                ftt=ft.split("\t")
                if len(fts)==1 and len(ftt)==1:
                    return ftt[0]# 如果只有1行且分割后只有1个数据,直接返回这个数据,否则试着按照cookie.txt解析数据
                if ftt[0]!=".bilibili.com"or ftt[-2]!="SESSDATA":
                    continue
                return ftt[-1]
            if not len(fts):
                raise ValueError("这个文件没有内容")
            self.p("[警告] 未找到SESSDATA")
            return None
        return s
    def build_argparser(self,
        desc:str="哔哩哔哩直播信息流处理\n允许使用@来引入参数文件",
        epil:str=""
    )->ArgsParser:
        """构造命令行参数解析
        desc: 放在前面的描述
        epil: 放在后面的说明
        """
        log.debug(f"构造命令行参数解析，参数信息：\ndesc = `{desc}`\nepil = `{epil}`")
        parser=ArgsParser(
            usage="%(prog)s [options] roomid",
            description=desc,
            epilog=epil,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            fromfile_prefix_chars="@"
        )
        parser.add_argument("roomid",help="直播间ID",type=int,default=23058)
        parser.add_argument("-d","--debug",help="开启调试模式",action="store_true")
        parser.add_argument("--sessdata",help="使用登录会话标识",type=self.get_SESSDATA,metavar="SESSDATA|FILE")
        parser.add_argument("--no-print-enable",help="不打印不支持的信息",action="store_true")
        parser.add_argument("--pack-error-no-exit",help="数据包处理异常时不退出",action="store_false")
        dbg=parser.add_argument_group("调试功能")
        dbg.add_argument("-u","--save-unknow-datapack",help="保存未知的数据包",action="store_true")
        dbg.add_argument("-C","--print-pack-count",help="打印数据包计数",action="store_true")
        dbg.add_argument("-c","--count-cmd",help="对某个cmd进行计数",action="append",metavar="CMD",default=[])
        dbg.add_argument("-s","--save-cmd",help="保存某个cmd数据包",action="append",metavar="CMD",default=[])
        cmd=parser.add_argument_group("关闭某个cmd的显示")
        self.from_list_add_args(cmd,self.cmd_args)
        return parser
    def other_arg_add(self,argp:argparse.ArgumentParser)->Any:
        """当 pararg 执行时会额外调用该函数，重写该方法来添加额外的命令行解析"""
        pass
    def pararg(self)->argparse.Namespace:
        """分析命令行数据"""
        global DEBUG
        parser=self.build_argparser()
        self.other_arg_add(parser)
        args=parser.parse_args()
        DEBUG=DEBUG or args.debug
        log.debug(f"命令行参数: {args}")
        self.args=args
        self.roomid=args.roomid
        self.save_cmd=args.save_cmd
        self.count_cmd=args.count_cmd
        return args

    def create_pack(self,op:int,data:str)->bytes:
        """创建数据包"""
        self.sequence+=1
        return bilipack(op,data,self.sequence)
    def get_uid(self)->int:
        """获取登录会话对应的uid
        需要提前于self.cookies字典内填入SESSDATA属性。
        若需要登录信息流则必须调用此接口获取uid，或者自行提供uid填入self.uid变量。
        """
        r=self.get_rest_data("获取uid","https://api.bilibili.com/x/member/web/account")
        u=r["data"]["mid"]
        self.uid=u
        return u
    def get_ws_info(self)->dict[str,str]:
        """获取信息流地址，房间号从roomid读取"""
        rn="获取信息流地址"
        log.info(f"{rn}，房间号: {self.roomid}")
        d=self.get_rest_data(rn,"https://api.live.bilibili.com/xlive/web-room/v1/index/getDanmuInfo?id="+str(self.roomid))
        u=d["data"]["host_list"][0]
        return {
            "token":d["data"]["token"],
            "wss_host":f"{u['host']}:{u['wss_port']}",
        }
    def join_room_pack(self,token:str="",uid:int=0)->bytes:
        """创建加入直播间数据包"""
        protover=3 if brotli else 2
        return self.create_pack(7,json.dumps({
            "roomid":self.roomid,
            "key":token,
            "uid":uid,
            "platform":"web",
            "protover":protover
        },separators=(",",":")))
    def create_heartbeat(self)->bytes:
        """创建心跳包"""
        return self.create_pack(2,"")
    async def loop_send_hp(self,ws:websockets.ClientConnection)->None:
        """循环发送心跳包"""
        def pl(p):
            log.debug(f"心跳包: {p}",stacklevel=2)
            return p
        try:
            while True:
                await ws.send(pl(self.create_heartbeat()))
                await asyncio.sleep(30)
        except(# 捕捉正常关闭时会引发的异常
            KeyboardInterrupt,
            websockets.ConnectionClosedOK
        ):pass# 忽略
        except Exception:
            self.error()
    def compute_popularity(self,data:bytes)->int:
        """从心跳包回复计算人气值"""
        if not isinstance(data,bytes):
            raise TypeError("变量'data'需要bytes类型")
        return int.from_bytes(data,"big")
    def print_popularity(self,data:bytes)->int:
        """打印人气值"""
        hp:int=self.compute_popularity(data)
        txt=str(hp)
        if DEBUG:
            txt+=f" [{bst(data,',')}]"
        if hp==1:
            txt+=" (未开播或不显示)"
        self.pct("人气",txt)
        return hp
    def split_datapack(self,msg:bytes)->list[dict]|None:
        """分割压缩数据包的内容"""
        data=msg.split(b"\0\x10\0\0\0\0\0\x05\0\0\0\0")[1:]# 能跑就行
        packlist:list[dict]=[]
        try:
            for item in data:
                if len(item)<5:
                    continue
                if item[-4]==0:
                    packlist.append(json.loads(item[:-4]))
                else:
                    packlist.append(json.loads(item))
            return packlist
        except:
            self.error("分割数据包时出现错误，原始字节串信息:\n"+str(msg))
            self.erron_split_pack(msg)
            return
    def cmd_count_add(self,cmd:str)->None:
        """添加某个cmd的计数"""
        if cmd not in self.pack_count:
            self.pack_count[cmd]=1
        else:
            self.pack_count[cmd]+=1
    def print_cmd_count(self)->dict[str,int]:
        """打印数据包计数"""
        self.p("数据包cmd计数结果:")
        if len(self.pack_count)==0:
            self.p("无内容")
        for key,value in self.pack_count.items():
            self.p("cmd",key,"计数",value)
        return self.pack_count
    def pac_cmd_call(self,pack:dict)->None:
        """查找cmd对应的处理函数"""
        cmd:str=pack["cmd"]
        if cmd in self.save_cmd:
            savepack(pack)
        if cmd in self.count_cmd:
            self.cmd_count_add(cmd)
        if cmd in self.only_count_cmd and cmd not in self.count_cmd:
            self.cmd_count_add(cmd)
            return
        cmd_handle=getattr(self,f"l_{cmd}",None)
        if callable(cmd_handle):
            cmd_handle(pack)
        else:
            log.debug(f"未支持的cmd: '{cmd}'")
            if self.no_run_enable_cmd:
                return
            if not self.args.no_print_enable:
                self.on_no_support_cmd_tip(cmd)
            if DEBUG or self.args.save_unknow_datapack:
                savepack(pack)
    def for_packlist(self,packlist:list[dict])->None:
        """循环遍历数据包列表给后续函数"""
        if packlist is None:
            log.warning("未收到数据包列表")
            self.on_no_packlist()
            return
        this_error_count:int=0
        for pack in packlist:
            try:
                self.pac_cmd_call(pack)
            except SavePack as sp:
                log.debug(f"代码期望保存数据包，信息: {sp}")
                if DEBUG or self.args.save_unknow_datapack:
                    savepack(pack)
            except:
                self.error("出现异常的数据包:\n"+json.dumps(pack,ensure_ascii=False,indent="\t"))
                this_error_count+=1
                log.info(f"数据包处理时出现异常，当前处理列表发生的错误数: {this_error_count} ，累计错误数: {cumulative_error_count}")
                self.p("数据错误")
                ie:bool=self.args.pack_error_no_exit
                if DEBUG:
                    ie=False
                if this_error_count>2:
                    ie=True
                    self.p("单个处理列表错误次数过多，强制进行关闭")
                if ie:
                    raise WSClientError("处理数据包时出现异常")
    async def ws_client(self,url:str,token:str)->NoReturn:
        """信息流ws客户端"""
        log.info(f"连接服务器: {url} ,token: {token}")
        self.on_conn_ws_server()
        async with websockets.connect(url,user_agent_header=self.UA)as ws:
            log.info("服务器已连接")
            self.on_conn_ws_server_ok()
            jrp=self.join_room_pack(token,self.uid)
            log.debug(f"认证: {jrp}")
            await ws.send(jrp)
            del jrp
            self.hpst=asyncio.create_task(self.loop_send_hp(ws),name="重复发送心跳包")
            async for msg in ws:
                p=Proto.unpack(msg)
                if p[2]==1 and p[3]==3:
                    rq=self.print_popularity(msg[16:20])
                    log.debug(f"处理后人气值: {rq}, 原始数据: {p[5]}")
                elif p[2]==1 and p[3]==8:
                    log.debug(f"认证回复: {p[5]}")
                    self.pct("认证",p[5])
                elif p[3]==5 and (p[2]==0 or p[2]==1):
                    self.for_packlist(
                        self.split_datapack(msg)
                    )
                elif p[2]==2:
                    self.for_packlist(
                        self.split_datapack(
                            zlib.decompress(msg[16:])
                        )
                    )
                elif p[2]==3:
                    if brotli:
                        self.for_packlist(
                            self.split_datapack(
                                brotli.decompress(msg[16:])
                            )
                        )
                    elif self.args.no_print_enable:
                        self.pct("支持","未安装brotli，无法处理相关数据，请尝试使用其它协议版本。")
                else:
                    upv="未知的协议版本"
                    log.warning(f"{upv} {p[2]}")
                    if self.args.no_print_enable:
                        continue
                    self.pct("支持",upv,p[2])
    def close_hpst(self,msg:str=None)->None:
        """关闭hpst"""
        if not self.hpst:
            return
        self.hpst.cancel(msg)
        self.hpst=None
    def run_blw_client(self,host:str,token:str)->None:
        """运行ws客户端"""
        try:
            asyncio.run(self.ws_client(f"wss://{host}/sub",token))
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
    def start(self)->NoReturn:
        """一般启动函数"""
        log.info("使用一般启动函数开始运行")
        log.debug(f"版本信息: {VERSIONINFO}")
        a=self.pararg()
        self.p("获取数据…")
        if a.sessdata:
            self.cookies["SESSDATA"]=a.sessdata
            self.get_uid()
        try:
            info=self.get_ws_info()
        except GetDataError as e:
            self.p(str(e))
            sys.exit(1)
        except KeyboardInterrupt:
            self.p("获取信息流操作被中断")
            sys.exit(0)
        self.p("启动客户端…")
        try:
            self.run_blw_client(info["wss_host"],info["token"])
        except WSClientError as e:
            self.p(str(e))
            sys.exit(1)
        except KeyboardInterrupt:
            self.p("关闭")
            sys.exit(0)

def set_logpath()->bool:
    """检查日志路径，若不存在将自动创建"""
    p=LOGDIRPATH
    if p.is_dir():
        return False
    log.info("新建保存日志用目录")
    p.mkdir()
    return True
def set_log()->None:
    """保存运行日志"""
    import logging.handlers
    set_logpath()
    h=logging.handlers.RotatingFileHandler(LOGDIRPATH/"ms.log",maxBytes=2097152,backupCount=3,encoding=ENCODING)
    h.setLevel(logging.DEBUG)
    h.setFormatter(logging.Formatter("{asctime} [{levelname}] '{filename}' {funcName}: {message}",style="{"))
    log.addHandler(h)
def set_wslog()->None:
    """保存ws客户端日志"""
    import logging.handlers
    set_logpath()
    if wslog.hasHandlers():return
    h=logging.handlers.RotatingFileHandler(LOGDIRPATH/"ws.log",maxBytes=2097152,backupCount=3,encoding=ENCODING)
    h.setLevel(logging.DEBUG)
    h.setFormatter(logging.Formatter("{asctime} {levelname}: {message}",style="{"))
    wslog.addHandler(h)
def save_log()->None:
    """配置保存日志"""
    global is_save_log
    if is_save_log:
        raise RuntimeError("不可重复配置保存日志")
    set_log()
    set_wslog()
    is_save_log=True

if __name__=="__main__":
    if "-d" in sys.argv:
        save_log()
    log.info("直接启动")
    BiliLiveWS().start()
