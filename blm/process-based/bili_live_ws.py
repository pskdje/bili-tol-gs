"""哔哩哔哩直播信息流
在Python 3.10或以上运行。经过测试的范围: 3.10 ~ 3.12
使用的第三方库: requests , websockets
可选的第三方库: brotli
数据包参考自: https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/live/message_stream.md
数据分析由我自己进行，请注意时效(更新日期:2025/02/21,新增条目)
已存在的cmd很难确认是否需要更新
本文件计划只实现基本功能
本文件自带一个异常保存功能，出现异常时调用error函数即可。
但要注意：它能记录的信息是有限的，并要尽快记录一些信息。因此，你可能需要自行处理一些信息。
本文件为了压缩文件大小所以部分结构较为混乱，代码量也很多，好孩子不要学。
"""

import sys,time,json,re,zlib
import errno,logging,traceback
import typing,requests
import asyncio,struct,argparse
import websockets
from pathlib import Path
from typing import Any,NoReturn
from collections.abc import Callable
try:
    import brotli
except ImportError:
    brotli=None

DEBUG:bool=not __debug__
TIMEFORMAT:str="%Y/%m/%d-%H:%M:%S"
UA:str="Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0"
VERSIONINFO:str=f"""Python/{sys.version.split()[0]}({sys.platform}) requests/{requests.__version__} websockets/{websockets.__version__}{" brotli/"+brotli.version if brotli else""}"""
LOGDIRPATH=Path("bili_live_ws_log")
ENCODING:str="utf_8"
starttime:float=time.time()
log=logging.getLogger("bili_live_ms")
log.setLevel(logging.DEBUG)
log.addHandler(logging.NullHandler())
wslog=logging.getLogger("websockets.client")
wslog.setLevel(logging.DEBUG)
cumulative_error_count:int=0
runoptions:argparse.Namespace=None
sequence:int=0
hpst:asyncio.Task=None
swd:list[str]=[]
brs:list[re.Pattern]=[]
test_pack_count:dict[str,int]={}
is_importCmdHandle:bool=False
cmdHandleList:list[str]=[]
other_args:list[str]=[]
create_joinroom_pack_funs:list[Callable[[dict,"NCJR"],str|Any]]=[]

def error(d=None)->NoReturn:# 错误记录
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
            f.write("\n是否为执行入口: "+str(__name__=="__main__"))
            f.write("\n版本信息: "+VERSIONINFO)
            f.write("\n命令行选项: "+str(runoptions))
            f.write("\n用户代理常量: "+str(UA))
            f.write("\n启动时间戳: "+str(starttime))
            f.write("\n累计错误数: "+str(cumulative_error_count))
            f.write("\n是否载入额外的处理函数: "+str(is_importCmdHandle))
            f.write("\n被替换的处理函数: "+str(cmdHandleList))
            f.write("\n其它附加入的参数: "+str(other_args))
            f.write("\n部分参数:\n")
            f.write("\tDEBUG= "+str(DEBUG))
            f.write("\n\tsequence= "+str(sequence))
            f.write("\n\thpst: "+repr(hpst))
            f.write("\n\tlen(swd)="+str(len(swd)))
            f.write("\n\tlen(brs)="+str(len(brs)))
            f.write("\n\ttest_pack_count="+str(test_pack_count))
            f.write("\n异常信息:\n")
            f.write("str(exception)=\""+str(sys.exc_info()[1])+"\"\n")
            traceback.print_exc(file=f)
            f.flush()
            if d is not None:
                f.write("\n[其它信息]:\n\n"+str(d))
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
        if DEBUG:print("错误信息已存储至",str(fp))
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

def idp(*d,**a)->bool:# 处于调试模式时打印传入的内容
    if not DEBUG:return False
    print(*d,**a)
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
        if not isinstance(pk,bytes):raise TypeError("需要字节串类型数据包")
        if len(pk)<16:raise ValueError("数据包长度不足")
        ui=lambda i:struct.unpack(">i",i)[0]
        uh=lambda i:struct.unpack(">h",i)[0]
        return cls(ui(pk[0:4]),uh(pk[4:6]),uh(pk[6:8]),ui(pk[8:12]),ui(pk[12:16]),pk[16:])

def bilipack(t:int,da:str)->bytes:
    """返回要发送的数据包\nt: 数据包类型\nda: 数据包内容"""
    global sequence
    d=str(da).encode()
    db=b""
    db+=bytes.fromhex("{:0>8X}".format(16+len(d)))# 数据包总长度
    db+=b"\0\x10"b"\0\x01"# 头部长度 和 协议版本
    db+=b"\0\0\0"+bytes.fromhex("0"+str(t))# 操作码
    db+=bytes.fromhex("{:0>8X}".format(sequence))# 每次递增
    db+=d # 内容
    sequence+=1
    return db

def joinroom(c:dict)->bytes:
    """返回加入直播间数据包\n连接后要立即发送
	id: 直播间id
	k: 令牌
	uid: 用户id
	2023/10/04增: 现在需要登录才能获得用户昵称（这么搞有什么用处？）"""
    cj=create_joinroom_pack_funs
    class NCJR(RuntimeError):
        """显式声明无法处理该加入直播间数据"""
    for i in cj:
        if not callable(i):continue
        try:
            cjr=i(c,NCJR)
        except(NCJR,AssertionError):pass
        except:error("某个函数无法处理数据")
        else:
            if isinstance(cjr,str):return bilipack(7,cjr)
    protover=3 if brotli else 2
    return bilipack(7,json.dumps({"roomid":c["id"],"key":c["k"],"uid":c["uid"],"platform":"web","protover":protover},separators=(",",":")))

def hp()->bytes:# 返回心跳包
    return bilipack(2,"")

async def hps(ws):# 每过30秒发送一次心跳包
    def pl(p):
        log.debug(f"心跳包: {p}",stacklevel=2)
        return p
    try:
        while True:
            await ws.send(pl(hp()))
            await asyncio.sleep(30)
    except(# 捕捉正常关闭时会引发的异常
        KeyboardInterrupt,
        websockets.ConnectionClosedOK
    ):pass# 忽略
    except Exception:
        error()

def fahp(data:bytes)->int:# 合并(用于处理人气值)
    if not isinstance(data,bytes):raise TypeError("variable 'data' instance not bytes")
    return int.from_bytes(data,"big")

def femsgd(msg:bytes)->list[dict]|None:# 分割数据包
    data=msg.split(b"\0\x10\0\0\0\0\0\x05\0\0\0\0")[1:]# 能跑就行
    packlist:list[dict]=[]
    try:
        for item in data:
            if len(item)==4:continue
            if item[-4]==0:
                packlist.append(json.loads(item[:-4]))
            else:
                packlist.append(json.loads(item))
        return packlist
    except:
        error("分割数据包时出现错误，原始字节串信息:\n"+str(msg))
        print("无法解析数据")
        return

def save_http_error(r:requests.Response,t:str)->NoReturn:
    """保存HTTP错误"""
    header="header:\n"
    for k,v in r.headers.items():
        header+=f"\t{k}: {v}\n"
    error(f"info: {t}\nurl: {r.url} "
        f"status: {r.status_code} {r.reason}\n"+
        header+f"body:[{r.encoding}]\n"+r.text+"\n")

