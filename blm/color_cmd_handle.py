"""额外的命令处理
由bili_live_ws.py的命令处理调用处派生而来
进行额外的上色，仅适用于shell
并不是所有的shell都支持这些颜色，在使用前请先确认你的终端是否支持对应颜色"""

import re,json,time,asyncio
from typing import Any
from __main__ import DEBUG,TIMEFORMAT,log,swd,brs,SavePack,error
try:
    from __main__ import ls_uid
except ImportError:
    ls_uid=-65536

def cbt(n):# 生成颜色操作
    return f"\33[{n}m"
def cfc(n):# 生成前景颜色
    return f"\33[38;5;{n}m"
def cfb(n):# 生成背景颜色
    return f"\33[48;5;{n}m"
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
TKEY=cfc(27)# key
TSTR=cfc(28)# string

# 正则表达式
RGPL=re.compile("<%(.+?)%>")

# 其它操作
dm_inter_list={}
clr_dm_inter_task=None

def cuse(m:str):# 渲染用户颜色
    return RGPL.sub(TUSR+"\\1"+CD,m)

def p(n:str,*d:Any,**t:"print参数")->None:
    print(f"{TRTG}{DB}[{n}]{DF}",*d,DF,**t)

def l_danmu_msg(d):# 弹幕
    if d[1]in swd:
        return
    for b in brs:
        if b.search(d[1]):
            return
    tc=""
    if ls_uid==d[2][0]:
        tc+=f"{C_01}(主播){CD}"
    if d[2][2]==1:
        tc+=f"{C_13}(房){CD}"
    p("弹幕",f"{tc}{TUSR}{d[2][1]}{CD}:{C_07}",d[1])
def l_interact_word(d,o):# 交互
    info="交互"
    mt=d["msg_type"]
    nm=f"{TUSR}{d['uname']}{CD}"
    if mt==1:
        if not o.no_enter_room:
            p(info,nm,"进入直播间")
    elif mt==2:
        p(info,nm,"关注直播间")
    elif mt==3:
        p(info,nm,"分享直播间")
    else:
        t=f"未知的交互类型: {d['msg_type']}"
        log.debug(t)
        if not o.no_print_enable:
            p("支持",t)
        raise SavePack("未知的交换类型")
def l_entry_effect(d):# 进场
    p("进场",cuse(d["copy_writing"]))
def l_send_gift(d):# 礼物
    p("礼物",f'{TUSR}{d["uname"]}{CD}',d["action"],d["giftName"],TNUM+"×",d["num"])
def l_combo_send(d):# 组合礼物
    p("礼物",f'{TUSR}{d["uname"]}{CD}',d["action"],d["gift_name"],TNUM+"×",d["total_num"])
def l_watched_change(d):# 看过
    if DEBUG:
        p("观看",f"{TNUM}{d['num']}{CD} 人看过; {TKEY}text_large: {TSTR}{d['text_large']}")
    else:
        p("观看",f"{TNUM}{d['num']}{CD} 人看过")
def l_super_chat_message(d):# 醒目留言
    p("留言",f"{TUSR}{d['user_info']['uname']}{CD}({C_11}￥{d['price']}{CD}):{C_07}",d["message"])
def l_super_chat_message_delete(d):# 醒目留言删除
    p("留言","醒目留言删除:",d["data"]["ids"])
def l_live_interactive_game(d):# 某种相同弹幕
    if d["msg"]in swd:
        return
    for b in brs:
        if b.search(d["msg"]):
            return
    p("弹幕(LIG)",f"{TUSR}{d['uname']}{CD}:{C_10}",d["msg"])
def l_room_change(d):# 直播间更新
    print(f"{B_05}{TRTG}[直播]{CD} 分区:{C_06} {d['parent_area_name']} {C_02}>{C_06} {d['area_name']} {CD}标题: {C_06}{d['title']}{DF}")
def l_live(b):# 开始直播
    print(f"{B_05}{TRTG}[直播]{CD} 直播间 {TRMI}{b['roomid']}{CD} 开始直播{DF}")
def l_preparing(b):# 结束直播
    print(f"{B_05}{TRTG}[直播]{CD} 直播间 {TRMI}{b['roomid']}{CD} 结束直播{DF}")
def l_room_real_time_message_update(d):# 数据更新
    p("信息",f"{TRMI}{d['roomid']}{CD} 直播间 {TNUM}{d['fans']}{CD} 粉丝")
