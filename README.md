# Agentic-PPT

AI PPT Pro - 智能PPT生成应用（Flutter版本）

## 📱 项目概述

AI PPT Pro 是一个基于 Flutter 的跨平台 AI PPT 生成应用，支持通过 AI 自动生成 PowerPoint 演示文稿。

**版本:** 1.0.0
**完成度:** 90%
**Flutter 版本:** 3.0+
**支持平台:** Android, iOS, Web, Linux, macOS, Windows

---

## 🚀 GitHub Actions 自动编译

此仓库配置了 GitHub Actions，支持自动编译 APK：

### 自动触发

- 推送代码到 `flutter-apk` 或 `main` 分支时自动编译
- 创建 Pull Request 时自动编译
- 支持手动触发编译

### 手动触发

1. 进入 GitHub 仓库的 "Actions" 标签
2. 选择 "Build Android APK" 工作流
3. 点击 "Run workflow" 按钮
4. 选择分支并点击运行

### 下载 APK

编译完成后，在 Actions 页面的运行详情中可以下载 APK 文件。

---

## 📦 项目结构

```
Agentic-PPT/
├── AI-PPT-Flutter/          # Flutter 项目源代码
├── configs/                 # 配置文件
├── ppt_generator/           # PPT 生成器（Python 版本）
├── example.py               # 示例代码
├── requirements.txt         # Python 依赖
├── .github/workflows/       # GitHub Actions 配置
├── .gitignore              # Git 忽略文件
└── README.md               # 项目说明
```

---

## 🔨 本地编译

### 前提条件

- Flutter SDK 3.0+
- Android SDK
- Java JDK 11+

### 编译步骤

```bash
# 进入 Flutter 项目
cd AI-PPT-Flutter

# 安装依赖
flutter pub get

# 生成代码
flutter pub run build_runner build --delete-conflicting-outputs

# 编译 APK
flutter build apk --release

# APK 位置
# build/app/outputs/flutter-apk/app-release.apk
```

---

## 📖 功能说明

### 1. 生成 PPT

**文案生成:**
- 输入文案内容
- 选择模板
- 点击"生成"
- 等待生成完成

**研报生成:**
- 上传研报文件（PDF、Word、文本）
- 选择模板
- 点击"生成"
- 等待生成完成

### 2. 模板画廊

- 查看内置模板
- 按分类筛选
- 预览模板效果
- 选择模板使用

### 3. 历史记录

- 查看生成的 PPT 历史
- 删除不需要的记录

### 4. 设置

- API Key 配置
- Base URL 配置
- 主题切换（浅色/深色/跟随系统）

---

## 🎨 内置模板

| 模板 | 分类 | 页数 | 风格 |
|------|------|------|------|
| 专业商务 | 商业路演 | 12 | 渐变蓝 |
| 科技前沿 | 技术报告 | 10 | 暗色系 |
| 学术经典 | 学术演讲 | 15 | 纯白 |
| 创意设计 | 产品发布 | 8 | 活力渐变 |
| 极简主义 | 极简高级 | 10 | 纯净 |
| 赛博朋克 | 赛博朋克 | 12 | 霓虹 |
| 小红书风 | 小红书风 | 8 | 温暖渐变 |

---

## ⚙️ 配置应用

### 1. 获取 API Key

访问 https://open.bigmodel.cn/ 并注册账号，获取 GLM API Key。

### 2. 配置应用

1. 打开应用
2. 进入"设置"标签
3. 点击"API Key"
4. 输入你的 GLM API Key
5. 保存配置

---

## 📊 技术栈

### Flutter 版本

- **Flutter 3.0+** - 跨平台 UI 框架
- **Riverpod** - 状态管理
- **Hive** - 本地存储
- **Dio** - 网络请求
- **GLM API** - AI 文本生成

### Python 版本

- **Python 3.10+** - PPT 生成器
- **python-pptx** - PPT 文件操作
- **GLM API** - AI 文本生成

---

## 🐛 常见问题

### 1. GitHub Actions 编译失败

**问题:** Actions 编译报错

**解决方案:**
- 检查 Flutter 项目配置
- 查看错误日志
- 确保代码没有语法错误

### 2. APK 安装失败

**问题:** 无法安装 APK

**解决方案:**
- 检查手机是否开启"未知来源"安装
- 检查 Android 版本（建议 5.0+）
- 检查存储空间

### 3. API Key 无效

**问题:** 提示 API Key 无效

**解决方案:**
- 检查 API Key 是否正确
- 检查网络连接
- 重新获取 API Key

---

## 📄 许可证

MIT License

---

## 🙏 致谢

感谢以下开源项目：
- [Flutter](https://flutter.dev/)
- [Riverpod](https://riverpod.dev/)
- [Dio](https://pub.dev/packages/dio)
- [Hive](https://pub.dev/packages/hive)
- [GLM](https://open.bigmodel.cn/)

---

**项目创建时间:** 2026-02-12
**项目版本:** 1.0.0
**完成度:** 90%

---

**🦞 祝你使用愉快！**