class SavePack(RuntimeError):
    """用于保存数据包的异常"""
    pass

def savepack(d:dict)->NoReturn:# 保存数据包
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

def test_pack_add(c:str)->NoReturn:# 对数据包进行计数(理论上能对任何数据进行计数)
    if c not in test_pack_count:
        test_pack_count[c]=1
    else:
        test_pack_count[c]+=1

def pct(name:str,*data:Any)->NoReturn:# 统一按照一定规则输出数据
    if not isinstance(name,str):raise TypeError("name必须为str")
    o=runoptions
    if isinstance(o.add_time,str):
        at=o.add_time
        if at=="datetime": t=time.strftime(TIMEFORMAT)
        elif at=="time": t=time.strftime("%H:%M:%S")
        elif at=="timestamp": t=str(int(time.time()))
        else: t=""
        if t:
            print(t,f"[{name}]",*data)
            return
    print(f"[{name}]",*data)

class RelOpt:
    """主要为了反转以'no_'开头的属性"""
    def __init__(self,opt:argparse.Namespace):
        self.o=opt
    def __getattr__(self,name:str)->bool|list|Any:
        """将要获取的属性前面加'no_'并对结果取非运算，已存在该开头时忽略。"""
        n=name
        if n in["roomid","uid","debug",# 根据需要不处理部分属性
            "save_cmd","count_cmd","save_unknow_datapack",
            "save_recommend_card",
        ]:
            return getattr(self.o,n)
        if n[:3]=="no_":
            return getattr(self.o,n)
        return not getattr(self.o,"no_"+n)

