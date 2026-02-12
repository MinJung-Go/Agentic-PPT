import 'package:json_annotation/json_annotation.dart';
import 'package:logger/logger.dart';

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

/// Document analyzer service
class DocumentAnalyzer {
  final Logger _logger = Logger();

  /// Analyze document structure and content
  Future<DocumentAnalysis> analyzeDocument(String text) async {
    try {
      _logger.i('Analyzing document...');

      // For now, return a basic analysis
      // TODO: Implement proper AI-based analysis
      await Future.delayed(const Duration(milliseconds: 500));

      return DocumentAnalysis(
        documentType: '通用文档',
        mainTheme: _extractMainTheme(text),
        targetAudience: '通用',
        suggestedStructure: 'Introduction, Content, Conclusion',
        keyPoints: _extractKeyPoints(text),
      );
    } catch (e) {
      _logger.e('Document analysis error: $e');
      rethrow;
    }
  }

  String _extractMainTheme(String text) {
    // Simple extraction: take the first sentence
    final sentences = text.split(RegExp(r'[。！？.!?]'));
    if (sentences.isNotEmpty) {
      return sentences.first.trim();
    }
    return '未命名主题';
  }

  List<String> _extractKeyPoints(String text) {
    // Simple extraction: split by newlines
    final lines = text.split('\n')
        .map((line) => line.trim())
        .where((line) => line.isNotEmpty)
        .take(5)
        .toList();

    if (lines.isEmpty) {
      return ['要点1', '要点2', '要点3'];
    }

    return lines;
  }
}
