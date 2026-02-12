import 'package:json_annotation/json_annotation.dart';

part 'ppt_models.g.dart';

@JsonSerializable()
class PPTOutline {
  final String title;
  final String? subtitle;
  final List<SlideData> slides;
  final String? documentType;
  final String? mainTheme;
  final String? targetAudience;

  PPTOutline({
    required this.title,
    this.subtitle,
    required this.slides,
    this.documentType,
    this.mainTheme,
    this.targetAudience,
  });

  factory PPTOutline.fromJson(Map<String, dynamic> json) =>
      _$PPTOutlineFromJson(json);

  Map<String, dynamic> toJson() => _$PPTOutlineToJson(this);
}

@JsonSerializable()
class SlideData {
  final int slideNumber;
  final SlideType slideType;
  final String title;
  final String contentSummary;
  final List<String> keyPoints;
  final Map<String, String> layoutPositions;
  final Map<String, String> visualElements;
  final String emotionalTone;

  SlideData({
    required this.slideNumber,
    required this.slideType,
    required this.title,
    required this.contentSummary,
    required this.keyPoints,
    required this.layoutPositions,
    required this.visualElements,
    required this.emotionalTone,
  });

  factory SlideData.fromJson(Map<String, dynamic> json) =>
      _$SlideDataFromJson(json);

  Map<String, dynamic> toJson() => _$SlideDataToJson(this);
}

enum SlideType {
  title,
  toc,
  content,
  problemSolution,
  dataDashboard,
  timeline,
  comparison,
  caseStudy,
  conclusionCTA,
  transition,
}

extension SlideTypeExtension on SlideType {
  String get value {
    switch (this) {
      case SlideType.title:
        return 'title';
      case SlideType.toc:
        return 'toc';
      case SlideType.content:
        return 'content';
      case SlideType.problemSolution:
        return 'problem_solution';
      case SlideType.dataDashboard:
        return 'data_dashboard';
      case SlideType.timeline:
        return 'timeline';
      case SlideType.comparison:
        return 'comparison';
      case SlideType.caseStudy:
        return 'case_study';
      case SlideType.conclusionCTA:
        return 'conclusion_cta';
      case SlideType.transition:
        return 'transition';
    }
  }

  static SlideType fromString(String value) {
    switch (value) {
      case 'title':
        return SlideType.title;
      case 'toc':
        return SlideType.toc;
      case 'content':
        return SlideType.content;
      case 'problem_solution':
        return SlideType.problemSolution;
      case 'data_dashboard':
        return SlideType.dataDashboard;
      case 'timeline':
        return SlideType.timeline;
      case 'comparison':
        return SlideType.comparison;
      case 'case_study':
        return SlideType.caseStudy;
      case 'conclusion_cta':
        return SlideType.conclusionCTA;
      case 'transition':
        return SlideType.transition;
      default:
        return SlideType.content;
    }
  }
}