def pac(pack:dict,o:argparse.Namespace):# 匹配cmd,处理内容
    cmd:str=pack["cmd"]
    if cmd in o.save_cmd: savepack(pack)
    if cmd in o.count_cmd: test_pack_add(cmd)
    match cmd:
        case "DANMU_MSG":# 弹幕
            l_danmu_msg(pack["info"])
        case "INTERACT_WORD":# 交互
            if o.interact_word:l_interact_word(pack["data"],o)
        case "ENTRY_EFFECT":# 进场
            if o.entry_effect:l_entry_effect(pack["data"])
        case "SEND_GIFT":# 礼物
            if o.send_gift:l_send_gift(pack["data"])
        case "COMBO_SEND":# 组合礼物(推测)
            if o.combo_send:l_combo_send(pack["data"])
        case "WATCHED_CHANGE":# 看过
            if o.watched_change:l_watched_change(pack["data"])
        case "SUPER_CHAT_MESSAGE":# 醒目留言
            if o.super_chat_message:l_super_chat_message(pack["data"])
        case "SUPER_CHAT_MESSAGE_JPN":# 醒目留言(日本)
            pass
        case "SUPER_CHAT_MESSAGE_DELETE":# 醒目留言删除(推测)
            if o.super_chat_message:l_super_chat_message_delete(pack)
        case "LIVE_INTERACTIVE_GAME":# 类似弹幕，未确定
            if o.live_interactive_game:l_live_interactive_game(pack["data"])
        case "ROOM_CHANGE":# 直播间更新
            l_room_change(pack["data"])
        case "LIVE":# 开始直播
            l_live(pack)
        case "PREPARING":# 结束直播
            l_preparing(pack)
        case "ROOM_REAL_TIME_MESSAGE_UPDATE":# 数据更新
            l_room_real_time_message_update(pack["data"])
        case "STOP_LIVE_ROOM_LIST":# 停止直播的房间列表(推测)
            if o.stop_live_room_list:l_stop_live_room_list(pack["data"])
        case "ROOM_BLOCK_MSG":# 用户被禁言
            l_room_block_msg(pack)
        case "CUT_OFF":# 切断
            l_cut_off(pack)
        case "ROOM_LOCK":# 封禁
            l_room_lock(pack)
        case "ROOM_ADMINS":# 房管列表
            l_room_admins(pack)
        case "room_admin_entrance":# 添加房管
            l_room_admin_entrance(pack)
        case "ROOM_ADMIN_REVOKE":# 撤销房管
            l_room_admin_revoke(pack)
        case "CHANGE_ROOM_INFO":# 背景更换
            l_change_room_info(pack)
        case "WARNING":# 警告
            l_warning(pack)
        case "DANMU_AGGREGATION":# 弹幕聚集
            if o.danmu_aggregation:l_danmu_aggregation(pack["data"])
        case "ONLINE_RANK_COUNT":# 在线计数
            if o.online_rank_count:l_online_rank_count(pack["data"])
        case "LITTLE_TIPS":# 某种提示，内容可能与使用的会话信息有关
            l_little_tips(pack["data"])
        case "LITTLE_MESSAGE_BOX":# 弹框提示
            l_little_message_box(pack["data"])
        case "VOICE_JOIN_LIST":# 连麦列表(推测,原始数据已删除，暂时不打算重新确定)
            if o.voice_join_list:l_voice_join_list(pack["data"])
        case "VOICE_JOIN_ROOM_COUNT_INFO":# 同上，现在无法确定是否与上面的数据相同
            if o.voice_join_list:l_voice_join_list(pack["data"])
        case "ONLINE_RANK_TOP3":# 前三个第一次成为高能用户
            if o.online_rank_top3:l_online_rank_top3(pack["data"])
        case "VOICE_JOIN_STATUS":# 连麦状态
            if o.voice_join_status:l_voice_join_status(pack["data"])
        case "ONLINE_RANK_V2":
            if o.online_rank_v2:l_online_rank_v2(pack["data"],o.no_print_enable)
        case "HOT_RANK_SETTLEMENT":# 热门通知
            if o.hot_rank_settlement:l_hot_rank_settlement(pack["data"])
        case "HOT_RANK_SETTLEMENT_V2":# 同上
            pass
        case "COMMON_NOTICE_DANMAKU":# 普通通知
            if o.common_notice_danmaku:l_common_notice_danmaku(pack["data"])
        case "NOTICE_MSG":# 公告(广播)
            if o.notice_msg:l_notice_msg(pack)
        case "GUARD_BUY":# 舰队购买
            if o.guard_buy:l_guard_buy(pack["data"])
        case "USER_TOAST_MSG":# 舰队续费
            if o.user_toast_msg:l_user_toast_msg(pack["data"])
        case "USER_TOAST_MSG_V2":# 同上
            pass
        case "WIDGET_BANNER":# 小部件
            if o.widget_banner:l_widget_banner(pack["data"])
        case "SUPER_CHAT_ENTRANCE":# 醒目留言入口变化
            if o.super_chat_entrance:l_super_chat_entrance(pack["data"])
        case "ROOM_SKIN_MSG":# 直播间皮肤更新
            l_room_skin_msg(pack)
        case "LIVE_MULTI_VIEW_CHANGE":
            l_live_multi_view_change(pack["data"])
        case "POPULARITY_RED_POCKET_NEW":# 新红包(?)
            if o.popularity_red_pocket:l_popularity_red_pocket_new(pack["data"])
        case "POPULARITY_RED_POCKET_V2_NEW":# 同上，V2
            pass
        case "POPULARITY_RED_POCKET_START":# 增加屏蔽词(才怪)
            l_popularity_red_pocket_start(pack["data"])
        case "POPULARITY_RED_POCKET_V2_START":# 同上，V2
            pass
        case "POPULARITY_RED_POCKET_WINNER_LIST":# 看起来好像是得到红包的列表
            pass
        case "POPULARITY_RED_POCKET_V2_WINNER_LIST":# 同上
            pass
        case "LIKE_INFO_V3_UPDATE":# 点赞数量
            if o.like_info_update:l_like_info_v3_update(pack["data"])
        case "LIKE_INFO_V3_CLICK":# 点赞点击
            if o.interact_word:# 使用屏蔽交互信息的选项
                l_like_info_v3_click(pack["data"])
        case "LIKE_INFO_V3_NOTICE":# 点赞提示
            if o.like_info_notice:l_like_info_v3_notice(pack["data"])
        case "POPULAR_RANK_CHANGED":# 人气排行更新
            if o.rank_changed:l_popular_rank_changed(pack["data"])
        case "AREA_RANK_CHANGED":# 大航海排行更新
            if o.rank_changed:l_area_rank_changed(pack["data"])
        case "RANK_CHANGED":# 人气榜
            if o.rank_changed:l_rank_changed(pack["data"])
        case "REVENUE_RANK_CHANGED":# 收入排行(机翻)
            if o.rank_changed:l_revenue_rank_changed(pack["data"])
        case "DM_INTERACTION":# 交互合并
            if o.dm_interaction:l_dm_interaction(pack["data"])
        case "PK_BATTLE_PRE":# PK即将开始
            if o.pk_message:l_pk_battle_pre(pack)
        case "PK_BATTLE_PRE_NEW":# PK即将开始
            if o.pk_message:l_pk_battle_pre_new(pack)
        case "PK_BATTLE_START":# PK开始
            if o.pk_message:l_pk_battle_start(pack)
        case "PK_BATTLE_START_NEW":# PK开始
            if o.pk_message:l_pk_battle_start_new(pack)
        case "PK_BATTLE_PROCESS":# PK过程
            if o.pk_message and o.pk_battle_process:l_pk_battle_process(pack)
        case "PK_BATTLE_PROCESS_NEW":# PK过程
            if o.pk_message and o.pk_battle_process:l_pk_battle_process_new(pack)
        case "PK_BATTLE_FINAL_PROCESS":# PK结束流程变化(推测)
            if o.pk_message:l_pk_battle_final_process(pack)
        case "PK_BATTLE_END":# PK结束
            if o.pk_message:l_pk_battle_end(pack)
        case "PK_BATTLE_SETTLE":# PK结算1
            if o.pk_message:l_pk_battle_settle(pack)
        case "PK_BATTLE_SETTLE_V2":# PK结算2
            if o.pk_message:l_pk_battle_settle_v2(pack)
        case "PK_BATTLE_SETTLE_NEW":# pk结算并进入惩罚
            if o.pk_message:l_pk_battle_settle_new(pack)
        case "PK_BATTLE_VIDEO_PUNISH_BEGIN":# 同上，数据格式不同
            if o.pk_message:l_pk_battle_video_punish_begin(pack)
        case "PK_BATTLE_PUNISH_END":# 惩罚结束
            if o.pk_message:l_pk_battle_punish_end(pack)
        case "PK_BATTLE_VIDEO_PUNISH_END":# 同上，少了data部分
            if o.pk_message:l_pk_battle_video_punish_end(pack)
        case "RECOMMEND_CARD":# 推荐卡片
            if o.recommend_card:l_recommend_card(pack["data"],False)# 参数2已弃用
        case "GOTO_BUY_FLOW":# 购买商品
            if o.buy_flow_info:l_goto_buy_flow(pack["data"])
        case "HOT_BUY_NUM":# 热购数量
            if o.buy_flow_info:l_hot_buy_num(pack["data"])
        case "LOG_IN_NOTICE":# 登录提示
            l_log_in_notice(pack["data"])
        case "GUARD_HONOR_THOUSAND":# 千舰主播增减
            if o.guard_honor_thousand:l_guard_honor_thousand(pack["data"])
        case "GIFT_STAR_PROCESS":# 礼物星球进度
            if o.gift_star_process:l_gift_star_process(pack["data"])
        case "ANCHOR_LOT_CHECKSTATUS":# 天选时刻审核状态(?)
            if o.anchor_lot:l_anchor_lot_checkstatus(pack["data"])
        case "ANCHOR_LOT_START":# 天选时刻开始
            if o.anchor_lot:l_anchor_lot_start(pack["data"])
        case "ANCHOR_LOT_END":# 天选时刻结束
            if o.anchor_lot:l_anchor_lot_end(pack["data"])
        case "ANCHOR_LOT_AWARD":# 天选时刻开奖
            if o.anchor_lot:l_anchor_lot_award(pack["data"])
        case "ANCHOR_LOT_NOTICE":# 天选时刻通知
            if o.anchor_lot:l_anchor_lot_notice(pack["data"])
        case "ANCHOR_NORMAL_NOTIFY":# 推荐提示(推测)
            if o.anchor_normal_notify:l_anchor_normal_notify(pack["data"])
        case "POPULAR_RANK_GUIDE_CARD":# 冲榜提示卡(推测)(发包情况未知)
            if o.popular_rank_guide_card:l_popular_rank_guide_card(pack["data"])
        case "ANCHOR_ECOLOGY_LIVING_DIALOG":# 提示框(用于警告?)
            l_anchor_ecology_living_dialog(pack["data"])
        case "CUT_OFF_V2":# 切断直播间(v2)
            l_cut_off_v2(pack["data"])
        case "ROOM_CONTENT_AUDIT_REPORT":# 直播间内容审核结果
            if o.room_content_audit_report:l_room_content_audit_report(pack["data"])
        case "SYS_MSG":# 系统消息(推测)
            if o.sys_msg:l_sys_msg(pack)
        case "PLAY_TAG":# 直播进度条节点标签
            if o.play_tag:l_play_tag(pack["data"])
        case "CHG_RANK_REFRESH":# 未知
            if o.rank_changed:l_chg_rank_refresh(pack["data"])
        case "POPULARITY_RANK_TAB_CHG":# 排行标签更新？
            if o.rank_changed:l_popularity_rank_tab_chg(pack["data"])
        case "ANCHOR_BROADCAST":# 初次抵达某种情况时的提示
            l_anchor_broadcast(pack["data"])
        case "ANCHOR_HELPER_DANMU":# 同上，但是格式不同
            l_anchor_helper_danmu(pack["data"])
        case "OTHER_SLICE_LOADING_RESULT":# 切片数据加载结果
            if o.event:l_other_slice_loading_result(pack["data"])
        case(# 不进行支持
            "HOT_ROOM_NOTIFY"|# 未知，内容会在哔哩哔哩直播播放器日志中显示。
            "WIDGET_GIFT_STAR_PROCESS"|# 礼物星球，不想写支持。
            "PK_BATTLE_SETTLE_USER"|# 不支持原因: 懒
            "PK_BATTLE_MULTIPLE_BEGIN"|# 看起来是某种pk加倍机制
            "PK_BATTLE_MULTIPLE_RES"|# 没看懂
            "PLAYTOGETHER_ICON_CHANGE"|# 陪玩图标？没看懂
            "ENTRY_EFFECT_MUST_RECEIVE"|# 未知的进入信息，先做计数
            None# 防错误
        ): test_pack_add(cmd)
        case _:# 未知命令
            log.debug(f"未支持的cmd: '{cmd}'")
            if o.print_enable: pct("支持",f"不支持'{cmd}'命令")
            if DEBUG or o.save_unknow_datapack: savepack(pack)