def l_stop_live_room_list(d):# 停止直播的房间列表
    p("停播","停止直播的房间列表:",f"len({len(d['room_id_list'])})")
def l_room_block_msg(b):# 用户被禁言
    p("直播","用户"+TUSR,b["uname"],CD+"已被禁言")
def l_cut_off(b):# 警告
    p("直播","直播间"+TRMI,b["room_id"],CD+"被警告:"+B_01,b["msg"])
def l_room_lock(b):# 封禁
    p("直播","直播间"+TRMI,b["roomid"],CD+"被封禁，解除时间:",b["expire"])
def l_room_admins(b):# 房管列表
    p("直播",f"房管列表: len({len(b['uids'])})")
def l_change_room_info(b):# 背景更换
    p("直播",f"直播间 {TRMI}{b['roomid']}{CD} 信息变更 背景图: {DU}{b['background']}")
def l_danmu_aggregation(d):# 弹幕聚集
    p("弹幕聚集",f"{C_10}{d['msg']}{CD} {TNUM}×{d['aggregation_num']}")
def l_online_rank_count(d):# 在线计数
    olc=""
    if "online_count"in d:
        olc=CD+"在线计数: "+TNUM+str(d["online_count"])
    p("计数","高能用户计数:"+TNUM,d["count"],olc)
def l_little_tips(d):# 小提示
    p("提示",f"{C_15}{d['msg']}")
def l_little_message_box(d):# 弹框提示
    p("弹框",f"{B_04}{C_17}{d['msg']}{BD}")
def l_voice_join_list(d):# 连麦列表
    p("连麦","申请计数:"+TNUM,d["apply_count"])
def l_online_rank_top3(d):# 前三个第一次成为高能用户
    ts=d["list"][0]
    if DEBUG:
        p("排行",f"len({len(d['list'])}) {cuse(ts['msg'])} {TKEY}rank:{TNUM}{ts['rank']}")
    else:
        p("排行",f"{cuse(ts['msg'])} {TKEY}rank:{TNUM}{ts['rank']}")
def l_voice_join_status(d):# 连麦状态
    if d["status"]==0:
        p("连麦","停止连麦")
    elif d["status"]==1:
        p("连麦","正在与"+TUSR,d["user_name"],CD+"连麦")
    else:
        log.debug(f"未知的语音状态: {d['status']}")
        raise SavePack("未知的语音连麦状态")
def l_online_rank_v2(d,npe):
    rt=d["rank_type"]
    if rt=="gold-rank":
        p("排行","高能用户部分列表(gr):",f"len({len(d['list'])})")
    elif rt=="online_rank":
        p("排行","高能用户部分列表:",f"len({len(d['online_list'])})")
    else:
        nt="未知的排行类型"
        log.debug(f"{nt}: '{d['rank_type']}'")
        if not npe:
            p("支持",nt+":",d["rank_type"])
        raise SavePack(nt)
def l_hot_rank_settlement(d):# 热门通知
    p("排行",d["dm_msg"])
def l_common_notice_danmaku(d):# 通知
    for cse in d["content_segments"]:
        cset=cse["type"]
        if cset==1:
            p("通知",RGPL.sub(C_13+"\\1"+CD,cse["text"]))
        elif cset==2:
            p("通知","图片:",f"{DU}{cse.get('img_url')}")
        else:
            p("通知",C_07+DI+"无法展示的通知组件")
            log.debug(f"未知的通知组件类型: {cset}")
            raise SavePack("通知组件类型")
def l_notice_msg(d):# 公告(广播)
    msg=d["msg_self"]
    msg=cuse(msg)
    if "name"in d:
        p("公告",d["name"],C_04+"=>"+CD,msg)
    else:
        p("公告",msg)
def l_guard_buy(d):# 舰队购买
    p("礼物",f"{TUSR}{d['username']}{CD} 购买了{TNUM}{d['num']}{CD}个 {d['gift_name']}")
def l_user_toast_msg(d):# 舰队续费
    p("提示",cuse(d["toast_msg"]))
def l_widget_banner(d):# 小部件
    for wi in d["widget_list"]:
        if d["widget_list"][wi]is None:
            continue
        p("小部件",f"{TKEY}key:{TSTR}{wi}{CD}","id",d["widget_list"][wi]["id"],"标题:",d["widget_list"][wi]["title"])
