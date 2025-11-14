
import os
import requests
from datetime import datetime
from demo.utils.respose_utils import success_response, error_response

class DingTalkController:
    @staticmethod
    def build_message_data(report_data, report_type, update_info=None, mode="daily"):
        """
        构建钉钉机器人消息数据

        Args:
            report_data (dict): 报告数据
            report_type (str): 报告类型
            update_info (dict, optional): 更新信息
            mode (str): 模式

        Returns:
            dict: 钉钉消息数据结构
        """
        content = DingTalkController._render_dingtalk_content(report_data, update_info, mode)

        return {
            "msgtype": "markdown",
            "markdown": {
                "title": f"TrendRadar 热点分析报告 - {report_type}",
                "text": content
            }
        }

    @staticmethod
    def _render_dingtalk_content(report_data, update_info, mode):
        """
        渲染钉钉内容

        Args:
            report_data (dict): 报告数据
            update_info (dict, optional): 更新信息
            mode (str): 模式

        Returns:
            str: 格式化后的内容
        """
        text_content = ""
        total_titles = 0
#        判断这个report_data是否包含stats字段，并且stats字段是否为空 就是判断键名存在不
# 在Python中，非空列表、非空字典、非零数字、非空字符串等在布尔上下文中被视为True
# 空列表[]、空字典{}、零0、空字符串''、None等被视为False
# enumerate 这玩意可以看做是foreach的一个那种逻辑的一环 只是没有对for这个改动
        if 'stats' in report_data and report_data['stats']:
            for stat in report_data['stats']:
                if stat['count'] > 0:
                    total_titles += len(stat['titles'])

        text_content += f"**总新闻数：** {total_titles}\n\n"
        text_content += f"**时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        text_content += "**类型：** 热点分析报告\n\n"
        text_content += "---\n\n"

        if 'stats' in report_data and report_data['stats']:
            text_content += "📊 **热点词汇统计**\n\n"
            total_count = len(report_data['stats'])

            for i, stat in enumerate(report_data['stats']):
                word = stat['word']
                count = stat['count']
                sequence_display = f"[{i + 1}/{total_count}]"

                if count >= 10:
                    text_content += f"🔥 {sequence_display} **{word}** : **{count}** 条\n\n"
                elif count >= 5:
                    text_content += f"📈 {sequence_display} **{word}** : **{count}** 条\n\n"
                else:
                    text_content += f"📌 {sequence_display} **{word}** : {count} 条\n\n"

                for j, title_data in enumerate(stat['titles']):
                    formatted_title = DingTalkController._format_title_for_platform("dingtalk", title_data, True)
                    text_content += f"  {j + 1}. {formatted_title}\n"

                    if j < len(stat['titles']) - 1:
                        text_content += "\n"

                if i < len(report_data['stats']) - 1:
                    text_content += "\n---\n\n"

        if not report_data.get('stats'):
            if mode == "incremental":
                mode_text = "增量模式下暂无新增匹配的热点词汇"
            elif mode == "current":
                mode_text = "当前榜单模式下暂无匹配的热点词汇"
            else:
                mode_text = "暂无匹配的热点词汇"
            text_content += f"📭 {mode_text}\n\n"

        if 'new_titles' in report_data and report_data['new_titles']:
            if text_content and "暂无匹配" not in text_content:
                text_content += "\n---\n\n"

            total_new_count = 0
            for source_data in report_data['new_titles']:
                total_new_count += len(source_data['titles'])

            text_content += f"🆕 **本次新增热点新闻** (共 {total_new_count} 条)\n\n"

            for source_data in report_data['new_titles']:
                text_content += f"**{source_data['source_name']}** ({len(source_data['titles'])} 条):\n\n"

                for j, title_data in enumerate(source_data['titles']):
                    title_data_copy = title_data.copy()
                    title_data_copy['is_new'] = False
                    formatted_title = DingTalkController._format_title_for_platform("dingtalk", title_data_copy, False)
                    text_content += f"  {j + 1}. {formatted_title}\n"

                text_content += "\n"

        if 'failed_ids' in report_data and report_data['failed_ids']:
            if text_content and "暂无匹配" not in text_content:
                text_content += "\n---\n\n"

            text_content += "⚠️ **数据获取失败的平台：**\n\n"
            for id_value in report_data['failed_ids']:
                text_content += f"  • **{id_value}**\n"

        text_content += f"\n\n> 更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        if update_info:
            text_content += f"\n> TrendRadar 发现新版本 **{update_info['remote_version']}**，当前 {update_info['current_version']}"

        return text_content

    @staticmethod
    # 实例调用 或者直接名.方法名调用
    def _format_title_for_platform(platform, title_data, show_source):
        """
        格式化标题用于不同平台

        Args:
            platform (str): 平台名称
            title_data (dict): 标题数据
            show_source (bool): 是否显示来源

        Returns:
            str: 格式化后的标题
        """
        rank_display = DingTalkController._format_rank_display(
            title_data['ranks'],
            title_data['rank_threshold'],
            platform
        )

        link_url = title_data.get('mobile_url') if title_data.get('mobile_url') else title_data.get('url')
        cleaned_title = DingTalkController._clean_title(title_data['title'])

        if link_url:
            formatted_title = f"[{cleaned_title}]({link_url})"
        else:
            formatted_title = cleaned_title

        title_prefix = "🆕 " if title_data.get('is_new') else ""

        if show_source:
            result = f"[{title_data['source_name']}] {title_prefix}{formatted_title}"
        else:
            result = f"{title_prefix}{formatted_title}"

        if rank_display:
            result += f" {rank_display}"

        if title_data.get('time_display'):
            result += f" - {title_data['time_display']}"

        if title_data.get('count', 0) > 1:
            result += f" ({title_data['count']}次)"

        return result

    @staticmethod
    def _format_rank_display(ranks, rank_threshold, platform):
        """
        格式化排名显示

        Args:
            ranks (list): 排名数组
            rank_threshold (int): 阈值
            platform (str): 平台

        Returns:
            str: 格式化后的排名
        """
        if not ranks:
            return ""

        unique_ranks = list(set(ranks))  # 去重并转换为列表
        unique_ranks.sort()
        min_rank = unique_ranks[0]
        max_rank = unique_ranks[-1]

        if platform == "dingtalk":
            highlight_start = "**"
            highlight_end = "**"
        else:
            highlight_start = "**"
            highlight_end = "**"
