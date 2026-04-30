"""哔哩哔哩信息流用户界面
基于Tkinter的UI，代码由AI生成后手动重构而来(因为看不懂文档)
"""

import time
import threading,queue
import random
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import font as tk_font
from typing import TYPE_CHECKING
if TYPE_CHECKING:
     import blt

type insert_text=tuple[str,str]
"""插入文本格式"""

class BLM_UI:
    """UI"""

    MAX_MSG:int=100
    """最多显示多少消息"""
    DEFAULT_FONT_NAME:str="Microsoft YaHei UI"
    """默认字体名称"""
    HIDE_DELAY:int=3000
    """底部默认隐藏时间"""

    TEXT_TAGS={
        "default":{"foreground":"black"},# 默认
        "datetime":{"foreground":"black","font":("Consolas",10)},# 日期时间
        "number":{"foreground":"#00e0e0"},# 数字
        "username":{"foreground":"#ffc706"},# 用户名
        "anchor":{"foreground":"red"},# 主播标签颜色
        "roomadmin":{"foreground":"#dbd800"},# 房管标签颜色
        "eventmsg":{"foreground":"black","font":(DEFAULT_FONT_NAME,10,"italic")},# 事件消息样式
        "gray":{"foreground":"gray"},# 灰色文本
        "warning":{"background":"#800000","foreground":"#FFFF00"},# 警告样式
        "superchat":{"background":"#2a60b2","foreground":"#ffffff"},# 醒目留言文本部分样式
        "notice":{"background":"#dfdfdf","foreground":"#818181"},# 通知样式
    }
    """预定义文本标签"""

    def __init__(self):
        """准备UI"""
        self.msg_queue=queue.Queue(1000)
        """消息队列"""
        self.running=threading.Event()
        """是否运行"""
        self.env:"blt.BiliLiveTools"|None=None
        """运行环境"""
        self.root=None
        """根窗口"""
        self.frame=None
        """主容器"""
        self.text=None
        """主消息区"""
        self.bottom_frame=None
        """底部文本容器"""
        self.bottom_text=None
        """底部文本"""
        self.bottom_font=None
        """底部文本格式"""
        self.context_menu=None
        """右键菜单"""
        self.hide_timer=None
        """隐藏id"""

    def p(self,*t)->None:
        """打印文本"""
        print(*t)

    def error(self,d=None,**v)->None:
        """记录错误"""
        import traceback
        traceback.print_exc()

    def create_ui(self)->None:
        """创建UI"""
        self.root=tk.Tk()
        self.root.title("直播")
        self.root.geometry("400x600")
        # frame
        self.frame=ttk.Frame(self.root,style="NoBorder.TFrame")
        self.frame.pack(side=tk.TOP,fill=tk.BOTH,expand=True,padx=0,pady=0)
        # text
        self.text=scrolledtext.ScrolledText(
            self.frame,
            wrap=tk.CHAR,
            state=tk.DISABLED,
            font=("Microsoft YaHei UI",10),
            width=0,
            height=0,
            bd=0,
            highlightthickness=0,
            relief=tk.FLAT
        )
        self.text.pack(side=tk.TOP,fill=tk.BOTH,expand=True,padx=0,pady=0)
        # bottom frame
        self.bottom_font=tk_font.Font(family=self.DEFAULT_FONT_NAME,size=10)
        self.bottom_frame=ttk.Frame(
            self.frame,
            style="NoBorder.TFrame",
            height=self.bottom_font.metrics("ascent") + self.bottom_font.metrics("descent") + 2
        )
        self.bottom_frame.pack(side=tk.TOP,fill=tk.BOTH,expand=True,padx=0,pady=0)
        self.bottom_frame.pack_propagate(False)
        self.bottom_frame.pack_forget()
        # bottom text
        self.bottom_text=tk.Text(
            self.bottom_frame,
            height=1,
            wrap=tk.NONE,
            state=tk.DISABLED,
            font=self.bottom_font,
            bd=0,
            highlightthickness=0,
            relief=tk.FLAT,
            bg=self.root.cget("bg"),# 匹配窗口背景色
            padx=2,
            pady=0
        )
        self.bottom_text.pack(side=tk.LEFT,fill=tk.X,expand=True,padx=0,pady=0)
        # text tags
        try:
            for TAG_NAME,TAG_CONFIG in self.TEXT_TAGS.items():
                self.text.tag_configure(TAG_NAME,**TAG_CONFIG)
                self.bottom_text.tag_configure(TAG_NAME,**TAG_CONFIG)
        except:
            self.error()
            self.p("[UI]: 有标签加载失败")
        # context menu
        self.context_menu=tk.Menu(self.root,tearoff=0)
        self.context_menu.add_command(label="复制全部",command=self.copy_all_text)
        self.context_menu.add_command(label="加载历史弹幕",command=self.load_history_danmu)
        self.context_menu.add_command(label="发送弹幕",command=self.send_danmu_dialog)
        self.text.bind("<Button-3>",self.show_context_menu)
        # end
        self.root.protocol("WM_DELETE_WINDOW",self.click_close_button)
        self.root.focus_force()
        self.root.update()

    def click_close_button(self)->None:
        """点击关闭按钮的操作"""
        self.p("[UI]: 通过关闭按钮关闭")
        self.stop()

    def is_scrolled_to_end(self)->bool:
        """判断是否滚动到末尾"""
        try:
            return self.text.yview()[1]>=0.95
        except:
            return True

    def show_context_menu(self,event)->None:
        """显示右键菜单"""
        self.context_menu.post(event.x_root,event.y_root)

    def copy_all_text(self)->None:
        """复制全部文本到剪贴板"""
        try:
            all_text=self.text.get(1.0,tk.END).strip()
            self.root.clipboard_clear()
            self.root.clipboard_append(all_text)
        except Exception as e:
            et="复制全部文本到剪贴板失败"
            self.error(et)
            self.p(f"[UI]: {et}:",e)

    def load_history_danmu(self)->None:
        """加载历史弹幕"""
        if self.env is None or not hasattr(self.env,"get_dm_history"):
            self.p("[UI]: 环境无效，无法加载历史弹幕")
            return
        def thread_func():
            from blw import GetDataError
            self.p("[UI]: 历史弹幕开始加载")
            hlet="历史弹幕加载失败"
            try:
                d=self.env.get_dm_history()["data"]
                for i in d["room"]:
                    self.send_msg({"t":"dm","uname":i["nickname"],"danmu":i["text"],"isAnchor":self.env.up_uid==i["uid"],"isAdmin":i["isadmin"]==1})
            except GetDataError as e:
                self.p(f"[UI]: {hlet}，可能是因为接口请求失败，错误信息: {e}")
            except:
                self.error(hlet)
                self.p(f"[UI]: {hlet}")
            else:
                self.p("[UI]: 历史弹幕加载完成")
        threading.Thread(target=thread_func,name="加载历史弹幕",daemon=True).start()

    def send_danmu_dialog(self)->None:
        """发送弹幕对话框"""
        dialog=tk.Toplevel(self.root)
        dialog.title("发送弹幕")
        dialog.geometry("300x100")
        dialog.resizable(False,False)

        entry=ttk.Entry(dialog,width=30)
        entry.pack(pady=10)
        entry.focus_set()

        def send():
            msg=entry.get().strip()
            if not msg:
                return
            dialog.destroy()
            if self.env is None:
                et="环境无效，无法发送弹幕"
                self.p(f"[UI]: {et}")
                self.show_error_dialog(et)
                return
            try:
                self.env.send_danmu(msg)
            except:
                et="发送弹幕失败"
                self.error(et)
                self.p(f"[UI]: {et}")
                self.show_error_dialog(et)

        def cancel():
            dialog.destroy()

        button_frame=ttk.Frame(dialog)
        button_frame.pack(pady=5)
        ttk.Button(button_frame,text="发送",command=send).pack(side=tk.LEFT,padx=5)
        ttk.Button(button_frame,text="取消",command=cancel).pack(side=tk.LEFT,padx=5)

    def show_error_dialog(self,message:str)->None:
        """显示错误对话框"""
        def to_thread():
            messagebox.showerror("错误",message)
        threading.Thread(target=to_thread,name="错误对话框",daemon=True).start()

    def calculate_text_width(self,text:str)->int:
        """计算文本宽度(像素)"""
        return self.bottom_font.measure(text) if self.bottom_font else 0

    def truncate_text_parts(self,text_parts:list[insert_text])->list[insert_text]:
        """截断多段文本"""
        if not isinstance(text_parts,list):
            raise TypeError("text_parts必须是list类型")
        max_width=max(50,self.root.winfo_width()-10)
        # 计算总文本和总宽度
        total_text=""
        total_width=0
        for text,tag in text_parts:
            text=str(text)
            total_text+=text
            total_width+=self.calculate_text_width(text)
        if total_width<=max_width:# 无需截断
            return text_parts
        ellipsis="…"
        ellipsis_width=self.calculate_text_width(ellipsis)
        available_width=max_width-ellipsis_width
        # 二分法找最大可显示长度
        start,end=0,len(total_text)
        max_len=0
        while start<=end:
            mid=(start+end)//2
            test_width=self.calculate_text_width(total_text[:mid])
            if test_width<=available_width:
                max_len=mid
                start=mid+1
            else:
                end=mid-1
        # 重新拆分截断后的文本段
        truncated_text=total_text[:max_len]+ellipsis
        result=[]
        current_pos=0
        # 处理文本
        for text,tag in text_parts:
            if current_pos>=len(truncated_text):
                break
            part_len=len(text)
            if current_pos+part_len<=len(truncated_text):
                result.append((truncated_text[current_pos:current_pos+part_len],tag))
                current_pos+=part_len
            else:
                result.append((truncated_text[current_pos:],tag))
                break
        return result

    def update_bottom_text(self,text_parts:list[insert_text],hide_delay:int=HIDE_DELAY)->None:
        """更新底部文本"""
        if not isinstance(text_parts,list):raise TypeError("text_parts必须为list类型")
        if not isinstance(hide_delay,int):raise TypeError("hide_delay必须为int类型")
        if self.hide_timer:
            self.root.after_cancel(self.hide_timer)
        output_text=self.truncate_text_parts(text_parts)
        self.bottom_text.config(state=tk.NORMAL)
        self.bottom_text.delete(1.0,tk.END)
        for text,tag in output_text:
            self.bottom_text.insert(tk.END,text,tag)
        self.bottom_text.config(state=tk.DISABLED)
        self.bottom_frame.pack(side=tk.BOTTOM,fill=tk.X,padx=0,pady=0)
        self.hide_timer=self.root.after(hide_delay,self.hide_bottom_text)

    def hide_bottom_text(self)->None:
        """隐藏并清空底部文本"""
        if not self.root:return
        self.bottom_text.config(state=tk.NORMAL)
        self.bottom_text.delete(1.0,tk.END)
        self.bottom_text.config(state=tk.DISABLED)
        self.bottom_frame.pack_forget()
        self.hide_timer=None

    def add_color_text(self,text:str,tag:str="default")->None:
        """添加带颜色的文本"""
        self.text.insert(tk.END,str(text),tag)

    def add_temp_color_text(self,text:str,**kw)->None:
        """添加带颜色的文本，颜色临时使用。"""
        tag=f"temp_color_{random.randint(100,999)}"
        self.text.tag_configure(tag,**kw)
        self.text.insert(tk.END,str(text),tag)
        self.text.tag_delete(tag)

    def add_end(self)->None:
        """添加末尾换行"""
        self.text.insert(tk.END,"\n")

    def add_time(self)->None:
        """添加时间"""
        self.add_color_text(time.strftime(r"[%H:%M:%S] "),"datetime")

    def add_msg(self,msg:dict[str]):
        """添加信息"""
        self.text.config(state=tk.NORMAL)
        if int(self.text.index("end-1c").split(".")[0])>self.MAX_MSG:
            self.text.delete(1.0,2.0)
        if isinstance(msg,dict):
            try:
                self.format_msg(msg)
            except:
                self.error(msg)
                self.p("[UI]: 信息处理失败")
                self.add_end()
        else:
            self.p("信息类型错误:",msg)
        if self.is_scrolled_to_end():
            self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def format_msg(self,msg:dict):
        """处理信息"""
        if not isinstance(msg,dict):raise TypeError("msg not dict")
        t=msg.get("t")
        if not isinstance(t,str):raise TypeError("msg.t not str")
        run=getattr(self,f"so_{t}",None)
        if callable(run):
            run(msg)
        else:
            self.p("[UI]: 未知的操作",t)
            self.add_time()
            self.add_color_text("unknown","eventmsg")
            self.add_end()

    def so_df(s,msg:dict):
        """默认"""
        s.add_time()
        s.add_color_text(msg["msg"])
        s.add_end()
    def so_bdf(s,msg:dict):
        """底部默认"""
        s.update_bottom_text([(msg["msg"],"default")])
    def so_dm(s,msg:dict):
        """弹幕"""
        s.add_time()
        if msg.get("isAnchor",False):
            s.add_color_text("(主播)","anchor")
        if msg.get("isAdmin",False):
            s.add_color_text("(房)","roomadmin")
        s.add_color_text(msg["uname"],"username")
        s.add_color_text(": ")
        s.add_color_text(msg["danmu"],"gray")
        s.add_end()
    def so_iw(s,msg:dict):
        """交互"""
        s.update_bottom_text([(msg["uname"],"username"),(msg["inter"],"default")])
    def so_ev(s,msg:dict):
        """事件"""
        s.add_time()
        s.add_color_text(msg["msg"],"eventmsg")
        s.add_end()
    def so_warning(s,msg:dict):
        """警告"""
        s.add_time()
        s.add_color_text(msg["msg"],"warning")
        s.add_end()
    def so_gift(s,msg:dict):
        """礼物"""
        s.update_bottom_text([(msg["uname"],"username"),(f" {msg['action']} {msg['giftName']} × ","default"),(f"{msg['num']}","number")])
    def so_SC(s,msg:dict):
        """醒目留言"""
        s.add_time()
        s.add_color_text(msg["uname"],"username")
        s.add_color_text(f"(￥{msg['price']}): ")
        s.add_color_text(f"{msg['msg']}","superchat")
        s.add_end()
    def so_nt(s,msg:dict):
        """通知"""
        s.add_time()
        s.add_color_text(msg["msg"],"notice")
        s.add_end()
    def so_CN_DANMU(s,msg:dict):
        """处理弹幕通知"""
        s.add_time()
        for i in msg["contents"]:
            t=i["type"]
            if t==1:
                s.add_temp_color_text(i["text"],foreground=i["font_color"])
        s.add_end()
    def so_DM_INTERACTION(s,msg:dict):
        """处理交互合并"""
        t=msg["s"]
        if t==1:# 数字描述对
            s.update_bottom_text([(str(msg["msg"][0]),"number"),(msg["msg"][1],"default")])
        elif t==2:# 弹幕定制
            s.update_bottom_text([(msg["msg"][0],"default"),(msg["msg"][1],"gray"),(f" ×{msg['msg'][2]}","number")])
        else:
            s.p(f"[UI]: 未知的交互合并类型{t}，消息内容:",msg["msg"])

    def process_queue(self)->None:
        """消息处理"""
        if not self.running.is_set():
            self.stop()
            return
        msg=[]
        while len(msg)<self.MAX_MSG:
            try:
                msg.append(self.msg_queue.get_nowait())
            except queue.Empty:
                break
        if msg:
            for i in msg:
                self.add_msg(i)
        self.root.after(100,self.process_queue)

    def send_msg(self,msg:dict[str])->None:
        """发送信息"""
        if not self.running.is_set():return
        try:
            self.msg_queue.put_nowait(msg)
        except queue.Full:
            pass

    def stop_sign(self)->None:
        """停止信号"""
        self.running.clear()

    def stop(self)->None:
        """停止"""
        self.running.clear()
        if self.root:
            if self.hide_timer:
                self.root.after_cancel(self.hide_timer)
                self.hide_timer=None
            self.root.after(100,self.stop_quit)

    def stop_quit(self)->None:
        """销毁UI"""
        if not self.root:return
        self.root.quit()
        self.root.destroy()
        self.root=None
        self.frame=None
        self.text=None
        self.bottom_font=None
        self.bottom_frame=None
        self.bottom_text=None
        self.context_menu=None

    def start(self)->None:
        """启动"""
        if self.running.is_set():
            raise RuntimeError("UI已在运行")
        self.running.set()
        self.create_ui()
        self.process_queue()

    def mainloop(self)->None:
        """主循环"""
        if self.running.is_set():
            self.root.mainloop()

def thread_run_ui(obj:BLM_UI)->None:
    """在子线程运行UI"""
    try:
        obj.start()
        obj.mainloop()
    except Exception:
        obj.error()
        obj.p("UI线程异常")
    finally:
        obj.stop()

def start_blm_ui():
    obj=BLM_UI()
    thread=threading.Thread(target=thread_run_ui,name="BLM_UI",args=(obj,),daemon=True)
    thread.start()
    return thread,obj
