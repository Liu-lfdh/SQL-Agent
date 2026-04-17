---
name: skill-generator
description: 从对话历史中提炼可复用工作流，自动生成新的 Skill 文件
---

# Skill 生成器

## 使用场景

当需要将对话中已经完成的操作流程保存为可复用的 Skill 时使用，例如：

- 用户要求将当前操作流程保存为 Skill
- 用户要求创建新的自动化工作流
- 用户希望将某个重复操作封装为 Skill

## 执行步骤

### 1. 确定工作流范围

根据用户描述，明确工作流的起止范围：
- 工作流从哪个操作开始
- 工作流到哪个操作结束

如果用户没有明确说明范围，必须向用户询问确认，不要自行猜测。

### 2. 调用生成工具

使用 `skill_generator_tool` 工具，传入两个参数：
- content 参数：描述用户想要生成的 Skill 功能
- workflow_scope 参数：明确工作流从哪里开始到哪里结束

示例：
```
skill_generator_tool(content="将Excel导入流程保存为Skill", workflow_scope="从读取Excel文件开始，到数据导入完成反馈结果结束")
```

### 3. 刷新 Skill 列表

Skill 生成完成后，使用 `list_skills_tool` 工具获取最新的 Skill 列表，确认新 Skill 已成功注册。

### 4. 展示概述

向用户展示工作流概述（步骤摘要），无需展示完整 Skill 内容。
