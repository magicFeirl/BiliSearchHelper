## B站视频批量检索工具

**用于批量检索 SM 号并找到对应的 AV 号并输出，支持检索被屏蔽的视频。可用于N站的 mylist/series/video 同步、各种N站期刊视频等需要大量搜索 SM 号的情况。**

提供了一个简单的可执行文件，该文件在 WIN10 下打包，所以可能非 WIN10 的系统无法运行，但也不保证 WIN10 就一定能运行。

此外这里还有个我以前写的老版[B站视频检索工具](https://github.com/magicFeirl/Crawlers/tree/master/SM2AV)。

推荐使用 [jupyter notebook](https://jupyter.org/) 运行代码，可自定义更多功能。

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