import 'package:json_annotation/json_annotation.dart';

part 'document_analyzer.g.dart';

@JsonSerializable()
class DocumentAnalysis {
  final String? documentType;
  final String? mainTheme;
  final String? targetAudience;
  final String? suggestedStructure;
  final List<String>? keyPoints;

  DocumentAnalysis({
    this.documentType,
    this.mainTheme,
    this.targetAudience,
    this.suggestedStructure,
    this.keyPoints,
  });

  factory DocumentAnalysis.fromJson(Map<String, dynamic> json) =>
      _$DocumentAnalysisFromJson(json);

  Map<String, dynamic> toJson() => _$DocumentAnalysisToJson(this);
}