def l_super_chat_entrance(d):# 醒目留言入口变化
    if d["status"]==0:
        p("信息","关闭醒目留言入口")
    else:
        log.debug(f"status: {d['status']}")
        p("支持",f"未知的'SUPER_CHAT_ENTRANCE'{TKEY}status{CD}数字:{TNUM}",d["status"])
        print(DB+DI+"因为样本稀少，暂不提供屏蔽该不支持信息"+DF)
        raise SavePack("未知的status")
def l_room_skin_msg(d):# 直播间皮肤更新
    p("信息","直播间皮肤更新",f"{TKEY}id: {TSTR}{d['skin_id']}{CD} ,{TKEY}status: {TSTR}{d['status']}{CD}",",结束时间:",time.strftime(TIMEFORMAT,time.gmtime(d["end_time"])),",当前时间:",time.strftime(TIMEFORMAT,time.gmtime(d["current_time"])))
def l_live_multi_view_change(d):
    p("信息","LIVE_MULTI_VIEW_CHANGE",d)
def l_popularity_red_pocket_new(d):
    p("通知",f"{TUSR}{d['uname']}{CD} {d['action']} 价值 {TNUM}{d['price']}{CD} 电池的 {d['gift_name']}")
def l_popularity_red_pocket_start(d):
    if d["danmu"]not in swd:
        swd.append(d["danmu"])
        p("屏蔽","屏蔽词增加:",d["danmu"])
def l_like_info_v3_update(d):# 点赞数量
    p("计数","点赞点击数量:"+TNUM,d["click_count"])
def l_like_info_v3_click(d):# 点赞点击
    p("交互",f"{TUSR}{d['uname']}{CD} {d['like_text']}")
def l_popular_rank_changed(d):# 人气排行更新
    p("排行","人气榜第"+TNUM,d["rank"],CD+"名")
def l_area_rank_changed(d):# 大航海排行更新
    p("排行",d["rank_name"],"第"+TNUM,d["rank"],CD+"名")
async def clr_dm_inter():# 清理长时间无变化的信息
    d=dm_inter_list
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
    except:
        error(f"dm_inter_list={d}")
def dm_inter_min(id,cnt):# 控制交互合并的打印
    global clr_dm_inter_task
    d=dm_inter_list
    def tm():
        return int(time.time())
    if clr_dm_inter_task is None:
        clr_dm_inter_task=asyncio.create_task(clr_dm_inter(),name="清理不使用的交互合并id")
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
def l_dm_interaction(d):# 交互合并
    s="交互合并"
    n=json.loads(d["data"])
    t=d["type"]
    if t==102:
        for c in n["combo"]:
            if dm_inter_min(c["id"],c["cnt"]):return
            p(s,f"{C_10}{c['guide']}{C_07}",c["content"],TNUM+"×"+str(c["cnt"]))
    elif t==104:
        if dm_inter_min(d["id"],n["cnt"]):return
        p(s,f"{TNUM}{n['cnt']}{C_10} {n['suffix_text']} {TKEY}gift_id: {TSTR}{n['gift_id']}")
    elif t==103 or t==105 or t==106:
        if dm_inter_min(d["id"],n["cnt"]):return
        p(s,f"{TNUM}{n['cnt']}{C_10} {n['suffix_text']}")
    else:
        log.debug(f"未知的交互合并类型: {t}")
        raise SavePack("交互合并类型")
def pk_id_status(d:dict)->str:# 处理pk的id和status
    return f"{TKEY}id:{TSTR}{d['pk_id']}{CD} {TKEY}s:{TNUM}{d['pk_status']}{CD}"
def l_pk_battle_pre(d):# PK即将开始
    p("PK","PK即将开始",pk_id_status(d),f"对方直播间 {TRMI}{d['data']['room_id']}{CD}","昵称:"+TUSR,d["data"]["uname"])
def l_pk_battle_start(d):# PK开始
    a=d["data"]
    p("PK","PK开始",pk_id_status(d),"计数名称:",a["pk_votes_name"],f"增量:{a['pk_votes_add']}")
def l_pk_battle_process(d):# PK过程
    a=d["data"]
    i=a["init_info"]
    m=a["match_info"]
    p("PK","计数更新",pk_id_status(d),f"直播间{TRMI}{i['room_id']}{CD}已有{TNUM}{i['votes']}{CD}票，直播间{TRMI}{m['room_id']}{CD}已有{TNUM}{m['votes']}{CD}票")
