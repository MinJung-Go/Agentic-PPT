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
  final GLMClient _glmClient = GLMClient();
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
    _logger.i('Analyzing document...');
    final analysis = await _documentAnalyzer.analyze(text: text);
    progressHandler?.call(0.15);

    // Step 2: Generate outline (two-stage)
    _logger.i('Generating outline...');
    final outline = await _outlineGenerator.generateTwoStage(
      text: text,
      analysis: analysis,
      template: styleTemplate,
    );
    progressHandler?.call(0.25);

    // Step 3: Generate slides
    _logger.i('Generating slides...');
    final slides = await _generateSlides(
      outline: outline,
      template: styleTemplate,
      outputDir: outputDir,
      progressHandler: progressHandler,
    );

    progressHandler?.call(1.0);

    return PPTResult(
      title: outline.title,
      slides: slides,
      templateUsed: styleTemplate.name,
      totalSlides: slides.length,
      createdAt: DateTime.now(),
    );
  }

  // MARK: - Generate PPT from Topic
  Future<PPTResult> generatePPTFromTopic({
    required String topic,
    required PPTTemplate styleTemplate,
    required Directory outputDir,
    void Function(double progress)? progressHandler,
  }) async {
    progressHandler?.call(0.05);

    // Step 1: Search and generate research report
    _logger.i('Searching for information...');
    final researchData = await _webSearchEngine.generateReport(topic: topic);
    progressHandler?.call(0.25);

    // Step 2: Generate PPT from research text
    final pptResult = await generatePPTFromText(
      text: researchData.content,
      styleTemplate: styleTemplate,
      outputDir: outputDir,
      progressHandler: (progress) {
        progressHandler?.call(0.25 + (progress * 0.75));
      },
    );

    return PPTResult(
      title: pptResult.title,
      slides: pptResult.slides,
      templateUsed: styleTemplate.name,
      totalSlides: pptResult.totalSlides,
      createdAt: DateTime.now(),
    );
  }

  // MARK: - Generate Slides
  Future<List<GeneratedSlide>> _generateSlides({
    required PPTOutline outline,
    required PPTTemplate template,
    required Directory outputDir,
    void Function(double progress)? progressHandler,
  }) async {
    final List<GeneratedSlide> slides = [];

    for (int i = 0; i < outline.slides.length; i++) {
      final slideData = outline.slides[i];
      final slideNumber = i + 1;

      _logger.i('Generating slide $slideNumber...');

      final fileName = 'slide_${slideNumber.toString().padLeft(2, '0')}.txt';
      final filePath = path.join(outputDir.path, fileName);
      final file = File(filePath);

      final content = _generateSlideContent(
        slideData: slideData,
        styleHints: template.styleHints,
      );

      await file.writeAsString(content);

      final generatedSlide = GeneratedSlide(
        slideNumber: slideNumber,
        title: slideData.title,
        fileUrl: file,
        isStyleAnchor: slideNumber == 1,
        generatedAt: DateTime.now(),
      );

      slides.add(generatedSlide);

      final progress = (i + 1) / outline.slides.length;
      progressHandler?.call(progress);
    }

    return slides;
  }

  // MARK: - Generate Slide Content
  String _generateSlideContent({
    required SlideData slideData,
    required StyleHints styleHints,
  }) {
    return '''
================================================================================
幻灯片 #${slideData.slideNumber}: ${slideData.title}
================================================================================

【类型】${slideData.slideType.value}
【情感基调】${slideData.emotionalTone}

【内容摘要】
${slideData.contentSummary}

【关键要点】
${slideData.keyPoints.asMap().entries.map((e) => '${e.key + 1}. ${e.value}').join('\n')}

【布局位置】
${slideData.layoutPositions.entries.map((e) => '${e.key}: ${e.value}').join('\n')}

【视觉元素】
${slideData.visualElements.entries.map((e) => '${e.key}: ${e.value}').join('\n')}

【风格提示】
- 背景: ${styleHints.background}
- 字体: ${styleHints.typography}
- 布局: ${styleHints.layout}
- 配色: ${styleHints.colors.join(', ')}
- 视觉: ${styleHints.visual}

================================================================================
Generated by AI PPT Pro (Flutter Version)
================================================================================
''';
  }

  // MARK: - Get Output Directory
  static Future<Directory> getOutputDirectory() async {
    final directory = await getApplicationDocumentsDirectory();
    final outputDir = Directory(path.join(directory.path, 'GeneratedPPTs'));

    if (!await outputDir.exists()) {
      await outputDir.create(recursive: true);
    }

    return outputDir;
  }
}
