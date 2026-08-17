# astrbot_plugin_vctgogo

VCT CN（无畏契约中国赛区）比赛播报插件，适用于 [AstrBot]

自动从 [vlr.gg](https://www.vlr.gg) 拉取 VCT 2026 中国赛区 Stage 2 的赛程、比分与选手数据，支持定时播报、手动查询、比赛详情（地图 / 半场比分 / 选手数据 / MVP）与实时监控。

## 功能

- 手动查询当日赛程、全部赛程、历史比赛结果
- 查询单场比赛详细数据：总比分、每图地图名、半场攻防、选手排行（Rating 2.0 / ACS / KDA / 英雄）、每图 MVP
- 定时自动监控：开赛提醒、比赛进行中实时比分播报、逐图播报结果（含每图 MVP）、整场结束后播报总结
- 错过直播的比赛自动补发完整总结
- 首次启动自动标记已有历史比赛，不会刷屏补发
- 播报状态持久化，重启不重复播报
- 全量中文翻译：地图名、英雄名、战队名、赛事阶段

## 安装

本插件通过 Git 安装，仓库根目录即插件目录。

### 方式一：AstrBot 面板安装（推荐）

1. 打开 AstrBot 管理面板 → 「插件管理」
2. 点击「安装」→ 填入 Git 仓库地址：`https://github.com/hesuing/astrbot_plugin_vctcngogo`
3. 安装完成后重启 AstrBot，插件自动加载

### 方式二：命令行手动克隆

```bash
cd /AstrBot/data/plugins
git clone https://github.com/hesuing/astrbot_plugin_vctcngogo
```

然后重启 AstrBot。

> 注意：`astrbot_plugin_vctgogo` 文件夹整体即插件目录，请勿只把里面的文件散放进去。

无第三方依赖，仅使用 Python 标准库及 AstrBot 内置组件。

## 手动指令

| 指令 | 说明 |
| --- | --- |
| `/vct` | 显示全部指令用法 |
| `/vct today`（`今日` / `今天`） | 24 小时内赛程（日期 + 时间 + 对阵） |
| `/vct all`（`全部` / `赛程`） | 所有未开打的赛程 |
| `/vct result`（`结果` / `比分`） | 已结束比赛比分 |
| `/vct match <比赛ID或链接>`（`详情` / `详细`） | 比赛详情：比分、每图地图、半场、选手数据、每图 MVP |
| `/vct bind`（`绑定` / `订阅`） | 把当前会话设为自动播报目标 |
| `/vct unbind`（`解绑` / `取消订阅`） | 取消当前会话的自动播报 |
| `/vct list`（`列表` / `目标`） | 查看已绑定的播报会话 |
| `/vct sid` | 显示当前会话 unified_msg_origin |

### 命令示例

```
/vct
/vct today
/vct all
/vct result
/vct match 701025
/vct match https://www.vlr.gg/701025/wolves-esports-vs-titan-esports-club
/vct bind
```

### 比赛 ID 说明

比赛 ID 即 vlr.gg 比赛链接 URL 中 `/` 后的第一个数字，例如链接

```
https://www.vlr.gg/701025/wolves-esports-vs-titan-esports-club-...
```

中的 `701025`。可用 `match 701025`（或直接贴整个链接）查询。

## 自动播报

配置 `target_sessions`（或发送 `/vct bind` 绑定当前会话）后，插件定时任务会自动：

> 提示：插件重启后请在播报目标群里随便发一条 `/vct` 命令，即可激活该群的自动播报能力（事件对象随命令刷新）。

1. 每 `poll_interval_min` 分钟检查一次赛程
2. 对临近开赛（60 分钟内）的比赛推送开赛提醒
3. 对进行中的比赛，比分变化时推送实时比分（总比分局数 + 每图比分）
4. 每张图打完后自动推送该图结果（地图名、双方比分、半场攻防、本图 MVP）
5. 整场比赛结束后自动推送总结（总比分 + 每图比分 + 每图 MVP）

## 配置

配置文件 `_conf_schema.json`（在 AstrBot 面板插件配置中修改）：

| 配置项 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `target_sessions` | list | `[]` | 定时播报目标会话列表（可用 `/vct bind` 动态添加）；留空则仅手动查询 |
| `poll_interval_min` | int | `30` | 定时自动播报的检查间隔（分钟） |

## 播报内容示例

比赛结束总结：

```
VCT 2026 中国赛区 Stage 2 · 比赛结束
WOL（Wolves Esports） 2 : 0 TEC（Titan Esports Club）
第一周

■ 日落之城: Wolves Esports 13 : 5 Titan Esports Club  (WOL 胜, MVP Deryeon (幽影) 1.92 / 397 / 28-11-8)
■ 霓虹町: Wolves Esports 13 : 10 Titan Esports Club  (WOL 胜, MVP yosemite (奇乐) 1.32 / 243 / 20-13-2)
```

进行中比赛实时比分：

```
VCT 2026 中国赛区 Stage 2 · 比赛进行中
TYLOO 2 : 0 TEC（Titan Esports Club）
■ 日落之城: TYLOO 13 : 5 TEC (已结束)
■ 霓虹町: TYLOO 10 : 4 TEC (已结束)
■ 亚海悬城: TYLOO 0 : 0 TEC (进行中)
```

开赛提醒：

```
VCT 2026 中国赛区 Stage 2 · 即将开赛
TYLOO vs TEC
2026年8月14日 下午7:00
约 30 分钟后开赛
[半决赛]
```

比赛详情：

```
比赛 #701025
总比分 2 : 0

■ 日落之城: WOL（Wolves Esports） 13 : 5 TEC（Titan Esports Club）
  WOL 上半场 8防/5攻 · TEC 上半场 4攻/1防
  1. Deryeon (幽影) 1.92 / 397 / 28-11-8
  2. aluba (猎枭) 1.39 / 255 / 16-9-2
  3. Spitfires (贤者) 1.12 / 247 / 14-16-5
  4. Spring (蝰蛇) 1.06 / 227 / 14-12-7
  5. Haodong (零) 0.97 / 197 / 13-14-1
  MVP: Deryeon (幽影) 1.92 / 397 / 28-11-8
```

## 项目结构

```
astrbot_plugin_vct_cn/
├── main.py              # 插件主逻辑：指令、定时播报、数据组装
├── match_parser.py      # vlr.gg 抓取与解析（赛程 / 比赛详情 / 选手数据）
├── translations.py      # 英雄与地图中文名映射
├── metadata.yaml        # 插件元数据
├── _conf_schema.json    # 插件配置项定义
└── monitor_state.json   # 运行时状态（自动生成，勿手动改动）
```
