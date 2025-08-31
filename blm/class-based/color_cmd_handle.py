"""带有颜色的cmd处理
"""

import blm
import re,time,json,asyncio
from typing import Any
from blw import SavePack,TIMEFORMAT,bst,log
from cmd_pb.protobuf_cmd_handle import ParseProtobufPack

__all__=[
    "cbt","cfc","cfb",
    "BLMColor",
    "CoreCmdHandle","FrequentCmdHandle","RareCmdHandle","PKCmdHandle",
    "AllCmdHandle",
    "DF","DB","DD","DI","DU","DC",
    "EB","ED","EI","EU","EC",
    "CD",# iter…
    "BD",#iter…
    # …
]

def cbt(n:str)->str:
    """生成颜色操作，终端需要支持ANSI编码"""
    return f"\33[{n}m"
def cfc(n:str)->str:
    """生成前景颜色，终端需要支持 ANSI 88/256 颜色"""
    return f"\33[38;5;{n}m"
def cfb(n:str)->str:
    """生成背景颜色，终端需要支持 ANSI 88/256 颜色"""
    return f"\33[48;5;{n}m"

# =定义颜色常量=
DF=cbt(0)# 重置全部
DB=cbt(1)# 加粗
DD=cbt(2)# 变暗
DI=cbt(3)# 斜体
DU=cbt(4)# 下划线
DC=cbt(5)# 闪烁
# 重置
EB=cbt(21)# 加粗
ED=cbt(22)# 变暗
EI=cbt(23)# 斜体
EU=cbt(24)# 下划线
EC=cbt(25)# 闪烁
# 字体颜色
CD=cbt(39)# 默认
C_00=cbt(30)# 黑
C_01=cbt(31)# 红
C_02=cbt(32)# 绿
C_03=cbt(33)# 黄
C_04=cbt(34)# 蓝
C_05=cbt(35)# 品红
C_06=cbt(36)# 青
C_07=cbt(37)# 浅灰
C_10=cbt(90)# 深灰
C_11=cbt(91)# 亮红
C_12=cbt(92)# 亮绿
C_13=cbt(93)# 亮黄
C_14=cbt(94)# 浅蓝
C_15=cbt(95)# 浅品红
C_16=cbt(96)# 亮青
C_17=cbt(97)# 白
# 背景颜色
BD=cbt(49)# 默认
B_00=cbt(40)# 黑
B_01=cbt(41)# 红
B_02=cbt(42)# 绿
B_03=cbt(43)# 黄
B_04=cbt(44)# 蓝
B_05=cbt(45)# 品红
B_06=cbt(46)# 青
B_07=cbt(47)# 浅灰
B_10=cbt(100)# 深灰
B_11=cbt(101)# 亮红
B_12=cbt(102)# 亮绿
B_13=cbt(103)# 亮黄
B_14=cbt(104)# 浅蓝
B_15=cbt(105)# 浅品红
B_16=cbt(106)# 亮青
B_17=cbt(107)# 白

# 对某种情况统一使用的颜色,命名规则: "T"+标记
TRTG=C_04# 最前面的那个[]的颜色
TUSR=C_03# 用户名
TNUM=C_06# 数字、数量
TRMI=C_14# 房间号
TVER=C_02# cmd版本
TKEY=cfc(27)# key
TSTR=cfc(28)# string
TBOL=cfc(29)# boolean

# 正则表达式
RGPL=re.compile("<%(.+?)%>")

class BLMColor(blm.BiliLiveExp):
    """带有颜色输出的框架"""

    def cbt(self,*a)->str:
        """调用模块的cfb"""
        return cbt(*a)
    def cfc(self,*a)->str:
        """调用模块的cfc"""
        return cfc(*a)
    def cfb(self,*a)->str:
        """调用模块的cfb"""
        return cfb(*a)

    def cuse(self,msg:str)->str:
        """渲染用户颜色"""
        return RGPL.sub(TUSR+"\\1"+CD,msg)

    def pct(self,name:str,*d:Any,b:str="",**t:"print参数")->None:
        """统一按照一定样式输出cmd处理后文本
        额外拥有添加时间的功能
        可用位置参数b来定义背景色(理论上)
        """
        if not isinstance(name,str):
            raise TypeError("name必须为str")
        if isinstance(self.args.add_time,str):
            at=self.args.add_time
            if at=="datetime":
                m=time.strftime(TIMEFORMAT)
            elif at=="time":
                m=time.strftime("%H:%M:%S")
            elif at=="timestamp":
                m=str(int(time.time()))
            else:
                m=""
            if m:
                self.p(f"{b}{C_16}{m}{CD} {TRTG}{DB}[{name}]{DF}{b}",*d,DF,**t)
                return
        self.p(f"{b}{TRTG}{DB}[{name}]{DF}{b}",*d,DF,**t)