def pacs(packlist:list[dict],o:argparse.Namespace)->NoReturn:
    # 将数据包列表遍历发送给pac处理
    # 记录出现异常的数据包
    if packlist is None:
        log.warning("未收到数据包列表")
        idp("数据包处理函数pacs未收到数据包列表")
        return
    this_error_count:int=0
    ro=RelOpt(o)
    for pack in packlist:
        try:
            pac(pack,ro)
        except SavePack as sp:
            log.debug(f"代码期望保存数据包，信息: {sp}")
            if DEBUG or o.save_unknow_datapack: savepack(pack)
        except:
            error("出现异常的数据包:\n"+json.dumps(pack,ensure_ascii=False,indent="\t"))
            this_error_count+=1
            log.info(f"数据包处理时出现异常，当前处理列表发生的错误数: {this_error_count} ，累计错误数: {cumulative_error_count}")
            print("数据错误",file=sys.stderr)
            ie:bool=o.pack_error_no_exit
            if DEBUG: ie=False
            if this_error_count>2:
                ie=True
                print("单个处理列表错误次数过多，强制进行关闭")
            if ie:sys.exit(1)

def print_rq(rq:bytes)->int:# 打印人气值
    hp:int=fahp(rq)
    txt:str=str(hp)
    if DEBUG: txt+=" ["+bst(rq,",")+"]"
    if hp==1: txt+=" (未开播或不显示)"
    pct("人气",txt)
    return hp

async def bililivemsg(url:str,o:argparse.Namespace,jo:dict)->NoReturn:
    """使用提供的参数连接直播间"""
    global hpst
    idp("连接服务器…")
    log.debug("连接服务器; "f"url: {url} ,joinroom: {jo}")
    async with websockets.connect(url,user_agent_header=UA)as ws:
        idp("服务器已连接")
        jrp=joinroom(jo)
        log.debug(f"认证: {jrp}")
        await ws.send(jrp)
        del jrp
        hpst=asyncio.create_task(hps(ws),name="重复发送心跳包")
        async for msg in ws:
            p=Proto.unpack(msg)
            if p[2]==1 and p[3]==3:
                rq=print_rq(msg[16:20])
                log.debug(f"处理后人气值: {rq}, 原始数据: {p[5]}")
            elif p[2]==1 and p[3]==8:
                log.debug(f"认证回复: {p[5]}")
                pct("认证",p[5])
            elif p[3]==5 and (p[2]==0 or p[2]==1):
                pacs(femsgd(msg),o)
            elif p[2]==2:
                pacs(femsgd(zlib.decompress(msg[16:])),o)
            elif p[2]==3:
                if brotli: pacs(femsgd(brotli.decompress(msg[16:])),o)
                elif o.no_print_enable: pct("支持","未安装brotli，无法处理相关数据，请尝试使用其它协议版本。")
            else:
                upv="未知的协议版本"
                log.warning(f"{upv} {p[2]}")
                if o.no_print_enable:continue
                pct("支持",upv,p[2])
                idp(msg)

def start(roomid:int,o:argparse.Namespace)->NoReturn:
    """程序入口
	roomid: 真实房间号
	o: 命令行解析后参数组"""
    if not isinstance(roomid,int):raise TypeError("roomid不是整数")
    log.debug(f"""WebSocket客户端即将启动，房间号: {roomid}\n版本信息: {VERSIONINFO}\n用户代理: {UA}""")
    idp("获取直播信息流地址…")
    log.info("获取信息流地址")
    try:
        r=requests.get("https://api.live.bilibili.com/xlive/web-room/v1/index/getDanmuInfo?id="+str(roomid),
            headers={
                "Origin":"https://live.bilibili.com/",
                "User-Agent":UA
            },cookies={"SESSDATA":o.sessdata})
    except KeyboardInterrupt:
        print("获取信息操作被中断")
        log.info("中断键按下，停止获取")
        sys.exit(0)
    except:
        print("获取信息流地址失败:",sys.exc_info()[1])
        error()
        sys.exit(1)
    log.debug(r.text)
    if r.status_code!=200:
        print("数据获取失败")
        print("HTTP",r.status_code)
        save_http_error(r,"状态码不为200")
        sys.exit(1)
    try:
        d=r.json()
    except:
        print("数据解析失败")
        save_http_error(r,"JSON解析失败")
        sys.exit(1)
    if d["code"]!=0:
        print("获取信息流地址时code不为0")
        print(d["code"],"-",d["message"])
        save_http_error(r,"获取到的code不为0")
        sys.exit(1)
    ws_host=None
    log.info("解析数据，连接服务器")
    try:
        u=d["data"]["host_list"][0]
        ws_host=f"{u['host']}:{u['wss_port']}"
        token=d["data"]["token"]
        asyncio.run(bililivemsg(f"wss://{ws_host}/sub",o,{"id":roomid,"k":token,"uid":o.uid}))
    except websockets.ConnectionClosedError as e:
        log.warning("连接关闭: "+str(e))
        error()
        print("连接关闭:",e)
        if (o.sessdata or o.uid) and time.time()-starttime<10:print("检测到使用了登录会话信息，请检查相关参数的正确性和有效性。")
        sys.exit(1)
    except TimeoutError:
        log.warning("超时")
        error()
        print("内部超时")
        print("请检查网络是否通畅。")
        sys.exit(errno.ETIMEDOUT)
    except OSError as e:
        log.critical("出现OS异常!")
        error()
        print("出现OS异常，详细信息请查看错误记录文件。")
        print("可以先检查一下网络。大部分异常都由网络问题引起的。")
        sys.exit(e.errno)
    except Exception:
        log.critical(f"出现异常! ws_host: {ws_host}")
        error("捕捉函数 bililivemsg 抛出的异常\n"f"WebSocket Server: {ws_host}"f"\nroomid: {roomid}\ntoken: {token}")
        print("=出现内部异常=\n请查看错误记录文件自行排除问题或在你获取本文件的git仓库开一个issue。")
        print("开issus请检查是否有相同的问题，若有就附加上去。记得附上错误文件，也不要忘记检查是否有敏感信息。")
        print("若使用登录信息，请将错误文件中命令行选项内的sessdata替换为'SESSDATA'字符串，切勿改成None，否则无法确定是否为登录时发生的问题。")
        print("uid也不要替换为0，随便一个正数。如果uid为0，这边会更偏向于没有正确使用参数导致出现问题。")
        sys.exit(1)
    except KeyboardInterrupt:
        hpst.cancel("中断键按下")
        log.info("中断键按下，停止运行")
        log.debug(f"数据包计数: {test_pack_count}")
        raise

