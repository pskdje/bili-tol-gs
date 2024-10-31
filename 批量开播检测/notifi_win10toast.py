# notifi
"""在win10中发送通知
未进行测试
"""

from win10toast import ToastNotifier

def start(d):
    t = ToastNotifier()
    t.show_toast(
        "哔哩哔哩开播提醒",
        f"您关注的主播 {d['uname']} 开始直播 {d['title']}"
    )
