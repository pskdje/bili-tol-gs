"""启动BLM UI
本文件高度定制，不建议作为模块导入。
可将扩展名从 .py 改为 .pyw 来避免启动时弹出终端窗口，但这将意味着无法看到运行细节，风险自负。
"""

import sys,os
import blw
import blt
import blm_ui
import argparse
import tkinter.simpledialog
import tkinter.messagebox
from pathlib import Path
from blw import GetDataError,WSClientError,ArgsParser,from_list_add_args

log=blw.log

class GUI(blm_ui.WindowCloseExit,blt.DanmuTools):
    """最终用户界面"""

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
        parser.add_argument("-d","--debug",help="开启调试模式",action="store_true")
        parser.add_argument("--roomid",help="直播间ID",type=int,default=0)
        parser.add_argument("--cookie",help="使用Cookie登录",type=self.get_Cookie,metavar="Cookie|FILE")
        parser.add_argument("--no-print-enable",help="不打印不支持的信息",action="store_true")
        parser.add_argument("--pack-error-no-exit",help="数据包处理异常时不退出",action="store_false")
        parser.add_argument("--no-del-error-dir-list",help="不删除错误记录文件夹内的旧文件",action="store_false",dest="del_errdir_list")
        dbg=parser.add_argument_group("调试功能")
        dbg.add_argument("-u","--save-unknow-datapack",help="保存未知的数据包",action="store_true")
        dbg.add_argument("-C","--print-pack-count",help="打印数据包计数",action="store_true")
        dbg.add_argument("-c","--count-cmd",help="对某个cmd进行计数",action="append",metavar="CMD",default=[])
        dbg.add_argument("-s","--save-cmd",help="保存某个cmd数据包",action="append",metavar="CMD",default=[])
        cmd=parser.add_argument_group("关闭某个cmd的显示")
        from_list_add_args(cmd,self.cmd_args)
        return parser

    def check_CWD(self)->None:
        """检查当前工作目录"""
        PATH=Path(__file__).parent
        log.info(f"CWD检查，文件路径: {PATH}")
        if Path.cwd()!=PATH:
            log.info(f"CWD偏移 '{os.getcwd()}' ，将修改回文件的父目录")
            print("CWD:",os.getcwd())
            os.chdir(PATH)
            print("   ->",os.getcwd())

    def handle_errdirlist(self):
        """处理错误记录列表"""
        log.info("清理错误记录文件夹内的文件")
        filelist=sorted(Path("bili_live_ws_err").iterdir())
        log.debug(f"文件列表: {filelist}")
        if len(filelist)<5:return
        del_num=len(filelist)-5
        for i in range(del_num-1):
            log.debug(f"删除文件: {filelist[i]}")
            filelist[i].unlink()

    def start(self):
        """启动用户界面(高度定制化)"""
        log.info("使用特化图形界面运行")
        a=self.pararg()
        self.p("启动 BLM UI")
        self.p("由于底层逻辑本身是基于终端下运行来编写的，再加上B站没有正确按照 RFC 6455 传输数据包，导致当前使用的WS库在关闭时会稍作等待，因此终端界面不会立即退出。")
        self.p("若你关闭GUI窗口后等待40秒终端依然未关闭，则需要手动按下窗口的关闭按钮。")
        self.p("若你是在终端界面按下中断键，当等待超过10秒才需强制关闭。")
        self.p("不想看到终端界面的话，可以考虑使用 pythonw 启动，这将意味着无法看到运行细节，风险自负。")
        self.p("")
        self.check_CWD()
        if not blw.DEBUG and a.del_errdir_list:
            self.handle_errdirlist()
        if self.roomid<1:
            roomid=tkinter.simpledialog.askinteger("输入直播间ID","在文本框中输入直播间ID\n短号ID将会自动解析为实际ID\n只允许输入正整数",minvalue=1)
            if roomid is None:
                self.p("中断: 未提供直播间ID")
                self.p("没有直播间ID你想让程序怎么运行？")
                tkinter.messagebox.showerror("中断","未提供直播间ID，无法运行。")
                sys.exit(1)
            self.roomid=roomid
            del roomid
        self.p("获取数据…")
        if isinstance(a.cookie,blw.CookiesAgent):
            for ck,cv in a.cookie.items():
                self.cookies.set(ck,cv,domain=".bilibili.com")
        elif len(self.cookies)<1:
            inputCookie=tkinter.simpledialog.askstring("提供登录信息","在文本框中提供登录Cookie。\n注意：若不登录将会导致服务器下发直播信息流的数据不完整。")
            if inputCookie:
                cookieData=blw.split_kv_cookie(inputCookie)
                for ck,cv in cookieData.items():
                    self.cookies.set(ck,cv,domain=".bilibili.com")
                del cookieData
            del inputCookie
        try:
            del ck,cv
        except NameError:pass
        log.info("获取信息")
        try:
            self.get_login_nav()
            self.get_room_init()
        except GetDataError as e:
            self.p(str(e))
            tkinter.messagebox.showwarning("初始化失败","获取直播间初始化信息失败，详见输出和日志。")
            sys.exit(1)
        except KeyboardInterrupt:
            self.p("获取信息流操作被中断")
            sys.exit(0)
        self.p("启动客户端…")
        log.info("初始化UI")
        self.start_blm_ui()
        self.blm_ui_obj.env=self
        log.info("开始循环")
        while True:
            try:
                info=self.get_ws_info()
                self.run_blw_client(info["wss_host"],info["token"])
            except GetDataError as e:
                self.p(str(e))
                t=e.datas.get("type")
                if t!="timeout" or t!="request":
                    self.close()
                    tkinter.messagebox.showwarning("无法认证","获取信息流地址和认证失败，详见输出和日志。")
                    sys.exit(1)
                del t
            except WSClientError as e:
                self.p(str(e))
                self.send_msg_to_ui({"t":"ev","msg":"信息流断开"})
            except KeyboardInterrupt:
                self.p("关闭")
                self.print_cmd_count()
                self.close()
                sys.exit(0)
            else:
                break
            self.p("重新连接")

if __name__=="__main__":
    GUI().start()
