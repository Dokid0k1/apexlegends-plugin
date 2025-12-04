# Apex Legends 查询插件

AstrBot 插件，用于查询 Apex Legends 游戏相关信息。

## 功能

- 查询玩家统计信息（等级、排位、击杀数等）
- 查询玩家 UID
- 查询匹配历史
- 查询排行榜
- 查询地图轮换
- 查询商店物品
- 查询制造轮换
- 查询游戏新闻
- 查询服务器状态
- 查询猎杀者排行榜

## 安装

1. 将插件克隆到 AstrBot 的 `addons/plugins/` 目录下：
```bash
cd addons/plugins/
git clone https://github.com/Dokid0k1/apexlegends-plugin
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置 API key：
   - 访问 [Apex Legends API](https://apexlegendsapi.com/) 注册并获取 API key
   - 在插件配置中设置 API key（具体配置方式请参考 AstrBot 文档）

## 使用方法

在群聊或私聊中发送以下指令：

### 基本指令

- `apex help` - 显示帮助信息

### 玩家查询

- `apex player <玩家名> <平台>` - 查询玩家统计信息
  - 示例：`apex player PlayerName PC`
  - 平台选项：`PC`, `PS4`, `X1`

- `apex uid <玩家名> <平台>` - 查询玩家 UID
  - 示例：`apex uid PlayerName PC`

- `apex matches <玩家名> <平台>` - 查询匹配历史
  - 示例：`apex matches PlayerName PC`

### 游戏信息查询

- `apex leaderboard` - 查询排行榜
- `apex map` - 查询地图轮换
- `apex store` - 查询商店
- `apex crafting` - 查询制造轮换
- `apex news` - 查询游戏新闻
- `apex status` - 查询服务器状态
- `apex predator` - 查询猎杀者排行榜

## API 说明

本插件使用 [Apex Legends API](https://apexlegendsapi.com/) 提供的数据。

**注意**：使用本插件需要注册并获取 API key。

## 配置

插件需要在配置中设置 API key 才能正常工作。API key 可以通过以下方式配置：

1. 在 AstrBot 的配置文件中添加插件配置
2. 或者在插件初始化时通过环境变量设置

## 依赖

- requests - HTTP 请求库

## 许可证

MIT License

## 作者

AstrBot Community

## 相关链接

- [Apex Legends API 文档](https://apexlegendsapi.com/)
- [AstrBot 项目](https://github.com/AstrBotDevs/AstrBot)