def set_logpath()->NoReturn:# 日志路径
    p=LOGDIRPATH
    if p.is_dir():return
    log.info("新建保存日志用目录")
    p.mkdir()
def set_log()->NoReturn:# 保存运行日志
    import logging.handlers
    set_logpath()
    h=logging.handlers.RotatingFileHandler(LOGDIRPATH/"ms.log",maxBytes=2097152,backupCount=3,encoding=ENCODING)
    h.setLevel(logging.DEBUG)
    h.setFormatter(logging.Formatter("{asctime} [{levelname}] '{filename}' {funcName}: {message}",style="{"))
    log.addHandler(h)
def set_wslog()->NoReturn:# 保存ws客户端日志
    import logging.handlers
    set_logpath()
    if wslog.hasHandlers():return
    h=logging.handlers.RotatingFileHandler(LOGDIRPATH/"ws.log",maxBytes=2097152,backupCount=3,encoding=ENCODING)
    h.setLevel(logging.DEBUG)
    h.setFormatter(logging.Formatter("{asctime} {levelname}: {message}",style="{"))
    wslog.addHandler(h)
    print("已启用ws记录")

def shielding_words(f:typing.TextIO)->NoReturn:
    """屏蔽词"""
    print("解析屏蔽词…")
    try:
        for l in f:
            t=l.rstrip("\r\n")
            if not t:continue
            if t[0]=="#":continue
            swd.append(t)
    except:
        print("处理屏蔽词时出现错误",file=sys.stderr)
        error()
    finally:
        f.close()
        log.debug(f"屏蔽词: {swd}")
        idp(swd)
def blocking_rules(f:typing.TextIO)->NoReturn:
    """屏蔽规则"""
    print("解析屏蔽规则…")
    try:
        for l in f:
            t=l.rstrip("\r\n")
            if not t:continue
            if t[0]=="#":continue
            brs.append(re.compile(t))
    except:
        print("处理屏蔽规则时出现错误",file=sys.stderr)
        error()
    finally:
        f.close()
        log.debug(f"屏蔽规则: {brs}")
        idp(brs)

def print_test_pack_count()->dict[str,int]:# 打印数据包计数
    cn=test_pack_count
    if len(cn)==0:
        print("无内容")
    for k,v in cn.items():
        print("cmd",k,"计数",v)
    return cn

class ArgsParser(argparse.ArgumentParser):
    """参数解析，覆盖部分默认行为"""
    def convert_arg_line_to_args(self,arg_line:str):
        """处理一行参数
        注：查源代码可得知，本方法需要参数输入一行文件，返回可迭代对象
        """
        if not arg_line:return []
        if re.fullmatch(r"^\s*#.*$",arg_line):return []
        if arg_line[0] in self.prefix_chars:
            lco=arg_line.split("#",1)
            return lco[0].split()
        return [arg_line]

def import_cmd_handle()->str:
    """导入命令处理"""
    global is_importCmdHandle
    if not runoptions.atirch:return"argument"
    log.info("进行'导入命令处理'操作")
    try:
        import cmd_handle as chm
    except ModuleNotFoundError:
        log.info("不存在额外的处理模块")
        return"not_found"
    except ImportError as e:
        error()
        log.warning("导入额外的命令处理失败")
        return"import_error"
    idp("存在cmd_handle模块，已导入。")
    for chn in dir(chm):
        if chn[0:2]!="l_":continue# 必须要以"l_"开头
        ch=getattr(chm,chn,None)
        if not callable(ch):continue
        globals()[chn]=ch
        cmdHandleList.append(chn)
        is_importCmdHandle=True
    else:
        print("检测到存在额外的命令处理，已自动导入并替换对应处理函数。")
    log.debug(f"替换列表: {cmdHandleList}")
    if DEBUG:
        print("是否载入函数:",is_importCmdHandle)
        print("被替换的函数:",cmdHandleList)
    return"success"

# 命令处理调用处(开始)
def l_danmu_msg(d):
    if d[1]in swd:return
    for b in brs:
        if b.search(d[1]):return
    pct("弹幕",f"{d[2][1]}:",d[1])
def l_interact_word(d,o):
    info="交互"
    mt=d["msg_type"]
    nm=d["uname"]
    if mt==1:
        if o.enter_room: pct(info,nm,"进入直播间")
    elif mt==2: pct(info,nm,"关注直播间")
    elif mt==3: pct(info,nm,"分享直播间")
    else:
        t=f"未知的交互类型: {d['msg_type']}"
        log.debug(t)
        if o.print_enable:
            pct("支持",t)
        raise SavePack("未知的交换类型")
def l_entry_effect(d):
    pct("进场",d["copy_writing"])
def l_send_gift(d):
    pct("礼物",d["uname"],d["action"],d["giftName"],"×",d["num"])
def l_combo_send(d):
    pct("礼物",d["uname"],d["action"],d["gift_name"],"×",d["total_num"])
def l_watched_change(d):
    if DEBUG: pct("观看",d["num"],"人看过;","text_large:",d["text_large"])
    else: pct("观看",d["num"],"人看过")
def l_super_chat_message(d):
    pct("留言",f"{d['user_info']['uname']}(￥{d['price']}):",d["message"])
def l_super_chat_message_delete(d):
    pct("留言","醒目留言删除:",d["data"]["ids"])
def l_live_interactive_game(d):
    if d["msg"]in swd:return
    for b in brs:
        if b.search(d["msg"]):return
    pct("弹幕(LIG)",f"{d['uname']}:",d["msg"])
def l_room_change(d):
    pct("直播","分区:",d["parent_area_name"],">",d["area_name"],",标题:",d["title"])
def l_live(p):
    pct("直播","直播间",p["roomid"],"开始直播")
def l_preparing(p):
    pct("直播","直播间",p["roomid"],"结束直播")
def l_room_real_time_message_update(d):
    pct("信息",d["roomid"],"直播间",d["fans"],"粉丝",d["fans_club"],"点亮粉丝勋章")
def l_stop_live_room_list(d):
    pass
def l_room_block_msg(p):
    pct("直播","用户",p["uname"],"已被禁言")
def l_cut_off(p):
    pct("直播","直播间",p["room_id"],"被警告:",p["msg"])
def l_room_lock(p):
    pct("直播","直播间",p["roomid"],"被封禁，解除时间:",p["expire"])
def l_room_admins(p):
    pct("直播",f"房管列表: len({len(p['uids'])})")
def l_room_admin_entrance(p):
    pct("直播","添加",p["uid"],"为房管，消息:",p["msg"])
def l_room_admin_revoke(p):
    pct("直播","撤销",p["uid"],"的房管权限，消息:",p["msg"])
def l_change_room_info(p):
    pct("直播","直播间",p["roomid"],"信息变更","背景图:",p["background"])
def l_warning(p):
    pct("警告",p["msg"])
def l_danmu_aggregation(d):
    pass
def l_online_rank_count(d):
    olc=""
    if "online_count"in d:
        olc="在线计数: "+str(d["online_count"])
    pct("计数","高能用户计数:",d["count"],olc)
