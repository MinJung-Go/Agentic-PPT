"""
PPT生成器使用示例

功能特点：
- 两阶段大纲生成（文档分析 → 大纲生成）
- 风格锚定批量图片生成
- 缓存机制（大纲 + 图片）
- 智能错误处理与降级
- 23种模板预设支持
"""

from ppt_generator import PPTGenerator
import os


# ==================== 示例内容库 ====================

SAMPLE_CONTENTS = {
    "ai_tech": {
        "name": "AI技术分享",
        "text": """
人工智能的发展与应用

人工智能（Artificial Intelligence, AI）是计算机科学的一个分支，它致力于创造能够模拟人类智能的机器。

AI的发展历程：
1. 1956年：达特茅斯会议，AI概念正式提出
2. 1960-1970年代：早期AI研究，符号主义兴起
3. 1980年代：专家系统的商业化应用
4. 2010年代：深度学习革命，AlphaGo击败围棋世界冠军
5. 2020年代：大语言模型时代，ChatGPT引发AI热潮

当前AI的主要技术领域：
- 机器学习：监督学习、无监督学习、强化学习
- 深度学习：神经网络、卷积神经网络、Transformer
- 自然语言处理：文本理解、机器翻译、对话系统
- 计算机视觉：图像识别、目标检测、图像生成

AI的实际应用：
1. 医疗健康：疾病诊断、药物发现
2. 金融服务：风险评估、算法交易
3. 自动驾驶：路径规划、环境感知
4. 智能助手：语音交互、任务执行

未来展望：
- 人工通用智能（AGI）的探索
- AI与各行业的深度融合
- AI伦理和安全规范的完善
        """,
        "style": "科技风格，深蓝色主题，现代简约"
    },

    "business_plan": {
        "name": "商业计划书",
        "text": """
智能健康管理平台商业计划书

项目概述：
我们致力于开发一个基于AI技术的智能健康管理平台，为用户提供个性化的健康监测、疾病预防和生活方式建议。

市场分析：
- 全球数字健康市场规模持续增长，预计2025年达到659亿美元
- 中国健康管理市场需求旺盛，用户健康意识不断提升
- 移动健康应用用户超过4亿，市场潜力巨大

产品功能：
1. 健康数据收集：智能穿戴设备数据同步、手动记录
2. AI健康分析：基于机器学习的健康状态评估
3. 个性化建议：定制化的运动、饮食、睡眠建议
4. 疾病预警：早期疾病风险识别和提醒

竞争优势：
- 先进的AI算法和大数据分析能力
- 多维度健康数据整合处理
- 高精度的健康风险预测模型

财务预测：
第一年：用户获取和产品完善，预计投入500万
第二年：实现盈亏平衡，收入目标1000万
第三年：快速增长期，收入目标3000万

融资需求：
寻求A轮融资1000万人民币，用于产品研发、市场推广和团队扩张。
        """,
        "style": "商务专业风格，深蓝色主题，简洁有说服力"
    },

    "lifestyle": {
        "name": "生活美学",
        "text": """
咖啡生活美学

咖啡不仅是一种饮品，更是一种生活态度。

咖啡的起源：
传说中，埃塞俄比亚的牧羊人发现羊群吃了咖啡果后变得异常兴奋，
于是人类开始了与咖啡的不解之缘。

咖啡的种类：
- 阿拉比卡：香气优雅，口感柔和
- 罗布斯塔：口感强烈，咖啡因含量高
- 利比里亚：稀有品种，独特风味

冲泡方式：
1. 手冲：细腻风味，仪式感满满
2. 意式浓缩：浓郁醇厚，经典之选
3. 冷萃：清爽顺滑，夏日最爱
4. 法压壶：简单方便，保留油脂

咖啡与生活：
一杯好咖啡，让早晨变得美好，
让下午充满期待，让生活充满仪式感。
        """,
        "style": "温馨治愈风格，奶油白、焦糖棕、暖木色"
    },

    "product_intro": {
        "name": "产品发布",
        "text": """
全新智能手表发布

产品亮点：
- 全天候健康监测：心率、血氧、睡眠质量
- 超长续航：一次充电，使用14天
- 极致轻薄：仅重32克，佩戴无感
- 百种表盘：个性定制，随心切换

核心功能：
1. 精准运动追踪：支持100+运动模式
2. 智能消息提醒：来电、短信、APP通知
3. NFC支付：抬腕即付，便捷生活
4. 语音助手：一句话，搞定一切

技术参数：
- 屏幕：1.5英寸AMOLED，分辨率466x466
- 防水：5ATM，游泳无忧
- 传感器：PPG心率、加速度、陀螺仪、气压计
- 连接：蓝牙5.0、NFC、GPS

售价：1999元起
        """,
        "style": "科技发布会风格，深色背景，产品聚焦"
    },

    "academic": {
        "name": "学术研究",
        "text": """
基于深度学习的图像识别研究

研究背景：
计算机视觉是人工智能领域的重要分支，图像识别技术在医疗诊断、自动驾驶、安防监控等领域有广泛应用。

研究方法：
1. 数据集：ImageNet、COCO、自建医学影像数据集
2. 模型架构：ResNet、EfficientNet、Vision Transformer
3. 训练策略：数据增强、迁移学习、知识蒸馏

实验结果：
- Top-1准确率：92.3%（ImageNet）
- mAP：78.5%（COCO目标检测）
- 推理速度：15ms/张（RTX 3090）

关键发现：
- Vision Transformer在大规模数据集上表现优异
- 知识蒸馏可有效压缩模型体积
- 多尺度特征融合提升小目标检测精度

未来工作：
- 探索更高效的注意力机制
- 研究少样本学习方法
- 优化边缘设备部署方案
        """,
        "style": "学术风格，清爽简洁，公式图表，专业严谨"
    }
}


