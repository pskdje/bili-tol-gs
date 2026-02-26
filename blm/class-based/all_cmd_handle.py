"""全部该项目已知cmd处理
数据分析由我自己进行，不保证准确，请注意时效，日期:2025/12/01，操作:修改
已存在的cmd很难确认是否需要更新
"""

import blw
import json,time
from blw import TIMEFORMAT,SavePack,log
from cmd_pb.protobuf_cmd_handle import ParseProtobufPack

class BiliLiveAllCmdHandle(ParseProtobufPack,blw.BiliLiveWS):
    """所有该项目已知cmd处理"""
    def l_DANMU_MSG(self,p):
        """弹幕"""
        d=p["info"]
        self.pct("弹幕",f"{d[2][1]}:",d[1])
    def l_DANMU_MSG_MIRROR(s,p):
        """跨房弹幕"""
        d=p["info"]
        s.pct("弹幕",f"(跨房) {d[2][1]}:",d[1])
    def l_INTERACT_WORD(s,p):
        """交互,JSON"""
        info="交互"
        d=p["data"]
        mt=int(d["msg_type"])
        nm=d["uname"]
        if mt==1:
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
    def l_INTERACT_WORD_V2(s,p):
        """交互V2,protobuf"""
        s.dc_INTERACT_WORD_V2(p)
        s.l_INTERACT_WORD(p)
    def l_ENTRY_EFFECT(s,p):
        """进场"""
        d=p["data"]
        s.pct("进场",d["copy_writing"])
    def l_ENTRY_EFFECT_MUST_RECEIVE(s,p):
        """必须接受的进场信息"""
        d=p["data"]
        s.pct("进场","(必须显示)",d["copy_writing"])
    def l_SEND_GIFT(s,p):
        """礼物"""
        d=p["data"]
        s.pct("礼物",d["uname"],d["action"],d["giftName"],"×",d["num"])
    def l_COMBO_SEND(s,p):
        """组合礼物"""
        d=p["data"]
        s.pct("礼物",d["uname"],d["action"],d["gift_name"],"×",d["total_num"])
    def l_WATCHED_CHANGE(s,p):
        """看过"""
        d=p["data"]
        if s.debug:
            s.pct("观看",d["num"],"人看过;","text_large:",d["text_large"])
        else:
            s.pct("观看",d["num"],"人看过")
    def l_SUPER_CHAT_MESSAGE(s,p):
        """醒目留言"""
        d=p["data"]
        s.pct("留言",f"{d['user_info']['uname']}(￥{d['price']}):",d["message"])
    def l_SUPER_CHAT_MESSAGE_JPN(s,p):
        """醒目留言日语"""
        d=p["data"]
        s.pct("留言","日语",d.get("message_jpn"))
    def l_SUPER_CHAT_MESSAGE_DELETE(s,p):
        """醒目留言删除"""
        s.pct("留言","醒目留言删除:",p["data"]["ids"])
    def l_LIVE_INTERACTIVE_GAME(s,p):
        """类似弹幕，未确定"""
        d=p["data"]
        s.pct("弹幕(LIG)",f"{d['uname']}:",d["msg"])
    def l_ROOM_CHANGE(s,p):
        """直播间更新"""
        d=p["data"]
        s.pct("直播","分区:",d["parent_area_name"],">",d["area_name"],",标题:",d["title"])
    def l_LIVE(s,p):
        """开始直播"""
        s.pct("直播","直播间",p["roomid"],"开始直播")
    def l_PREPARING(s,p):
        """结束直播"""
        s.pct("直播","直播间",p["roomid"],"结束直播")
    def l_ROOM_REAL_TIME_MESSAGE_UPDATE(s,p):
        """数据更新"""
        d=p["data"]
        s.pct("信息",d["roomid"],"直播间",d["fans"],"粉丝",d["fans_club"],"点亮粉丝勋章")
    def l_STOP_LIVE_ROOM_LIST(s,p):
        """停止直播的房间列表"""
        pass
    def l_ROOM_BLOCK_MSG(s,p):
        """用户被禁言"""
        s.pct("直播","用户",p["uname"],"已被禁言")
    def l_CUT_OFF(s,p):
        """切断"""
        s.pct("直播","直播间",p["room_id"],"被警告:",p["msg"])
    def l_ROOM_LOCK(s,p):
        """封禁"""
        s.pct("直播","直播间",p["roomid"],"被封禁，解除时间:",p["expire"])
    def l_ROOM_ADMINS(s,p):
        """房管列表"""
        s.pct("直播",f"房管列表: len({len(p['uids'])})")
    def l_room_admin_entrance(s,p):
        """添加房管"""
        s.pct("直播","添加",p["uid"],"为房管，消息:",p["msg"])
    def l_ROOM_ADMIN_REVOKE(s,p):
        """撤销房管"""
        s.pct("直播","撤销",p["uid"],"的房管权限，消息:",p["msg"])
    def l_CHANGE_ROOM_INFO(s,p):
        """背景更换"""
        s.pct("直播","直播间",p["roomid"],"信息变更","背景图:",p["background"])
    def l_WARNING(s,p):
        """警告"""
        s.pct("警告",p["msg"])
    def l_PLAYURL_RELOAD(s,p):
        """播放链接刷新"""
        s.pct("直播","播放链接刷新")
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
    def l_LITTLE_TIPS(s,p):
        """某种提示，内容可能与使用的会话信息有关"""
        d=p["data"]
        s.pct("提示",d["msg"])
    def l_LITTLE_MESSAGE_BOX(s,p):
        """弹框提示"""
        d=p["data"]
        s.pct("弹框",d["msg"])
    def l_VOICE_JOIN_SWITCH(s,p):
        """连麦开关状态"""
        a=p["data"]["room_status"]
        if a==0:
            t="关闭"
        elif a==1:
            t="开启"
        else:
            s.pct("连麦",f"未知的连麦开关状态 {a}")
            raise SavePack("连麦开关状态")
        s.pct("连麦","(V1)",f"连麦开关状态: {t}")
    def l_VOICE_JOIN_SWITCH_V2(s,p):
        """连麦开关状态V2"""
        a=p["data"]["room_status"]
        if a==0:
            t="关闭"
        elif a==1:
            t="开启"
        else:
            s.pct("连麦",f"未知的V2连麦开关状态 {a}")
            raise SavePack("连麦开关状态")
        s.pct("连麦","(V2)",f"连麦开关状态: {t}")
    def l_VOICE_JOIN_LIST(s,p):
        """连麦列表(需要更新)"""
        d=p["data"]
        s.pct("连麦","申请计数:",d["apply_count"])
    def l_VOICE_JOIN_ROOM_COUNT_INFO(s,p):
        """(同上)"""
        pass
    def l_ONLINE_RANK_TOP3(s,p):
        """前三个第一次成为高能用户\n可能已弃用"""
        d=p["data"]
        if s.debug:
            s.pct("排行",f"len({len(d['list'])})",d["list"][0]["msg"],f"rank:{d['list'][0]['rank']}")
        else:
            s.pct("排行",d["list"][0]["msg"],f"rank:{d['list'][0]['rank']}")
    def l_VOICE_JOIN_STATUS(s,p):
        """连麦状态"""
        d=p["data"]
        if d["status"]==0:
            s.pct("连麦","停止连麦")
        elif d["status"]==1:
            s.pct("连麦","正在与",d["user_name"],"连麦")
        else:
            t="未知的语音连麦状态"
            log.debug(f"{t}: {d['status']}")
            raise SavePack(t)
    def l_ONLINE_RANK_V2(s,p):
        """在线排行V2,JSON"""
        pass
    def l_ONLINE_RANK_V3(s,p):
        """在线排行V3,protobuf"""
        s.dc_ONLINE_RANK_V3(p)
        s.l_ONLINE_RANK_V2(p)
    def l_COLLABORATION_LIVE_WATCHED(s,p):
        """跨房看过"""
        d=p["data"]
        if s.debug:
            s.pct("观看","跨房",d["num"],"人看过;","text_large:",d["text_large"])
        else:
            s.pct("观看","跨房",d["num"],"人看过")
    def l_COLLABORATION_LIVE_ONLINE(s,p):
        """跨房在线"""
        d=p["data"]
        s.pct("计数","跨房在线人数:",d["text"])
    def l_COLLABORATION_LIVE_POPULARITY(s,p):
        """跨房人气"""
        d=p["data"]
        s.pct("计数","跨房人气:",d["num"])
    def l_COLLABORATION_LIVE_INFO(s,p):
        """跨房直播信息"""
        d=p["data"]
        if d["if_collaboration_room"]:
            m=d["multi_view"]
            s.pct("信息","跨房直播",f"提示: {d['copy_writing']} ,活动名称: {d['activity_name']}")
        else:
            s.pct("信息","跨房直播关闭")
    def l_HOT_RANK_SETTLEMENT(s,p):
        """热门通知"""
        d=p["data"]
        s.pct("排行",d["dm_msg"])
    def l_HOT_RANK_SETTLEMENT_V2(s,p):
        """(同上)V2"""
        d=p["data"]
    def l_COMMON_NOTICE_DANMAKU(s,p):
        """普通通知"""
        for cse in p["data"]["content_segments"]:
            cset=cse["type"]
            if cset==1:
                s.pct("通知",cse["text"])
            elif cset==2:
                s.pct("通知","图片:",cse.get("img_url"))
            elif cset==3:
                s.pct("通知",cse["text"],",链接:",cse.get("uri"))
            else:
                log.debug(f"未知的通知组件类型: {cset}")
                raise SavePack("通知组件类型")
    def l_NOTICE_MSG(s,p):
        """广播通知"""
        if "name" in p:
            s.pct("公告",p["name"],"=>",p["msg_self"])
        else:
            s.pct("公告",p["msg_self"])
    def l_GUARD_BUY(s,p):
        """舰队购买"""
        d=p["data"]
        s.pct("礼物",d["username"],"购买了",d["num"],"个",d["gift_name"])
    def l_USER_TOAST_MSG(s,p):
        """舰队续费"""
        d=p["data"]
        s.pct("提示",d["toast_msg"])
    def l_USER_TOAST_MSG_V2(s,p):
        """(同上)"""
        d=p["data"]
    def l_WIDGET_BANNER(s,p):
        """小部件"""
        d=p["data"]
        for wi in d["widget_list"]:
            wic=d["widget_list"][wi]
            if wic is None:
                continue
            s.pct("小部件",f"key:{wi}","id",wic["id"],"标题:",wic["title"])
    def l_SUPER_CHAT_ENTRANCE(s,p):
        """醒目留言入口变化"""
        d=p["data"]
        if d["status"]==0:
            s.pct("信息","关闭醒目留言入口")
        else:
            log.debug(f"status: {d['status']}")
            s.pct("支持","未知的'SUPER_CHAT_ENTRANCE'status数字:",d["status"])
            raise SavePack("未知的status")
    def l_ROOM_SKIN_MSG(s,p):
        """直播间皮肤更新"""
        s.pct("信息","直播间皮肤更新","id:",p["skin_id"],",status:",p["status"],",结束时间:",time.strftime(TIMEFORMAT,time.gmtime(p["end_time"])),",当前时间:",time.strftime(TIMEFORMAT,time.gmtime(p["current_time"])))
    def l_LIVE_MULTI_VIEW_CHANGE(s,p):
        """多个直播视角信息更新"""
        s.pct("信息","LIVE_MULTI_VIEW_CHANGE",p["data"])
        raise SavePack("未知数据包")
    def l_LIVE_MULTI_VIEW_NEW_INFO(s,p):
        """多个直播视角信息更新"""
        d=p["data"]
        if d["room_list"]is None:
            s.pct("信息","直播多视角已结束")
        else:
            s.pct("信息","直播多视角",d["title"],d["copy_writing"],"房间数量",len(d["room_list"]))
    def l_POPULARITY_RED_POCKET_NEW(s,p):
        """新红包"""
        d=p["data"]
        s.pct("通知",d["uname"],d["action"],"价值",d["price"],"电池的",d["gift_name"])
    def l_POPULARITY_RED_POCKET_V2_NEW(s,p):
        """(同上)"""
        d=p["data"]
    def l_POPULARITY_RED_POCKET_START(s,p):
        """红包开始"""
        d=p["data"]
    def l_POPULARITY_RED_POCKET_V2_START(s,p):
        """(同上)"""
        d=p["data"]
    def l_POPULARITY_RED_POCKET_WINNER_LIST(s,p):
        """红包结束，获得红包的列表"""
        d=p["data"]
    def l_POPULARITY_RED_POCKET_V2_WINNER_LIST(s,p):
        """(同上)"""
        d=p["data"]
    def l_LIKE_INFO_V3_UPDATE(s,p):
        """点赞数量"""
        s.pct("计数","点赞点击数量:",p["data"]["click_count"])
    def l_LIKE_INFO_V3_CLICK(s,p):
        """点赞点击"""
        d=p["data"]
        s.pct("交互",d["uname"],d["like_text"])
    def l_LIKE_INFO_V3_NOTICE(s,p):
        """点赞通知"""
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
    def l_LIKE_GUIDE_USER(s,p):
        """引导用户点赞"""
        d=p["data"]
        s.pct("提示","点赞提醒",d["like_text"])
    def l_UNIVERSAL_EVENT_GIFT(s,p):
        """连线礼物累计变化信息"""
        s.pct("信息","(V1)","连线礼物累计变化")
    def l_UNIVERSAL_EVENT_GIFT_V2(s,p):
        """连线礼物累计变化信息V2"""
        s.pct("信息","(V2)","连线礼物累计变化")
    def l_POPULAR_RANK_CHANGED(s,p):
        """人气排行榜更新(可能已弃用)"""
        d=p["data"]
        s.pct("排行","人气榜第",d["rank"],"名")
    def l_AREA_RANK_CHANGED(s,p):
        """大航海排行更新(可能已弃用)"""
        d=p["data"]
        s.pct("排行",d["rank_name"],"第",d["rank"],"名")
    def l_RANK_CHANGED(s,p):
        """人气榜"""
        d=p["data"]
        s.pct("排行","(V1)",d["rank_name_by_type"],f"rank_type:{d['rank_type']},rank:{d['rank']}")# 无法确定rank与实际排名相关，有数据包表明这是不同的
    def l_RANK_CHANGED_V2(s,p):
        """人气榜V2"""
        d=p["data"]
        s.pct("排行","(V2)",d["rank_name_by_type"],f"rank_type:{d['rank_type']},rank:{d['rank']}")# 无法确定rank与实际排名相关，有数据包表明这是不同的
    def l_REVENUE_RANK_CHANGED(s,p):
        """收入排行(机翻)"""
        d=p["data"]
        s.pct("排行",d["rank_name"],"第",d["rank"],"名")
    def l_DM_INTERACTION(s,p):
        """交互合并"""
        d=p["data"]
        h="交互合并"
        n=json.loads(d["data"])
        t=d["type"]
        if t==101:# 投票
            s.pct(h,"投票",n["question"],f"有{n['cnt']}人参与")
        elif t==102:# 弹幕
            for c in n["combo"]:
                s.pct(h,c["guide"],c["content"],"×"+str(c["cnt"]))
        elif t==104:# 送礼
            s.pct(h,n["cnt"],n["suffix_text"],"gift_id:",n["gift_id"])
        elif t==103 or t==105 or t==106:# 关注，分享，点赞
            s.pct(h,n["cnt"],n["suffix_text"])
        else:
            log.debug(f"未知的交互合并类型: {t}")
            raise SavePack("交互合并类型")
    def l_PK_BATTLE_PRE(s,p):
        """PK即将开始"""
        pass
    def l_PK_BATTLE_PRE_NEW(s,p):
        """PK即将开始"""
        s.pct("PK","PK即将开始",f"id:{p['pk_id']}",f"s:{p['pk_status']}","对方直播间",p["data"]["room_id"],"昵称:",p["data"]["uname"])
    def l_PK_BATTLE_START(s,p):
        """PK开始"""
        pass
    def l_PK_BATTLE_START_NEW(s,p):
        """PK开始"""
        a=p["data"]
        s.pct("PK","PK开始",f"id:{p['pk_id']}",f"s:{p['pk_status']}","计数名称:",a["pk_votes_name"],f"增量:{a['pk_votes_add']}")
    def l_PK_BATTLE_PROCESS(s,p):
        """PK过程"""
        pass
    def l_PK_BATTLE_PROCESS_NEW(s,p):
        """PK过程"""
        a=p["data"]
        i=a["init_info"]
        m=a["match_info"]
        s.pct("PK","计数更新",f"id:{p['pk_id']}",f"s:{p['pk_status']}","直播间",i["room_id"],"已有",i["votes"],"票，直播间",m["room_id"],"已有",m["votes"],"票")
    def l_PK_BATTLE_FINAL_PROCESS(s,p):
        """PK结束流程变化"""
        s.pct("PK","PK结束流程变化",f"id:{p['pk_id']}",f"s:{p['pk_status']}")
    def l_PK_BATTLE_END(s,p):
        """PK结束"""
        a=p["data"]
        i=a["init_info"]
        m=a["match_info"]
        s.pct("PK","PK结束",f"id:{p['pk_id']}",f"s:{p['pk_status']}","直播间",i["room_id"],"获得",i["votes"],"票，直播间",m["room_id"],"获得",m["votes"],"票")
    def l_PK_BATTLE_SETTLE(s,p):
        """PK结算1"""
        pass
    def l_PK_BATTLE_SETTLE_V2(s,p):
        """PK结算2"""
        a=p["data"]
        s.pct("PK","PK结算",f"id:{p['pk_id']}",f"s:{p['pk_status']}","主播获得",a["result_info"]["pk_votes"],a["result_info"]["pk_votes_name"])
    def l_PK_BATTLE_SETTLE_NEW(s,p):
        """PK结算并进入惩罚"""
        s.pct("PK","进入惩罚时间",f"id:{p['pk_id']}",f"s:{p['pk_status']}")
    def l_PK_BATTLE_VIDEO_PUNISH_BEGIN(s,p):
        """PK结算并进入惩罚"""
        s.pct("PK","进入惩罚时间",f"id:{p['pk_id']}",f"s:{p['pk_status']}")
    def l_PK_BATTLE_PUNISH_END(s,p):
        """PK惩罚结束"""
        s.pct("PK","惩罚时间结束",f"id:{p['pk_id']}",f"s:{p['pk_status']}")
    def l_PK_BATTLE_VIDEO_PUNISH_END(s,p):
        """同上，少了data部分"""
        s.pct("PK","惩罚时间结束",f"id:{p['pk_id']}",f"s:{p['pk_status']}")
    def l_PK_BATTLE_ENTRANCE(s,p):
        """PK入口"""
        s.pct("PK","是否开启:",p["data"]["is_open"])
    def l_PK_INFO(s,p):
        """PK信息"""
        s.pct("PK","服务器下发PK信息")
    def l_MESSAGEBOX_USER_GAIN_MEDAL(s,p):
        """获得粉丝勋章"""
        d=p["data"]
        s.pct("提示",f"{d['fan_name']} 获得粉丝勋章")
        s.pct("提示",f"提示标题: {d['msg_title']}")
        s.pct("提示",f"提示内容: {d['msg_content']}")
    def l_MESSAGEBOX_USER_MEDAL_CHANGE(s,p):
        """粉丝勋章更新"""
        d=p["data"]
        y=d["type"]
        if y==1:
            s.pct("提示",d["upper_bound_content"])
        elif y==2:
            s.pct("提示","重新点亮了勋章:",d["medal_name"])
        else:
            z=f"未知的粉丝勋章更新类型: {y}"
            s.pct("支持",z)
            raise SavePack(z)
    def l_RECOMMEND_CARD(s,p):
        """推荐卡片"""
        d=p["data"]
        s.pct("广告","推荐卡片","推荐数量:",len(d["recommend_list"]),"更新数量:",len(d["update_list"]))
    def l_GOTO_BUY_FLOW(s,p):
        """购买商品"""
        s.pct("广告",p["data"]["text"])
    def l_HOT_BUY_NUM(s,p):
        """热购数量"""
        d=p["data"]
        s.pct("广告","商品id",d["goods_id"],"热抢数量",d["num"])
    def l_AD_GAME_CARD_REFRESH(s,p):
        """推广游戏卡刷新"""
        d=p["data"]
        s.pct("广告",f"游戏卡id:{d['card_id']} 用户不重复点击数: {d['game_card_click_uv']}")
    def l_LOG_IN_NOTICE(s,p):
        """登录提示"""
        d=p["data"]
        s.pct("需要登录",d["notice_msg"])
    def l_GUARD_HONOR_THOUSAND(s,p):
        """千舰主播增减"""
        pass
    def l_GIFT_STAR_PROCESS(s,p):
        """礼物星球进度"""
        d=p["data"]
        s.pct("提示","礼物星球",f"status:{d['status']}",d["tip"])
    def l_WIDGET_GIFT_STAR_PROCESS(s,p):
        """礼物星球小部件进度更新"""
        d=p["data"]
        s.pct("提示","礼物星球进度更新")
    def l_ANCHOR_LOT_CHECKSTATUS(s,p):
        """天选时刻审核状态"""
        d=p["data"]
        s.pct("天选时刻","状态更新",f"id:{d['id']},status:{d['status']},uid:{d['uid']}")
    def l_ANCHOR_LOT_START(s,p):
        """天选时刻开始"""
        d=p["data"]
        s.pct("天选时刻",d["award_name"],f"{d['award_num']}人",f'''发送"{d['danmu']}"参与,需要"{d['require_text']}"''',f"id:{d['id']}",f"最大时间{d['max_time']}秒,剩余{d['time']}秒")
    def l_ANCHOR_LOT_END(s,p):
        """天选时刻结束"""
        d=p["data"]
        s.pct("天选时刻","id为",d["id"],"的天选时刻已结束")
    def l_ANCHOR_LOT_AWARD(s,p):
        """天选时刻开奖"""
        d=p["data"]
        s.pct("天选时刻",d["award_name"],f"{d['award_num']}人","已开奖",f"id:{d['id']}",f"中奖用户数量{len(d['award_users'])}")
    def l_ANCHOR_LOT_NOTICE(s,p):
        """天选时刻通知"""
        d=p["data"]
        if d["notice_type"]!=1:
            s.pct("支持","天选时刻类型为:",d["notice_type"])
            raise SavePack("未知的天选通知类型")
        c=d["lottery_card"]
        s.pct("天选时刻","通知卡",c["title"])
    def l_ANCHOR_NORMAL_NOTIFY(s,p):
        """推荐提示(推测)"""
        d=p["data"]
        s.pct("通知","推荐",f"type:{d['type']},show_type:{d['show_type']}",d["info"]["content"])
    def l_POPULAR_RANK_GUIDE_CARD(s,p):
        """冲榜提示卡"""
        h="提示"
        d=p["data"]
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
        s.pct(h,"标题:",d["dialog_title"])
        for i in d["dialog_message_list"]:
            if i["type"]==1:
                s.pct(h,f"{i['label']}：{i['content']}")
            else:
                s.pct(z,"未知对话框内容类型",i["type"])
                e=True
        for i in d["dialog_tip_list"]:
            t=sp(i)
            for i1 in i["message_list"]:
                if i1["type"] in [1,2]:
                    t+=i1["content"]
                else:
                    e=True
            s.pct(h,"提示:",t)
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
        s.pct(h,"窗口标题:",cut["cut_off_title"])
        for i in cut["cut_off_message_list"]:
            if i["type"]==1:
                s.pct(h,f"{i['label']}：{i['content']}")
            else:
                s.pct(z,"未知对话框内容类型",i["type"])
                e=True
        for i in cut["cut_off_tip_list"]:
            t=sp(i)
            for i1 in i["message_list"]:
                if i1["type"] in [1,2]:
                    t+=i1["content"]
                else:
                    e=True
            s.pct(h,"提示:",t)
        for i in cut["cut_off_button_list"]:
            if i["button_action"]==1:
                s.pct(h,"[按钮:关闭窗口]",i["button_text"])
            else:
                e=True
        if e:
            raise SavePack("对话框有某个类型未知")
    def l_ROOM_CONTENT_AUDIT_REPORT(s,p):
        """直播间内容审核结果"""
        d=p["data"]
        s.pct("直播","标题:",d["audit_title"],"审核结果:",d["audit_reason"])
    def l_SYS_MSG(s,p):
        """系统消息"""
        s.pct("系统消息",p["msg"])
    def l_PLAY_TAG(s,p):
        """直播进度条节点标签"""
        d=p["data"]
        s.pct("直播","进度条标签",f"id:{d['tag_id']} 时间戳:{d['timestamp']} 类型: {d['type']}")
    def l_PLAYTOGETHER_ICON_CHANGE(s,p):
        """(未知)一起玩图标更新"""
        d=p["data"]
        s.pct("状态","一起玩图标","分区",d["area_id"],"has_perm:",d["has_perm"],"show_count:",d["show_count"])
    def l_CHG_RANK_REFRESH(s,p):
        """(未知)可能是刷新排行榜"""
        pass
    def l_POPULARITY_RANK_TAB_CHG(s,p):
        """(未知)排行标签更新?"""
        pass
    def l_ANCHOR_BROADCAST(s,p):
        """初次抵达某种情况时的提示"""
        d=p["data"]
        s.pct("提示",d["sender"],d["msg"])
    def l_ANCHOR_HELPER_DANMU(s,p):
        """同上，但是格式不同"""
        d=p["data"]
        s.pct("提示",d["sender"],d["msg"])
    def l_OTHER_SLICE_LOADING_RESULT(s,p):
        """直播切片数据加载结果"""
        d=p["data"]
        for i in d["data"]:
            s.pct("事件","剪辑片段数据","开始于:",i["start_time"],",结束于:",i["end_time"],",片段视频流:",i["stream"])
    def l_INTERACTIVE_USER(s,p):
        """交互提示?"""
        s.pct("提示","用户交互",p["data"]["value"]["dm_msg"])
    def l_PANEL_INTERACTIVE_NOTIFY_CHANGE(s,p):
        """面板交互通知更改?"""
        s.pct("提示","玩法交互通知",p["data"]["text"])
    def l_FANS_CLUB_POKE_GIFT_NOTICE(s,p):
        """粉丝团戳一戳要礼通知"""
        s.pct("提示",p["data"]["text"])
    def l_master_qn_strategy_chg(s,p):
        """某种更新"""
        s.pct("数据包","master_qn_strategy_chg",p["data"])
