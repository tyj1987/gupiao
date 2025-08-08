#!/bin/bash
# 本地CI/CD测试脚本 - 模拟GitHub Actions流程

set -e

echo "🧪 开始本地CI/CD测试..."
echo "模拟GitHub Actions生产部署流程"
echo "==============================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 配置变量
DOCKER_IMAGE="gupiao-stock-analysis-local"
VERSION_TAG="test-$(date +%Y%m%d-%H%M%S)"
CONTAINER_NAME="gupiao-app-test"
PORT="8502"  # 使用不同端口避免冲突

# 步骤1: 代码质量检查
lint_and_test() {
    print_status "🔍 执行代码质量检查..."
    
    # 检查Python语法
    print_status "检查Python语法..."
    python3 -m py_compile src/ui/streamlit_app.py
    
    # 基础导入测试
    print_status "测试模块导入..."
    python3 -c "
import sys
sys.path.append('src')
try:
    from ui.streamlit_app import main
    print('✅ 主应用导入成功')
except Exception as e:
    print(f'❌ 导入失败: {e}')
    exit(1)
"
    
    print_success "代码质量检查通过"
}

# 步骤2: 项目清理
cleanup_project() {
    print_status "🧹 执行构建前清理..."
    
    # 清理Python缓存
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # 清理临时文件
    rm -rf .pytest_cache/ .coverage .tox/ 2>/dev/null || true
    
    # 显示构建上下文大小
    print_status "📊 构建上下文大小:"
    du -sh . --exclude=.git --exclude=venv | awk '{print "总大小: " $1}'
    du -sh src/ | awk '{print "核心代码: " $1}'
    
    print_success "项目清理完成"
}

# 步骤3: 构建Docker镜像
build_docker_image() {
    print_status "🐳 构建优化Docker镜像..."
    
    # 构建镜像
    docker build \
        --no-cache \
        --tag $DOCKER_IMAGE:$VERSION_TAG \
        --tag $DOCKER_IMAGE:latest \
        --file Dockerfile \
        .
    
    # 显示镜像信息
    print_status "📦 镜像构建完成:"
    docker images $DOCKER_IMAGE:$VERSION_TAG --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}"
    
    print_success "Docker镜像构建成功"
}

# 步骤4: 模拟生产部署
deploy_locally() {
    print_status "🚀 模拟生产环境部署..."
    
    # 停止现有容器
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
    
    # 创建数据目录
    mkdir -p test-deployment/{logs,data,exports,cache,models}
    
    # 启动容器
    docker run -d \
        --name $CONTAINER_NAME \
        --restart unless-stopped \
        -p $PORT:8501 \
        -e ENVIRONMENT=production \
        -e STREAMLIT_SERVER_PORT=8501 \
        -e STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
        -e STREAMLIT_SERVER_HEADLESS=true \
        -e STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
        -v $(pwd)/test-deployment/logs:/app/logs \
        -v $(pwd)/test-deployment/data:/app/data \
        -v $(pwd)/test-deployment/exports:/app/exports \
        -v $(pwd)/test-deployment/cache:/app/cache \
        -v $(pwd)/test-deployment/models:/app/models \
        $DOCKER_IMAGE:$VERSION_TAG
    
    print_success "容器启动完成"
}

# 步骤5: 健康检查
health_check() {
    print_status "🩺 执行健康检查..."
    
    sleep 10
    
    # 检查容器状态
    if docker ps | grep -q $CONTAINER_NAME; then
        print_success "容器运行正常"
    else
        print_error "容器启动失败"
        docker logs $CONTAINER_NAME
        exit 1
    fi
    
    # 检查应用响应
    max_attempts=30
    attempt=1
    
    print_status "等待应用启动..."
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:$PORT &> /dev/null; then
            print_success "应用健康检查通过"
            break
        else
            print_status "等待应用启动... ($attempt/$max_attempts)"
            sleep 2
            ((attempt++))
        fi
    done
    
    if [ $attempt -gt $max_attempts ]; then
        print_error "应用健康检查失败"
        print_status "查看应用日志:"
        docker logs $CONTAINER_NAME --tail 50
        exit 1
    fi
}

