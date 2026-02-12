import 'package:logger/logger.dart';
import 'glm_client.dart';

class SearchResult {
  final String title;
  final String url;
  final String snippet;
  final DateTime? date;

  SearchResult({
    required this.title,
    required this.url,
    required this.snippet,
    this.date,
  });
}

class ResearchData {
  final String topic;
  final List<SearchResult> searchResults;
  final String content;
  final DateTime generatedAt;

  ResearchData({
    required this.topic,
    required this.searchResults,
    required this.content,
    required this.generatedAt,
  });
}

class WebSearchEngine {
  final GLMClient _glmClient = GLMClient();
  final Logger _logger = Logger();

  // MARK: - Perform Search
  Future<List<SearchResult>> performSearch({
    required String topic,
    int maxResults = 10,
  }) async {
    // TODO: Implement actual web search
    // Options:
    // 1. Bing Search API (recommended)
    // 2. Google Custom Search API
    // 3. DuckDuckGo Instant Answer API (free, limited)

    _logger.i('Searching for: $topic');

    // For now, return mock data
    // In production, integrate with real search API

    return List.generate(maxResults, (index) => SearchResult(
          title: '搜索结果 ${index + 1}',
          url: 'https://example.com/result/${index + 1}',
          snippet: '这是搜索结果 ${index + 1} 的摘要',
          date: DateTime.now(),
        ));
  }

  // MARK: - Generate Research Report
  Future<ResearchData> generateReport({
    required String topic,
  }) async {
    _logger.i('Generating research report for: $topic');

    // Step 1: Perform search
    final searchResults = await performSearch(topic: topic);
    _logger.i('Found ${searchResults.length} search results');

    // Step 2: Extract content from search results
    final contents = <String>[];
    for (final result in searchResults) {
      try {
        final content = await extractContent(result.url);
        contents.add(content);
      } catch (e) {
        _logger.w('Failed to extract content from ${result.url}: $e');
      }
    }

    // Step 3: Generate research report using GLM
    final combinedContent = contents.join('\n\n---\n\n');
    final report = await _glmClient.generateSlideContent(
      title: topic,
      outline: combinedContent,
      style: 'Research Report',
    );

    return ResearchData(
      topic: topic,
      searchResults: searchResults,
      content: report,
      generatedAt: DateTime.now(),
    );
  }

  // MARK: - Extract Content from URL
  Future<String> extractContent(String url) async {
    // TODO: Implement web scraping
    // For now, return mock content
    await Future.delayed(const Duration(milliseconds: 100));
    return '这是从 $url 提取的内容';
  }

  // MARK: - Build Research Report Prompt
  String _buildResearchReportPrompt(String topic, String content) {
    return '''
基于以下搜索结果，生成一份关于"$topic"的专业研报文案。

【搜索结果内容】
$content

【要求】
1. 结构清晰：背景、现状、趋势、结论
2. 数据支撑：引用搜索结果中的关键数据
3. 专业表达：使用行业术语，避免口语化
4. 逻辑严密：段落之间有清晰的逻辑关系
5. 适合 PPT：每段内容可以独立成页

【输出格式】
直接输出研报文案，不需要额外说明。

【示例结构】
一、背景介绍
（200-300字，介绍研究背景和意义）

二、市场现状
（300-400字，分析当前市场状况）

三、发展趋势
（300-400字，预测未来发展方向）

四、关键结论
（200-300字，总结核心观点）
''';
  }
}
