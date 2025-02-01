# Changelog

所有重要的更改都会记录在这个文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## 版本说明
- 主版本号：做了不兼容的 API 修改
- 次版本号：做了向下兼容的功能性新增
- 修订号：做了向下兼容的问题修正

## 更新类型
- Added：新添加的功能
- Changed：对现有功能的变更
- Deprecated：已经不建议使用，准备很快移除的功能
- Removed：已经移除的功能
- Fixed：对bug的修复
- Security：对安全性的改进

## [0.1.0] - 2024-01-30

### Added
- 基础功能
  - 支持处理 vmkernel、vmkwarning 和 vobd 日志
  - 实现日志解析和格式化
  - 添加模块识别和分类功能
  - 实现时间范围过滤

- 用户界面
  - 基于 Streamlit 的交互式界面
  - 实时数据过滤和展示
  - 图表统计展示功能
  - 数据导出功能

- 报告功能
  - 支持导出 HTML 报告
  - 支持导出 PDF 报告
  - 添加日志统计和可视化

- 开发功能
  - 添加调试模式支持
  - 优化中间文件处理
  - 统一日志处理流程

### Changed
- 优化文件结构，分离处理器和视图逻辑
- 统一日志处理流程和命名规范
- 改进错误处理和用户反馈

### Fixed
- 修复时间过滤功能的 UTC 时区问题
- 修复大文件处理时的内存问题
- 修复模块匹配的大小写敏感问题

[0.1.0]: https://github.com/username/repository/releases/tag/v0.1.0 