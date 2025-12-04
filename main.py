from nakuru.entities.components import *
from nakuru import (
    GroupMessage,
    FriendMessage
)
from botpy.message import Message, DirectMessage
from model.platform.qq import QQ
import time
import requests
import json
import os
from cores.qqbot.global_object import AstrMessageEvent

"""
Apex Legends 查询插件
支持查询玩家统计、匹配历史、排行榜、地图轮换、商店、新闻等信息
"""

class ApexLegendsPlugin:
    """
    初始化函数
    """
    def __init__(self) -> None:
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
            print("警告：未设置 APEX_LEGENDS_API_KEY，部分功能可能无法使用")
            print("提示：可通过环境变量或 config.py 文件设置 API key")
        else:
            print("Apex Legends 插件已加载！API key 已配置")

    """
    机器人程序会调用此函数。
    返回规范: bool: 插件是否响应该消息
             Tuple: None 或者长度为 3 的元组
    """
    def run(self, ame: AstrMessageEvent):
        message = ame.message_str.strip()
        
        # 检查是否是 Apex 相关指令
        if not message.startswith("apex") and not message.startswith("Apex") and not message.startswith("APEX"):
            return False, None
        
        # 解析指令
        parts = message.split()
        if len(parts) < 2:
            return True, tuple([False, "用法：apex <指令> [参数]\n输入 'apex help' 查看帮助", "apexlegends"])
        
        command = parts[1].lower()
        
        try:
            if command == "help":
                return self._show_help()
            elif command == "player" or command == "p":
                if len(parts) < 4:
                    return True, tuple([False, "用法：apex player <玩家名> <平台(PC/PS4/X1)>", "apexlegends"])
                player_name = parts[2]
                platform = parts[3].upper()
                return self._query_player(player_name, platform)
            elif command == "uid":
                if len(parts) < 3:
                    return True, tuple([False, "用法：apex uid <玩家名> <平台(PC/PS4/X1)>", "apexlegends"])
                player_name = parts[2]
                platform = parts[3].upper() if len(parts) > 3 else "PC"
                return self._name_to_uid(player_name, platform)
            elif command == "matches" or command == "m":
                if len(parts) < 4:
                    return True, tuple([False, "用法：apex matches <玩家名> <平台(PC/PS4/X1)>", "apexlegends"])
                player_name = parts[2]
                platform = parts[3].upper()
                return self._query_matches(player_name, platform)
            elif command == "leaderboard" or command == "lb":
                return self._query_leaderboard()
            elif command == "map" or command == "maps":
                return self._query_map_rotation()
            elif command == "store":
                return self._query_store()
            elif command == "crafting":
                return self._query_crafting()
            elif command == "news":
                return self._query_news()
            elif command == "status":
                return self._query_server_status()
            elif command == "predator":
                return self._query_predator()
            else:
                return True, tuple([False, f"未知指令：{command}\n输入 'apex help' 查看帮助", "apexlegends"])
        except Exception as e:
            return True, tuple([False, f"查询出错：{str(e)}", "apexlegends"])

    """
    显示帮助信息
    """
    def _show_help(self):
        help_text = """Apex Legends 查询插件帮助

可用指令：
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
注意：使用前需要配置 API key"""
        return True, tuple([True, help_text, "apexlegends"])

    """
    查询玩家统计信息
    """
    def _query_player(self, player_name: str, platform: str):
        if not self.api_key:
            return True, tuple([False, "未配置 API key，请在插件配置中添加", "apexlegends"])
        
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
                return True, tuple([False, f"未找到玩家：{player_name} (平台: {platform})", "apexlegends"])
            elif response.status_code == 403:
                return True, tuple([False, "API key 无效或未授权", "apexlegends"])
            else:
                return True, tuple([False, f"API 请求失败：{response.status_code}", "apexlegends"])
        except requests.exceptions.RequestException as e:
            return True, tuple([False, f"网络请求失败：{str(e)}", "apexlegends"])

    """
    格式化玩家统计数据
    """
    def _format_player_stats(self, data: dict, player_name: str, platform: str):
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
            
            return True, tuple([True, result, "apexlegends"])
        except Exception as e:
            return True, tuple([False, f"数据解析失败：{str(e)}", "apexlegends"])

    """
    名称转 UID
    """
    def _name_to_uid(self, player_name: str, platform: str):
        if not self.api_key:
            return True, tuple([False, "未配置 API key，请在插件配置中添加", "apexlegends"])
        
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
                return True, tuple([True, f"玩家 {player_name} ({platform}) 的 UID：{uid}", "apexlegends"])
            elif response.status_code == 404:
                return True, tuple([False, f"未找到玩家：{player_name}", "apexlegends"])
            else:
                return True, tuple([False, f"查询失败：{response.status_code}", "apexlegends"])
        except requests.exceptions.RequestException as e:
            return True, tuple([False, f"网络请求失败：{str(e)}", "apexlegends"])

    """
    查询匹配历史
    """
    def _query_matches(self, player_name: str, platform: str):
        if not self.api_key:
            return True, tuple([False, "未配置 API key，请在插件配置中添加", "apexlegends"])
        
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
                    return True, tuple([True, f"玩家 {player_name} 暂无匹配历史", "apexlegends"])
                
                result = f"【{player_name} 最近匹配记录】\n\n"
                for i, match in enumerate(recent_matches[:5], 1):  # 只显示最近5场
                    result += f"第 {i} 场：\n"
                    result += f"  模式：{match.get('gameMode', 'N/A')}\n"
                    result += f"  击杀：{match.get('kills', 0)}\n"
                    result += f"  伤害：{match.get('damage', 0)}\n"
                    result += f"  排名：{match.get('rank', 'N/A')}\n"
                    result += "\n"
                
                return True, tuple([True, result, "apexlegends"])
            else:
                return True, tuple([False, f"查询失败：{response.status_code}", "apexlegends"])
        except requests.exceptions.RequestException as e:
            return True, tuple([False, f"网络请求失败：{str(e)}", "apexlegends"])

    """
    查询排行榜
    """
    def _query_leaderboard(self):
        if not self.api_key:
            return True, tuple([False, "未配置 API key，请在插件配置中添加", "apexlegends"])
        
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
                
                return True, tuple([True, result, "apexlegends"])
            else:
                return True, tuple([False, f"查询失败：{response.status_code}", "apexlegends"])
        except requests.exceptions.RequestException as e:
            return True, tuple([False, f"网络请求失败：{str(e)}", "apexlegends"])

    """
    查询地图轮换
    """
    def _query_map_rotation(self):
        if not self.api_key:
            return True, tuple([False, "未配置 API key，请在插件配置中添加", "apexlegends"])
        
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
                
                return True, tuple([True, result, "apexlegends"])
            else:
                return True, tuple([False, f"查询失败：{response.status_code}", "apexlegends"])
        except requests.exceptions.RequestException as e:
            return True, tuple([False, f"网络请求失败：{str(e)}", "apexlegends"])

    """
    查询商店
    """
    def _query_store(self):
        if not self.api_key:
            return True, tuple([False, "未配置 API key，请在插件配置中添加", "apexlegends"])
        
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
                
                return True, tuple([True, result, "apexlegends"])
            else:
                return True, tuple([False, f"查询失败：{response.status_code}", "apexlegends"])
        except requests.exceptions.RequestException as e:
            return True, tuple([False, f"网络请求失败：{str(e)}", "apexlegends"])

    """
    查询制造轮换
    """
    def _query_crafting(self):
        if not self.api_key:
            return True, tuple([False, "未配置 API key，请在插件配置中添加", "apexlegends"])
        
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
                
                return True, tuple([True, result, "apexlegends"])
            else:
                return True, tuple([False, f"查询失败：{response.status_code}", "apexlegends"])
        except requests.exceptions.RequestException as e:
            return True, tuple([False, f"网络请求失败：{str(e)}", "apexlegends"])

    """
    查询新闻
    """
    def _query_news(self):
        if not self.api_key:
            return True, tuple([False, "未配置 API key，请在插件配置中添加", "apexlegends"])
        
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
                
                return True, tuple([True, result, "apexlegends"])
            else:
                return True, tuple([False, f"查询失败：{response.status_code}", "apexlegends"])
        except requests.exceptions.RequestException as e:
            return True, tuple([False, f"网络请求失败：{str(e)}", "apexlegends"])

    """
    查询服务器状态
    """
    def _query_server_status(self):
        if not self.api_key:
            return True, tuple([False, "未配置 API key，请在插件配置中添加", "apexlegends"])
        
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
                
                return True, tuple([True, result, "apexlegends"])
            else:
                return True, tuple([False, f"查询失败：{response.status_code}", "apexlegends"])
        except requests.exceptions.RequestException as e:
            return True, tuple([False, f"网络请求失败：{str(e)}", "apexlegends"])

    """
    查询猎杀者排行榜
    """
    def _query_predator(self):
        if not self.api_key:
            return True, tuple([False, "未配置 API key，请在插件配置中添加", "apexlegends"])
        
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
                
                return True, tuple([True, result, "apexlegends"])
            else:
                return True, tuple([False, f"查询失败：{response.status_code}", "apexlegends"])
        except requests.exceptions.RequestException as e:
            return True, tuple([False, f"网络请求失败：{str(e)}", "apexlegends"])

    """
    插件元信息
    """
    def info(self):
        return {
            "name": "apexlegends",
            "desc": "Apex Legends 游戏信息查询插件",
            "help": """Apex Legends 查询插件

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

注意：使用前需要在插件配置中设置 API key
获取 API key：https://apexlegendsapi.com/""",
            "version": "v1.0.0",
            "author": "AstrBot Community",
            "repo": "https://github.com/Dokid0k1/apexlegends-plugin",
            "homepage": "https://apexlegendsapi.com/"
        }

