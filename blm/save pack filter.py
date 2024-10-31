#!/bin/env python
"""过滤保存的数据包"""

import json
import argparse
from pathlib import Path
from traceback import print_exc

DEBUG=False
savepackname="bili live msg.py"
dir=Path("bili live msg data")
packlist=[]
ofileind=0

def output_dir(p,c):
    global ofileind
    if not p.is_dir():
        p.mkdir(parents=True)
    fn=p/(str(ofileind)+".json")
    if DEBUG:
        print("保存文件:",str(fn))
    with open(fn,"w")as f:
        json.dump(c,f,ensure_ascii=False,indent="\t")
    ofileind+=1

def output_file(p):
    if p.is_file():
        print("提示: 文件已存在，将覆盖")
    with p.open("w")as f:
        json.dump(packlist,f,ensure_ascii=False,indent="\t")

def main():
    global DEBUG
    p=argparse.ArgumentParser(
        description="过滤保存的数据包\n"
            f"请先运行 {savepackname} 来保存数据包（一般情况下该文件就在本目录下）",
        epilog="输出到文件和输出到路径同时存在时，优先输出到路径\n"
            "输出到路径时，任何找不到的父目录将会自动创建\n"
            "警告：若过滤结果过多的话，使用输出到文件功能可能导致内存耗尽。",
        formatter_class=argparse.RawTextHelpFormatter,
        prefix_chars="-",
        fromfile_prefix_chars="@+"
    )
    def a(*arg1,**arg2):
        p.add_argument(*arg1,**arg2)
    a("-d","--debug",help="调试开关",action="store_true")
    a("-c","--cmd",help="要过滤出来的cmd",action="append")
    a("-o","--output-file",help="输出到文件",type=Path)
    a("-O","--output-dir",help="输出到路径",type=Path)
    n=p.parse_args()
    DEBUG=n.debug
    if DEBUG:
        print("命令行参数:",n)
    if not dir.is_dir():
        print("未找到数据包目录，请确认是否运行",savepackname,"来保存数据包")
        print("当然，也可能什么都没保存")
        return 0
    if not n.cmd:
        print("未提供筛选列表，请使用参数 -c 或 --cmd 来提供")
        return 0
    fl=dir.iterdir()
    for i in fl:# file
        with i.open()as f:
            try:
                l=json.load(f)
            except Exception as e:
                print("处理数据出错:",e)
                if DEBUG:
                    print_exc()
                return 1
            for p in l:# index
                if p["cmd"]in n.cmd:
                    print("file:",i.name)
                    if n.output_dir:
                        output_dir(n.output_dir,p)
                    elif n.output_file:
                        packlist.append(p)
                    else:
                        print(p)
    if not n.output_dir and n.output_file:
        output_file(n.output_file)

if __name__=="__main__":
    main()
