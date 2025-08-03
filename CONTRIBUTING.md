# 🤝 贡献指南

感谢您对股票分析系统项目的关注！我们欢迎所有形式的贡献，包括但不限于代码提交、bug报告、功能建议、文档完善等。

## 📋 贡献方式

### 🐛 报告Bug

如果您发现了bug，请：

1. 在[Issues](https://github.com/tyj1987/gupiao/issues)中搜索是否已有相同问题
2. 如果没有，请创建新的Issue，包含：
   - 清晰的问题描述
   - 复现步骤
   - 期望的行为
   - 实际的行为
   - 系统环境信息（操作系统、Python版本等）
   - 相关的错误日志

### ✨ 提出功能建议

如果您有好的想法：

1. 在[Discussions](https://github.com/tyj1987/gupiao/discussions)中讨论
2. 或创建Feature Request类型的Issue
3. 描述功能的用途和价值
4. 如果可能，提供设计思路

### 🔧 代码贡献

#### 开发环境设置

```bash
# 1. Fork并克隆仓库
git clone https://github.com/YOUR_USERNAME/gupiao.git
cd gupiao

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置API密钥
cp config/api_keys.example.py config/api_keys.py
# 编辑api_keys.py，添加您的测试token

# 5. 运行测试
python local_test.py
```

#### 开发流程

1. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-fix-name
   ```

2. **编写代码**
   - 遵循项目的代码风格
   - 添加必要的注释
   - 编写测试用例

3. **测试代码**
   ```bash
   # 运行本地测试
   python local_test.py
   
   # 运行功能测试
   python functional_test.py
   
   # 启动应用测试
   streamlit run src/ui/streamlit_app.py
   ```

4. **提交代码**
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   # 或
   git commit -m "fix: 修复问题描述"
   ```

5. **推送并创建PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   然后在GitHub上创建Pull Request

## 📝 代码风格指南

### Python代码规范

- 遵循[PEP 8](https://pep8.org/)代码风格
- 使用有意义的变量和函数名
- 添加必要的docstring和注释
- 保持函数简洁，单一职责

```python
def get_stock_data(symbol: str, start_date: str = None) -> Dict[str, Any]:
    """
    获取股票数据
    
    Args:
        symbol: 股票代码，如 '000001.SZ'
        start_date: 开始日期，格式 'YYYY-MM-DD'
    
    Returns:
        包含股票数据的字典
    
    Raises:
        ValueError: 当股票代码格式不正确时
    """
    pass
```

### 文件组织

- 新功能放在对应的模块中
- 测试文件以`test_`开头
- 工具脚本以`.sh`结尾
- 文档使用Markdown格式

### 提交信息规范

使用[Conventional Commits](https://www.conventionalcommits.org/)格式：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

类型说明：
- `feat`: 新功能
- `fix`: bug修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

示例：
```
feat(search): 添加拼音搜索功能

支持使用拼音缩写搜索股票，如输入"zgyh"可以找到"中国银行"

Closes #123
```

## 🧪 测试指南

### 运行测试

```bash
# 基础环境测试
./check_environment.sh

# 功能模块测试
python local_test.py

# 完整功能测试
python functional_test.py

# Docker部署测试
./docker-quick-deploy.sh
```

### 编写测试

为新功能编写测试：

```python
def test_stock_search():
    """测试股票搜索功能"""
    from src.data.universal_stock_fetcher import UniversalStockFetcher
    
    fetcher = UniversalStockFetcher()
    
    # 测试代码搜索
    results = fetcher.search_stocks("600036")
    assert len(results) > 0
    assert "600036.SH" in [r[0] for r in results]
    
    # 测试名称搜索
    results = fetcher.search_stocks("中国银行")
    assert len(results) > 0
```

## 📚 文档贡献

### 文档类型

- **README.md**: 项目介绍和快速开始
- **DEPLOYMENT_GUIDE.md**: 详细部署指南
- **代码注释**: 函数和类的文档字符串
- **API文档**: 接口说明

### 文档规范

- 使用清晰的标题层级
- 提供代码示例
- 包含必要的截图或图表
- 保持内容的时效性

## 🔄 发布流程

### 版本号规范

遵循[Semantic Versioning](https://semver.org/)：

- `MAJOR`: 不兼容的API修改
- `MINOR`: 向后兼容的功能性新增
- `PATCH`: 向后兼容的问题修正

### 发布检查清单

发布新版本前：

- [ ] 所有测试通过
- [ ] 文档已更新
- [ ] 版本号已更新
- [ ] CHANGELOG已更新
- [ ] Docker镜像构建成功

## 👥 社区规范

### 行为准则

我们承诺为每个人提供友好、安全和包容的环境：

- 使用友好和包容的语言
- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注最有利于社区的事情
- 对其他社区成员表示同理心

### 沟通渠道

- **GitHub Issues**: 报告bug和功能请求
- **GitHub Discussions**: 一般讨论和问答
- **Pull Requests**: 代码审查和讨论

## 🎖️ 贡献者认可

我们重视每一个贡献，会在以下方面给予认可：

- 在README中列出贡献者
- 在发布说明中感谢贡献者
- 为重要贡献者授予仓库权限

## 📞 获取帮助

如果您在贡献过程中遇到问题：

1. 查看现有的Issues和Discussions
2. 阅读项目文档
3. 创建新的Discussion询问
4. 联系项目维护者

## 🚀 开始贡献

准备好开始贡献了吗？

1. ⭐ Star本项目
2. 🍴 Fork到您的账户
3. 💻 克隆到本地开发
4. 🔧 进行您的改进
5. 📤 提交Pull Request

感谢您的贡献，让我们一起构建更好的股票分析系统！

---

**需要帮助？** 请查看[Issues](https://github.com/tyj1987/gupiao/issues)或创建[Discussion](https://github.com/tyj1987/gupiao/discussions)
