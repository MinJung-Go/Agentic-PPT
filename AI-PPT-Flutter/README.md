# AI PPT Pro

## 📱 项目简介

AI PPT Pro 是一款基于 Flutter 开发的智能 PPT 生成应用，支持文案生成和研报生成两种模式。

### 核心功能

- ✅ **文案生成 PPT** - 输入文案，自动生成 PPT
- ✅ **研报生成 PPT** - 基于主题自动搜索资料，生成专业研报
- ✅ **风格可选** - 内置 7 种精美模板
- ✅ **两阶段生成** - 深度文档分析 + 智能大纲规划
- ✅ **风格锚定** - 首页确定风格，后续保持一致

### 技术栈

- **Flutter** 3.0+ - 跨平台 UI 框架
- **Dart** - 编程语言
- **Riverpod** - 状态管理
- **Hive** - 本地数据存储
- **Dio** - HTTP 客户端

---

## 🚀 快速开始

### 环境要求

- Flutter SDK 3.0+
- Dart SDK 3.0+
- Android Studio / Xcode（可选）

### 安装步骤

1. **克隆项目**

```bash
git clone https://github.com/your-username/AI-PPT-Flutter.git
cd AI-PPT-Flutter
```

2. **安装依赖**

```bash
flutter pub get
```

3. **生成代码**

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

4. **运行应用**

```bash
# Linux Desktop
flutter run -d linux

# Android
flutter run -d android

# iOS
flutter run -d ios
```

---

## 📱 编译 APK

### 构建 Release APK

```bash
flutter build apk --release
```

### APK 位置

```
build/app/outputs/flutter-apk/app-release.apk
```

---

## 📦 项目结构

```
AI-PPT-Flutter/
├── lib/
│   ├── main.dart                      # 应用入口
│   ├── models/                        # 数据模型
│   │   ├── ppt_models.dart           # PPT 数据模型
│   │   ├── template_models.dart      # 模板数据模型
│   │   └── user_config.dart          # 用户配置
│   ├── services/                      # 服务层
│   │   ├── glm_client.dart           # GLM API 客户端
│   │   ├── document_analyzer.dart    # 文档分析器
│   │   ├── outline_generator.dart    # 大纲生成器
│   │   ├── ppt_generation_engine.dart # PPT 生成引擎
│   │   ├── web_search_engine.dart   # Web 搜索引擎
│   │   └── user_config_manager.dart # 用户配置管理
│   └── views/                         # UI 视图
│       ├── main_view.dart            # 主视图
│       ├── generation_view.dart      # 生成视图
│       ├── template_gallery_view.dart # 模板画廊
│       ├── history_view.dart         # 历史记录
│       └── settings_view.dart        # 设置视图
├── pubspec.yaml                       # 项目配置
└── README.md                          # 项目说明
```

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

## ⚙️ 配置说明

### GLM API Key

1. 打开应用
2. 进入"设置"标签
3. 点击"API Key"
4. 输入从 https://open.bigmodel.cn/ 获取的 API Key
5. 点击"保存"

### Base URL（可选）

默认：`https://open.bigmodel.cn/api/paas/v4`

如有需要，可以在设置中修改。

---

## 📖 使用指南

### 1. 文案生成模式

1. 打开"生成"标签
2. 选择"文案生成"模式
3. 输入文案
4. 选择模板
5. 点击"生成 PPT"

### 2. 研报生成模式

1. 打开"生成"标签
2. 选择"研报生成"模式
3. 输入研究主题
4. 选择模板
5. 点击"生成 PPT"

### 3. 查看模板

1. 打开"模板"标签
2. 浏览所有模板
3. 点击选择模板
4. 预览颜色方案

### 4. 查看历史

1. 打开"历史"标签
2. 查看生成的 PPT
3. 点击查看详情

### 5. 修改设置

1. 打开"设置"标签
2. 修改 API 配置
3. 修改通用设置
4. 修改外观主题

---

## 📊 项目统计

| 项目 | 数值 |
|------|------|
| 代码文件 | 14 个 |
| 总代码行数 | ~2,900 行 |
| 依赖包 | 111 个 |
| 模板数量 | 7 种 |
| 支持平台 | Android, iOS, Web, Linux, Mac, Windows |

---

## 🔧 开发说明

### 添加新功能

1. 在 `models/` 中添加数据模型
2. 在 `services/` 中添加服务逻辑
3. 在 `views/` 中添加 UI 视图
4. 使用 Riverpod 管理状态

### 代码生成

```bash
# 修改模型后，运行
flutter pub run build_runner build --delete-conflicting-outputs
```

---

## 🐛 常见问题

### Q: Flutter Doctor 提示错误？

A: 安装必要的依赖

```bash
# Linux
sudo apt-get install clang cmake ninja-build pkg-config libgtk-3-dev liblzma-dev libstdc++-12-dev

# Android SDK 依赖
flutter doctor --android-licenses
```

### Q: 无法生成 APK？

A: 确保已安装 Android SDK

```bash
flutter doctor --android-licenses
```

### Q: API Key 无效？

A: 检查：
1. API Key 是否正确
2. 网络连接是否正常
3. Base URL 是否正确

---

## 📝 许可证

MIT License

---

## 🙏 致谢

感谢以下开源项目：
- [Flutter](https://flutter.dev/)
- [Riverpod](https://riverpod.dev/)
- [Dio](https://pub.dev/packages/dio)
- [Hive](https://pub.dev/packages/hive)

---

## 📞 技术支持

如有问题，请查阅：

- [Flutter 官方文档](https://flutter.dev/docs)
- [Riverpod 文档](https://riverpod.dev/)
- [GLM API 文档](https://open.bigmodel.cn/)

---

**项目创建时间**: 2026-02-12
**项目版本**: 1.0.0
**Flutter 版本**: 3.24.5

---

## 📄 相关文档

- [完整代码文档](../CODE_COMPLETE.md)
- [项目总结](../AI-PPT-Flutter/PROJECT_SUMMARY.md)
- [APK 生成指南](../APK_GENERATION_GUIDE.md)

**祝你开发愉快！** 🦞🚀
