import 'dart:convert';
import 'dart:io';
import 'package:path/path.dart' as path;
import 'package:path_provider/path_provider.dart';
import 'package:logger/logger.dart';
import '../models/template_models.dart';
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

  static Future<Directory> getOutputDirectory() async {
    final directory = await getApplicationDocumentsDirectory();
    final pptDir = Directory(path.join(directory.path, 'ai_ppt_pro'));
    if (!await pptDir.exists()) {
      await pptDir.create(recursive: true);
    }
    return pptDir;
  }

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
    final outline = await _outlineGenerator.generateTwoStage(
      text: text,
      analysis: analysis,
      template: styleTemplate,
    );
    _logger.i('Generated outline: ${outline.slides.length} slides');

    progressHandler?.call(0.25);

    // Step 3: Generate slides
    final slides = <GeneratedSlide>[];
    for (var i = 0; i < outline.slides.length; i++) {
      final slide = outline.slides[i];
      final content = '幻灯片内容：${slide.title}';

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
          title: slide.title,
          fileUrl: slideFile,
          isStyleAnchor: i % 3 == 0,
          generatedAt: DateTime.now(),
        ),
      );

      progressHandler?.call(0.25 + (i / outline.slides.length) * 0.5);
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
    final searchResults = await _webSearchEngine.performSearch(topic: topic);
    _logger.i('Search results: ${searchResults.length} items');

    progressHandler?.call(0.15);

    // Step 2: Generate outline
    final analysis = DocumentAnalysis(
      documentType: 'Web Search',
      mainTheme: topic,
      targetAudience: '通用',
      suggestedStructure: 'Introduction, Content, Conclusion',
      keyPoints: [],
    );

    final outline = await _outlineGenerator.generateTwoStage(
      text: topic,
      analysis: analysis,
      template: styleTemplate,
    );
    _logger.i('Generated outline: ${outline.slides.length} slides');

    progressHandler?.call(0.25);

    // Step 3: Generate slides
    final slides = <GeneratedSlide>[];
    for (var i = 0; i < outline.slides.length; i++) {
      final slide = outline.slides[i];
      final content = '幻灯片内容：${slide.title}';

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
          title: slide.title,
          fileUrl: slideFile,
          isStyleAnchor: i % 3 == 0,
          generatedAt: DateTime.now(),
        ),
      );

      progressHandler?.call(0.25 + (i / outline.slides.length) * 0.5);
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
