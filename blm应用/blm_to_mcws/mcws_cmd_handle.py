"""哔哩哔哩直播信息流转发到 Minecraft WebSocket 服务器
信息流处理依赖: blm项目的blm(包括blw)和cmd_pb
Minecraft WebSocket依赖: mcws
"""

import blm
import mcws
import json,asyncio,re
from cmd_pb.protobuf_cmd_handle import ParseProtobufPack

"""颜色代码
参见 Minecraft Wiki
https://zh.minecraft.wiki/w/格式化代码
"""
MC_0="§0"# 黑
MC_1="§1"# 深蓝
MC_2="§2"# 深绿
MC_3="§3"# 暗水蓝
MC_4="§4"# 深红
MC_5="§5"# 深紫
MC_6="§6"# 金
MC_7="§7"# 灰
MC_8="§8"# 深灰
MC_9="§9"# 蓝
MC_a="§a"# 绿
MC_b="§b"# 水蓝
MC_c="§c"# 红
MC_d="§d"# 淡紫
MC_e="§e"# 黄
MC_f="§f"# 白
# 仅基岩版
MC_g="§g"# Minecoin金
MC_h="§h"# 石英
MC_i="§i"# 铁锭
MC_j="§j"# 下界合金
MC_m="§m"# 红石
MC_n="§n"# 铜锭
MC_p="§p"# 金锭
MC_q="§q"# 绿宝石
MC_s="§s"# 钻石
MC_t="§t"# 青金石
MC_u="§u"# 紫水晶
MC_v="§v"# 树脂
# =格式代码=
MF_k="§k"# 随机
MF_l="§l"# 粗体
MF_m="§m"# 删除线，基岩版不可用，实际被用于颜色
MF_n="§n"# 下划线，基岩版不可用，实际被用于颜色
MF_o="§o"# 斜体
MF_r="§r"# 重置

# 某种情况统一使用的颜色
TUSR=MC_6# 用户名
TNUM=MC_3# 数字
TRMI=MC_9# 房间号

# 正则表达式
RGPL=re.compile("<%(.+?)%>")

def cuse(msg:str)->str:
    """渲染用户颜色"""
    return RGPL.sub(TUSR+"\\1"+MF_r,msg)

