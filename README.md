# VMware ESXi Log Analyzer

一个用于分析 VMware ESXi 系统日志的工具，支持处理 vmkernel、vmkwarning 和 vobd 日志。

## 功能特点

- 支持多种日志类型分析
  - vmkernel 日志
  - vmkwarning 日志
  - vobd 日志

- 强大的分析功能
  - 基础日志解析和格式化
  - 按模块分类
  - 时间范围过滤
  - 日志统计和可视化
  - 导出报告（HTML/PDF）

- 用户友好的界面
  - 基于 Streamlit 的交互式界面
  - 实时数据过滤和展示
  - 图表统计展示
  - 灵活的数据导出

## 安装

### 系统依赖

需要安装 wkhtmltopdf 用于生成 PDF 报告：

- MacOS:
  ```bash
  brew install wkhtmltopdf
  ```

- Ubuntu/Debian:
  ```bash
  sudo apt-get install wkhtmltopdf
  ```

- CentOS/RHEL:
  ```bash
  sudo yum install wkhtmltopdf
  ```

### Python 依赖

1. 克隆仓库
```
bash
git clone [repository-url]
cd vmw-esxi-log-extractor
```
2. 安装依赖
```
bash
pip install -r requirements.txt
```
3. 运行
```
bash
streamlit run app/Home.py
```
4. 调试模式运行（生成详细处理文件）
```
bash
VMK_DEBUG=true streamlit run app/Home.py
```


## 日志处理流程

### vmkernel 日志
1. 基础处理：解析原始日志
2. 过滤处理：提取模块信息
3. 分类处理：按类别分类

### vmkwarning 日志
1. 基础处理：解析原始日志
2. 分类处理：按类别分类

### vobd 日志
1. 基础处理：解析原始日志
2. 分类处理：按类别分类

## 主要功能

- 日志解析和格式化
- 模块识别和分类
- 时间范围过滤
- 日志统计分析
- 数据可视化
- 报告生成
- 原始日志导出
- 调试模式支持

## 注意事项

- 建议使用 Python 3.8 或更高版本
- 确保有足够的内存处理大型日志文件
- 调试模式会生成中间处理文件，需要额外磁盘空间

## 贡献

欢迎提交 Issue 和 Pull Request

## 联系方式

Bug Report: chang.wang@broadcom.com