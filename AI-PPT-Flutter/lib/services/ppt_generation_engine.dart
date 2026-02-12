import 'dart:io';
import 'package:path/path.dart' as path;
import 'package:path_provider/path_provider.dart';
import 'package:logger/logger.dart';
import '../models/ppt_models.dart';
import '../models/template_models.dart';
import 'glm_client.dart';
import 'document_analyzer.dart';
import 'outline_generator.dart';
import 'web_search_engine.dart';

class GeneratedSlide {
  final int slideNumber;
  final String title;
  final File fileUrl;
  final bool isStyleAnchor;
  final DateTime generatedAt;

  GeneratedSlide({
    required this.slideNumber,
    required this.title,
    required this.fileUrl,
    required this.isStyleAnchor,
    required this.generatedAt,
  });
}

class PPTResult {
  final String title;
  final List<GeneratedSlide> slides;
  final String templateUsed;
  final int totalSlides;
  final DateTime createdAt;

  PPTResult({
    required this.title,
    required this.slides,
    required this.templateUsed,
    required this.totalSlides,
    required this.createdAt,
  });
}

class PPTGenerationEngine {
  final DocumentAnalyzer _documentAnalyzer = DocumentAnalyzer();
  final OutlineGenerator _outlineGenerator = OutlineGenerator();
  final WebSearchEngine _webSearchEngine = WebSearchEngine();
  final Logger _logger = Logger();

  // MARK: - Generate PPT from Text
  Future<PPTResult> generatePPTFromText({
    required String text,
    required PPTTemplate styleTemplate,
    required Directory outputDir,
    void Function(double progress)? progressHandler,
  }) async {
    progressHandler?.call(0.05);

    // Step 1: Analyze document
    final analysis = await _documentAnalyzer.analyzeDocument(text);
    _logger.i('Document analysis: $analysis');

    progressHandler?.call(0.15);

    // Step 2: Generate outline
    final outline = await _outlineGenerator.generateOutline(
      topic: analysis.mainTheme ?? text,
      depth: 3,
    );
    _logger.i('Generated outline: $outline');

    progressHandler?.call(0.25);

    // Step 3: Generate slides
    final slides = <GeneratedSlide>[];
    for (var i = 0; i < outline['points'].length; i++) {
      final point = outline['points'][i];
      final content = await GLMClient().generateSlideContent(
        title: point['title'] ?? point,
        outline: point.toString(),
        style: styleTemplate.styleHints.join(', '),
      );

      final slideFile = File(
        path.join(
          outputDir.path,
          'slide_${i + 1}.txt',
        ),
      );

      await slideFile.writeAsString(content);

      slides.add(
        GeneratedSlide(
          slideNumber: i + 1,
          title: point['title'] ?? point,
          fileUrl: slideFile,
          isStyleAnchor: i % 3 == 0,
          generatedAt: DateTime.now(),
        ),
      );

      progressHandler?.call(0.25 + (i / outline['points'].length) * 0.5);
    }

    // Step 4: Generate index
    final indexFile = File(
      path.join(outputDir.path, 'index.json'),
    );
    final indexData = {
      'title': analysis.mainTheme ?? text,
      'slides': slides.map((s) => {
        'number': s.slideNumber,
        'title': s.title,
        'file': path.basename(s.fileUrl.path),
        'generatedAt': s.generatedAt.toIso8601String(),
      }).toList(),
      'template': styleTemplate.name,
      'createdAt': DateTime.now().toIso8601String(),
    };
    await indexFile.writeAsString(jsonEncode(indexData));

    progressHandler?.call(1.0);

    return PPTResult(
      title: analysis.mainTheme ?? text,
      slides: slides,
      templateUsed: styleTemplate.name,
      totalSlides: slides.length,
      createdAt: DateTime.now(),
    );
  }

  // MARK: - Generate PPT from Web Search
  Future<PPTResult> generatePPTFromWebSearch({
    required String topic,
    required PPTTemplate styleTemplate,
    required Directory outputDir,
    void Function(double progress)? progressHandler,
  }) async {
    progressHandler?.call(0.05);

    // Step 1: Search for content
    final searchResults = await _webSearchEngine.search(topic);
    _logger.i('Search results: ${searchResults.length} items');

    progressHandler?.call(0.15);

    // Step 2: Generate outline
    final outline = await _outlineGenerator.generateOutline(
      topic: topic,
      depth: 3,
    );
    _logger.i('Generated outline: $outline');

    progressHandler?.call(0.25);

    // Step 3: Generate slides
    final slides = <GeneratedSlide>[];
    for (var i = 0; i < outline['points'].length; i++) {
      final point = outline['points'][i];
      final content = await GLMClient().generateSlideContent(
        title: point['title'] ?? point,
        outline: point.toString(),
        style: styleTemplate.styleHints.join(', '),
      );

      final slideFile = File(
        path.join(
          outputDir.path,
          'slide_${i + 1}.txt',
        ),
      );

      await slideFile.writeAsString(content);

      slides.add(
        GeneratedSlide(
          slideNumber: i + 1,
          title: point['title'] ?? point,
          fileUrl: slideFile,
          isStyleAnchor: i % 3 == 0,
          generatedAt: DateTime.now(),
        ),
      );

      progressHandler?.call(0.25 + (i / outline['points'].length) * 0.5);
    }

    // Step 4: Generate index
    final indexFile = File(
      path.join(outputDir.path, 'index.json'),
    );
    final indexData = {
      'title': topic,
      'slides': slides.map((s) => {
        'number': s.slideNumber,
        'title': s.title,
        'file': path.basename(s.fileUrl.path),
        'generatedAt': s.generatedAt.toIso8601String(),
      }).toList(),
      'template': styleTemplate.name,
      'createdAt': DateTime.now().toIso8601String(),
    };
    await indexFile.writeAsString(jsonEncode(indexData));

    progressHandler?.call(1.0);

    return PPTResult(
      title: topic,
      slides: slides,
      templateUsed: styleTemplate.name,
      totalSlides: slides.length,
      createdAt: DateTime.now(),
    );
  }
}
