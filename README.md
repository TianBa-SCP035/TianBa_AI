<p align="center">
  <img src="Web/apps/web-antd/public/favicon.ico" alt="TianBa AI Logo" width="60" style="vertical-align: middle; margin-right: 15px;">
</p>

<h1 align="center">TianBa AI - 智能科研工具集成平台</h1>

<p align="center">
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

TianBa AI 科研工具集成平台是一个专注于**生物医药研究领域**的内部AI工具集成平台，主要为药理药效实验提供智能化解决方案。系统集成了先进的AI算法、自然语言处理和数据分析技术，专注于小鼠实验数据分析、药理药效评估、研究报告生成和抗体研究等核心科研场景。

### 🌟 核心价值

- **智能实验分析**：基于AI算法提供精准的药理药效实验数据分析
- **多模态数据处理**：整合文本、图像、结构化数据等多种实验信息
- **专业领域聚焦**：深度针对小鼠实验、药效评估和抗体研究等专业场景
- **高效工作流**：自动化处理复杂实验数据，显著提升科研效率

## 🧬 AI核心功能

### 🐭 小鼠实验数据分析
- **AI驱动分析**：基于小鼠实验数据自动生成药理药效分析报告
- **多维度评估**：从药效、毒性、耐受性等多维度评估实验结果
- **智能可视化**：自动生成专业实验图表和统计分析
- **异常检测**：AI识别实验数据中的异常模式和潜在问题

### 📊 科研报告智能生成
- **模板化报告**：基于标准科研模板自动生成结构化报告
- **数据驱动内容**：从实验数据中自动提取关键信息和结论
- **多语言支持**：自动生成中英文双语科研报告，适应国际交流需求
- **图表智能生成**：根据数据特点自动选择最适合的图表类型

### 🔬 药理药效分析
- **药效动力学建模**：AI模型预测药物在实验动物体内的吸收、分布、代谢和排泄
- **剂量优化算法**：基于实验数据计算最优给药方案
- **药物相互作用分析**：智能识别潜在药物相互作用和禁忌症
- **疗效-毒性平衡评估**：量化评估治疗效果与副作用风险

### 🧪 抗体研究工具集
- **抗体结构预测**：基于深度学习的抗体三维结构预测
- **抗原-抗体结合分析**：计算预测结合亲和力和特异性
- **人源化优化建议**：AI辅助抗体人源化改造方案
- **免疫原性评估**：预测潜在免疫反应风险

### 🌐 智能多语言翻译
- **专业术语精准翻译**：生物医药专业词汇的准确中英互译
- **上下文理解**：基于科研语境的智能翻译
- **文献辅助翻译**：支持科研文献和实验报告的翻译
- **术语一致性**：确保专业术语在整个文档中的一致性

### 📄 智能文档处理
- **OCR智能识别**：高精度科研文档和实验图像文字识别
- **关键信息提取**：自动从实验报告中提取结构化数据
- **智能分类归档**：AI自动分类和组织科研文档
- **模板智能填充**：基于数据自动生成标准化科研文档

## 🛠️ 技术架构

### 🧠 AI技术栈
- **深度学习框架**：PyTorch, TensorFlow
- **自然语言处理**：Transformers, spaCy, NLTK
- **计算机视觉**：OpenCV, PaddleOCR
- **数据分析**：pandas, numpy, scikit-learn
- **生物信息学**：BioPython, RDKit

### 🖥️ 后端技术
- **框架**：FastAPI
- **服务器**：Uvicorn
- **数据库**：MySQL, Redis
- **任务队列**：Celery
- **数据验证**：Pydantic
- **文档处理**：PyMuPDF, python-docx

### 🎨 前端技术
- **框架**：React + TypeScript
- **UI库**：Ant Design
- **状态管理**：Zustand
- **可视化**：ECharts, D3.js
- **构建工具**：Vite

## 🏗️ 项目结构

```
TianBa_AI/
├── Code/                     # 后端代码
│   ├── app/                  # 应用核心
│   │   ├── api/             # API接口层
│   │   │   ├── v1/         # API版本1
│   │   │   │   ├── experiment_chinese.py  # 中文实验报告API
│   │   │   │   ├── experiment_english.py   # 英文实验报告API
│   │   │   │   ├── plan_api.py             # 项目方案API
│   │   │   │   └── report_api.py           # 项目报告API
│   │   ├── services/        # 业务逻辑层
│   │   │   ├── experiment/  # 实验分析服务
│   │   │   ├── antibody/    # 抗体研究服务
│   │   │   ├── pharmacology/ # 药理药效服务
│   │   │   └── translation/  # 翻译服务
│   │   ├── models/          # 数据模型
│   │   ├── utils/           # 工具函数
│   │   └── tasks/           # 异步任务
│   ├── config/              # 配置文件
│   ├── docs/                # 文档和临时文件
│   └── tests/               # 测试代码
├── Web/                     # 前端代码
│   ├── apps/                # 前端应用
│   │   ├── web-antd/       # 主应用
│   │   └── backend-mock/   # 模拟后端
│   ├── packages/            # 共享包
│   └── internal/            # 内部工具
└── Start/                   # 启动脚本
```

