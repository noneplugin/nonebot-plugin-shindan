# nonebot-plugin-shindan

使用 [ShindanMaker](https://shindanmaker.com) 网站的~~无聊~~趣味占卜

利用 playwright 将占卜结果转换为图片发出，因此可以显示图片、图表结果

### 安装

- 使用 nb-cli

```
nb plugin install nonebot_plugin_shindan
```

- 使用 pip

```
pip install nonebot_plugin_shindan
```

插件依赖 [nonebot-plugin-htmlrender](https://github.com/kexue-z/nonebot-plugin-htmlrender) 插件来渲染图片，使用前需要检查 playwright 相关的依赖是否正常安装；同时为确保字体正常渲染，需要系统中存在中文字体


### 使用方式

默认占卜列表及对应的网站id如下：

- 今天是什么少女 (162207)
- 人设生成 (917962)
- 中二称号 (790697)
- 异世界转生 (587874)
- 魔法人生 (940824)
- 抽老婆 (1075116)
- 抽舰娘 (400813)
- 抽高达 (361845)
- 英灵召唤 (595068)
- 卖萌 (360578)

发送 “占卜指令 名字” 即可，如：`人设生成 小Q`

发送 “/占卜列表” 可以查看上述列表；

**超级用户** 可以发送 “/添加占卜 id 指令”、“/删除占卜 id” 增删占卜列表，可以发送 “/设置占卜 id image/text”设置输出形式

超级用户设置方式：[Nonebot 超级用户配置](https://v2.nonebot.dev/docs/appendices/config#superusers)

对于需要登录推特的占卜，可以在 `.env.xxx` 文件中添加 ShindanMaker cookie：

```
shindanmaker_cookie=xxx
```

`cookie` 获取方式：

`F12` 打开开发工具，查看 `shindanmaker.com` 请求的响应头，找形如 `_session=xxx;` 的片段，如：

```
shindanmaker_cookie="_session=xxx;"
```

<div align="left">
  <img src="https://s2.loli.net/2022/06/18/1CqlcTrdVt5vJp6.png" width="500" />
</div>
