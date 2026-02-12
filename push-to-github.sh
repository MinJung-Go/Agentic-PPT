#!/bin/bash

# ========================================
# 上传到 GitHub 并创建分支脚本
# ========================================

set -e

echo "=========================================="
echo "🚀 上传到 GitHub"
echo "=========================================="
echo ""

# 检查是否在正确的目录
if [ ! -d "Agentic-PPT" ]; then
    echo "❌ 错误: 请在 Agentic-PPT 目录下运行此脚本"
    exit 1
fi

cd Agentic-PPT

echo "=========================================="
echo "📋 1. 添加所有文件"
echo "=========================================="
git add -A
echo "✅ 文件已添加"
echo ""

echo "=========================================="
echo "📋 2. 提交更改"
echo "=========================================="
git commit -m "Add AI PPT Flutter project and GitHub Actions workflow"
echo "✅ 提交完成"
echo ""

echo "=========================================="
echo "📋 3. 创建新分支"
echo "=========================================="
git checkout -b flutter-apk
echo "✅ 分支 flutter-apk 已创建"
echo ""

echo "=========================================="
echo "📋 4. 设置为私人仓库"
echo "=========================================="
echo "请手动在 GitHub 仓库设置中设置为私人状态："
echo "  1. 访问 https://github.com/MinJung-Go/Agentic-PPT/settings"
echo "  2. 滚动到 'Danger Zone'"
echo "  3. 点击 'Change visibility'"
echo "  4. 选择 'Make private'"
echo "  5. 确认更改"
echo ""

echo "=========================================="
echo "📋 5. 推送到 GitHub"
echo "=========================================="
echo "请运行以下命令推送："
echo ""
echo "  git push -u origin flutter-apk"
echo ""
echo "如果遇到认证问题，请使用 Personal Access Token："
echo "  1. 访问 https://github.com/settings/tokens"
echo "  2. 生成新的 Token"
echo "  3. 选择 'repo' 权限"
echo "  4. 复制 Token"
echo "  5. 运行以下命令："
echo ""
echo "  git push https://<username>:<token>@github.com/MinJung-Go/Agentic-PPT.git flutter-apk"
echo ""

echo "=========================================="
echo "📋 6. 触发自动编译"
echo "=========================================="
echo "推送后，GitHub Actions 会自动开始编译 APK："
echo "  1. 访问 https://github.com/MinJung-Go/Agentic-PPT/actions"
echo "  2. 查看 'Build Android APK' 工作流"
echo "  3. 等待编译完成"
echo "  4. 下载 APK 文件"
echo ""

echo "=========================================="
echo "✅ 脚本执行完成！"
echo "=========================================="
