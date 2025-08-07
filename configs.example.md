# 🔐 CI/CD 敏感信息配置示例

## 环境变量和密钥配置

### Docker Hub 配置
```bash
DOCKER_USERNAME=tuoyongjun1987
DOCKER_IMAGE=tuoyongjun1987/gupiao-stock-analysis
DOCKER_HUB_TOKEN=dckr_pat_[您的令牌]
```

### 服务器信息
```bash
# 生产服务器
PROD_SERVER_IP=47.94.225.76
PROD_SERVER_USER=root
PROD_SERVER_PASSWORD=[您的密码]
PROD_SERVER_PORT=22

# 测试服务器  
TEST_SERVER_IP=192.168.2.8
TEST_SERVER_USER=root
TEST_SERVER_PASSWORD=[您的密码]
TEST_SERVER_PORT=22
```

### GitHub配置
```bash
GITHUB_USERNAME=tyj1987
GITHUB_EMAIL=tuoyongjun1987@qq.com
GITHUB_REPO=https://github.com/tyj1987/gupiao
```

## 安全说明

⚠️ **重要提醒**:
- 请勿将真实的密码、令牌等敏感信息提交到Git仓库
- 使用GitHub Secrets管理敏感信息
- 在本地测试时使用.env文件(已在.gitignore中排除)
- 定期更换访问令牌和密码

## 配置步骤

1. **复制此文件为.env.local**
   ```bash
   cp configs.example.md .env.local
   ```

2. **填入真实信息**
   编辑.env.local文件，填入您的真实配置信息

3. **设置GitHub Secrets**
   ```bash
   ./setup-github-secrets.sh
   ```

4. **验证配置**
   ```bash
   # 测试Docker登录
   docker login -u tuoyongjun1987
   
   # 测试服务器连接
   ssh root@47.94.225.76
   ssh root@192.168.2.8
   ```
