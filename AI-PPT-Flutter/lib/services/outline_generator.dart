import 'package:json_annotation/json_annotation.dart';
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
  // MARK: - Generate Two-Stage Outline
  Future<PPTOutline> generateTwoStage({
    required String text,
    required DocumentAnalysis analysis,
    required PPTTemplate template,
  }) async {
    // For now, return a simple outline structure
    // TODO: Implement proper AI-based outline generation
    return PPTOutline(
      title: analysis.mainTheme ?? '未命名 PPT',
      subtitle: template.name,
      slides: [
        SlideData(
          slideNumber: 1,
          slideType: SlideType.title,
          title: '介绍',
          contentSummary: '本 PPT 的介绍部分',
          keyPoints: ['要点1', '要点2', '要点3'],
          layoutPositions: {},
          visualElements: {},
          emotionalTone: 'professional',
        ),
        SlideData(
          slideNumber: 2,
          slideType: SlideType.content,
          title: '核心内容',
          contentSummary: 'PPT 的核心内容部分',
          keyPoints: (analysis.keyPoints ?? ['要点1']).take(3).toList(),
          layoutPositions: {},
          visualElements: {},
          emotionalTone: 'professional',
        ),
        SlideData(
          slideNumber: 3,
          slideType: SlideType.conclusionCTA,
          title: '总结',
          contentSummary: 'PPT 的总结部分',
          keyPoints: ['要点1', '要点2'],
          layoutPositions: {},
          visualElements: {},
          emotionalTone: 'optimistic',
        ),
      ],
      documentType: analysis.documentType,
      mainTheme: analysis.mainTheme,
      targetAudience: analysis.targetAudience,
    );
  }
}