def l_pk_battle_final_process(d):# PK结束流程变化
    p("PK","PK结束流程变化",pk_id_status(d))
def l_pk_battle_end(d):# PK结束
    a=d["data"]
    i=a["init_info"]
    m=a["match_info"]
    p("PK","PK结束",pk_id_status(d),f"直播间{TRMI}{i['room_id']}{CD}获得{TNUM}{i['votes']}{CD}票，直播间{TRMI}{m['room_id']}{CD}获得{TNUM}{m['votes']}{CD}票")
def l_pk_battle_settle_v2(d):# PK结算2
    a=d["data"]
    p("PK","PK结算",pk_id_status(d),"主播获得",a["result_info"]["pk_votes"],a["result_info"]["pk_votes_name"])
def l_pk_battle_settle_new(b):# 惩罚
    p("PK","进入惩罚时间",pk_id_status(b))
def l_pk_battle_video_punish_begin(b):# 视频惩罚
    p("PK","进入惩罚时间",pk_id_status(b))
def l_pk_battle_punish_end(b):# 惩罚结束
    p("PK","惩罚时间结束",pk_id_status(b))
def l_pk_battle_video_punish_end(b):# 视频惩罚结束
    p("PK","惩罚时间结束",pk_id_status(b))
def l_recommend_card(d,s):# 推荐卡片
    p("广告","推荐卡片","推荐数量:",len(d["recommend_list"]),"更新数量:",len(d["update_list"]))
    if s:
        raise SavePack("保存推荐卡片")
def l_goto_buy_flow(d):# 购买推荐
    p("广告",d["text"])
def l_log_in_notice(d):# 登录通知
    print(f"{B_02}{TRTG}[需要登录]{CD}",d["notice_msg"],DF)
def l_guard_honor_thousand(d):# 千舰主播增减
    def ts(l:list[int])->list[str]:
        r:list[str]=[]
        for i in l:
            r.append(str(i))
        return r
    ad=ts(d["add"])
    dl=ts(d["del"])
    p("提示","千舰主播增加:",','.join(ad),"减少:",','.join(dl))
def l_gift_star_process(d):# 礼物星球进度
    p("提示","礼物星球",f"{TKEY}status:{TNUM}{d['status']}{CD}",d["tip"])
def l_anchor_lot_checkstatus(d):# 天选时刻审核状态
    p("天选时刻","状态更新",f"{TKEY}id:{TNUM}{d['id']}{TKEY},status:{TNUM}{d['status']}{TKEY},uid:{TNUM}{d['uid']}")
def l_anchor_lot_start(d):# 天选时刻开始
    p("天选时刻",d["award_name"],f"{TNUM}{d['award_num']}{CD}人",f'''发送{C_07}"{d['danmu']}"{CD}参与,需要"{d['require_text']}"''',f"{TKEY}id:{TNUM}{d['id']}{CD}",f"最大时间{TNUM}{d['max_time']}{CD}秒,剩余{TNUM}{d['time']}{CD}秒")
def l_anchor_lot_end(d):# 天选时刻结束
    p("天选时刻","id为",d["id"],"的天选时刻已结束")
def l_anchor_lot_award(d):# 天选时刻开奖
    p("天选时刻",d["award_name"],f"{d['award_num']}人","已开奖",f"{TKEY}id:{TNUM}{d['id']}{CD}",f"中奖用户数量{len(d['award_users'])}")
def l_anchor_normal_notify(d):# 推荐提示
    p("通知","推荐",f"{TKEY}type:{TNUM}{d['type']}{TKEY},show_type:{TNUM}{d['show_type']}{CD}",d["info"]["content"])
def l_popular_rank_guide_card(d):
    h="提示"
    p(h,d["title"])
    p(h,d["sub_text"])
    p(h,d["popup_title"])
def l_sys_msg(b):# 系统消息
    p("系统消息",b["msg"])
def l_play_tag(d):# 直播进度条标签
    p("直播","进度条标签",f"{TKEY}id:{TNUM}{d['tag_id']}{CD} 时间戳:{TNUM}{d['timestamp']}{CD} 类型: {TSTR}{d['type']}{CD} 图片: {DU}{d['pic']}")
