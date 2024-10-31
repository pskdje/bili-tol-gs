# notifi
"""用pywin32库弹出窗口来提示
注意: 这会影响使用
未进行测试
"""

import win32api, win32con

def start(d):
    win32api.MessageBox(
        0,
        f"您关注的主播 {d['uname']} 开始直播 {d['title']}",
        "哔哩哔哩开播提醒",
        win32con.MB_OK
    )
