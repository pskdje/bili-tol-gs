# bili_live_open

文件: `bili_live_open.py`

直播开放平台互动框架。

文档: <show-url>https://open-live.bilibili.com/document/</show-url>

## 依赖

Python:

- \>3.11
- 未测试是否可在低版本中使用

第三方库:

- `requests`
- `websockets`

本目录:

- blw.py
- blm.py

## 使用

文件允许直接在命令行中启动，但没有实现cmd处理。

<pre><code class="language-shell">python bili_live_open.py --BLO-config app.json XXXXXXXX</code></pre>

使用 `-h` 或 `--help` 获取命令行参数提示。

<docs-warn>本框架并未在直播开放平台进行上架。若需使用本框架，需要自行前往<a target="_blank" href="https://open-live.bilibili.com/" referrerpolicy="no-referrer">直播开放平台</a>申请开发密钥，并且<strong>只能在自己的直播间里使用</strong>。</docs-warn>

前往[play-live.bilibili.com](https://play-live.bilibili.com/)或[开播设置](https://link.bilibili.com/#/my-room/start-live)获取主播身份码。

使用时必须传入专用配置文件，除非使用某些手段提供了必要属性。

## 专用配置文件格式

文件类型: JSON (application/json)

<pre><code class="language-json">{
	"accessKeyId":"xxXXXxxXxaaa",// 直播开放平台开发者 access key id
	"accessKeySecret":"xXXXXxxXxxxXXXXXXxbbb",// 直播开放平台开发者 access key secret
	"appID":0 // 直播开放平台项目id
}</code></pre>

## 接口

为节省文档维护工作量，接口的类型标注可能会省略，参见源代码获取类型标注。

### 类 `LiveOpenAPI`

直播开放平台接口包装。

**继承:** `blm.BiliLiveExp`

#### 常量 `LiveOpenAPI.BLOHS`

直播开放平台origin，用于拼接请求URL。

#### 变量 `LiveOpenAPI.accessKeyId`

直播开放平台开发者 access key id 。

#### 变量 `LiveOpenAPI.accessKeySecret`

直播开放平台开发者 access key secret 。

#### 变量 `LiveOpenAPI.appID`

直播开放平台项目id。

#### 变量 `LiveOpenAPI.gameID`

直播开放平台游戏id，由[liveOpenStart](#方法-liveopenapiliveopenstart)设置。

#### 常量 `LiveOpenAPI.UA`

专用自定义用户代理字符串。

继承后可按需修改。

#### 方法 `LiveOpenAPI.error`

记录异常，附带该类的部分变量。

#### 方法 `LiveOpenAPI.create_headers`

创建开放平台需要的请求头。

*参数* `body` : 要发送的数据

**返回值:** 请求头字典

#### 方法 `LiveOpenAPI.post_openAPI_data`

发送数据。

*参数* `tip` : 操作提示

*参数* `url` : 请求的URL

*参数* `body` : 要发送的字典，将被处理为json数据

**返回值:** [self.get_rest_data](blw.md#方法-bililivewsget_rest_data)的返回值

可能出现json和self.get_rest_data的异常。

#### 方法 `LiveOpenAPI.liveOpenStart`

请求开始游戏。

设置 `gameID` 、 `roomid` 、 `up_uid` 属性。

*参数* `code` : 主播身份码

<details>
<summary>查看响应标注</summary>

<pre><code class="language-json">{
	"code":0,// 返回值
	"message":"0",// 错误信息
	"request_id":"10",// 请求id
	"data":{// 信息本体
		"anchor_info":{// 主播信息
			"open_id":"16",// 用户唯一标识
			"room_id":1,// 直播间id
			"uface":"https://i0.hdslb.com/bfs/face/member/noface.jpg",// 主播头像
			"uid":1,// 主播UID
			"uname":"",// 主播名称
			"union_id":""// 开发者维度下用户唯一标识
		},
		"game_info":{// 游戏信息
			"game_id":"b6809af1-6484-41a5-b7a6-45e5bf0c4275"// 游戏场次id
		},
		"websocket_info":{// 信息流
			"auth_body":"{\"roomid\":1,\"protover\":2,\"uid\":0,\"key\":\"认证key\",\"group\":\"open\"}",// 认证信息，直接作为认证包内容发送
			"wss_link":[// 完整信息流链接
				"wss://zj-cn-live-comet.chat.bilibili.com:443/sub",
				"wss://bd-bj-live-comet-05.chat.bilibili.com:443/sub",
				"wss://bd-bj-live-comet-12.chat.bilibili.com:443/sub",
				"wss://broadcastlv.chat.bilibili.com:443/sub"
			]
		}
	}
}</code></pre>

</details>

#### 方法 `LiveOpenAPI.liveOpenEnd`

请求结束游戏。

若参数 `game_id` 不存在，将读取 `gameID` 属性。

*参数* `game_id` : 游戏场次id

#### 方法 `LiveOpenAPI.liveOpenHeartbeat`

进行心跳上报。

若参数 `game_id` 不存在，将读取 `gameID` 属性。

*参数* `game_id` : 游戏场次id

#### 方法 `LiveOpenAPI.liveOpenBatchHeartbeat`

进行批量心跳上报。

*参数* `game_ids` : 多个游戏场次id

### 类 `LiveOpenClient`

直播开放平台信息流客户端。

**继承:** `blm.BiliLiveExp`

#### 方法 `LiveOpenClient.join_room_pack`

直播开放平台专用加入直播间数据包。

若参数 `token` 的开始和结束字符不分别为 `{` `}` ，将回退为默认行为。

*参数* `token` : 开放平台的认证信息或信息流的token

*参数* `uid` : 用户UID，通过开放平台时不需要

#### 方法 `LiveOpenClient.run_open_client`

启动开放平台专用客户端。

*参数* `url` : 信息流链接

*参数* `auth` : 开放平台的认证信息

### 类 `LiveOpen`

直播开放平台框架。

**继承:** `LiveOpenAPI,LiveOpenClient`

#### 变量 `LiveOpen.bloghp`

循环发送开放平台心跳任务容纳。

#### 方法 `LiveOpen.error`

记录异常，附带该类的部分变量。

#### 方法 `LiveOpen.load_liveopen_config`

加载配置数据。

*参数* `arg` : 命令行参数输入，允许“json内容”、“文件路径”、“URL”

**返回值:** 解析后的字典

#### 方法 `LiveOpen.build_argparser`

构造直播开放平台专用命令行参数解析。

*参数* `desc` : 放在前面的描述

*参数* `epil` : 放在后面的说明

#### 异步方法 `LiveOpen.loop_liveopen_hp`

循环发送开放平台心跳。

若参数 `game_id` 不存在，将读取 `gameID` 属性。

*参数* `game_id` : 游戏场次id

#### 异步方法 `LiveOpen.loop_liveopen_hps`

循环批量发送开放平台心跳。(未测试)

自动分割游戏场次id。（若游戏场次id过多可能影响性能）

*参数* `game_ids` : 多个游戏场次id

#### 方法 `LiveOpen.on_conn_ws_server`

在conn_ws_server事件发生时启动循环发送开放平台心跳。

#### 方法 `LiveOpen.start`

启动。

### 顶层启动逻辑

调用 `LiveOpen.start` 。

## 某时间的源代码

滞后于当前源代码。

<img src="https://i0.hdslb.com/bfs/new_dyn/ff5e4d7dd9f7e664424fe75ee7714c7c438160221.png" alt="source image" referrerpolicy="no-referrer" />

该图片上传在<a href="https://www.bilibili.com/video/BV1ECYPzLEyb/" title="哔哩哔哩视频链接" referrerpolicy="no-referrer">BV1ECYPzLEyb</a>的<a href="https://www.bilibili.com/video/BV1ECYPzLEyb/#reply275597849920" title="哔哩哔哩视频评论链接" referrerpolicy="no-referrer">评论区</a>中。

<hr id="markdown-html-space" />

<script>// 为默认jekyll不处理HTML标签内的内容准备的。 <!-- 
	(()=>{
		let hr=document.getElementById("markdown-html-space");
		if(hr) hr.remove();
		let cs=document.createElement("link"),js=document.createElement("script"),dark=false;
		if(config.storage.colorScheme==="dark") dark=true;
		else if(config.storage.colorScheme==="auto"&&docsScript.pageData.isDark) dark=true;
		cs.rel="stylesheet";
		cs.href=`https://unpkg.com/@highlightjs/cdn-assets/styles/github${dark?"-dark":""}.min.css`;
		js.src="https://unpkg.com/@highlightjs/cdn-assets/highlight.min.js";
		js.onload=()=>{js.onload=null;hljs.highlightAll()};
		document.head.append(cs,js);
	})();
// --></script>
