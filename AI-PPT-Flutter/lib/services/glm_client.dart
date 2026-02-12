import 'package:dio/dio.dart';
import 'package:logger/logger.dart';

class GLMClient {
  static final GLMClient _instance = GLMClient._internal();
  factory GLMClient() => _instance;
  GLMClient._internal();

  final Dio _dio = Dio();
  final Logger _logger = Logger();
  String? _apiKey;
  String _baseUrl = 'https://open.bigmodel.cn/api/paas/v4';

  void initialize({required String apiKey, String? baseUrl}) {
    _apiKey = apiKey;
    if (baseUrl != null) {
      _baseUrl = baseUrl!;
    }
  }

  Future<Map<String, dynamic>> generateOutline({
    required String topic,
    int depth = 3,
    int sectionsPerLevel = 3,
  }) async {
    if (_apiKey == null || _apiKey!.isEmpty) {
      throw Exception('API Key not initialized');
    }

    final prompt = '''
    作为一个专业的PPT内容生成助手，请为以下主题生成一个详细的PPT大纲。

    主题：$topic

    要求：
    1. 大纲深度：$depth 层
    2. 每层节数：$sectionsPerLevel 个
    3. 内容要符合PPT展示的逻辑
    4. 每个部分应该有明确的标题和要点
    5. 返回JSON格式，包含title和points（要点列表）
    6. points每个点控制在30字以内

    示例格式：
    {
      "title": "介绍",
      "points": ["要点1", "要点2", "要点3"]
    }
    ''';

    try {
      final response = await _dio.post(
        '$_baseUrl/chat/completions',
        options: Options(
          headers: {
            'Authorization': 'Bearer $_apiKey',
            'Content-Type': 'application/json',
          },
        ),
        data: {
          'model': 'glm-4',
          'messages': [
            {
              'role': 'user',
              'content': prompt,
            }
          ],
        },
      );

      _logger.i('GLM API response: ${response.statusCode}');

      final content = response.data['choices'][0]['message']['content'];

      // Parse JSON from response
      final jsonMatch = RegExp(r'\{[\s\S]*\}').firstMatch(content);
      if (jsonMatch != null) {
        return jsonDecode(jsonMatch.group(0)!) as Map<String, dynamic>;
      }

      // Fallback: return basic structure
      return {
        'title': topic,
        'points': [content],
      };
    } catch (e) {
      _logger.e('GLM API error: $e');
      rethrow;
    }
  }

  Future<String> generateSlideContent({
    required String title,
    required String outline,
    String? style,
  }) async {
    if (_apiKey == null || _apiKey!.isEmpty) {
      throw Exception('API Key not initialized');
    }

    final stylePrompt = style != null ? '\n风格要求：$style' : '';

    final prompt = '''
    作为一个专业的PPT内容生成助手，请为以下幻灯片生成详细内容。

    标题：$title
    大纲：$outline
    $stylePrompt

    要求：
    1. 内容要简洁明了
    2. 每页幻灯片控制在100-150字
    3. 返回纯文本格式
    4. 适合展示和演讲

    生成内容：
    ''';

    try {
      final response = await _dio.post(
        '$_baseUrl/chat/completions',
        options: Options(
          headers: {
            'Authorization': 'Bearer $_apiKey',
            'Content-Type': 'application/json',
          },
        ),
        data: {
          'model': 'glm-4',
          'messages': [
            {
              'role': 'user',
              'content': prompt,
            }
          ],
        },
      );

      _logger.i('GLM API response: ${response.statusCode}');

      return response.data['choices'][0]['message']['content'];
    } catch (e) {
      _logger.e('GLM API error: $e');
      rethrow;
    }
  }

  Future<String> generateWebSearchQuery({
    required String topic,
    String? context,
  }) async {
    if (_apiKey == null || _apiKey!.isEmpty) {
      throw Exception('API Key not initialized');
    }

    final contextPrompt = context != null ? '\n上下文：$context' : '';

    final prompt = '''
    请根据以下主题，生成一个精准的网页搜索查询。

    主题：$topic
    $contextPrompt

    要求：
    1. 查询要精准，能找到相关信息
    2. 关键词要相关
    3. 返回纯文本格式，只返回查询字符串
    4. 不要添加任何解释

    搜索查询：
    ''';

    try {
      final response = await _dio.post(
        '$_baseUrl/chat/completions',
        options: Options(
          headers: {
            'Authorization': 'Bearer $_apiKey',
            'Content-Type': 'application/json',
          },
        ),
        data: {
          'model': 'glm-4',
          'messages': [
            {
              'role': 'user',
              'content': prompt,
            }
          ],
        },
      );

      return response.data['choices'][0]['message']['content'].trim();
    } catch (e) {
      _logger.e('GLM API error: $e');
      rethrow;
    }
  }
}