## 🚀 快速开始

### 环境要求
- **Python**：3.8+
- **Node.js**：16+
- **MySQL**：8.0+
- **Redis**：6.0+ (可选，用于缓存)
- **GPU**：NVIDIA GPU + CUDA (推荐，用于AI模型加速)

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
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等信息
```

3. **数据库初始化**
```bash
# 创建数据库表
python -m app.db.init_db

# 导入初始数据（可选）
python -m app.db.seed_data
```

4. **前端设置**
```bash
cd ../Web

# 安装依赖
npm install

# 或使用 pnpm
pnpm install
```

5. **启动应用**

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
python main.py

# 新终端中启动前端
cd ../Web
npm run dev
# 或
pnpm dev
```

6. **访问应用**
- 前端界面：http://localhost:5173
- API文档：http://localhost:8000/docs
- 后端管理：http://localhost:8000/admin

## 📖 使用指南

### 生成小鼠实验报告
1. 登录系统，选择"实验分析"模块
2. 输入实验基本信息和小鼠实验数据
3. 选择报告类型（药效分析、毒性评估等）
4. 点击"AI生成报告"，系统将基于实验数据生成专业报告
5. 可选择生成中英文双语版本

### 药理药效分析
1. 选择"药理药效"模块
2. 输入药物基本信息和实验数据
3. 选择分析类型（药效动力学、药物相互作用等）
4. 启动AI分析，查看结果和可视化图表
5. 导出分析报告

### 抗体研究工具
1. 选择"抗体研究"模块
2. 上传抗体序列或结构数据
3. 选择分析工具（结构预测、结合分析等）
4. 配置分析参数
5. 查看AI分析结果和建议

### 智能翻译
1. 选择"翻译工具"模块
2. 上传科研文档或输入文本
3. 选择翻译方向（中→英或英→中）
4. 启动翻译，系统将保持专业术语准确性
5. 下载翻译结果

## 🔧 API文档

### 主要API端点

#### 实验报告生成
```http
POST /api/v1/experiment/chinese/generate
POST /api/v1/experiment/english/generate
GET /api/v1/experiment/templates
```

#### 药理药效分析
```http
POST /api/v1/pharmacology/analyze
POST /api/v1/pharmacology/dosage-optimize
GET /api/v1/pharmacology/drug-interaction
```

#### 抗体研究
```http
POST /api/v1/antibody/structure-predict
POST /api/v1/antibody/binding-analysis
POST /api/v1/antibody/humanization
```

#### 智能翻译
```http
POST /api/v1/translation/scientific
POST /api/v1/translation/document
```

完整API文档可在服务启动后访问: `http://localhost:8000/docs`

## 🧪 AI模型说明

### 实验数据分析模型
- **训练数据**：基于大量小鼠实验数据和科研文献
- **模型架构**：Transformer + 图神经网络
- **更新频率**：定期更新，纳入最新研究成果

### 药理药效模型
- **训练数据**：整合药物数据库和实验数据
- **模型架构**：多任务学习 + 注意力机制
- **预测精度**：药效预测准确率>85%

### 抗体结构模型
- **训练数据**：PDB数据库 + 专利抗体序列
- **模型架构**：AlphaFold改进版 + 专门优化
- **预测精度**：RMSD < 2.0Å

## 🤝 贡献指南

我们欢迎生物医药AI领域的专家和开发者贡献代码、数据和专业知识！

### 如何贡献
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 特别欢迎
- 新的生物医药AI模型和算法
- 实验数据集和标注
- 专业生物医学知识库扩展
- 实验验证和案例研究

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢以下开源项目和组织的支持：
- [PyTorch](https://pytorch.org/) - 深度学习框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Web框架
- [React](https://reactjs.org/) - 用户界面库
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - OCR工具库
- [Transformers](https://huggingface.co/transformers/) - NLP模型库

特别感谢科研机构和生物医药专家提供的专业指导。

---

<p align="center">
  <p>🧬 专注于AI驱动的科研创新 🧬</p>
  <p>© 2025 TianBa AI. All rights reserved.</p>
  <p>
    <a href="mailto:contact@tianba-ai.com">联系我们</a> • 
    <a href="https://tianba-ai.com">官方网站</a> • 
    <a href="https://docs.tianba-ai.com">文档中心</a>
  </p>
</p>
