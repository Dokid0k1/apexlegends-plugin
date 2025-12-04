from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import requests
import json
import os

@register("apexlegends", "AstrBot Community", "Apex Legends 游戏信息查询插件", "v1.0.0")
class ApexLegendsPlugin(Star):
    """
    Apex Legends 查询插件
    支持查询玩家统计、匹配历史、排行榜、地图轮换、商店、新闻等信息
    """
    
    def __init__(self, context: Context):
        super().__init__(context)
        self.api_base_url = "https://api.mozambiquehe.re"
        # 优先从环境变量读取 API key
        self.api_key = os.getenv("APEX_LEGENDS_API_KEY", None)
        
        # 如果环境变量没有，尝试从配置文件读取
        if not self.api_key:
            try:
                import config
                self.api_key = getattr(config, "APEX_LEGENDS_API_KEY", None)
            except ImportError:
                pass
        
        if not self.api_key:
            logger.warning("未设置 APEX_LEGENDS_API_KEY，部分功能可能无法使用")
            logger.info("提示：可通过环境变量或 config.py 文件设置 API key")
        else:
            logger.info("Apex Legends 插件已加载！API key 已配置")

    async def initialize(self):
        """插件初始化方法"""
        pass

    @filter.command("apex")
    async def apex_command(self, event: AstrMessageEvent):
        """Apex Legends 查询指令"""
        message = event.message_str.strip()
        
        # 解析指令
        parts = message.split()
        if len(parts) < 2:
            yield event.plain_result("用法：apex <指令> [参数]\n输入 'apex help' 查看帮助")
            return
        
        command = parts[1].lower()
        
        try:
            if command == "help":
                yield event.plain_result(self._show_help())
            elif command == "player" or command == "p":
                if len(parts) < 4:
                    yield event.plain_result("用法：apex player <玩家名> <平台(PC/PS4/X1)>")
                    return
                player_name = parts[2]
                platform = parts[3].upper()
                result = await self._query_player(player_name, platform)
                yield event.plain_result(result)
            elif command == "uid":
                if len(parts) < 3:
                    yield event.plain_result("用法：apex uid <玩家名> <平台(PC/PS4/X1)>")
                    return
                player_name = parts[2]
                platform = parts[3].upper() if len(parts) > 3 else "PC"
                result = await self._name_to_uid(player_name, platform)
                yield event.plain_result(result)
            elif command == "matches" or command == "m":
                if len(parts) < 4:
                    yield event.plain_result("用法：apex matches <玩家名> <平台(PC/PS4/X1)>")
                    return
                player_name = parts[2]
                platform = parts[3].upper()
                result = await self._query_matches(player_name, platform)
                yield event.plain_result(result)
            elif command == "leaderboard" or command == "lb":
                result = await self._query_leaderboard()
                yield event.plain_result(result)
            elif command == "map" or command == "maps":
                result = await self._query_map_rotation()
                yield event.plain_result(result)
            elif command == "store":
                result = await self._query_store()
                yield event.plain_result(result)
            elif command == "crafting":
                result = await self._query_crafting()
                yield event.plain_result(result)
            elif command == "news":
                result = await self._query_news()
                yield event.plain_result(result)
            elif command == "status":
                result = await self._query_server_status()
                yield event.plain_result(result)
            elif command == "predator":
                result = await self._query_predator()
                yield event.plain_result(result)
            else:
                yield event.plain_result(f"未知指令：{command}\n输入 'apex help' 查看帮助")
        except Exception as e:
            logger.error(f"Apex Legends 插件错误: {str(e)}")
            yield event.plain_result(f"查询出错：{str(e)}")

    def _show_help(self):
        """显示帮助信息"""
        return """Apex Legends 查询插件帮助

可用指令：
• apex help - 显示帮助信息
• apex player <玩家名> <平台> - 查询玩家统计信息
• apex uid <玩家名> <平台> - 查询玩家 UID
• apex matches <玩家名> <平台> - 查询匹配历史
• apex leaderboard - 查询排行榜
• apex map - 查询地图轮换
• apex store - 查询商店
• apex crafting - 查询制造轮换
• apex news - 查询新闻
• apex status - 查询服务器状态
• apex predator - 查询猎杀者排行榜

平台选项：PC, PS4, X1
注意：使用前需要配置 API key
获取 API key：https://apexlegendsapi.com/"""

    async def _query_player(self, player_name: str, platform: str):
        """查询玩家统计信息"""
        if not self.api_key:
            return "未配置 API key，请在插件配置中添加"
        
        url = f"{self.api_base_url}/bridge"
        params = {
            "auth": self.api_key,
            "player": player_name,
            "platform": platform
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return self._format_player_stats(data, player_name, platform)
            elif response.status_code == 404:
                return f"未找到玩家：{player_name} (平台: {platform})"
            elif response.status_code == 403:
                return "API key 无效或未授权"
            else:
                return f"API 请求失败：{response.status_code}"
        except requests.exceptions.RequestException as e:
            return f"网络请求失败：{str(e)}"

    def _format_player_stats(self, data: dict, player_name: str, platform: str):
        """格式化玩家统计数据"""
        try:
            global_stats = data.get("global", {})
            realtime = data.get("realtime", {})
            
            result = f"【Apex Legends 玩家统计】\n"
            result += f"玩家：{player_name} ({platform})\n"
            result += f"UID：{data.get('global', {}).get('uid', 'N/A')}\n\n"
            
            # 实时状态
            if realtime:
                result += "【实时状态】\n"
                result += f"在线：{'是' if realtime.get('isOnline', 0) == 1 else '否'}\n"
                result += f"游戏中：{'是' if realtime.get('isInGame', 0) == 1 else '否'}\n"
                if realtime.get('currentStateAsText'):
                    result += f"状态：{realtime.get('currentStateAsText')}\n"
                result += "\n"
            
            # 等级
            if global_stats.get("level"):
                result += f"等级：{global_stats.get('level')}\n"
            
            # 排名
            if global_stats.get("rank"):
                rank = global_stats.get("rank")
                result += f"排位等级：{rank.get('rankName', 'N/A')} {rank.get('rankDiv', '')}\n"
                result += f"排位分数：{rank.get('rankScore', 0)}\n"
            
            # 总击杀数
            if global_stats.get("total"):
                total = global_stats.get("total")
                result += f"\n【总数据】\n"
                result += f"总击杀：{total.get('kills', {}).get('value', 0)}\n"
                result += f"总伤害：{total.get('damage', {}).get('value', 0)}\n"
                result += f"总游戏数：{total.get('games_played', {}).get('value', 0)}\n"
            
            # 本赛季数据
            if global_stats.get("season"):
                season = global_stats.get("season")
                result += f"\n【本赛季数据】\n"
                result += f"击杀：{season.get('kills', {}).get('value', 0)}\n"
                result += f"伤害：{season.get('damage', {}).get('value', 0)}\n"
                result += f"游戏数：{season.get('games_played', {}).get('value', 0)}\n"
            
            return result
        except Exception as e:
            return f"数据解析失败：{str(e)}"

    async def _name_to_uid(self, player_name: str, platform: str):
        """名称转 UID"""
        if not self.api_key:
            return "未配置 API key，请在插件配置中添加"
        
        url = f"{self.api_base_url}/nametouid"
        params = {
            "auth": self.api_key,
            "player": player_name,
            "platform": platform
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                uid = data.get("uid", "N/A")
                return f"玩家 {player_name} ({platform}) 的 UID：{uid}"
            elif response.status_code == 404:
                return f"未找到玩家：{player_name}"
            else:
                return f"查询失败：{response.status_code}"
        except requests.exceptions.RequestException as e:
            return f"网络请求失败：{str(e)}"

    async def _query_matches(self, player_name: str, platform: str):
        """查询匹配历史"""
        if not self.api_key:
            return "未配置 API key，请在插件配置中添加"
        
        url = f"{self.api_base_url}/bridge"
        params = {
            "auth": self.api_key,
            "player": player_name,
            "platform": platform
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                recent_matches = data.get("recentMatches", [])
                
                if not recent_matches:
                    return f"玩家 {player_name} 暂无匹配历史"
                
                result = f"【{player_name} 最近匹配记录】\n\n"
                for i, match in enumerate(recent_matches[:5], 1):  # 只显示最近5场
                    result += f"第 {i} 场：\n"
                    result += f"  模式：{match.get('gameMode', 'N/A')}\n"
                    result += f"  击杀：{match.get('kills', 0)}\n"
                    result += f"  伤害：{match.get('damage', 0)}\n"
                    result += f"  排名：{match.get('rank', 'N/A')}\n"
                    result += "\n"
                
                return result
            else:
                return f"查询失败：{response.status_code}"
        except requests.exceptions.RequestException as e:
            return f"网络请求失败：{str(e)}"

    async def _query_leaderboard(self):
        """查询排行榜"""
        if not self.api_key:
            return "未配置 API key，请在插件配置中添加"
        
        url = f"{self.api_base_url}/leaderboard"
        params = {"auth": self.api_key}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                result = "【Apex Legends 排行榜】\n\n"
                
                # 显示各个平台的排行榜
                for platform in ["PC", "PS4", "X1"]:
                    if platform in data:
                        platform_data = data[platform]
                        result += f"【{platform} 平台】\n"
                        for i, entry in enumerate(platform_data[:5], 1):  # 只显示前5名
                            result += f"{i}. {entry.get('name', 'N/A')} - {entry.get('rank', {}).get('rankScore', 0)} 分\n"
                        result += "\n"
                
                return result
            else:
                return f"查询失败：{response.status_code}"
        except requests.exceptions.RequestException as e:
            return f"网络请求失败：{str(e)}"

    async def _query_map_rotation(self):
        """查询地图轮换"""
        if not self.api_key:
            return "未配置 API key，请在插件配置中添加"
        
        url = f"{self.api_base_url}/maprotation"
        params = {"auth": self.api_key}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                result = "【Apex Legends 地图轮换】\n\n"
                
                # 大逃杀地图
                if "battle_royale" in data:
                    br = data["battle_royale"]
                    result += "【大逃杀模式】\n"
                    result += f"当前地图：{br.get('current', {}).get('map', 'N/A')}\n"
                    result += f"剩余时间：{br.get('current', {}).get('remainingTimer', 'N/A')}\n"
                    result += f"下一张地图：{br.get('next', {}).get('map', 'N/A')}\n\n"
                
                # 竞技场地图
                if "arenas" in data:
                    arenas = data["arenas"]
                    result += "【竞技场模式】\n"
                    result += f"当前地图：{arenas.get('current', {}).get('map', 'N/A')}\n"
                    result += f"剩余时间：{arenas.get('current', {}).get('remainingTimer', 'N/A')}\n"
                    result += f"下一张地图：{arenas.get('next', {}).get('map', 'N/A')}\n"
                
                return result
            else:
                return f"查询失败：{response.status_code}"
        except requests.exceptions.RequestException as e:
            return f"网络请求失败：{str(e)}"

    async def _query_store(self):
        """查询商店"""
        if not self.api_key:
            return "未配置 API key，请在插件配置中添加"
        
        url = f"{self.api_base_url}/store"
        params = {"auth": self.api_key}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                result = "【Apex Legends 商店】\n\n"
                
                # 显示商店物品
                for i, item in enumerate(data.get("bundleContent", [])[:10], 1):
                    result += f"{i}. {item.get('item', {}).get('name', 'N/A')}\n"
                    result += f"   价格：{item.get('cost', {}).get('amount', 0)} {item.get('cost', {}).get('currency', '')}\n\n"
                
                return result
            else:
                return f"查询失败：{response.status_code}"
        except requests.exceptions.RequestException as e:
            return f"网络请求失败：{str(e)}"

    async def _query_crafting(self):
        """查询制造轮换"""
        if not self.api_key:
            return "未配置 API key，请在插件配置中添加"
        
        url = f"{self.api_base_url}/crafting"
        params = {"auth": self.api_key}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                result = "【Apex Legends 制造轮换】\n\n"
                
                # 显示制造物品
                for i, item in enumerate(data[:10], 1):
                    result += f"{i}. {item.get('itemType', {}).get('name', 'N/A')}\n"
                    result += f"   成本：{item.get('cost', 0)} 材料\n"
                    result += f"   结束时间：{item.get('endDate', {}).get('date', 'N/A')}\n\n"
                
                return result
            else:
                return f"查询失败：{response.status_code}"
        except requests.exceptions.RequestException as e:
            return f"网络请求失败：{str(e)}"

    async def _query_news(self):
        """查询新闻"""
        if not self.api_key:
            return "未配置 API key，请在插件配置中添加"
        
        url = f"{self.api_base_url}/news"
        params = {"auth": self.api_key}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                result = "【Apex Legends 新闻】\n\n"
                
                # 显示新闻
                for i, news in enumerate(data[:5], 1):
                    result += f"{i}. {news.get('title', 'N/A')}\n"
                    result += f"   {news.get('short_desc', '')}\n"
                    result += f"   链接：{news.get('link', 'N/A')}\n\n"
                
                return result
            else:
                return f"查询失败：{response.status_code}"
        except requests.exceptions.RequestException as e:
            return f"网络请求失败：{str(e)}"

    async def _query_server_status(self):
        """查询服务器状态"""
        if not self.api_key:
            return "未配置 API key，请在插件配置中添加"
        
        url = f"{self.api_base_url}/servers"
        params = {"auth": self.api_key}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                result = "【Apex Legends 服务器状态】\n\n"
                
                # 显示服务器状态
                for server in data:
                    result += f"【{server.get('Server', 'N/A')}】\n"
                    result += f"状态：{server.get('Status', 'N/A')}\n"
                    result += f"响应时间：{server.get('ResponseTime', 'N/A')}\n\n"
                
                return result
            else:
                return f"查询失败：{response.status_code}"
        except requests.exceptions.RequestException as e:
            return f"网络请求失败：{str(e)}"

    async def _query_predator(self):
        """查询猎杀者排行榜"""
        if not self.api_key:
            return "未配置 API key，请在插件配置中添加"
        
        url = f"{self.api_base_url}/predator"
        params = {"auth": self.api_key}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                result = "【Apex Legends 猎杀者排行榜】\n\n"
                
                # 显示各平台猎杀者
                for platform in ["PC", "PS4", "X1"]:
                    if platform in data:
                        platform_data = data[platform]
                        result += f"【{platform} 平台】\n"
                        for i, entry in enumerate(platform_data[:5], 1):
                            result += f"{i}. {entry.get('name', 'N/A')} - {entry.get('rank', {}).get('rankScore', 0)} 分\n"
                        result += "\n"
                
                return result
            else:
                return f"查询失败：{response.status_code}"
        except requests.exceptions.RequestException as e:
            return f"网络请求失败：{str(e)}"

    async def terminate(self):
        """插件销毁方法"""
        pass