# 根据阈值决定是否高亮 文本加高亮
        if min_rank <= rank_threshold:
            if min_rank == max_rank:
                return f"{highlight_start}[{min_rank}]{highlight_end}"
            else:
                return f"{highlight_start}[{min_rank} - {max_rank}]{highlight_end}"
        else:
            if min_rank == max_rank:
                return f"[{min_rank}]"
            else:
                return f"[{min_rank} - {max_rank}]"

    @staticmethod
    def _clean_title(title):
        """
        清理标题

        Args:
            title (str): 标题

        Returns:
            str: 清理后的标题
        """
        if not isinstance(title, str):
            title = str(title)

        cleaned_title = title.replace("\n", " ").replace("\r", " ")#替换文本为空
        cleaned_title = ' '.join(cleaned_title.split())# 规范化所有空白字符 多个空格转1个空格
        return cleaned_title.strip()#左右2变的空格截断

    @staticmethod
    def send_dingtalk_message(report_data, report_type, update_info=None, mode="daily"):
        """
        发送钉钉消息

        Args:
            report_data (dict): 报告数据
            report_type (str): 报告类型
            update_info (dict, optional): 更新信息
            mode (str): 模式

        Returns:
            dict: 操作结果
        """
        try:
            # 构建消息数据
            message_data = DingTalkController.build_message_data(report_data, report_type, update_info, mode)

            # 获取钉钉机器人URL
            dingtalk_url = os.getenv('DING_TALK')
            if not dingtalk_url:
                return error_response(message="钉钉机器人URL未配置")

            # 发送请求
            response = requests.post(
                dingtalk_url,
                json=message_data,
                headers={'Content-Type': 'application/json'}
            )

            # 解析响应
            response_data = response.json()

            if response_data.get('errcode') == 0:
                return success_response(data={"message": "消息发送成功", "response": response_data})
            else:
                return error_response(message=f"消息发送失败: {response_data.get('errmsg', '未知错误')}")

        except Exception as e:
            return error_response(message=f"发送钉钉消息时出错: {str(e)}")
