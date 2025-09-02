#!/bin/python
"""blm启动入口
可以用于启动 all_cmd_handle 和 color_cmd_handle
利用第1个位置参数控制要启动哪个。
若不填或填入的是非启动控制的项目，将启动color。
可选值: "all", "color"
"""

import sys,time
import blw,blm
import all_cmd_handle
import color_cmd_handle

class S(blm.BiliLiveMsg,blm.BiliLiveSaveExp):
    """特化启动逻辑"""
    add_args= blm.BiliLiveSaveExp.add_args + blm.BiliLiveMsg.add_args
    def start(self)->None:
        """带信息启动"""
        blm.log.info("使用项目启动函数开始运行")
        try:
            if sys.argv[1]in["all","color"]:
                ma=sys.argv[2:]
            else:
                ma=sys.argv[1:]
        except IndexError:
            ma=[]
        a=self.pararg(ma)
        self.p("获取数据…")
        if a.cookie:
            self.cookies|=a.cookie
        try:
            self.get_login_nav()
            if "buvid3" not in self.cookies:
                self.set_buvid3_4()
        except blw.GetDataError as e:
            self.p(str(e))
            sys.exit(1)
        try:
            ri=self.get_room_init()
        except blw.GetDataError as e:
            self.p(str(e))
            sys.exit(1)
        self.p("直播间:",ri["room_id"],""if ri["short_id"]==0 else f"({ri['short_id']})")
        self.p("用户ID:",ri["uid"])
        lis=ri["live_status"]
        lsm=str(lis)
        if lis==0:
            lsm="未开播"
        elif lis==1:
            lsm="直播中"
        elif lis==2:
            lsm="轮播中"
        self.p("状态:",lsm)
        ltt=""
        if ri["live_time"]>0:
            ltt=time.strftime(blw.TIMEFORMAT,time.localtime(ri["live_time"]))
        else:
            ltt="0 (未开播)"
        self.p("开播时间:",ltt)
        del lis,lsm,ltt,ri
        if a.no_show_room_info:
            self.print_room_info()
        if a.no_show_master_info:
            self.print_master_info()
        if a.get_room_playurl:
            self.print_playurl()
        try:
            info=self.get_ws_info()
        except blw.GetDataError as e:
            self.p(str(e))
            sys.exit(1)
        except KeyboardInterrupt:
            self.p("获取信息流操作被中断")
            sys.exit(0)
        self.p("启动客户端…")
        try:
            self.run_blw_client(info["wss_host"],info["token"])
        except blw.WSClientError as e:
            self.p(str(e))
            sys.exit(1)
        except KeyboardInterrupt:
            self.p("关闭")
            self.print_cmd_count()
            sys.exit(0)

class StartAllCmdHandle(all_cmd_handle.BiliLiveAllCmdHandle,S):
    """启动all"""

class StartColorCmdHandle(color_cmd_handle.AllCmdHandle,all_cmd_handle.BiliLiveAllCmdHandle,S):
    """启动color"""

    add_args= S.add_args + color_cmd_handle.AllCmdHandle.add_args

if __name__=="__main__":
    try:
        n=sys.argv[1]
    except IndexError:
        t=1
    else:
        if n=="all":
            t=0
        elif n=="color":
            t=1
        else:
            t=1
    if t==0:
        StartAllCmdHandle().start()
    elif t==1:
        StartColorCmdHandle().start()
    else:
        print("出现了奇怪的情况，请自行调试源代码。")
