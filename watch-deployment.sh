#!/bin/bash
# 实时监控CI/CD部署状态

echo "🔍 实时监控CI/CD部署状态"
echo "========================"

# 获取最新运行的ID
RUN_ID=$(gh run list --workflow="ci.yml" --limit 1 --json id --jq '.[0].id')

if [ -z "$RUN_ID" ]; then
    echo "❌ 没有找到运行中的工作流"
    exit 1
fi

echo "📊 监控运行ID: $RUN_ID"
echo "🔗 GitHub Actions: https://github.com/tyj1987/gupiao/actions/runs/$RUN_ID"
echo ""

# 监控循环
echo "🕐 开始实时监控 (每10秒刷新一次，按Ctrl+C停止)..."
echo ""

while true; do
    clear
    echo "🔍 CI/CD部署状态监控 - $(date)"
    echo "================================"
    echo "📊 运行ID: $RUN_ID"
    echo "🔗 查看详情: https://github.com/tyj1987/gupiao/actions/runs/$RUN_ID"
    echo ""
    
    # 获取运行状态
    STATUS=$(gh run view $RUN_ID --json status,conclusion --jq '.status')
    CONCLUSION=$(gh run view $RUN_ID --json status,conclusion --jq '.conclusion')
    
    echo "📈 状态: $STATUS"
    if [ "$CONCLUSION" != "null" ]; then
        echo "📋 结果: $CONCLUSION"
    fi
    echo ""
    
    # 显示作业状态
    echo "📋 作业状态:"
    gh run view $RUN_ID --json jobs --jq '.jobs[] | "- \(.name): \(.status) \(if .conclusion then "(\(.conclusion))" else "" end)"'
    echo ""
    
    # 如果完成了，检查生产环境
    if [ "$STATUS" = "completed" ]; then
        echo "🎯 部署完成，检查生产环境..."
        
        if curl -f http://47.94.225.76:8501 --connect-timeout 10 &> /dev/null; then
            echo "✅ 生产环境运行正常!"
            echo "🌐 访问地址: http://47.94.225.76:8501"
        else
            echo "⚠️ 生产环境暂不可达"
        fi
        
        echo ""
        if [ "$CONCLUSION" = "success" ]; then
            echo "🎉 部署成功完成!"
        else
            echo "❌ 部署失败，请查看详细日志"
        fi
        break
    fi
    
    echo "⏳ 等待10秒后刷新..."
    sleep 10
done