def l_little_tips(d):
    pct("提示",d["msg"])
def l_little_message_box(d):
    pct("弹框",d["msg"])
def l_voice_join_list(d):
    pct("连麦","申请计数:",d["apply_count"])
def l_online_rank_top3(d):
    if DEBUG: pct("排行",f"len({len(d['list'])})",d["list"][0]["msg"],f"rank:{d['list'][0]['rank']}")
    else: pct("排行",d["list"][0]["msg"],f"rank:{d['list'][0]['rank']}")
def l_voice_join_status(d):
    if d["status"]==0: pct("连麦","停止连麦")
    elif d["status"]==1: pct("连麦","正在与",d["user_name"],"连麦")
    else:
        t="未知的语音连麦状态"
        log.debug(f"{t}: {d['status']}")
        raise SavePack(t)
def l_online_rank_v2(d,npe):
    pass
def l_hot_rank_settlement(d):
    pct("排行",d["dm_msg"])
def l_common_notice_danmaku(d):
    for cse in d["content_segments"]:
        cset=cse["type"]
        if cset==1: pct("通知",cse["text"])
        elif cset==2: pct("通知","图片:",cse.get("img_url"))
        else:
            log.debug(f"未知的通知组件类型: {cset}")
            raise SavePack("通知组件类型")
def l_notice_msg(d):
    if "name"in d: pct("公告",d["name"],"=>",d["msg_self"])
    else: pct("公告",d["msg_self"])
def l_guard_buy(d):
    pct("礼物",d["username"],"购买了",d["num"],"个",d["gift_name"])
def l_user_toast_msg(d):
    pct("提示",d["toast_msg"])
def l_widget_banner(d):
    for wi in d["widget_list"]:
        if d["widget_list"][wi]is None:continue
        pct("小部件",f"key:{wi}","id",d["widget_list"][wi]["id"],"标题:",d["widget_list"][wi]["title"])
def l_super_chat_entrance(d):
    if d["status"]==0: pct("信息","关闭醒目留言入口")
    else:
        log.debug(f"status: {d['status']}")
        pct("支持","未知的'SUPER_CHAT_ENTRANCE'status数字:",d["status"])
        raise SavePack("未知的status")
def l_room_skin_msg(d):
    pct("信息","直播间皮肤更新","id:",d["skin_id"],",status:",d["status"],",结束时间:",time.strftime(TIMEFORMAT,time.gmtime(d["end_time"])),",当前时间:",time.strftime(TIMEFORMAT,time.gmtime(d["current_time"])))
def l_live_multi_view_change(d):
    pct("信息","LIVE_MULTI_VIEW_CHANGE",d)
    raise SavePack("未知数据包")
def l_popularity_red_pocket_new(d):
    pct("通知",d["uname"],d["action"],"价值",d["price"],"电池的",d["gift_name"])
def l_popularity_red_pocket_start(d):
    if d["danmu"]not in swd:
        swd.append(d["danmu"])
        pct("屏蔽","屏蔽词增加:",d["danmu"])
def l_like_info_v3_update(d):
    pct("计数","点赞点击数量:",d["click_count"])
def l_like_info_v3_click(d):
    pct("交互",d["uname"],d["like_text"])
def l_like_info_v3_notice(d):
    s=False
    for i in d["content_segments"]:
        t=i["type"]
        if t==1: pct("通知",i["text"])
        else:
            pct("支持","不支持的点赞通知类型",t)
            s=True
    if s:raise SavePack(f"未知点赞通知类型:{t}")
def l_popular_rank_changed(d):
    pct("排行","人气榜第",d["rank"],"名")
def l_area_rank_changed(d):
    pct("排行",d["rank_name"],"第",d["rank"],"名")
def l_rank_changed(d):
    pct("排行",d["rank_name_by_type"],f"rank_type:{d['rank_type']},rank:{d['rank']}")# 无法确定rank与实际排名相关，有数据包表明这是不同的
def l_revenue_rank_changed(d):
    pct("排行",d["rank_name"],"第",d["rank"],"名")
def l_dm_interaction(d):
    p="交互合并"
    n=json.loads(d["data"])
    t=d["type"]
    if t==102:
        for c in n["combo"]:
            pct(p,c["guide"],c["content"],"×"+str(c["cnt"]))
    elif t==104:
        pct(p,n["cnt"],n["suffix_text"],"gift_id:",n["gift_id"])
    elif t==103 or t==105 or t==106:
        pct(p,n["cnt"],n["suffix_text"])
    else:
        log.debug(f"未知的交互合并类型: {t}")
        raise SavePack("交互合并类型")
def l_pk_battle_pre(d):
    pass
def l_pk_battle_pre_new(d):
    pct("PK","PK即将开始",f"id:{d['pk_id']}",f"s:{d['pk_status']}","对方直播间",d["data"]["room_id"],"昵称:",d["data"]["uname"])
def l_pk_battle_start(d):
    pass
def l_pk_battle_start_new(d):
    a=d["data"]
    pct("PK","PK开始",f"id:{d['pk_id']}",f"s:{d['pk_status']}","计数名称:",a["pk_votes_name"],f"增量:{a['pk_votes_add']}")
def l_pk_battle_process(d):
    pass
def l_pk_battle_process_new(d):
    a=d["data"]
    i=a["init_info"]
    m=a["match_info"]
    pct("PK","计数更新",f"id:{d['pk_id']}",f"s:{d['pk_status']}","直播间",i["room_id"],"已有",i["votes"],"票，直播间",m["room_id"],"已有",m["votes"],"票")
def l_pk_battle_final_process(d):
    pct("PK","PK结束流程变化",f"id:{d['pk_id']}",f"s:{d['pk_status']}")
def l_pk_battle_end(d):
    a=d["data"]
    i=a["init_info"]
    m=a["match_info"]
    pct("PK","PK结束",f"id:{d['pk_id']}",f"s:{d['pk_status']}","直播间",i["room_id"],"获得",i["votes"],"票，直播间",m["room_id"],"获得",m["votes"],"票")
def l_pk_battle_settle(d):
    pass
def l_pk_battle_settle_v2(d):
    a=d["data"]
    pct("PK","PK结算",f"id:{d['pk_id']}",f"s:{d['pk_status']}","主播获得",a["result_info"]["pk_votes"],a["result_info"]["pk_votes_name"])
def l_pk_battle_settle_new(p):
    pct("PK","进入惩罚时间",f"id:{p['pk_id']}",f"s:{p['pk_status']}")
def l_pk_battle_video_punish_begin(p):
    pct("PK","进入惩罚时间",f"id:{p['pk_id']}",f"s:{p['pk_status']}")
def l_pk_battle_punish_end(p):
    pct("PK","惩罚时间结束",f"id:{p['pk_id']}",f"s:{p['pk_status']}")
def l_pk_battle_video_punish_end(p):
    pct("PK","惩罚时间结束",f"id:{p['pk_id']}",f"s:{p['pk_status']}")
def l_recommend_card(d,s):# s已弃用
    pct("广告","推荐卡片","推荐数量:",len(d["recommend_list"]),"更新数量:",len(d["update_list"]))
