## B站视频批量检索工具

**用于批量检索 SM 号并找到对应的视频 AV 号等信息并输出，支持检索被屏蔽的视频。可用于N站的 mylist/series/video 同步、各种N站期刊视频等需要大量搜索 SM 号的情况。**

提供了一个简单的可执行文件，该文件在 WIN10 下打包，所以可能非 WIN10 的系统无法运行，但也不保证 WIN10 就一定能运行。

> Github 下载慢的话可以去 [蓝奏云](https://wwe.lanzous.com/b01c31m4j) 密码:2zbx

此外这里还有个我以前写的老版[B站视频检索工具](https://github.com/magicFeirl/Crawlers/tree/master/SM2AV)。

推荐使用 [jupyter notebook](https://jupyter.org/) 运行代码，可自定义更多功能。

**使用例**

```html
*** 开始站内检索，预计耗时 8s
Searching sm30346510 ...
休眠 0.5s
Searching sm30228423 ...
sm30228423 无数据，可能是因为被屏蔽或被删除
Searching sm30392810 ...
休眠 0.5s
Searching sm30310014 ...
休眠 0.5s
找到 6 个数据

*** 开始站外检索(Dogedoge)，预计耗时 2s
Searching sm30228423 ...
休眠 1s.
找到 6 个数据

*** 开始站外检索(Baidu)，预计耗时 2s
Searching sm30228423 ...
休眠 1s.
找到 6 个数据


================= 检索结果 =================
sm30310014 av7725905 (COOKIE LINING☆) 疯到skr机(uid:2329127)
sm30346510 av7797230 (Dummy☆.unernorth) 疯到skr机(uid:2329127)
sm30392810 av7911051 (MystiCookie (alt+41454) Girl) 琪露诺瓦露(uid:360389)

未找到的数据:
['sm30228423']

可能没找到的数据:
[]

相关数据:
********************
sm30346510 av243640152 (【合作单品】Dummy!★.undernorth) 游客12345679(uid:2417251)
简介:
sm37111551
原标题：【合作単品】Dummy!★.undernorth
原作者：E-tum
原简介：クッソー☆合作3 ～COOL KUSSO!!!～(sm37096692/av286219009)のDummy!パート単品です

＊メドレー：batman【user/78370940】
＊音声：にす【user/88819378】
＊映像：E-tum【mylist/60842568】

＊リスペクト元：sm30346510/av7797230
********************

********************
sm30392810 av795548473 (MystiCookie ☆☆ Girl) 游客12345679(uid:2417251)
简介:
sm36788699
原作者：ってね
原简介：原曲→sm30392810/av7911051
原曲の原曲→https://soundcloud.com/ujico/mystic-girlsweety-sweety（av3736568）
どうしても作りたくなってしまったので許してください。
********************

********************
sm30392810 av10033377 (Mystic Jack) 暴龙天-毛颜酱(uid:4622162)
简介:
sm31078606
原作者：KinkyOats
致敬作品：sm30392810/av7911051
哦哦哦天啦噜这个图形有八条边！是八边形！
********************


耗时 6.35s
```

**今天发现 doge 搜索不能用了，R.I.P**

### 批量获取N站视频的URL.js

```JavaScript
// series
document.querySelectorAll('div.VideoMediaObject-title > a').forEach((x)=>{console.log(x.href)});

// video & mylist 
document.querySelectorAll('a.VideoMediaObject-linkArea').forEach((x)=>{console.log(x.href)});
```

打开浏览器的控制台然后根据页面输入对应的 js 代码，控制台会批量输出 SM 号链接，把输出的链接保存到本地文本文件共检索工具使用。

### 思路

如果你觉得我的脚本不够好的话可以自己造个轮子，思路很简单:

* 调B站的接口实现站内检索

* 请求各种搜索引擎实现站外检索，大致步骤如下

  1. 请求搜索 URL

  2. 解析返回的网页，提取出要用的链接
  3. 请求提取出来的链接，获取到视频信息
  4. 格式化获取到的视频信息然后输出