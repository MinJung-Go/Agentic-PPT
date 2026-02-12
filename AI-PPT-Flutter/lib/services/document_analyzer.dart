import 'package:json_annotation/json_annotation.dart';
import 'glm_client.dart';
import '../models/template_models.dart';

part 'document_analyzer.g.dart';

@JsonSerializable()
class DocumentAnalysis {
  final String? documentType;
  final String? mainTheme;
  final List<KeySection> keySections;
  final List<DataPoint> dataPoints;
  final String? narrativeStructure;
  final String? audience;
  final Map<String, double> importanceScores;

  DocumentAnalysis({
    this.documentType,
    this.mainTheme,
    required this.keySections,
    required this.dataPoints,
    this.narrativeStructure,
    this.audience,
    required this.importanceScores,
  });

  factory DocumentAnalysis.fromJson(Map<String, dynamic> json) =>
      _$DocumentAnalysisFromJson(json);

  Map<String, dynamic> toJson() => _$DocumentAnalysisToJson(this);
}

@JsonSerializable()
class KeySection {
  final String title;
  final double importance;
  final String summary;
  final int slideRecommendation;

  KeySection({
    required this.title,
    required this.importance,
    required this.summary,
    required this.slideRecommendation,
  });

  factory KeySection.fromJson(Map<String, dynamic> json) =>
      _$KeySectionFromJson(json);

  Map<String, dynamic> toJson() => _$KeySectionToJson(this);
}

@JsonSerializable()
class DataPoint {
  final String type;
  final String value;
  final String context;
  final String visualizationSuggestion;

  DataPoint({
    required this.type,
    required this.value,
    required this.context,
    required this.visualizationSuggestion,
  });

  factory DataPoint.fromJson(Map<String, dynamic> json) =>
      _$DataPointFromJson(json);

  Map<String, dynamic> toJson() => _$DataPointToJson(this);
}

class DocumentAnalyzer {
  final GLMClient _glmClient = GLMClient();

  Future<DocumentAnalysis> analyze({
    required String text,
    Map<String, String>? contextHints,
  }) async {
    final prompt = _buildAnalysisPrompt(text, contextHints);

    final schema = {
      'type': 'object',
      'properties': {
        'documentType': {'type': 'string'},
        'mainTheme': {'type': 'string'},
        'keySections': {
          'type': 'array',
          'items': {
            'type': 'object',
            'properties': {
              'title': {'type': 'string'},
              'importance': {'type': 'number'},
              'summary': {'type': 'string'},
              'slideRecommendation': {'type': 'number'},
            },
            'required': ['title', 'importance', 'summary', 'slideRecommendation'],
          },
        },
        'dataPoints': {
          'type': 'array',
          'items': {
            'type': 'object',
            'properties': {
              'type': {'type': 'string'},
              'value': {'type': 'string'},
              'context': {'type': 'string'},
              'visualizationSuggestion': {'type': 'string'},
            },
            'required': ['type', 'value', 'context', 'visualizationSuggestion'],
          },
        },
        'narrativeStructure': {'type': 'string'},
        'audience': {'type': 'string'},
      },
      'required': [
        'documentType',
        'mainTheme',
        'keySections',
        'dataPoints',
        'narrativeStructure',
        'audience',
      ],
    };

    final analysisData = await _glmClient.generateStructured<DocumentAnalysis>(
      prompt: prompt,
      schema: schema,
    );

    final importanceScores = <String, double>{};
    for (final section in analysisData.keySections) {
      importanceScores[section.title] = section.importance;
    }

    return DocumentAnalysis(
      documentType: analysisData.documentType,
      mainTheme: analysisData.mainTheme,
      keySections: analysisData.keySections,
      dataPoints: analysisData.dataPoints,
      narrativeStructure: analysisData.narrativeStructure,
      audience: analysisData.audience,
      importanceScores: importanceScores,
    );
  }

  String _buildAnalysisPrompt(
    String text,
    Map<String, String>? contextHints,
  ) {
    var prompt = '''
你是一位专业的文档分析师。

【任务】
深度分析以下文档，提取关键信息用于生成 PPT 大纲。

【原始文档】
$text

【分析要求】
1. 文档类型：识别文档的性质（商业计划、技术报告、学术研究等）
2. 核心主题：提炼文档的核心主题和主旨
3. 关键章节：列出所有重要章节，并为每个章节评分（1-10）
4. 数据点：提取所有重要数据、数字、统计信息
5. 叙事结构：推荐合适的 PPT 叙事结构
6. 目标受众：推测文档的目标受众

【评分标准】
- importance: 1-10 分
  - 8-10: 极其重要，2-3 页
  - 5-7: 重要，1-2 页
  - 1-4: 次要，可合并或省略

【输出格式（JSON）】
{
  "documentType": "文档类型",
  "mainTheme": "核心主题",
  "keySections": [
    {
      "title": "章节标题",
      "importance": 8.5,
      "summary": "章节摘要（50-100字）",
      "slideRecommendation": 2
    }
  ],
  "dataPoints": [
    {
      "type": "数据类型",
      "value": "数据值",
      "context": "上下文",
      "visualizationSuggestion": "建议的可视化方式"
    }
  ],
  "narrativeStructure": "problem_solution_result|background_analysis_conclusion|introduction_methodology_results_conclusion",
  "audience": "目标受众"
}
''';

    if (contextHints != null && contextHints.isNotEmpty) {
      prompt += '\n\n【上下文提示】\n';
      for (final entry in contextHints.entries) {
        prompt += '${entry.key}: ${entry.value}\n';
      }
    }

    return prompt;
  }
}
