# nonebot-plugin-shindan

使用 [ShindanMaker](https://shindanmaker.com) 网站的~~无聊~~趣味占卜

利用 playwright 将占卜结果转换为图片发出，因此可以显示图片、图表结果

### 使用方式

默认占卜列表及对应的网站id如下：

- 二次元少女 (162207)
- 人设生成 (917962)
- 中二称号 (790697)
- 异世界转生 (587874)
- 特殊能力 (1098085)
- 魔法人生 (940824)
- 抽老婆 (1075116)
- 抽舰娘 (400813)

发送 “占卜指令 名字” 即可，如：`人设生成 小Q`

发送 “占卜列表” 可以查看上述列表；

超级用户可以发送 “添加占卜 id 指令”、“删除占卜 id” 增删占卜列表

### 安装

- 使用 nb-cli

```
nb plugin install nonebot_plugin_shindan
```

- 使用 pip

```
pip install nonebot_plugin_shindan
```
