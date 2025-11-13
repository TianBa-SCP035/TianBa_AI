<h1 style="font-size: 3em;">
  <img src="Web/apps/web-antd/public/favicon.ico" alt="TianBa AI Logo" width="50"  margin-right: 40px; vertical-align: middle;">
  TianBa AI - 智能科研平台
</h1>

<p>
  <a href="https://python.org">
    <img src="https://img.shields.io/badge/python-3.8%2B-blue.svg" alt="Python">
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  </a>
  <a href="https://github.com/TianBa-SCP035/TianBa_AI">
    <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg" alt="Platform">
  </a>
</p>

## 🎯 项目简介

TianBa AI 是一个专注于生物医药领域的科研文档生成平台，主要为药理药效实验提供项目方案和项目报告的自动化生成服务。系统通过模板化处理和数据整合，帮助研究人员快速生成标准化的科研文档，提高工作效率。

### 🌟 核心价值

- **文档自动化生成**：基于数据库信息和预设模板，快速生成项目方案和项目报告
- **多语言支持**：支持中英文双语文档生成
- **专业领域聚焦**：针对肿瘤和自身免疫疾病研究的特定需求
- **数据整合能力**：从多个数据源获取信息，确保文档内容准确性

## 📋 主要功能

### 📝 项目方案生成
- **模板化生成**：基于标准模板生成项目方案文档
- **数据自动填充**：从数据库自动获取项目信息填充到文档
- **多疾病类型支持**：支持肿瘤和自身免疫疾病的项目方案
- **双语输出**：支持中英文项目方案生成

### 📊 项目报告生成
- **实验数据整合**：整合实验数据生成结构化报告
- **图表自动生成**：根据数据特点生成相应图表
- **多格式输出**：支持Word文档、Excel表格等多种格式
- **图片资源管理**：自动整理和打包实验相关图片

### 🔧 辅助工具
- **OCR文字识别**：支持科研文档的文字识别和提取
- **文档翻译**：提供科研文档的中英文翻译功能
- **Excel处理**：支持Excel数据的读取、处理和导出

## 🛠️ 技术架构

### 🧠 后端技术
- **框架**：FastAPI
- **数据库**：MySQL
- **文档处理**：python-docx, openpyxl, PyMuPDF
- **OCR工具**：PaddleOCR
- **图像处理**：OpenCV, Pillow
- **数据分析**：pandas, numpy

### 🎨 前端技术
- **框架**：Vue 3 + TypeScript
- **UI库**：Ant Design
- **构建工具**：Vite
- **状态管理**：Zustand
- **网络请求**：Axios

## 🏗️ 项目结构

```
TianBa_AI/
├── Code/                     # 后端代码
│   ├── app/                  # 应用核心
│   │   ├── api/             # API接口层
│   │   │   ├── v1/         # API版本1
│   │   │   │   ├── plan_api.py           # 项目方案API
│   │   │   │   ├── report_api.py         # 项目报告API
│   │   │   │   ├── project_plan/         # 项目方案实现
│   │   │   │   └── project_report/       # 项目报告实现
│   │   ├── services/        # 业务逻辑层
│   │   │   ├── project_plan/             # 项目方案服务
│   │   │   └── project_report/           # 项目报告服务
│   │   ├── data/            # 数据处理层
│   │   ├── main/            # 主程序
│   │   ├── utils/           # 工具函数
│   │   │   ├── OCR/         # OCR相关工具
│   │   │   ├── Translate/   # 翻译工具
│   │   │   └── Solve/       # 问题解决工具
│   │   └── tasks/           # 异步任务
│   ├── config/              # 配置文件
│   ├── docs/                # 文档和临时文件
│   └── tests/               # 测试代码
├── Web/                     # 前端代码
│   ├── apps/                # 前端应用
│   │   ├── web-antd/        # 主应用
│   │   │   └── src/         # 源代码
│   │   │       ├── views/   # 页面组件
│   │   │       │   ├── Report-generator/  # 报告生成器
│   │   │       │   └── word-generator/    # 项目方案生成器
│   │   │       └── api/     # API调用
│   │   └── backend-mock/    # 模拟后端
│   ├── packages/            # 共享包
│   └── internal/            # 内部工具
└── Start/                   # 启动脚本
```

## 🚀 快速开始

### 环境要求
- **Python**：3.8+
- **Node.js**：20.10.0+
- **MySQL**：8.0+
- **pnpm**：9.12.0+

### 安装与运行

1. **克隆项目**
```bash
git clone https://github.com/your-username/TianBa_AI.git
cd TianBa_AI
```

2. **后端设置**
```bash
cd Code

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r public/requirements.txt

# 配置环境变量
# 编辑 Code/config/settings.py 文件，配置数据库连接等信息
```

3. **前端设置**
```bash
cd ../Web

# 安装依赖
pnpm install
```

4. **启动应用**

**方式一：使用启动脚本**
```bash
# Windows
cd ../Start
start.bat

# Linux/macOS
cd ../Start
chmod +x start.sh
./start.sh
```

**方式二：手动启动**
```bash
# 启动后端
cd ../Code
python app/main/main.py

# 新终端中启动前端
cd ../Web
pnpm dev:antd
```

5. **访问应用**
- 前端界面：http://localhost:5173
- 项目方案API：http://localhost:6001
- 项目报告API：http://localhost:6002

## 📖 使用指南

### 生成项目方案
1. 打开前端界面，选择"项目方案生成器"
2. 输入项目编号（如：25P1156）
3. 选择疾病类型（肿瘤/自身免疫）
4. 选择输出语言（中文/英文）
5. 点击"生成项目方案"
6. 下载生成的Word文档

### 生成项目报告
1. 打开前端界面，选择"报告生成器"
2. 输入实验编号
3. 可选输入结束天数
4. 点击"生成报告"
5. 下载生成的Word文档、Excel表格和图片压缩包

## 🔧 API文档

### 项目方案API

#### 生成项目方案
```http
POST /project-plan/execute
Content-Type: application/json

{
  "disease": "tumor|autoimmune",
  "language": "chinese|english",
  "function": "generate",
  "content": {
    "project_code": "项目编号"
  }
}
```

### 项目报告API

#### 生成项目报告
```http
POST /project-report/execute
Content-Type: application/json

{
  "disease": "tumor|autoimmune",
  "language": "chinese|english",
  "function": "generate",
  "content": {
    "project_code": "项目编号",
    "end_day": "结束天数（可选）"
  }
}
```

## 🤝 贡献指南

我们欢迎开发者贡献代码和改进建议！

### 如何贡献
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢以下开源项目的支持：
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Web框架
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [Ant Design](https://ant.design/) - 企业级UI设计语言
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - OCR工具库
- [python-docx](https://github.com/python-openxml/python-docx) - Word文档处理库

---

<p align="center">
  <p>📄 专注于科研文档自动化生成 📄</p>
  <p>© 2025 TianBa AI. All rights reserved.</p>
</p>
