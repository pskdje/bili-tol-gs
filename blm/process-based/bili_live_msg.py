#!/usr/bin/env python
"""哔哩哔哩直播信息流
直接使用bili_live_ws的功能
在该基础上增加一些功能
使用的第三方库: requests
还需注意bili_live_ws使用的第三方库
可以尝试给予本文件执行权限来直接运行
"""

import time
from sys import exit
import requests
import bili_live_ws as blw

ua=blw.UA
log=blw.log
ls_uid=0
default_header={"User-Agent":ua}

def __getattr__(name):
    log.debug(f"在blm获取blw的'{name}'",stacklevel=2)
    return getattr(blw,name)

def get_rest_data(url:str,tip:str="",header:dict=None,**oa)->dict:
    he={}
    if isinstance(header,dict):
        he=header
    try:
        r=requests.get(
            url,
            headers=default_header|he,
            **oa
        )
    except Exception:
        blw.error()
        exit(f"获取{tip}信息失败")
    log.debug(r.text,stacklevel=2)
    if r.status_code!=200:
        print(r.text)
        blw.save_http_error(r,"状态码")
        exit("服务器错误")
    try:
        d=r.json()
    except:
        blw.save_http_error(r,f"{tip}json数据")
        exit(f"无法解析{tip}数据")
    if d["code"]==60004:
        print("直播间不存在")
        exit(0)
    if d["code"]!=0:
        print(f"{tip}接口返回的code不为0")
        print(d["code"],"-",d["message"])
        blw.save_http_error(r,"键code")
        exit(1)
    return d["data"]

def get_room_init(roomid:int)->dict:
    """获取直播间初始化信息"""
    return get_rest_data("https://api.live.bilibili.com/room/v1/Room/room_init?id="+str(roomid),"直播间初始化")

def get_room_info(mid:int)->dict:
    """获取直播间信息"""
    return get_rest_data("https://api.live.bilibili.com/room/v1/Room/get_info?room_id="+str(mid),"直播间信息")

def get_master_info(mid:int)->dict:
    """获取主播信息"""
    return get_rest_data("https://api.live.bilibili.com/live_user/v1/Master/info?uid="+str(mid),"主播信息")

def get_playurl(cid:int)->dict:
    """获取直播视频流"""
    return get_rest_data("https://api.live.bilibili.com/room/v1/Room/playUrl","直播视频流",
    params={
        "cid":cid,
        "platform":"web",
        "quality":4
    })

def print_playurl(rmid):
    d=get_playurl(rmid)
    print("当前画质代码:",d["current_quality"])
    print("可选画质:",d["accept_quality"])
    for i in d["durl"]:
        print(f"线路{i['order']}链接:",i["url"])

def main():
    global ls_uid
    try:
        o=blw.pararg([
            {"name":"not-live-retain","help":"未直播时不退出","action":"store_false"},
            {"name":"no-show-room-info","help":"不显示房间信息","action":"store_false"},
            {"name":"no-show-master-info","help":"不显示主播信息","action":"store_false"},
            {"name":"get-room-playurl","help":"获取直播视频流","action":"store_true"}
        ])
        if blw.DEBUG:
            print("版本信息:",blw.VERSIONINFO)
            print("命令行参数:",o)
            print("启动时间戳:",blw.starttime)
            blw.set_log()
            blw.set_wslog()
        log.info("获取额外信息")
        print("获取数据…")
        ri=get_room_init(o.roomid)
        roomid=ri["room_id"]
        ls_uid=ri["uid"]
        print("直播间:",ri["room_id"],""if ri["short_id"]==0 else f"({ri['short_id']})")
        print("用户ID:",ri["uid"])
        print("状态:",end=" ")
        lis=ri["live_status"]
        if lis==0:
            print("未开播")
        elif lis==1:
            print("直播中")
        elif lis==2:
            print("轮播中")
        else:
            print(lis)
        print("开播时间:",end=" ")
        if ri["live_time"]>0:
            print(time.strftime(blw.TIMEFORMAT,time.localtime(ri["live_time"])))
        else:
            print("0 (未开播)")
        if o.no_show_room_info:
            ru=get_room_info(roomid)
            print("标题:",ru["title"])
            print("封面:",ru["user_cover"])
            print("背景图:",ru["background"])
            print("关键帧:",ru["keyframe"])
            print("《简介》:`",ru["description"],"`")
            print("分区:",ru["parent_area_name"],">",ru["area_name"])
            print("开始时间:",ru["live_time"])
            print("观看人数:",ru["online"])
            print("标签:",ru["tags"])
            del ru
        if o.no_show_master_info:
            mi=get_master_info(ls_uid)
            mif=mi["info"]
            print("主播:",mif["uid"],f"({mif['uname']})")
            print("性别:",end=" ")
            gdr=mif["gender"]
            if gdr==-1:
                print("保密")
            elif gdr==0:
                print("女")
            elif gdr==1:
                print("男")
            else:
                print("未知")
            oflv=mif["official_verify"]
            print("认证:","无"if oflv["type"]==-1 else oflv["desc"])
            print("等级:",mi["exp"]["master_level"]["level"])
            print("粉丝数量:",mi["follower_num"])
            print("粉丝勋章:",mi["medal_name"])
            print("荣誉数量:",mi["glory_count"])
            print("直播间头像框:",mi["pendant"])
            rnw=mi["room_news"]
            print("主播公告:`",rnw["content"],"`",rnw["ctime"])
            del mif,gdr,oflv,rnw,mi
        if lis==0 and o.not_live_retain:
            log.info("直播间未直播且未阻止自动退出")
            print("当前直播间未直播，将自动退出。")
            exit(0)
        del lis,ri
        if o.get_room_playurl:
            print_playurl(roomid)
        # live
        log.info("载入数据")
        print("载入数据…")
        if o.shielding_words:
            blw.shielding_words(o.shielding_words)
        if o.blocking_rules:
            blw.blocking_rules(o.blocking_rules)
        if o.atirch:
            r_ich=blw.import_cmd_handle()
            blw.idp("导入命令处理的结果:",r_ich)
            del r_ich
        print("连接直播间…")
        blw.start(roomid,o)
    except Exception:
        print("出现错误")
        blw.error()
        exit(1)
    except KeyboardInterrupt:
        print("关闭")
        if blw.DEBUG or o.print_pack_count:
            print("被测试的cmd计数:")
            blw.print_test_pack_count()
        exit(0)

if __name__=="__main__":
    log.info("blm已作为顶层入口")
    print("哔哩哔哩直播信息流")
    print("额外获取一些信息")
    main()