class CoreCmdHandle(BLMColor,blm.BiliLiveBlackWordExp):
    """核心cmd处理"""

    cmd_args=blm.add_no_cmd_args([],{
        "INTERACT_WORD":"交互",
        "enter-room":"进入直播间",
    })

    def print_popularity(self,data:bytes)->int:
        """打印人气值"""
        hp:int=self.compute_popularity(data)
        txt=f"{TNUM}{hp}{CD}"
        if self.debug:
            txt+=f" [{bst(data,',')}]"
        if hp==1:
            txt+=f" {C_05}(未开播或不显示){CD}"
        self.pct("人气",txt,b=B_10)
        return hp

    def on_no_support_cmd_tip(s,cmd:str)->None:
        """带颜色的不支持提示"""
        s.pct("支持",f"{B_07}{C_01}不支持'{cmd}'命令{DF}")

    def l_DANMU_MSG(s,p):
        """弹幕"""
        d:list=p["info"]
        if s.is_blocked_msg(d[1]):
            return
        tc=""
        if s.up_uid==d[2][0]:
            tc+=f"{C_01}(主播){CD}"
        if d[2][2]==1:
            tc+=f"{C_13}(房){CD}"
        s.pct("弹幕",f"{tc}{TUSR}{d[2][1]}{CD}:{C_07}",d[1])
    def l_INTERACT_WORD(s,p):
        """交互"""
        if s.args.no_INTERACT_WORD:
            return
        info="交互"
        d=p["data"]
        mt=d["msg_type"]
        nm=f"{TUSR}{d['uname']}{CD}"
        if mt==1:
            if s.args.no_enter_room:return
            s.pct(info,nm,"进入直播间")
        elif mt==2:
            s.pct(info,nm,"关注直播间")
        elif mt==3:
            s.pct(info,nm,"分享直播间")
        else:
            t=f"未知的交互类型: {d['msg_type']}"
            log.debug(t)
            if not s.args.no_print_enable:
                s.pct("支持",t)
            raise SavePack("未知的交互类型")
    def l_ROOM_CHANGE(s,p):
        """直播间更新"""
        d=p["data"]
        s.pct("直播",f"分区:{C_06} {d['parent_area_name']} {C_02}>{C_06} {d['area_name']} {CD}标题: {C_06}{d['title']}{DF}",b=B_05)
    def l_LIVE(s,p):
        """开始直播"""
        s.pct("直播",f"直播间 {TRMI}{p['roomid']}{CD} 开始直播{DF}",b=B_05)
    def l_PREPARING(s,p):
        """结束直播"""
        s.pct("直播",f"直播间 {TRMI}{p['roomid']}{CD} 结束直播{DF}",b=B_05)
    def l_ROOM_REAL_TIME_MESSAGE_UPDATE(s,p):
        """数据更新"""
        d=p["data"]
        s.pct("信息",f"{TRMI}{d['roomid']}{CD} 直播间 {TNUM}{d['fans']}{CD} 粉丝 {TNUM}{d['fans_club']}{CD} 点亮粉丝勋章")
    def l_ROOM_BLOCK_MSG(s,p):
        """用户被禁言"""
        s.pct("直播",f"用户 {TUSR}{p['uname']}{CD} 已被禁言")
    def l_CUT_OFF(s,p):
        """切断"""
        s.pct("直播",f"直播间 {TRMI}{p['room_id']}{CD} 被警告: {B_01}{p['msg']}{BD}")
    def l_ROOM_LOCK(s,p):
        """封禁"""
        s.pct("直播",f"直播间 {TRMI}{p['roomid']}{CD} 被封禁，解除时间: {p['expire']}")
    def l_ROOM_ADMINS(s,p):
        """房管列表"""
        s.pct("直播",f"房管列表: len({len(p['uids'])})")
    def l_room_admin_entrance(s,p):
        """添加房管"""
        s.pct("直播",f"添加 {TNUM}{p['uid']}{CD} 为房管，消息: {TSTR}{p['msg']}{CD}")
    def l_ROOM_ADMIN_REVOKE(s,p):
        """撤销房管"""
        s.pct("直播",f"撤销 {TNUM}{p['uid']}{CD} 的房管权限，消息: {TSTR}{p['msg']}{CD}")
    def l_CHANGE_ROOM_INFO(s,p):
        """背景更换"""
        s.pct("直播",f"直播间 {TRMI}{p['roomid']}{CD} 信息变更 背景图: {DU}{p['background']}{EU}")
    def l_WARNING(s,p):
        """警告"""
        s.pct("警告",f"{C_03}{p['msg']}",b=B_01)
    def l_ROOM_CONTENT_AUDIT_REPORT(s,p):
        """直播间内容审核结果(主要是审核标题)"""
        d=p["data"]
        s.pct("直播",f"直播间{TRMI}{d['room_id']}{CD}标题 {TSTR}{d['audit_title']}{CD} 审核结果: {C_07}{d['audit_reason']}{CD} ,{TKEY}审核内容类型:{TNUM}{d['audit_content_type']}{CD},{TKEY}审核类型:{TNUM}{d['audit_status']}{CD}")
    def l_PLAYURL_RELOAD(s,p):
        """播放链接刷新"""
        s.pct("直播",f"{DI}播放链接刷新{DF}")

