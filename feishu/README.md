# 飞书(Feishu)相关项目

这个仓库包含了多个与飞书集成和开发相关的项目。

## 项目列表

### 1. doc-reformat - 文档一键排版工具

基于AI的飞书文档智能排版工具，可以自动优化文档格式。

**功能特点**：
- AI智能分析文档结构
- 自动转换列表格式
- 添加高亮提示块
- 数据表格化
- 优化标题层级

**技术栈**：
- 前端：React + TypeScript + Ant Design
- 后端：Python + FastAPI + 通义千问AI
- 部署：支持云函数/云服务器

📖 [查看详细文档](./doc-reformat/README.md)

## 项目结构

```
feishu/
├── README.md           # 本文件
└── doc-reformat/       # 文档排版工具
    ├── frontend/       # 前端代码
    ├── backend/        # 后端代码
    ├── docs/           # 文档
    └── scripts/        # 部署脚本
```

## 开发计划

- [x] 文档排版工具
- [ ] 更多飞书集成工具...

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License