def l_goto_buy_flow(d):
    pct("广告",d["text"])
def l_hot_buy_num(d):
    pct("广告","商品id",d["goods_id"],"热抢数量",d["num"])
def l_log_in_notice(d):
    pct("需要登录",d["notice_msg"])
def l_guard_honor_thousand(d):
    pass
def l_gift_star_process(d):
    pct("提示","礼物星球",f"status:{d['status']}",d["tip"])
def l_anchor_lot_checkstatus(d):
    pct("天选时刻","状态更新",f"id:{d['id']},status:{d['status']},uid:{d['uid']}")
def l_anchor_lot_start(d):
    pct("天选时刻",d["award_name"],f"{d['award_num']}人",f'''发送"{d['danmu']}"参与,需要"{d['require_text']}"''',f"id:{d['id']}",f"最大时间{d['max_time']}秒,剩余{d['time']}秒")
def l_anchor_lot_end(d):
    pct("天选时刻","id为",d["id"],"的天选时刻已结束")
def l_anchor_lot_award(d):
    pct("天选时刻",d["award_name"],f"{d['award_num']}人","已开奖",f"id:{d['id']}",f"中奖用户数量{len(d['award_users'])}")
def l_anchor_lot_notice(d):
    if d["notice_type"]!=1:
        pct("支持","天选时刻类型为:",d["notice_type"])
        raise SavePack("未知的天选通知类型")
    c=d["lottery_card"]
    pct("天选时刻","通知卡",c["title"])
def l_anchor_normal_notify(d):
    pct("通知","推荐",f"type:{d['type']},show_type:{d['show_type']}",d["info"]["content"])
def l_popular_rank_guide_card(d):
    h="提示"
    pct(h,d["title"])
    pct(h,d["sub_text"])
    pct(h,d["popup_title"])
def l_anchor_ecology_living_dialog(d):
    h="对话框"
    z="支持"
    s=False
    sp=lambda i:str(i["show_platform"])+" "
    pct(h,"标题:",d["dialog_title"])
    for i in d["dialog_message_list"]:
        if i["type"]==1: pct(h,f"{i['label']}：{i['content']}")
        else:
            pct(z,"未知对话框内容类型",i["type"])
            s=True
    for i in d["dialog_tip_list"]:
        t=sp(i)
        for i1 in i["message_list"]:
            if i1["type"]in[1,2]:t+=i1["content"]
            else:s=True
        pct(h,"提示:",t)
    for i in d["dialog_button_list"]:
        if i["button_action"]==1: pct(h,"[按钮:关闭窗口]",i["button_text"])
        else:s=True
    if s:raise SavePack("对话框有某个类型未知")
def l_cut_off_v2(d):
    z="支持"
    if d["cut_off_version"]!=1:
        pct(z,"不支持的切断直播间数据")
        raise SavePack("切断直播间")
    cut=d["cut_off_data"]
    h="直播"
    s=False
    sp=lambda i:str(i["show_platform"])+" "
    pct(h,"窗口标题:",cut["cut_off_title"])
    for i in cut["cut_off_message_list"]:
        if i["type"]==1: pct(h,f"{i['label']}：{i['content']}")
        else:
            pct(z,"未知对话框内容类型",i["type"])
            s=True
    for i in cut["cut_off_tip_list"]:
        t=sp(i)
        for i1 in i["message_list"]:
            if i1["type"]in[1,2]:t+=i1["content"]
            else:s=True
        pct(h,"提示:",t)
    for i in cut["cut_off_button_list"]:
        if i["button_action"]==1: pct(h,"[按钮:关闭窗口]",i["button_text"])
        else:s=True
    if s:raise SavePack("对话框有某个类型未知")
def l_room_content_audit_report(d):
    pct("直播","内容审核报告:",d["audit_reason"])
def l_sys_msg(p):
    pct("系统消息",p["msg"])
def l_play_tag(d):
    pct("直播","进度条标签",f"id:{d['tag_id']} 时间戳:{d['timestamp']} 类型: {d['type']}")
def l_chg_rank_refresh(d):
    pass
def l_popularity_rank_tab_chg(d):
    pass
def l_anchor_broadcast(d):
    pct("提示",d["sender"],d["msg"])
def l_anchor_helper_danmu(d):
    pct("提示",d["sender"],d["msg"])
def l_other_slice_loading_result(d):
    for i in d["data"]:
        pct("事件","剪辑片段数据","开始于:",i["start_time"],",结束于:",i["end_time"],",片段视频流:",i["stream"])
# 命令处理调用处(结束)

def get_SESSDATA(s:str)->str|None:# 获取登录会话标识
    print("警告: 错误记录文件会自动记录命令行参数，其中有SESSDATA数据。")
    rs=re.compile(r"(?:^|.*;\s*)SESSDATA\s*\=\s*([^;]*).*$")
    p=Path(s)
    if p.is_file():
        if p.stat().st_size>65536:
            print("[错误] 会话文件过大")
            raise ValueError("file large")
        fts=p.read_text().splitlines()
        for ft in fts:
            rst=rs.search(ft)# 支持使用Cookie头内容或之类的数据
            if(rst):return rst[1]
            ftt=ft.split("\t")
            if len(fts)==1 and len(ftt)==1:return ftt[0]# 如果只有1行且分割后只有1个数据,直接返回这个数据,否则试着按照cookie.txt解析数据
            if ftt[0]!=".bilibili.com"or ftt[-2]!="SESSDATA":continue
            return ftt[-1]
        if not len(fts):raise ValueError("The file has no items.")
        print("[警告] 未找到SESSDATA")
        return None
    return s

