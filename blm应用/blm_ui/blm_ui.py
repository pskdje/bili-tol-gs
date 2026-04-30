"""哔哩哔哩信息流信息转发到UI
"""

import blw,blm
import json
import blm_tkui as tkui
from typing import Any
from cmd_pb.protobuf_cmd_handle import ParseProtobufPack

class CmdHandle(blm.BiliLiveExp):
    """部分cmd处理"""

    blm_ui_thread=None
    """UI线程容纳"""
    blm_ui_obj:tkui.BLM_UI|None=None
    """UI对象容纳"""

    add_args=[{"type":"group","title":"网页端的屏蔽参数","list":[
        {"name":"--no-all-gift-and-notice","help":"屏蔽全部礼物和广播","action":"store_true"},
        {"name":"--no-lottery-danmu","help":"屏蔽抽奖弹幕","action":"store_true"},
        {"name":"--no-enter-room-info","help":"屏蔽进场信息","action":"store_true"},
        {"name":"--no-super-chat","help":"屏蔽醒目留言","action":"store_true"},
        {"name":"--no-emoji-danmu","help":"屏蔽表情弹幕","action":"store_true"},
    ]}]

    def error(self,d=None,**v):
        """记录异常，附带该类的部分变量"""
        return super().error(d,
            blm_ui_thread=self.blm_ui_thread,
            blm_ui_obj=self.blm_ui_obj,
            **v
        )

    def close(self):
        """执行关闭流程"""
        if self.blm_ui_obj:
            self.blm_ui_obj.stop_sign()
            self.blm_ui_thread.join(3)
        self.blm_ui_obj=None
        self.blm_ui_thread=None
        return super().close()

    @property
    def has_running(self)->bool:
        """是否运行"""
        if self.blm_ui_obj:
            return self.blm_ui_obj.running.is_set()
        return False

    def start_blm_ui(self)->None:
        """启动 blm UI"""
        thread,obj=tkui.start_blm_ui()
        self.blm_ui_thread=thread
        self.blm_ui_obj=obj
        obj.p=self.p
        obj.error=self.error

    def send_msg_to_ui(self,msg:dict[str,Any])->None:
        """发送信息到UI"""
        if self.blm_ui_obj:
            self.blm_ui_obj.send_msg(msg)

    def l_DANMU_MSG(s,p):
        """弹幕"""
        d:list=p["info"]
        s.send_msg_to_ui({"t":"dm","uname":d[2][1],"danmu":d[1],"isAnchor":s.up_uid==d[2][0],"isAdmin":d[2][2]==1})
    def l_INTERACT_WORD(s,p):
        """交互"""
        d=p["data"]
        match d["msg_type"]:
            case 1:
                if s.args.no_enter_room_info:return
                t="进入直播间"
            case 2:
                t="关注直播间"
            case 3:
                t="分享直播间"
            case _:
                t="不知道在做什么"
        s.send_msg_to_ui({"t":"iw","uname":d["uname"],"inter":" "+t})
    def l_ROOM_CHANGE(s,p):
        """直播间更新"""
        d=p["data"]
        s.send_msg_to_ui({"t":"ev","msg":f"分区: {d['parent_area_name']} > {d['area_name']} 标题: {d['title']}"})
    def l_LIVE(s,p):
        """开始直播"""
        s.send_msg_to_ui({"t":"ev","msg":"开始直播"})
    def l_PREPARING(s,p):
        """结束直播"""
        s.send_msg_to_ui({"t":"ev","msg":"结束直播"})
    def l_ROOM_REAL_TIME_MESSAGE_UPDATE(s,p):
        """数据更新"""
        d=p["data"]
        s.pct("信息",d["roomid"],"直播间",d["fans"],"粉丝",d["fans_club"],"点亮粉丝勋章")
    def l_ROOM_BLOCK_MSG(s,p):
        """用户被禁言"""
        s.send_msg_to_ui({"t":"df","msg":f"用户 {p['uname']} 已被禁言"})
    def l_CUT_OFF(s,p):
        """切断"""
        s.send_msg_to_ui({"t":"warning","msg":f"直播间被切断: {p['msg']}"})
    def l_ROOM_LOCK(s,p):
        """封禁"""
        s.send_msg_to_ui({"t":"warning","msg":f"直播间被封禁，解除时间: {p['expire']}"})
    def l_ROOM_ADMINS(s,p):
        """房管列表"""
    def l_room_admin_entrance(s,p):
        """添加房管"""
        s.send_msg_to_ui({"t":"df","msg":f"添加 {p['uid']} 为房管"})
    def l_ROOM_ADMIN_REVOKE(s,p):
        """撤销房管"""
        s.send_msg_to_ui({"t":"df","msg":f"撤销 {p['uid']} 的房管权限"})
    def l_CHANGE_ROOM_INFO(s,p):
        """背景更换"""
        s.pct("直播","直播间",p["roomid"],"信息变更","背景图:",p["background"])
    def l_WARNING(s,p):
        """警告"""
        s.send_msg_to_ui({"t":"warning","msg":f"超管警告: {p['msg']}"})
    def l_ROOM_CONTENT_AUDIT_REPORT(s,p):
        """直播间内容审核结果(主要是审核标题)"""
        d=p["data"]
        s.pct("直播","标题:",d["audit_title"],"审核结果:",d["audit_reason"])
    def l_PLAYURL_RELOAD(s,p):
        """播放链接刷新"""
        s.send_msg_to_ui({"t":"ev","msg":f"播放链接刷新"})
    def l_ENTRY_EFFECT(s,p):
        """进场"""
        if s.args.no_enter_room_info:return
        d=p["data"]
    def l_ENTRY_EFFECT_MUST_RECEIVE(s,p):
        """必须接受的进场信息"""
        d=p["data"]
        s.send_msg_to_ui({"t":"bdf","msg":d["copy_writing"]})
    def l_SEND_GIFT(s,p):
        """礼物"""
        if s.args.no_all_gift_and_notice:return
        d=p["data"]
        s.send_msg_to_ui({"t":"gift","uname":d["uname"],"action":d["action"],"giftName":d["giftName"],"num":d["num"]})
    def l_COMBO_SEND(s,p):
        """组合礼物"""
        if s.args.no_all_gift_and_notice:return
        d=p["data"]
        s.send_msg_to_ui({"t":"gift","uname":d["uname"],"action":d["action"],"giftName":d["gift_name"],"num":d["total_num"]})
    def l_WATCHED_CHANGE(s,p):
        """看过"""
        d=p["data"]
        s.pct("观看",d["num"],"人看过;","text_large:",d["text_large"])
    def l_SUPER_CHAT_MESSAGE(s,p):
        """醒目留言"""
        if s.args.no_super_chat:return
        d=p["data"]
        s.send_msg_to_ui({"t":"SC","uname":d['user_info']['uname'],"price":d['price'],"msg":d["message"]})
    def l_SUPER_CHAT_MESSAGE_DELETE(s,p):
        """醒目留言删除"""
        s.pct("留言","醒目留言删除:",p["data"]["ids"])
    def l_LIVE_INTERACTIVE_GAME(s,p):
        """类似弹幕，未确定"""
        d=p["data"]
    def l_STOP_LIVE_ROOM_LIST(s,p):
        """停止直播的房间列表"""
        d=p["data"]
    def l_DANMU_AGGREGATION(s,p):
        """弹幕聚集"""
        pass
    def l_ONLINE_RANK_COUNT(s,p):
        """在线榜计数"""
        d=p["data"]
        olc=""
        if "online_count"in d:
            olc="在线计数: "+str(d["online_count"])
        s.pct("计数","高能用户计数:",d["count"],olc)
    def l_ONLINE_RANK_V2(s,p):
        """在线排行"""
        d=p["data"]
    def l_NOTICE_MSG(s,p):
        """广播通知"""
        if s.args.no_all_gift_and_notice:return
        s.send_msg_to_ui({"t":"nt","msg":p["msg_self"]})
    def l_COMMON_NOTICE_DANMAKU(s,p):
        """弹幕通知"""
        s.send_msg_to_ui({"t":"CN_DANMU","contents":p["data"]["content_segments"]})
    def l_LIKE_INFO_V3_UPDATE(s,p):
        """点赞数量"""
        s.pct("计数","点赞点击数量:",p["data"]["click_count"])
    def l_LIKE_INFO_V3_CLICK(s,p):
        """点赞点击"""
        d=p["data"]
        s.send_msg_to_ui({"t":"iw","uname":d["uname"],"inter":d["like_text"]})
    def l_WIDGET_BANNER(s,p):
        """小部件"""
        d=p["data"]
    def l_DM_INTERACTION(s,p):
        """交互合并"""
        d=p["data"]
        n=json.loads(d["data"])
        t=d["type"]
        if t==101:# 投票
            pass
        elif t==102:# 弹幕
            c=n["combo"][-1]
            s.send_msg_to_ui({"t":"DM_INTERACTION","s":2,"msg":[c["guide"],c["content"],c["cnt"]]})
        elif t==104:# 送礼
            s.send_msg_to_ui({"t":"DM_INTERACTION","s":1,"msg":[n["cnt"],f'{n["suffix_text"]} gift_id: {n["gift_id"]}']})
        elif t==103 or t==105 or t==106:# 关注，分享，点赞
            s.send_msg_to_ui({"t":"DM_INTERACTION","s":1,"msg":[n["cnt"],n["suffix_text"]]})
        else:
            raise blw.SavePack("交互合并类型")
    def l_HOT_RANK_SETTLEMENT(s,p):
        """热门通知"""
        d=p["data"]
        s.send_msg_to_ui({"t":"nt","msg":d["dm_msg"]})
    def l_GUARD_BUY(s,p):
        """舰队购买"""
        d=p["data"]
        s.send_msg_to_ui({"t":"gift","uname":d["username"],"action":"购买","giftName":d["gift_name"],"num":d["num"]})
    def l_USER_TOAST_MSG(s,p):
        """舰队续费"""
        d=p["data"]
        s.send_msg_to_ui({"t":"nt","msg":d["toast_msg"]})
    def l_LOG_IN_NOTICE(s,p):
        """登录提示"""
        d=p["data"]
        s.send_msg_to_ui({"t":"ev","msg":f"需要登录: {d['notice_msg']}"})

class AddProtoCmdHandle(CmdHandle,ParseProtobufPack):
    """添加protobuf处理"""

    def l_INTERACT_WORD_V2(s,p):
        """进入直播间V2,protobuf"""
        s.dc_INTERACT_WORD_V2(p)
        s.l_INTERACT_WORD(p)
    def l_ONLINE_RANK_V3(s,p):
        """在线排行V3,protobuf"""
        s.dc_ONLINE_RANK_V3(p)
        s.l_ONLINE_RANK_V2(p)

class WindowCloseExit(AddProtoCmdHandle):
    """窗口关闭将退出"""

    def on_cert_pack_reply(s,p):
        super().on_cert_pack_reply(p)
        s.send_msg_to_ui({"t":"ev","msg":"信息流连接"})

    def print_popularity(self,data):
        """打印人气值，但检测到窗口关闭后退出"""
        if not self.has_running:
            raise SystemExit(0)
        return super().print_popularity(data)

    def send_msg_to_ui(self,msg):
        if not self.has_running:
            raise blw.ExitBLW("Window")
        return super().send_msg_to_ui(msg)

if __name__=="__main__":
    o=WindowCloseExit()
    o.start_blm_ui()
    o.start()