# 步骤6: 性能测试
performance_test() {
    print_status "📊 执行性能测试..."
    
    # 检查内存使用
    memory_usage=$(docker stats $CONTAINER_NAME --no-stream --format "table {{.MemUsage}}" | tail -n 1)
    print_status "内存使用: $memory_usage"
    
    # 检查响应时间
    response_time=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:$PORT)
    print_status "响应时间: ${response_time}s"
    
    print_success "性能测试完成"
}

# 步骤7: 生成测试报告
generate_report() {
    print_status "📋 生成测试报告..."
    
    echo "## 🧪 CI/CD本地测试报告" > test-report.md
    echo "" >> test-report.md
    echo "### 📦 构建信息" >> test-report.md
    echo "- **镜像标签**: $VERSION_TAG" >> test-report.md
    echo "- **镜像**: $DOCKER_IMAGE" >> test-report.md
    echo "- **测试时间**: $(date)" >> test-report.md
    echo "- **测试端口**: $PORT" >> test-report.md
    echo "" >> test-report.md
    
    echo "### 📊 镜像信息" >> test-report.md
    docker images $DOCKER_IMAGE:$VERSION_TAG --format "- **仓库**: {{.Repository}}" >> test-report.md
    docker images $DOCKER_IMAGE:$VERSION_TAG --format "- **标签**: {{.Tag}}" >> test-report.md
    docker images $DOCKER_IMAGE:$VERSION_TAG --format "- **大小**: {{.Size}}" >> test-report.md
    docker images $DOCKER_IMAGE:$VERSION_TAG --format "- **创建时间**: {{.CreatedSince}}" >> test-report.md
    echo "" >> test-report.md
    
    echo "### 🔗 访问信息" >> test-report.md
    echo "- **本地访问**: http://localhost:$PORT" >> test-report.md
    echo "- **容器名称**: $CONTAINER_NAME" >> test-report.md
    echo "" >> test-report.md
    
    echo "### ✅ 测试结果" >> test-report.md
    echo "- 代码质量检查: ✅ 通过" >> test-report.md
    echo "- Docker镜像构建: ✅ 成功" >> test-report.md
    echo "- 容器部署: ✅ 正常" >> test-report.md
    echo "- 健康检查: ✅ 通过" >> test-report.md
    echo "- 性能测试: ✅ 完成" >> test-report.md
    
    print_success "测试报告已生成: test-report.md"
}

# 清理函数
cleanup() {
    print_status "🧹 清理测试环境..."
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
    rm -rf test-deployment/
    print_success "清理完成"
}

# 显示结果
show_results() {
    print_success "🎉 CI/CD本地测试完成!"
    echo "=============================="
    echo ""
    echo "📊 测试结果:"
    echo "✅ 代码质量检查通过"
    echo "✅ Docker镜像构建成功"
    echo "✅ 本地部署正常"
    echo "✅ 健康检查通过"
    echo "✅ 性能测试完成"
    echo ""
    echo "🌐 访问地址:"
    echo "http://localhost:$PORT"
    echo ""
    echo "🔧 管理命令:"
    echo "docker logs $CONTAINER_NAME -f     # 查看日志"
    echo "docker stats $CONTAINER_NAME       # 查看资源使用"
    echo "docker stop $CONTAINER_NAME        # 停止容器"
    echo ""
    echo "📋 测试报告: test-report.md"
    echo ""
    echo "💡 CI/CD流程验证成功，可以推送到GitHub触发自动部署！"
}

# 主函数
main() {
    echo "测试开始时间: $(date)"
    
    # 设置错误处理
    trap cleanup EXIT
    
    lint_and_test
    cleanup_project
    build_docker_image
    deploy_locally
    health_check
    performance_test
    generate_report
    show_results
    
    echo "测试完成时间: $(date)"
    
    # 询问是否保持容器运行
    echo ""
    read -p "是否保持测试容器运行以便查看? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        cleanup
    else
        trap - EXIT  # 取消自动清理
        echo "容器将继续运行，手动停止: docker stop $CONTAINER_NAME"
    fi
}

# 运行主函数
main "$@"