class FrequentCmdHandle(BLMColor,blm.BiliLiveBlackWordExp):
    """频繁常见下发数据包的处理"""

    cmd_args=blm.add_no_cmd_args([],{
        "ENTRY_EFFECT":"进场",
        "SEND_GIFT":"礼物",
        "COMBO_SEND":"组合礼物",
        "WATCHED_CHANGE":"看过",
        "SUPER_CHAT_MESSAGE":"醒目留言",
        "SUPER_CHAT_MESSAGE_DELETE":"醒目留言删除",
        "STOP_LIVE_ROOM_LIST":"停止直播的房间列表",
        "ONLINE_RANK_V2":"在线排行榜",
        "NOTICE_MSG":"广播通知",
        "LIKE_INFO_V3_UPDATE":"点赞数量更新",
        "LIKE_INFO_V3_CLICK":"点赞点击",
    })

    def l_ENTRY_EFFECT(s,p):
        """进场"""
        if s.args.no_ENTRY_EFFECT:
            return
        d=p["data"]
        s.pct("进场",s.cuse(d["copy_writing"]))
    def l_ENTRY_EFFECT_MUST_RECEIVE(s,p):
        """必须接受的进场信息"""
        if s.args.no_ENTRY_EFFECT:# 允许不显示
            return
        d=p["data"]
        s.pct("进场",f"{C_11}(必须显示){CD}",s.cuse(d["copy_writing"]))
    def l_SEND_GIFT(s,p):
        """礼物"""
        if s.args.no_SEND_GIFT:
            return
        d=p["data"]
        s.pct("礼物",f'{TUSR}{d["uname"]}{CD}',d["action"],d["giftName"],TNUM+"×",d["num"])
    def l_COMBO_SEND(s,p):
        """组合礼物"""
        if s.args.no_COMBO_SEND:
            return
        d=p["data"]
        s.pct("礼物",f'{TUSR}{d["uname"]}{CD}',d["action"],d["gift_name"],TNUM+"×",d["total_num"])
    def l_WATCHED_CHANGE(s,p):
        """看过"""
        if s.args.no_WATCHED_CHANGE:
            return
        d=p["data"]
        if s.debug:
            s.pct("观看",f"{TNUM}{d['num']}{CD} 人看过; {TKEY}text_large: {TSTR}{d['text_large']}")
        else:
            s.pct("观看",f"{TNUM}{d['num']}{CD} 人看过")
    def l_SUPER_CHAT_MESSAGE(s,p):
        """醒目留言"""
        if s.args.no_SUPER_CHAT_MESSAGE:
            return
        d=p["data"]
        s.pct("留言",f"{TUSR}{d['user_info']['uname']}{CD}({C_11}￥{d['price']}{CD}):{C_07}",d["message"])
    def l_SUPER_CHAT_MESSAGE_JPN(s,p):
        """醒目留言日语"""
        if s.args.no_SUPER_CHAT_MESSAGE:
            return
        d=p["data"]
        s.pct("留言","日语"+C_07,d.get("message_jpg"))
    def l_SUPER_CHAT_MESSAGE_DELETE(s,p):
        """醒目留言删除"""
        if s.args.no_SUPER_CHAT_MESSAGE_DELETE:
            return
        s.pct("留言","醒目留言删除:",p["data"]["ids"])
    def l_LIVE_INTERACTIVE_GAME(s,p):
        """类似弹幕，未确定"""
        d=p["data"]
        m=d["msg"]
        if m in s.swd:
            return
        for b in s.brs:
            if b.search(m):
                return
        s.pct("弹幕(LIG)",f"{d['uname']}:",m)
    def l_STOP_LIVE_ROOM_LIST(s,p):
        """停止直播的房间列表"""
        if s.args.no_STOP_LIVE_ROOM_LIST:
            return
        d=p["data"]
        s.pct("停播","停止直播的房间列表:",f"len({len(d['room_id_list'])})")
    def l_DANMU_AGGREGATION(s,p):
        """弹幕聚集"""
        pass
    def l_ONLINE_RANK_COUNT(s,p):
        """在线榜计数"""
        d=p["data"]
        olc=""
        if "online_count" in d:
            olc=f"在线计数: {TNUM}{d['online_count']}{CD}"
        s.pct("计数",f"高能用户计数: {TNUM}{d['count']}{CD}",olc)
    def l_ONLINE_RANK_V2(s,p):
        """在线排行"""
        if s.args.no_ONLINE_RANK_V2:
            return
        d=p["data"]
        rt=d["rank_type"]
        if rt=="gold-rank":
            s.pct("排行","高能用户部分列表:",f"len({len(d['list'])})")
        elif rt=="online_rank":
            l=[]
            for i in d["online_list"]:
                l.append(f"{C_11}({i['rank']}){TUSR}{i['uname']}{CD}")
            s.pct("排行","在线用户部分列表:",f"{'、'.join(l)}")
        else:
            nt="未知的排行类型"
            log.debug(f"{nt}: '{d['rank_type']}'")
            if not s.args.no_print_enable:
                s.pct("支持",nt+":",d["rank_type"])
            raise SavePack(nt)
    def l_NOTICE_MSG(s,p):
        """广播通知"""
        if s.args.no_NOTICE_MSG:
            return
        msg=s.cuse(p["msg_self"])
        if "name" in p:
            s.pct("公告",p["name"],C_04+"=>"+CD,msg)
        else:
            s.pct("公告",msg)
    def l_LIKE_INFO_V3_UPDATE(s,p):
        """点赞数量"""
        if s.args.no_LIKE_INFO_V3_UPDATE:
            return
        s.pct("计数","点赞点击数量:"+TNUM,p["data"]["click_count"])
    def l_LIKE_INFO_V3_CLICK(s,p):
        """点赞点击"""
        if s.args.no_LIKE_INFO_V3_CLICK:
            return
        d=p["data"]
        s.pct("交互",f"{TUSR}{d['uname']}{CD} {d['like_text']}")

