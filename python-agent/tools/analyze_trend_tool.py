"""热度分析工具 + 数据清洗工具"""
from tools import BaseTool


class AnalyzeTrendTool(BaseTool):
    name = "analyze_trend"
    description = "分析关键词的热度趋势和运营建议"

    async def execute(self, keyword: str) -> dict:
        from application.services.hot_radar_service import HotRadarService
        svc = HotRadarService()
        return await svc.analyze_trend(keyword)

    def _parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "要分析的关键词"},
            },
            "required": ["keyword"],
        }


class DataCleanTool(BaseTool):
    name = "data_clean"
    description = "清洗文本数据，去除多余空格、HTML标签、特殊字符"

    async def execute(self, text: str, remove_html: bool = True, strip_whitespace: bool = True) -> str:
        import re
        if remove_html:
            text = re.sub(r"<[^>]+>", "", text)
        if strip_whitespace:
            text = re.sub(r"\s+", " ", text).strip()
        return text

    def _parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "待清洗的文本"},
                "remove_html": {"type": "boolean", "description": "是否移除HTML标签"},
                "strip_whitespace": {"type": "boolean", "description": "是否压缩空白字符"},
            },
            "required": ["text"],
        }