def pararg(aarg:list[dict]|tuple[dict,...]=None,*,args:list=None,desc:str=None,epil:str=None)->argparse.Namespace:
    """命令行参数解析"""
    global DEBUG
    global runoptions
    if runoptions:raise RuntimeError("检测到已进行过一次命令行参数获取")
    de="哔哩哔哩直播信息流处理\n允许使用@来引入参数文件\n默认在文件夹下会附带bili_live_ws.md来提供额外信息"
    ep="关于登录信息的使用可查看md的参数部分。"
    if desc:
        de+="\n;其它模块提供的信息:\n"+str(desc)
    if epil:
        ep+="\n*"+str(epil)
    parser=ArgsParser(usage="%(prog)s [options] roomid",description=de,epilog=ep,formatter_class=argparse.RawDescriptionHelpFormatter,fromfile_prefix_chars="@")
    parser.add_argument("roomid",help="直播间ID",type=int,default=23058)
    parser.add_argument("-d","--debug",help="开启调试模式",action="store_true")
    parser.add_argument("--sessdata",help="使用登录会话标识",type=get_SESSDATA,metavar="SESSDATA|FILE")
    parser.add_argument("--uid",help="用户UID，使用SESSDATA时必须",type=int,default=0)
    parser.add_argument("--no-print-enable",help="不打印不支持的信息",action="store_true")
    parser.add_argument("--pack-error-no-exit",help="数据包处理异常时不退出",action="store_false")
    parser.add_argument("--no-auto-import-cmd-handle",help="阻止自动导入额外的命令处理",action="store_false",dest="atirch")
    dbg=parser.add_argument_group("调试功能")
    dbg.add_argument("-u","--save-unknow-datapack",help="保存未知的数据包",action="store_true")
    dbg.add_argument("-C","--print-pack-count",help="打印数据包计数",action="store_true")
    dbg.add_argument("-c","--count-cmd",help="对某个cmd进行计数",action="append",metavar="CMD",default=[])
    dbg.add_argument("-s","--save-cmd",help="保存某个cmd数据包",action="append",metavar="CMD",default=[])
    # 关闭一个或多个cmd显示
    cmd=parser.add_argument_group("关闭某个cmd的显示")
    cmd.add_argument("--no-interact-word",help="关闭直播间交互信息",action="store_true")
    cmd.add_argument("--no-enter-room",help="关闭进入直播间信息。与交互信息关联",action="store_true")
    cmd.add_argument("--no-entry-effect",help="关闭进场信息",action="store_true")
    cmd.add_argument("--no-send-gift",help="关闭礼物信息",action="store_true")
    cmd.add_argument("--no-combo-send",help="关闭组合礼物信息",action="store_true")
    cmd.add_argument("--no-watched-change",help="关闭看过信息",action="store_true")
    cmd.add_argument("--no-super-chat-message",help="关闭醒目留言信息",action="store_true")
    cmd.add_argument("--no-event",help="关闭归类为事件的信息",action="store_true")
    cmd.add_argument("--no-live-interactive-game",help="关闭特殊数据格式弹幕",action="store_true")
    cmd.add_argument("--no-stop-live-room-list",help="关闭停止直播的房间列表信息",action="store_true")
    cmd.add_argument("--no-danmu-aggregation",help="关闭弹幕聚集信息",action="store_true")
    cmd.add_argument("--no-online-rank-count",help="关闭高能用户计数信息",action="store_true")
    cmd.add_argument("--no-voice-join-list",help="关闭连麦列表信息",action="store_true")
    cmd.add_argument("--no-online-rank-top3",help="关闭前三个第一次成为高能用户信息",action="store_true")
    cmd.add_argument("--no-voice-join-status",help="关闭连麦状态信息",action="store_true")
    cmd.add_argument("--no-online-rank-v2",help="关闭高能用户列表信息(暂定)",action="store_true")
    cmd.add_argument("--no-hot-rank-settlement",help="关闭热门通知信息",action="store_true")
    cmd.add_argument("--no-common-notice-danmaku",help="关闭普通通知信息",action="store_true")
    cmd.add_argument("--no-notice-msg",help="关闭公告信息",action="store_true")
    cmd.add_argument("--no-guard-buy",help="关闭购买舰队信息",action="store_true")
    cmd.add_argument("--no-user-toast-msg",help="关闭续费舰队信息",action="store_true")
    cmd.add_argument("--no-widget-banner",help="关闭小部件信息",action="store_true")
    cmd.add_argument("--no-super-chat-entrance",help="关醒目留言入口信息",action="store_true")
    cmd.add_argument("--no-popularity-red-pocket",help="关闭红包信息",action="store_true")
    cmd.add_argument("--no-like-info-update",help="关闭点赞计数信息",action="store_true")
    cmd.add_argument("--no-like-info-notice",help="关闭点赞通知信息",action="store_true")
    cmd.add_argument("--no-rank-changed",help="关闭所有全站排行榜更新",action="store_true")
    cmd.add_argument("--no-dm-interaction",help="关闭交互合并信息",action="store_true")
    cmd.add_argument("--no-pk-message",help="关闭全部PK信息",action="store_true")
    cmd.add_argument("--no-pk-battle-process",help="关闭PK过程信息",action="store_true")
    cmd.add_argument("--no-recommend-card",help="关闭推荐卡片信息",action="store_true")
    cmd.add_argument("--no-buy-flow-info",help="关闭推荐商品信息",action="store_true")
    cmd.add_argument("--no-guard-honor-thousand",help="关闭千舰主播增减信息",action="store_true")
    cmd.add_argument("--no-gift-star-process",help="关闭礼物星球进度信息",action="store_true")
    cmd.add_argument("--no-anchor-lot",help="关闭天选时刻信息",action="store_true")
    cmd.add_argument("--no-anchor-normal-notify",help="关闭推荐通知信息",action="store_true")
    cmd.add_argument("--no-popular-rank-guide-card",help="关闭冲榜提示信息",action="store_true")
    cmd.add_argument("--no-room-content-audit-report",help="关闭直播间内容审核结果信息",action="store_true")
    cmd.add_argument("--no-sys-msg",help="关闭系统消息信息",action="store_true")
    cmd.add_argument("--no-play-tag",help="关闭进度条标签信息",action="store_true")
    # 附加功能
    parser.add_argument("-S","--shielding-words",help="屏蔽词(完全匹配)",type=argparse.FileType("rt"),metavar="FILE")
    parser.add_argument("-B","--blocking-rules",help="屏蔽规则",type=argparse.FileType("rt"),metavar="FILE")
    parser.add_argument("--add-time",help="建议命令处理添加时间显示",nargs="?",const="datetime",choices=["datetime","time","timestamp"])
    # 处理其它模块的命令行参数需求
    def setit(n):# 只可在下面的循环中使用
        ov=ari.get(n)
        if ov is None:return
        aro[n]=ov
    if isinstance(aarg,(list,tuple)):
        log.debug("其它模块设置参数:")
        ota=parser.add_argument_group("其它模块设置的参数")
        for ari in aarg:
            if not isinstance(ari,dict):continue
            arin=ari.get("name")
            if not isinstance(arin,str):continue
            if arin[0:2]!="--": arin="--"+arin
            aro={}# 参数组
            setit("help")
            setit("action")
            setit("const")
            setit("default")
            setit("type")
            setit("choices")
            setit("required")
            setit("metavar")
            setit("dest")
            log.debug(str(ota.add_argument(arin,**aro)))
            other_args.append(arin)
    args=parser.parse_args(args)
    runoptions=args
    log.debug(f"命令行参数: {args}")
    DEBUG=DEBUG or args.debug
    return args

def main():# 启动
    args=pararg()
    if DEBUG:
        print("版本信息:",VERSIONINFO)
        print("命令行选项:",args)
        print("启动时间戳:",starttime)
        set_log()
        set_wslog()
    roomid=args.roomid
    print("直播间ID:",roomid)
    log.info("处理屏蔽数据文件")
    if args.shielding_words: shielding_words(args.shielding_words)
    if args.blocking_rules: blocking_rules(args.blocking_rules)
    if args.atirch:
        r_ich=import_cmd_handle()
        idp("导入命令处理的结果:",r_ich)
    print("连接直播间…")
    try:
        start(roomid,args)
    except KeyboardInterrupt:
        print("关闭连接")
        if DEBUG or args.print_pack_count:
            print("被测试的cmd计数:")
            print_test_pack_count()
        sys.exit(0)
log.info(f"当前运行路径: {Path.cwd()}")
if __name__=="__main__":
    print("=[哔哩哔哩直播信息流]=")
    log.info("文件已作为顶层入口")
    main()