class BLM_to_MCWS(blm.BiliLiveBlackWordExp,ParseProtobufPack,mcws.MinecraftWS):
    """信息流到WS"""

    add_args= blm.BiliLiveBlackWordExp.add_args + blm.BiliLiveMsg.add_args

    cmd_args=blm.add_no_cmd_args([],{
        "INTERACT_WORD":"交互",
        "enter-room":"进入直播间",
        "ENTRY_EFFECT":"进场",
        "WATCHED_CHANGE":"看过",
        "SUPER_CHAT_MESSAGE_DELETE":"醒目留言删除",
        "LIKE_INFO_V3_UPDATE":"点赞数量更新",
        "LIKE_INFO_V3_CLICK":"点赞点击",
        "NOTICE_MSG":"广播通知",
    })

    def error(self,d=None,**v)->None:
        """记录异常，附带该类的部分变量"""
        super().error(d,MCWS_server=self.MCWS_server,**v)

    def push_msg(self,msg:str)->None:
        """推送消息"""
        self.broadcast_say(msg,has_ignore_nostart=True)

    async def mcws_start(self,port:int=19134):
        """启动"""
        ser=await self.MCWS(port)
        print(f"Minecraft WS 服务器已在 {port} 端口启动。")
    async def mcws_join_event(self,ws):
        """加入"""
        print(ws.remote_address,"加入服务器")
        d=self.create_commandRequest(f"say 已加入直播间{TRMI}{self.roomid}{MF_r}的信息流")
        await ws.send(json.dumps(d))
    async def mcws_exit_event(self,ws):
        """退出"""
        print(ws.remote_address,"退出服务器")

    def l_DANMU_MSG(s,p):
        """弹幕"""
        d=p["info"]
        if s.is_blocked_msg(d[1]):
            return
        tc=""
        if s.up_uid==d[2][0]:
            tc+=f"{MC_4}(主播){MF_r}"
        if d[2][2]==1:
            tc+=f"{MC_e}(房){MF_r}"
        s.push_msg(f"{tc}{TUSR}{d[2][1]}{MF_r}:{MC_7} {d[1]}")

    def l_INTERACT_WORD(s,p):
        """交互"""
        if s.args.no_INTERACT_WORD:return
        d=p["data"]
        mt=d["msg_type"]
        nm=f"{TUSR}{d['uname']}{MF_r}"
        if mt==1:
            if s.args.no_enter_room:return
            s.push_msg(f"{nm} 进入直播间")
        elif mt==2:
            s.push_msg(f"{nm} 关注直播间")
        elif mt==3:
            s.push_msg(f"{nm} 分享直播间")
        else:
            s.push_msg(f"{nm} 不知道在做什么")
    def l_INTERACT_WORD_V2(s,p):
        """交互V2"""
        if s.args.no_INTERACT_WORD:return
        s.dc_INTERACT_WORD_V2(p)
        s.l_INTERACT_WORD(p)

    def l_ROOM_CHANGE(s,p):
        """直播间更新"""
        d=p["data"]
        s.push_msg(f"分区:{MC_1} {d['parent_area_name']} {MC_5}>{MC_1} {d['area_name']} {MF_r}标题: {MC_2}{d['title']}{MF_r}")
    def l_LIVE(s,p):
        """开始直播"""
        s.push_msg(f"直播间 {TRMI}{p['roomid']}{MF_r} 开始直播")
    def l_PREPARING(s,p):
        """结束直播"""
        s.push_msg(f"直播间 {TRMI}{p['roomid']}{MF_r} 结束直播")
    def l_ROOM_REAL_TIME_MESSAGE_UPDATE(s,p):
        """数据更新"""
        d=p["data"]
        s.push_msg(f"{TRMI}{d['roomid']}{MF_r} 直播间 {TNUM}{d['fans']}{MF_r} 粉丝 {TNUM}{d['fans_club']}{MF_r} 点亮粉丝勋章")
    def l_ROOM_BLOCK_MSG(s,p):
        """用户被禁言"""
        s.push_msg(f"用户 {TUSR}{p['uname']}{MF_r} 已被禁言")
    def l_WARNING(s,p):
        """警告"""
        s.push_msg(f"{MC_4}警告:{MC_e}{p['msg']}")
    def l_ENTRY_EFFECT(s,p):
        """进场"""
        if s.args.no_ENTRY_EFFECT:
            return
        d=p["data"]
        s.push_msg(cuse(d["copy_writing"]))
    def l_ENTRY_EFFECT_MUST_RECEIVE(s,p):
        """必须接受的进场信息"""
        if s.args.no_ENTRY_EFFECT:# 允许不显示
            return
        d=p["data"]
        s.push_msg("进场",f"{MC_c}(必须显示){MF_r}",cuse(d["copy_writing"]))
    def l_WATCHED_CHANGE(s,p):
        """看过"""
        if s.args.no_WATCHED_CHANGE:
            return
        d=p["data"]
        s.push_msg(f"{TNUM}{d['num']}{MF_r} 人看过")
    def l_SUPER_CHAT_MESSAGE(s,p):
        """醒目留言"""
        d=p["data"]
        s.push_msg(f"{TUSR}{d['user_info']['uname']}{MF_r}({MC_4}￥{d['price']}{MF_r}):{MC_7} {d['message']}")
    def l_SUPER_CHAT_MESSAGE_DELETE(s,p):
        """醒目留言删除"""
        if s.args.no_SUPER_CHAT_MESSAGE_DELETE:
            return
        s.push_msg("醒目留言删除: "+str(p["data"]["ids"]))
    def l_ONLINE_RANK_COUNT(s,p):
        """在线榜计数"""
        d=p["data"]
        olc=""
        if "online_count" in d:
            olc=f"在线计数: {TNUM}{d['online_count']}{MF_r}"
        s.push_msg(f"高能用户计数: {TNUM}{d['count']}{MF_r} {olc}")
    def l_LIKE_INFO_V3_UPDATE(s,p):
        """点赞数量"""
        if s.args.no_LIKE_INFO_V3_UPDATE:
            return
        s.push_msg(f"点赞点击数量: {TNUM}{p['data']['click_count']}")
    def l_LIKE_INFO_V3_CLICK(s,p):
        """点赞点击"""
        if s.args.no_LIKE_INFO_V3_CLICK:
            return
        d=p["data"]
        s.push_msg(f"{TUSR}{d['uname']}{MF_r} {d['like_text']}")
    def l_NOTICE_MSG(s,p):
        """广播通知"""
        if s.args.no_NOTICE_MSG:
            return
        msg=cuse(p["msg_self"])
        if (not msg) and ("name" in p):
            s.push_msg(f"{MC_1}空的公告: {MF_r}{p["name"]}")
        elif not msg:
            s.push_msg(MC_c+"无效公告")
        else:
            s.push_msg(msg)

class StartMCWS(BLM_to_MCWS):
    """自动启动MCWS，在默认端口开放。"""

    def on_cert_pack_reply(s,p):
        """通过认证回复启动"""
        super().on_cert_pack_reply(p)
        asyncio.create_task(s.mcws_start(),name="启动MCWS")