class ConditionsFrequentCmdHandle(BLMColor):
    """特定条件时高频下发的数据包处理"""

    cmd_args=blm.add_no_cmd_args([],{
        "WIDGET_BANNER":"小部件",
        "LIVE_MULTI_VIEW_CHANGE":"多个直播视角信息更新",
        "DM_INTERACTION":"交互合并",
        "UNIVERSAL_EVENT_GIFT":"连线礼物累计变化",
    })

    clr_dm_inter_task:asyncio.Task=None
    """清除已过期的交互合并任务"""
    dm_inter_list:dict[int,dict[str,int]]={}
    """交互合并暂存"""

    def l_WIDGET_BANNER(s,p):
        """小部件"""
        if s.args.no_WIDGET_BANNER:return
        d=p["data"]
        for wi in d["widget_list"]:
            wic=d["widget_list"][wi]
            if wic is None:
                continue
            s.pct("小部件",f"{TKEY}key:{TSTR}{wi}{CD} id {wic['id']} 标题: {TSTR}{wic['title']}{CD}")
    def l_LIVE_MULTI_VIEW_CHANGE(s,p):
        """多个直播视角信息更新"""
        if s.args.no_LIVE_MULTI_VIEW_CHANGE:return
        s.pct("信息","LIVE_MULTI_VIEW_CHANGE",p["data"])
        raise SavePack("未知数据包")
    def l_LIVE_MULTI_VIEW_NEW_INFO(s,p):
        """多个直播视角信息更新"""
        if s.args.no_LIVE_MULTI_VIEW_CHANGE:return
        d=p["data"]
        if d["room_list"]is None:
            s.pct("信息","直播多视角已结束")
        else:
            s.pct("信息","直播多视角",d['title'],f"{TSTR}{d['copy_writing']}{CD}",f"房间数量{TNUM}{len(d['room_list'])}{CD} 关系数量{TNUM}{len(d['relation_view'])}")
    async def clr_dm_inter(self)->None:
        """清理长时间无变化的信息"""
        d=self.dm_inter_list
        try:
            while True:
                await asyncio.sleep(60)
                t=int(time.time())
                dl=[]
                for k in d:
                    v=d[k]
                    if v["time"]>t-30:continue
                    dl.append(k)
                for n in dl:
                    del d[n]
                del dl
        except(KeyboardInterrupt,asyncio.CancelledError):
            pass
    def dm_inter_min(self,id:int,cnt:int)->bool:
        """控制交互合并的打印"""
        d=self.dm_inter_list
        def tm()->int:
            return int(time.time())
        if self.clr_dm_inter_task is None:
            self.clr_dm_inter_task=asyncio.create_task(self.clr_dm_inter(),name="清理不使用的交互合并id")
        if id not in d:
            d[id]={
                "time":tm(),
                "num":cnt
            }
            return False
        s=d[id]
        if s["num"]<cnt:
            s["time"]=tm()
            s["num"]=cnt
            return False
        if s["time"]<tm()-1:
            s["time"]=tm()
            s["num"]=cnt
            return False
        return True
    def l_DM_INTERACTION(s,p):
        """交互合并"""
        if s.args.no_DM_INTERACTION:return
        d=p["data"]
        h="交互合并"
        n=json.loads(d["data"])
        t=d["type"]
        if t==101:# 投票
            if s.dm_inter_min(d["id"],n["cnt"]):return
            tp=""
            for o in n["options"]:
                tp+=f" {TSTR}{o['desc']}{TNUM} ×{o['cnt']}{CD}({round(o['percent'],4)})"
            if n["audit_reason"]:
                tp+=f" {TKEY}审核结果: {TSTR}{n['audit_reason']}{CD}"
            s.pct(h,"投票",f"{TSTR}{n['question']}{CD}:",tp)
        elif t==102:# 弹幕
            for c in n["combo"]:
                if s.dm_inter_min(c["id"],c["cnt"]):return
                s.pct(h,f"{C_10}{c['guide']}{C_07}",c["content"],TNUM+"×"+str(c["cnt"]))
        elif t==104:# 送礼
            if s.dm_inter_min(d["id"],n["cnt"]):return
            s.pct(h,f"{TNUM}{n['cnt']}{C_10} {n['suffix_text']} {TKEY}gift_id: {TSTR}{n['gift_id']}")
        elif t==103 or t==105 or t==106:# 关注，分享，点赞
            if s.dm_inter_min(d["id"],n["cnt"]):return
            s.pct(h,f"{TNUM}{n['cnt']}{C_10} {n['suffix_text']}")
        else:
            log.debug(f"未知的交互合并类型: {t}")
            raise SavePack("交互合并类型")
    def l_UNIVERSAL_EVENT_GIFT(s,p):
        """连线礼物累计变化信息"""
        if s.args.no_UNIVERSAL_EVENT_GIFT:return
        n=p["data"]["info"]
        s.pct("信息",f"{TVER}(V1){CD}","连线礼物累计变化",f"样式id:{TSTR}{n['interact_template']['layout_id']}{CD},模板id:{TSTR}{n['interact_template']['template_id']}{CD}")
    def l_UNIVERSAL_EVENT_GIFT_V2(s,p):
        """连线礼物累计变化信息V2"""
        if s.args.no_UNIVERSAL_EVENT_GIFT:return
        d=p["data"]
        s.pct("信息",f"{TVER}(V2){CD}","连线礼物累计变化",f"连线主播:len({len(d['members'])})")

