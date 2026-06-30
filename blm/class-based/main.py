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
        if isinstance(a.cookie,blw.CookiesAgent):
            for ck,cv in a.cookie.items():
                self.cookies.set(ck,cv,domain=".bilibili.com")
        try:
            self.get_login_nav()
            if "buvid3" not in self.cookies:
                self.set_buvid3_4()
        except blw.GetDataError as e:
            self.p(str(e))
            sys.exit(1)
        except KeyboardInterrupt:
            self.p("处理鉴权信息流程被用户中断")
            sys.exit(0)
        self.run_room_init()
        self.run_getOtherMsg()
        try:
            info=self.get_ws_info()
        except blw.GetDataError as e:
            self.p(str(e))
            sys.exit(1)
        except KeyboardInterrupt:
            self.p("获取信息流操作被用户中断")
            sys.exit(0)
        self.p("启动客户端…")
        try:
            self.run_blw_client(info["wss_host"],info["token"])
        except blw.WSClientError as e:
            self.p(str(e))
            sys.exit(1)
        except SystemExit:
            self.p("cmd处理退出")
            self.print_cmd_count()
            raise
        except KeyboardInterrupt:
            self.p("用户中断")
            self.print_cmd_count()
            sys.exit(0)
        else:
            self.p("程序退出")
        finally:
            self.close()

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
