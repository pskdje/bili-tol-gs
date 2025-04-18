"""bili_live_ws.py测试"""

import unittest
import json
from pathlib import Path

class PackTest(unittest.TestCase):
    """数据包处理测试"""
    def setUp(self):
        import bili_live_ws as blw
        self.blw=blw
        self.encoding=blw.ENCODING
        self.arg=blw.pararg(args=["1"])
        blwp=Path("bili_live_ws_pack")
        self.packlist=blwp.glob("*.json")
    def test_pack(self):
        o=self.blw.RelOpt(self.arg)
        for pp in self.packlist:
            p=json.loads(pp.read_text(encoding=self.encoding))
            with self.subTest(name=pp.name):
                try:
                    self.blw.pac(p,o)
                except self.blw.SavePack:
                    pass

if __name__=="__main__":
    unittest.main()