class RareCmdHandle(BLMColor):
    """低频少见特定条件的数据包处理"""

    cmd_args=blm.add_no_cmd_args([],{
        "HOT_RANK_SETTLEMENT":"热门通知",
        "COMMON_NOTICE_DANMAKU":"普通通知",
        "GUARD_BUY":"舰队购买",
        "USER_TOAST_MSG":"舰队续费",
        "SUPER_CHAT_ENTRANCE":"醒目留言入口变化",
        "rank-changed":"排行更新",
        "popularity-red-pocket":"红包相关",
        "LIKE_INFO_V3_NOTICE":"点赞通知",
        "GUARD_HONOR_THOUSAND":"千舰主播增减",
        "RECOMMEND_CARD":"推荐卡片",
        "GOTO_BUY_FLOW":"购买商品",
        "HOT_BUY_NUM":"热购数量",
        "GIFT_STAR_PROCESS":"礼物星球进度",
        "anchor-lot":"天选时刻",
        "ANCHOR_NORMAL_NOTIFY":"推荐提示",
        "POPULAR_RANK_GUIDE_CARD":"冲榜提示卡",
        "SYS_MSG":"系统消息",
        "PLAY_TAG":"直播进度条节点标签",
        "ANCHOR_BROADCAST":"直播小助手广播",
        "ANCHOR_HELPER_DANMU":"直播小助手弹幕",
        "OTHER_SLICE_LOADING_RESULT":"直播切片数据加载结果",
        "FANS_CLUB_POKE_GIFT_NOTICE":"粉丝团戳一戳要礼通知",
    })

    only_count_cmd=[
        "HOT_ROOM_NOTIFY",
    ]

    def l_LITTLE_TIPS(s,p):
        """某种提示，内容可能与使用的会话信息有关"""
        d=p["data"]
        s.pct("提示",f"{C_15}{d['msg']}")
    def l_LITTLE_MESSAGE_BOX(s,p):
        """弹框提示"""
        d=p["data"]
        s.pct("弹框",f"{B_04}{C_17}{d['msg']}{BD}")
    def l_HOT_RANK_SETTLEMENT(s,p):
        """热门通知"""
        if s.args.no_HOT_RANK_SETTLEMENT:return
        d=p["data"]
        s.pct("排行",d["dm_msg"])
    def l_HOT_RANK_SETTLEMENT_V2(s,p):
        """(同上)V2"""
        if s.args.no_HOT_RANK_SETTLEMENT:return
        d=p["data"]
    def l_COMMON_NOTICE_DANMAKU(s,p):
        """普通通知"""
        if s.args.no_COMMON_NOTICE_DANMAKU:return
        for cse in p["data"]["content_segments"]:
            cset=cse["type"]
            if cset==1:
                s.pct("通知",RGPL.sub(C_13+"\\1"+CD,cse["text"]))
            elif cset==2:
                s.pct("通知","图片:",f"{DU}{cse.get('img_url')}{EU}")
            elif cset==3:
                s.pct("通知",f"{TSTR}{cse['text']}{CD} ,链接: {DU}{cse.get('uri')}{EU}")
            else:
                s.pct("通知",C_07+DI+"无法展示的通知组件")
                log.debug(f"未知的通知组件类型: {cset}")
                raise SavePack("通知组件类型")
    def l_GUARD_BUY(s,p):
        """舰队购买"""
        if s.args.no_GUARD_BUY:return
        d=p["data"]
        s.pct("礼物",f"{TUSR}{d['username']}{CD} 购买了{TNUM}{d['num']}{CD}个 {d['gift_name']}")
    def l_USER_TOAST_MSG(s,p):
        """舰队续费"""
        if s.args.no_USER_TOAST_MSG:return
        d=p["data"]
        s.pct("提示",s.cuse(d["toast_msg"]))
    def l_USER_TOAST_MSG_V2(s,p):
        """(同上)"""
        if s.args.no_USER_TOAST_MSG:return
        d=p["data"]
    def l_SUPER_CHAT_ENTRANCE(s,p):
        """醒目留言入口变化"""
        if s.args.no_SUPER_CHAT_ENTRANCE:return
        d=p["data"]
        t=d["status"]
        if t==0:
            s.pct("信息","关闭醒目留言入口")
        elif t==1:
            s.pct("信息","开启醒目留言入口")
        else:
            log.debug(f"status: {t}")
            s.pct("支持",f"未知的'SUPER_CHAT_ENTRANCE'{TKEY}status{CD}数字:{TNUM}",t)
            raise SavePack("未知的status")
    def l_ROOM_SKIN_MSG(s,p):
        """直播间皮肤更新"""
        d=p["data"]
        s.pct("信息","直播间皮肤更新",f"{TKEY}id: {TSTR}{d['skin_id']}{CD} ,{TKEY}status: {TSTR}{d['status']}{CD}",",结束时间:",time.strftime(TIMEFORMAT,time.gmtime(d["end_time"])),",当前时间:",time.strftime(TIMEFORMAT,time.gmtime(d["current_time"])))
    def l_MESSAGEBOX_USER_GAIN_MEDAL(s,p):
        """获得粉丝勋章"""
        d=p["data"]
        s.pct("提示",f"{TUSR}{d['fan_name']}{CD} 获得粉丝勋章")
        s.pct("提示",f"提示标题: {d['msg_title']}")
        s.pct("提示",f"提示内容: {d['msg_content']}")
    def l_MESSAGEBOX_USER_MEDAL_CHANGE(s,p):
        """粉丝勋章更新"""
        d=p["data"]
        y=d["type"]
        if y==1:
            s.pct("提示",d["upper_bound_content"])
        elif y==2:
            s.pct("提示","重新点亮了勋章")
        else:
            z=f"未知的粉丝勋章更新类型: {y}"
            s.pct("支持",z)
            raise SavePack(z)
    def l_VOICE_JOIN_SWITCH(s,p):
        """连麦开关状态"""
        a=p["data"]["room_status"]
        if a==0:
            t="关闭"
        elif a==1:
            t="开启"
        else:
            s.pct("连麦",f"未知的连麦开关状态 {TNUM}{a}{CD}")
            raise SavePack("连麦开关状态")
        s.pct("连麦",f"{TVER}(V1){CD}",f"连麦开关状态: {t}")
    def l_VOICE_JOIN_SWITCH_V2(s,p):
        """连麦开关状态V2"""
        d=p["data"]
        a=d["room_status"]
        if a==0:
            t="关闭"
        elif a==1:
            t="开启"
        else:
            s.pct("连麦",f"未知的连麦开关状态 {TNUM}{a}{CD}")
            raise SavePack("连麦开关状态")
        s.pct("连麦",f"{TVER}(V2){CD}",f"连麦开关状态: {t} root状态:{TNUM}{d['root_status']}{CD},conn_type:{TNUM}{d['conn_type']}{CD}")
    def l_POPULAR_RANK_CHANGED(s,p):
        """人气排行榜更新(可能已弃用)"""
        if s.args.no_rank_changed:return
        d=p["data"]
        s.pct("排行","人气榜第",d["rank"],"名")
    def l_AREA_RANK_CHANGED(s,p):
        """大航海排行更新(可能已弃用)"""
        if s.args.no_rank_changed:return
        d=p["data"]
        s.pct("排行",d["rank_name"],"第",d["rank"],"名")
    def l_RANK_CHANGED(s,p):
        """人气榜"""
        if s.args.no_rank_changed:return
        d=p["data"]
        s.pct("排行",f"{TVER}(V1){CD}",d["rank_name_by_type"],f"{TKEY}rank_type:{TNUM}{d['rank_type']}{CD},{TKEY}rank:{TNUM}{d['rank']}{CD}")# 无法确定rank与实际排名相关，有数据包表明这是不同的
    def l_RANK_CHANGED_V2(s,p):
        """人气榜V2"""
        if s.args.no_rank_changed:return
        d=p["data"]
        s.pct("排行",f"{TVER}(V2){CD}",d["rank_name_by_type"],f"{TKEY}rank_type:{TNUM}{d['rank_type']}{CD},{TKEY}rank:{TNUM}{d['rank']}{CD}")# 无法确定rank与实际排名相关，有数据包表明这是不同的
    def l_REVENUE_RANK_CHANGED(s,p):
        """收入排行(机翻)"""
        if s.args.no_rank_changed:return
        d=p["data"]
        s.pct("排行",d["rank_name"],f"第 {TNUM}{d['rank']}{CD} 名")
    def l_POPULARITY_RED_POCKET_NEW(s,p):
        """新红包"""
        if s.args.no_popularity_red_pocket:return
        d=p["data"]
        s.pct("通知",f"{TUSR}{d['uname']}{CD} {d['action']} 价值 {TNUM}{d['price']}{CD} 电池的 {d['gift_name']}")
    def l_POPULARITY_RED_POCKET_V2_NEW(s,p):
        """(同上)"""
        if s.args.no_popularity_red_pocket:return
        d=p["data"]
    def l_POPULARITY_RED_POCKET_START(s,p):
        """红包开始"""
        if s.args.no_popularity_red_pocket:return
        d=p["data"]
        s.pct("提示","红包开始","发送特定弹幕参与")
    def l_POPULARITY_RED_POCKET_V2_START(s,p):
        """(同上)"""
        if s.args.no_popularity_red_pocket:return
        d=p["data"]
    def l_POPULARITY_RED_POCKET_WINNER_LIST(s,p):
        """红包结束，获得红包的列表"""
        if s.args.no_popularity_red_pocket:return
        d=p["data"]
        s.pct("提示","红包结束","奖励已结算")
    def l_POPULARITY_RED_POCKET_V2_WINNER_LIST(s,p):
        """(同上)"""
        if s.args.no_popularity_red_pocket:return
        d=p["data"]
    def l_LIKE_INFO_V3_NOTICE(s,p):
        """点赞通知"""
        if s.args.no_LIKE_INFO_V3_NOTICE:return
        d=p["data"]
        e=False
        for i in d["content_segments"]:
            t=i["type"]
            if t==1:
                s.pct("通知",i["text"])
            else:
                s.pct("支持","不支持的点赞通知类型",t)
                e=True
        if e:
            raise SavePack(f"未知点赞通知类型:{t}")
    def l_LOG_IN_NOTICE(s,p):
        """登录提示"""
        d=p["data"]
        s.pct("需要登录",d["notice_msg"],b=B_02)
    def l_GUARD_HONOR_THOUSAND(s,p):
        """千舰主播增减"""
        if s.args.no_GUARD_HONOR_THOUSAND:return
        d=p["data"]
        def ts(l:list[int])->list[str]:
            r:list[str]=[]
            for i in l:
                r.append(TUSR+str(i)+CD)
            return r
        ad=ts(d["add"])
        dl=ts(d["del"])
        s.pct("提示","千舰主播增加:",','.join(ad),"减少:",','.join(dl))
    def l_RECOMMEND_CARD(s,p):
        """推荐卡片"""
        if s.args.no_RECOMMEND_CARD:return
        d=p["data"]
        s.pct("广告","推荐卡片","推荐数量:",len(d["recommend_list"]),"更新数量:",len(d["update_list"]))
    def l_GOTO_BUY_FLOW(s,p):
        """购买商品"""
        if s.args.no_GOTO_BUY_FLOW:return
        s.pct("广告",p["data"]["text"])
    def l_HOT_BUY_NUM(s,p):
        """热购数量"""
        if s.args.no_HOT_BUY_NUM:return
        d=p["data"]
        s.pct("广告",f"商品id {TSTR}{d['goods_id']}{CD} 热抢数量 {TNUM}{d['num']}{CD}")
    def l_GIFT_STAR_PROCESS(s,p):
        """礼物星球进度"""
        if s.args.no_GIFT_STAR_PROCESS:return
        d=p["data"]
        s.pct("提示","礼物星球",f"{TKEY}status:{TNUM}{d['status']}{CD}",d["tip"])
    def l_WIDGET_GIFT_STAR_PROCESS(s,p):
        """礼物星球小部件进度更新"""
        if s.args.no_GIFT_STAR_PROCESS:return
        d=p["data"]
        for pi in d["process_list"]:
            s.pct("信息","礼物星球",f"礼物{TNUM}{pi['gift_id']}{CD}当前{TNUM}{pi['completed_num']}{CD}个,目标{TNUM}{pi['target_num']}{CD}个")
    def l_ANCHOR_LOT_CHECKSTATUS(s,p):
        """天选时刻审核状态"""
        if s.args.no_anchor_lot:return
        d=p["data"]
        s.pct("天选时刻","状态更新",f"{TKEY}id:{TNUM}{d['id']}{TKEY},status:{TNUM}{d['status']}{TKEY},uid:{TNUM}{d['uid']}")
    def l_ANCHOR_LOT_START(s,p):
        """天选时刻开始"""
        if s.args.no_anchor_lot:return
        d=p["data"]
        s.pct("天选时刻",d["award_name"],f"{TNUM}{d['award_num']}{CD}人",f'''发送{C_07}"{d['danmu']}"{CD}参与,需要"{d['require_text']}"''',f"{TKEY}id:{TNUM}{d['id']}{CD}",f"最大时间{TNUM}{d['max_time']}{CD}秒,剩余{TNUM}{d['time']}{CD}秒")
    def l_ANCHOR_LOT_END(s,p):
        """天选时刻结束"""
        if s.args.no_anchor_lot:return
        d=p["data"]
        s.pct("天选时刻","id为",d["id"],"的天选时刻已结束")
    def l_ANCHOR_LOT_AWARD(s,p):
        """天选时刻开奖"""
        if s.args.no_anchor_lot:return
        d=p["data"]
        s.pct("天选时刻",d["award_name"],f"{d['award_num']}人","已开奖",f"{TKEY}id:{TNUM}{d['id']}{CD}",f"中奖用户数量{len(d['award_users'])}")
    def l_ANCHOR_LOT_NOTICE(s,p):
        """天选时刻通知"""
        if s.args.no_anchor_lot:return
        d=p["data"]
        if d["notice_type"]!=1:
            s.pct("支持","天选时刻类型为:"+TNUM,d["notice_type"])
            raise SavePack("未知的天选通知类型")
        c=d["lottery_card"]
        s.pct("天选时刻","天选时刻","通知卡"+C_10,c["title"],f"{CD},按钮:{C_10}",c["button_text"])
    def l_ANCHOR_NORMAL_NOTIFY(s,p):
        """推荐提示(推测)"""
        if s.args.no_ANCHOR_NORMAL_NOTIFY:return
        d=p["data"]
        s.pct("通知","推荐",f"{TKEY}type:{TNUM}{d['type']}{TKEY},show_type:{TNUM}{d['show_type']}{CD}",d["info"]["content"])
    def l_POPULAR_RANK_GUIDE_CARD(s,p):
        """冲榜提示卡"""
        if s.args.no_POPULAR_RANK_GUIDE_CARD:return
        d=p["data"]
        h="提示"
        s.pct(h,d["title"])
        s.pct(h,d["sub_text"])
        s.pct(h,d["popup_title"])
    def l_ANCHOR_ECOLOGY_LIVING_DIALOG(s,p):
        """提示框(用于警告?)"""
        h="对话框"
        z="支持"
        d=p["data"]
        e=False
        sp=lambda i:str(i["show_platform"])+" "
        s.pct(h,f"标题: {EB}{d['dialog_title']}{DF}")
        for i in d["dialog_message_list"]:
            if i["type"]==1:
                s.pct(h,f"{i['label']}：{i['content']}")
            else:
                s.pct(z,"未知对话框内容类型"+TNUM,i["type"])
                e=True
        for i in d["dialog_tip_list"]:
            t=sp(i)
            for i1 in i["message_list"]:
                if i1["type"] in [1,2]:
                    t+=i1["content"]
                else:
                    e=True
            s.pct(h,f"提示: {B_10}{t}{BD}")
        for i in d["dialog_button_list"]:
            if i["button_action"]==1:
                s.pct(h,"[按钮:关闭窗口]",i["button_text"])
            else:
                e=True
        if e:
            raise SavePack("对话框有某个类型未知")
    def l_CUT_OFF_V2(s,p):
        """切断直播间v2，自带对话框"""
        d=p["data"]
        z="支持"
        if d["cut_off_version"]!=1:
            s.pct(z,"不支持的切断直播间数据")
            raise SavePack("切断直播间")
        cut=d["cut_off_data"]
        h="直播"
        e=False
        sp=lambda i:str(i["show_platform"])+" "
        s.pct(h,f"窗口标题: {EB}{cut['cut_off_title']}{DF}")
        for i in cut["cut_off_message_list"]:
            if i["type"]==1:
                s.pct(h,f"{i['label']}：{i['content']}")
            else:
                s.pct(z,"未知对话框内容类型"+TNUM,i["type"])
                e=True
        for i in cut["cut_off_tip_list"]:
            t=sp(i)
            for i1 in i["message_list"]:
                if i1["type"] in [1,2]:
                    t+=i1["content"]
                else:
                    e=True
            s.pct(h,f"提示: {B_10}{t}{BD}")
        for i in cut["cut_off_button_list"]:
            if i["button_action"]==1:
                s.pct(h,"[按钮:关闭窗口]",i["button_text"])
            else:
                e=True
        if e:
            raise SavePack("对话框有某个类型未知")
    def l_SYS_MSG(s,p):
        """系统消息"""
        if s.args.no_SYS_MSG:return
        s.pct("系统消息",p["msg"])
    def l_PLAY_TAG(s,p):
        """直播进度条节点标签"""
        if s.args.no_PLAY_TAG:return
        d=p["data"]
        s.pct("直播","进度条标签",f"{TKEY}id:{TNUM}{d['tag_id']}{CD} 时间戳:{TNUM}{d['timestamp']}{CD} 类型: {TSTR}{d['type']}{CD} 图片: {DU}{d['pic']}")
    def l_PLAYTOGETHER_ICON_CHANGE(s,p):
        """(未知)一起玩图标更新"""
        d=p["data"]
        s.pct("状态","一起玩图标",f"分区 {TNUM}{d['area_id']}{CD} {TKEY}has_perm:{TNUM}{d['has_perm']}{CD},{TKEY}show_count:{TNUM}{d['show_count']}{CD}")
    def l_CHG_RANK_REFRESH(s,p):
        """(未知)可能是刷新排行榜"""
        pass
    def l_POPULARITY_RANK_TAB_CHG(s,p):
        """(未知)排行标签更新?"""
        pass
    def l_ANCHOR_BROADCAST(s,p):
        """初次抵达某种情况时的提示"""
        if s.args.no_ANCHOR_BROADCAST:return
        d=p["data"]
        s.pct("提示",d["sender"],d["msg"])
    def l_ANCHOR_HELPER_DANMU(s,p):
        """同上，但是格式不同"""
        if s.args.no_ANCHOR_HELPER_DANMU:return
        d=p["data"]
        s.pct("提示",d["sender"],d["msg"])
    def l_OTHER_SLICE_LOADING_RESULT(s,p):
        """直播切片数据加载结果"""
        if s.args.no_OTHER_SLICE_LOADING_RESULT:return
        d=p["data"]
        for i in d["data"]:
            s.pct("事件","剪辑片段数据",f"开始于: {i['start_time']} ,结束于: {i['end_time']} ,片段视频流: {DU}{i['stream']}{DF} {TKEY}type:{TNUM}{i['type']}{CD},{TKEY}ban_ec:{TBOL}{i['ban_ec']}{CD}")
    def l_FANS_CLUB_POKE_GIFT_NOTICE(s,p):
        """粉丝团戳一戳要礼通知"""
        if s.args.no_FANS_CLUB_POKE_GIFT_NOTICE:return
        s.pct("提示",p["data"]["text"])

