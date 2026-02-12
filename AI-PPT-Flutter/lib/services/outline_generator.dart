import 'package:json_annotation/json_annotation.dart';
import 'glm_client.dart';
import '../models/ppt_models.dart';
import '../models/template_models.dart';
import 'document_analyzer.dart';

part 'outline_generator.g.dart';

@JsonSerializable()
class OutlineData {
  final String title;
  final String subtitle;
  final List<OutlineSlideData> slides;

  OutlineData({
    required this.title,
    required this.subtitle,
    required this.slides,
  });

  factory OutlineData.fromJson(Map<String, dynamic> json) =>
      _$OutlineDataFromJson(json);

  Map<String, dynamic> toJson() => _$OutlineDataToJson(this);
}

@JsonSerializable()
class OutlineSlideData {
  final int slideNumber;
  final String slideType;
  final String title;
  final String contentSummary;
  final List<String> keyPoints;
  final Map<String, String> layoutPositions;
  final Map<String, String> visualElements;
  final String emotionalTone;

  OutlineSlideData({
    required this.slideNumber,
    required this.slideType,
    required this.title,
    required this.contentSummary,
    required this.keyPoints,
    required this.layoutPositions,
    required this.visualElements,
    required this.emotionalTone,
  });

  factory OutlineSlideData.fromJson(Map<String, dynamic> json) =>
      _$OutlineSlideDataFromJson(json);

  Map<String, dynamic> toJson() => _$OutlineSlideDataToJson(this);
}

class OutlineGenerator {
  final GLMClient _glmClient = GLMClient();

  // MARK: - Generate Two-Stage Outline
  Future<PPTOutline> generateTwoStage({
    required String text,
    required DocumentAnalysis analysis,
    required PPTTemplate template,
  }) async {
    final prompt = _buildTwoStagePrompt(
      analysis: analysis,
      text: text,
      template: template,
    );

    final schema = {
      'type': 'object',
      'properties': {
        'title': {'type': 'string'},
        'subtitle': {'type': 'string'},
        'slides': {
          'type': 'array',
          'items': {
            'type': 'object',
            'properties': {
              'slideNumber': {'type': 'number'},
              'slideType': {
                'type': 'string',
                'enum': [
                  'title',
                  'toc',
                  'content',
                  'problem_solution',
                  'data_dashboard',
                  'timeline',
                  'comparison',
                  'case_study',
                  'conclusion_cta',
                  'transition',
                ],
              },
              'title': {'type': 'string'},
              'contentSummary': {'type': 'string'},
              'keyPoints': {
                'type': 'array',
                'items': {'type': 'string'},
              },
              'layoutPositions': {
                'type': 'object',
                'additionalProperties': {'type': 'string'},
              },
              'visualElements': {
                'type': 'object',
                'additionalProperties': {'type': 'string'},
              },
              'emotionalTone': {
                'type': 'string',
                'enum': ['professional', 'inspiring', 'cautious', 'optimistic'],
              },
            },
            'required': [
              'slideNumber',
              'slideType',
              'title',
              'contentSummary',
              'keyPoints',
              'layoutPositions',
              'visualElements',
              'emotionalTone',
            ],
          },
        },
      },
      'required': ['title', 'subtitle', 'slides'],
    };

    final outlineData = await _glmClient.generateStructured<OutlineData>(
      prompt: prompt,
      schema: schema,
    );

    return _convertToOutline(outlineData, template);
  }

  // MARK: - Build Two-Stage Prompt
  String _buildTwoStagePrompt({
    required DocumentAnalysis analysis,
    required String text,
    required PPTTemplate template,
  }) {
    return '''
你是一位专业的 PPT 设计架构师。

【文档分析结果】
- 文档类型：${analysis.documentType ?? '未知'}
- 核心主题：${analysis.mainTheme ?? '未知'}
- 关键章节：${analysis.keySections.map((s) => '${s.title} (重要性: ${s.importance})').join('\n')}
- 目标受众：${analysis.audience ?? '通用'}

【模板信息】
- 模板名称：${template.name}
- 叙事结构：${template.narrative}
- 推荐页面数：${template.suggestedSlides}

【设计原则 - Problem → Solution → Result】

1. 开场（30%页面）
   - 吸引注意力的标题页
   - 清晰的目录/路线图
   - 问题/背景设定

2. 核心内容（50%页面）
   - 按重要性排序的关键章节
   - 数据支撑页面
   - 案例/证据页面

3. 收尾（20%页面）
   - 解决方案总结
   - 行动号召

【页面分配策略】
- importance >= 8: 2-3 页
- importance 5-7: 1-2 页
- importance < 5: 合并或省略

【原始文本】
$text

【输出要求】
严格按照 JSON 格式输出，确保总页数为 ${template.suggestedSlides}。
''';
  }

  // MARK: - Convert to PPTOutline
  PPTOutline _convertToOutline(OutlineData data, PPTTemplate template) {
    final slides = data.slides.map((slideData) {
      return SlideData(
        slideNumber: slideData.slideNumber,
        slideType: SlideTypeExtension.fromString(slideData.slideType),
        title: slideData.title,
        contentSummary: slideData.contentSummary,
        keyPoints: slideData.keyPoints,
        layoutPositions: slideData.layoutPositions,
        visualElements: slideData.visualElements,
        emotionalTone: slideData.emotionalTone,
      );
    }).toList();

    return PPTOutline(
      title: data.title,
      subtitle: data.subtitle,
      slides: slides,
      documentType: null,
      mainTheme: null,
      targetAudience: null,
    );
  }
}