# ==================== 模板预设分类 ====================

PRESET_CATEGORIES = {
    "classic": {
        "name": "经典商务",
        "presets": ["business_pitch", "technical_report", "product_launch", "training",
                   "quarterly_review", "project_proposal", "company_intro", "academic"]
    },
    "stylish": {
        "name": "时尚风格",
        "presets": ["minimal_luxury", "kawaii_cute", "cyberpunk", "morandi", "chinese_modern",
                   "magazine", "glassmorphism", "doodle", "3d_modern", "vintage"]
    },
    "special": {
        "name": "特色场景",
        "presets": ["academic_paper", "xiaohongshu", "instagram", "tech_launch", "muji_minimal"]
    }
}


def create_generator():
    """创建PPT生成器实例"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("错误: 请设置 DEEPSEEK_API_KEY 环境变量")
        print("示例: export DEEPSEEK_API_KEY=your-api-key")
        exit(1)

    return PPTGenerator(
        api_key=api_key,
        provider="deepseek",
        base_url="https://api.deepseek.com/v1",
        enable_cache=True
    )


def display_all_presets(generator):
    """显示所有可用的模板预设"""
    all_presets = generator.list_template_presets()
    preset_dict = {p['key']: p for p in all_presets}

    print("\n" + "=" * 60)
    print("📋 所有可用的模板预设（共 23 种）")
    print("=" * 60)

    idx = 1
    preset_list = []

    for category_key, category in PRESET_CATEGORIES.items():
        print(f"\n【{category['name']}】")
        for preset_key in category['presets']:
            if preset_key in preset_dict:
                p = preset_dict[preset_key]
                print(f"  {idx:2d}. {preset_key:<18} - {p['name']:<8} | {p['description']}")
                preset_list.append(preset_key)
                idx += 1

    return preset_list


def display_sample_contents():
    """显示示例内容选项"""
    print("\n" + "-" * 40)
    print("📝 选择示例内容：")
    print("-" * 40)

    content_list = list(SAMPLE_CONTENTS.keys())
    for i, key in enumerate(content_list, 1):
        print(f"  {i}. {SAMPLE_CONTENTS[key]['name']}")

    return content_list


def generate_with_preset(generator, preset_key: str, content_key: str):
    """使用指定预设和内容生成PPT"""
    content = SAMPLE_CONTENTS[content_key]
    preset_info = generator.get_template_preset_info(preset_key)

    if not preset_info:
        print(f"❌ 未找到预设: {preset_key}")
        return None

    print("\n" + "=" * 60)
    print(f"🚀 开始生成 PPT")
    print("=" * 60)
    print(f"   模板预设: {preset_info['name']} ({preset_key})")
    print(f"   内容主题: {content['name']}")
    print(f"   页面序列: {' → '.join(preset_info['sequence'])}")

    # 显示风格提示（如果有）
    if 'style_hints' in preset_info:
        hints = preset_info['style_hints']
        print(f"\n📎 风格特点:")
        print(f"   背景: {hints.get('background', 'N/A')}")
        print(f"   配色: {', '.join(hints.get('colors', []))}")
        print(f"   视觉: {hints.get('visual', 'N/A')}")

    print("\n⏳ 生成中...")
    print("   - 两阶段大纲生成")
    print("   - 风格锚定批量生成")

    try:
        result = generator.generate_ppt(
            reference_text=content['text'],
            style_requirements=content['style'],
            output_dir=f"examples/{preset_key}_{content_key}",
            template_preset=preset_key,
            use_cache=True
        )

        print("\n✅ 生成完成！")
        print(f"   总页数：{result['total_slides']}")
        print(f"   成功页数：{result['success_slides']}")
        print(f"   PPTX文件：{result['pptx_file']}")

        # 显示生成信息
        gen_info = result.get('generation_info', {})
        print(f"\n📊 生成信息：")
        print(f"   - 两阶段生成: {'是' if gen_info.get('two_stage', False) else '否'}")
        print(f"   - 风格锚定: {'是' if gen_info.get('style_anchored', False) else '否'}")
        print(f"   - 缓存命中: {'是' if gen_info.get('cache_used', False) else '否'}")

        if result.get('cache_hits'):
            print(f"   - 图片缓存命中: {result['cache_hits']}")

        return result

    except Exception as e:
        print(f"\n❌ 生成失败：{e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """交互式主程序"""
    print("=" * 60)
    print("🎯 PPT生成器 v2.0 - 交互式模式")
    print("=" * 60)

    generator = create_generator()

    while True:
        # 显示所有预设
        preset_list = display_all_presets(generator)

        # 选择预设
        print("\n" + "-" * 40)
        choice = input("请选择模板编号 (输入 q 退出): ").strip()

        if choice.lower() == 'q':
            print("\n👋 再见!")
            break

        try:
            preset_idx = int(choice) - 1
            if preset_idx < 0 or preset_idx >= len(preset_list):
                print("❌ 无效编号")
                continue
            preset_key = preset_list[preset_idx]
        except ValueError:
            print("❌ 请输入数字")
            continue

        # 显示示例内容
        content_list = display_sample_contents()

        # 选择内容
        content_choice = input("请选择示例内容编号: ").strip()
        try:
            content_idx = int(content_choice) - 1
            if content_idx < 0 or content_idx >= len(content_list):
                print("❌ 无效编号")
                continue
            content_key = content_list[content_idx]
        except ValueError:
            print("❌ 请输入数字")
            continue

        # 生成PPT
        generate_with_preset(generator, preset_key, content_key)

        # 显示缓存统计
        stats = generator.get_cache_stats()
        if stats:
            print(f"\n📁 缓存统计：")
            print(f"   - 大纲缓存: {stats['outline_count']} 个")
            print(f"   - 图片缓存: {stats['image_count']} 个")
            print(f"   - 总大小: {stats['total_size_mb']} MB")

        # 继续？
        print("\n" + "-" * 40)
        again = input("继续生成？(y/n): ").strip().lower()
        if again != 'y':
            print("\n👋 再见!")
            break


if __name__ == "__main__":
    main()
