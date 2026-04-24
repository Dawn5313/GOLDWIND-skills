# GOLDWIND Skills

这是金风科技 PPT 制作专用 Codex Skill 分发仓库。

## AI 安装指令

如果用户只提供了本仓库链接，请不要安装仓库根目录。请直接安装以下技能路径：

```text
skills/ppt-master
```

推荐安装方式：

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo firstlightwcx/GOLDWIND-skills --path skills/ppt-master
```

也可以使用 GitHub tree URL：

```text
https://github.com/firstlightwcx/GOLDWIND-skills/tree/main/skills/ppt-master
```

如果你的运行环境不支持上述脚本，请将本仓库中的 `skills/ppt-master` 目录安装或复制到当前用户的 Codex skills 目录中。安装完成后，重启 Codex 或刷新技能列表。

## 技能说明

技能名称：`ppt-master`

用途：金风科技 PPT 制作流程。首次调用时，技能会先进入正式资料收集流程，并要求用户提供：

1. 历史 PPT 或样式参考文件
2. 需要填充进 PPT 的文字或文件素材
3. 是否需要联网扩展搜索，以及搜索范围

资料齐备后，技能会按 PPT Master 的标准流程继续进行历史样式提取、内容整理、页面设计、SVG 生成和 PPTX 导出。

## 给同事的使用方式

把下面这个仓库地址发给 AI，并说明“请安装这个技能包”：

```text
https://github.com/firstlightwcx/GOLDWIND-skills.git
```

推荐话术：

```text
请帮我安装这个 Codex 技能包：https://github.com/firstlightwcx/GOLDWIND-skills.git
```