class PKCmdHandle(BLMColor):
    """PK相关数据包"""

    cmd_args=blm.add_no_cmd_args([],{
        "pk-message":"PK",
    })

    def pk_id_status(self,d:dict)->str:
        """处理PK的id和status"""
        return f"{TKEY}id:{TSTR}{d['pk_id']}{CD} {TKEY}s:{TNUM}{d['pk_status']}{CD}"

    def l_PK_BATTLE_PRE(s,p):
        """PK即将开始"""
        pass
    def l_PK_BATTLE_PRE_NEW(s,p):
        """PK即将开始"""
        s.pct("PK","PK即将开始",s.pk_id_status(p),"对方直播间",p["data"]["room_id"],"昵称:",p["data"]["uname"])
    def l_PK_BATTLE_START(s,p):
        """PK开始"""
        pass
    def l_PK_BATTLE_START_NEW(s,p):
        """PK开始"""
        a=p["data"]
        s.pct("PK","PK开始",s.pk_id_status(p),f"计数名称: {TSTR}{a['pk_votes_name']}{CD} 增量:{a['pk_votes_add']}")
    def l_PK_BATTLE_PROCESS(s,p):
        """PK过程"""
        pass
    def l_PK_BATTLE_PROCESS_NEW(s,p):
        """PK过程"""
        a=p["data"]
        i=a["init_info"]
        m=a["match_info"]
        s.pct("PK","计数更新",s.pk_id_status(p),f"直播间{TRMI}{i['room_id']}{CD}已有{TNUM}{i['votes']}{CD}票，直播间{TRMI}{m['room_id']}{CD}已有{TNUM}{m['votes']}{CD}票")
    def l_PK_BATTLE_FINAL_PROCESS(s,p):
        """PK结束流程变化"""
        s.pct("PK","PK结束流程变化",s.pk_id_status(p))
    def l_PK_BATTLE_END(s,p):
        """PK结束"""
        a=p["data"]
        i=a["init_info"]
        m=a["match_info"]
        s.pct("PK","PK结束",s.pk_id_status(p),f"直播间{TRMI}{i['room_id']}{CD}获得{TNUM}{i['votes']}{CD}票，直播间{TRMI}{m['room_id']}{CD}获得{TNUM}{m['votes']}{CD}票")
    def l_PK_BATTLE_SETTLE(s,p):
        """PK结算1"""
        pass
    def l_PK_BATTLE_SETTLE_V2(s,p):
        """PK结算2"""
        a=p["data"]
        s.pct("PK","PK结算",s.pk_id_status(p),"主播获得",a["result_info"]["pk_votes"],a["result_info"]["pk_votes_name"])
    def l_PK_BATTLE_SETTLE_NEW(s,p):
        """PK结算并进入惩罚"""
        s.pct("PK","进入惩罚时间",s.pk_id_status(p))
    def l_PK_BATTLE_VIDEO_PUNISH_BEGIN(s,p):
        """PK结算并进入惩罚"""
        s.pct("PK","进入惩罚时间",s.pk_id_status(p))
    def l_PK_BATTLE_PUNISH_END(s,p):
        """PK惩罚结束"""
        s.pct("PK","惩罚时间结束",s.pk_id_status(p))
    def l_PK_BATTLE_VIDEO_PUNISH_END(s,p):
        """同上，少了data部分"""
        s.pct("PK","惩罚时间结束",s.pk_id_status(p))
    def l_PK_INFO(s,p):
        """PK信息"""
        s.pct("PK",f"{DI}服务器下发PK信息{EI}")

class ModuleAllCmdHandle(CoreCmdHandle,FrequentCmdHandle,ConditionsFrequentCmdHandle,RareCmdHandle,PKCmdHandle):
    """该模块全部cmd的集合"""

    cmd_args= CoreCmdHandle.cmd_args + FrequentCmdHandle.cmd_args + ConditionsFrequentCmdHandle.cmd_args + RareCmdHandle.cmd_args + PKCmdHandle.cmd_args

    only_count_cmd= RareCmdHandle.only_count_cmd

class AllCmdHandle(ModuleAllCmdHandle,ParseProtobufPack):
    """添加protobuf处理"""

    def l_INTERACT_WORD_V2(s,p):
        """进入直播间V2,protobuf"""
        s.dc_INTERACT_WORD_V2(p)
        s.l_INTERACT_WORD(p)
    def l_ONLINE_RANK_V3(s,p):
        """在线排行V3,protobuf"""
        s.dc_ONLINE_RANK_V3(p)
        s.l_ONLINE_RANK_V2(p)
