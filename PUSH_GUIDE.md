# 🚀 上传到 GitHub 指南

## ✅ 已完成的工作

1. ✅ 克隆 GitHub 仓库
2. ✅ 复制 Flutter 项目到仓库
3. ✅ 创建 GitHub Actions 配置（自动编译 APK）
4. ✅ 更新 README.md
5. ✅ 提交更改
6. ✅ 创建新分支 `flutter-apk`

---

## 📋 接下来的步骤

### 步骤 1: 推送到 GitHub

在你的本地电脑上运行：

```bash
# 进入仓库目录
cd /path/to/Agentic-PPT

# 拉取最新更改
git pull origin main

# 切换到 flutter-apk 分支
git checkout flutter-apk

# 推送到 GitHub
git push -u origin flutter-apk
```

如果遇到认证问题，使用 Personal Access Token：

```bash
# 1. 访问 https://github.com/settings/tokens
# 2. 生成新的 Token，选择 'repo' 权限
# 3. 复制 Token

# 4. 使用 Token 推送
git push https://<your-username>:<your-token>@github.com/MinJung-Go/Agentic-PPT.git flutter-apk
```

---

### 步骤 2: 设置为私人仓库

1. 访问 https://github.com/MinJung-Go/Agentic-PPT/settings
2. 滚动到 "Danger Zone"
3. 点击 "Change visibility"
4. 选择 "Make private"
5. 确认更改

---

### 步骤 3: 触发自动编译

推送代码后，GitHub Actions 会自动开始编译 APK：

1. 访问 https://github.com/MinJung-Go/Agentic-PPT/actions
2. 查看 "Build Android APK" 工作流
3. 等待编译完成（约 5-10 分钟）
4. 下载 APK 文件

---

## 📱 下载 APK

编译完成后：

1. 进入 Actions 页面
2. 点击最新的 "Build Android APK" 运行
3. 滚动到 "Artifacts" 部分
4. 点击 "app-release" 下载 APK
5. 解压下载的 ZIP 文件
6. 安装 APK 到手机

---

## 🔨 手动触发编译

你也可以手动触发编译：

1. 访问 https://github.com/MinJung-Go/Agentic-PPT/actions
2. 选择 "Build Android APK" 工作流
3. 点击 "Run workflow" 按钮
4. 选择分支（flutter-apk 或 main）
5. 点击运行

---

## 📊 GitHub Actions 配置

项目已配置了 GitHub Actions 自动编译：

- **触发条件：**
  - 推送代码到 `flutter-apk` 或 `main` 分支
  - 创建 Pull Request
  - 手动触发

- **编译步骤：**
  1. 设置 Java 17
  2. 设置 Flutter SDK
  3. 安装依赖
  4. 生成代码
  5. 编译 APK
  6. 上传 APK 作为 Artifact

- **APK 保留：**
  - APK 会保存 30 天
  - 可以随时下载

---

## 🐛 常见问题

### 1. 推送失败

**问题:** 提示认证失败

**解决方案:**
- 使用 Personal Access Token 替代密码
- 确保 Token 有 'repo' 权限

### 2. Actions 编译失败

**问题:** Actions 编译报错

**解决方案:**
- 查看错误日志
- 检查 Flutter 项目配置
- 确保代码没有语法错误

### 3. APK 下载失败

**问题:** 无法下载 APK

**解决方案:**
- 确保 Actions 运行完成
- 刷新 Actions 页面
- 检查 Artifacts 是否存在

---

## 📞 需要帮助？

如果遇到问题，请查看：

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Flutter 文档](https://flutter.dev/docs)
- [GitHub 文档](https://docs.github.com/)

---

**祝你使用愉快！** 🎉
