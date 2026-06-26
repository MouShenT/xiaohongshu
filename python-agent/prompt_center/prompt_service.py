"""Prompt 管理中心 — 管理所有AI提示词模板"""
import os
import yaml
from pathlib import Path


class PromptCenter:
    """提示词中心：加载、渲染、版本化管理所有 Prompt 模板"""

    def __init__(self, template_dir: str = None):
        self.template_dir = template_dir or os.path.join(
            Path(__file__).parent, "templates"
        )
        self._templates: dict[str, dict[str, str]] = {}
        self._load_all()

    def _load_all(self):
        """从模板目录加载所有 YAML 文件"""
        if not os.path.isdir(self.template_dir):
            return

        for fname in os.listdir(self.template_dir):
            if fname.endswith(".yaml") or fname.endswith(".yml"):
                path = os.path.join(self.template_dir, fname)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        if data:
                            self._templates.update(data)
                except Exception as e:
                    print(f"加载模板失败 {fname}: {e}")

    def get(self, template_name: str) -> str | None:
        """获取原始模板文本"""
        return self._templates.get(template_name)

    def render(self, template_name: str, **kwargs) -> str:
        """渲染模板: 用传入参数填充 {placeholder}"""
        template = self.get(template_name)
        if not template:
            return ""
        try:
            return template.format(**kwargs)
        except KeyError as e:
            return f"[模板渲染错误: 缺少参数 {e}]"

    def list_templates(self) -> list[str]:
        """列出所有可用模板名"""
        return list(self._templates.keys())


prompt_center = PromptCenter()
