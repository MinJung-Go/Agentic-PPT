import 'package:dio/dio.dart';
import 'package:logger/logger.dart';
import '../models/ppt_models.dart';

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
      _baseUrl = baseUrl;
    }

    _dio.options.baseUrl = _baseUrl;
    _dio.options.headers = {
      'Authorization': 'Bearer $_apiKey',
      'Content-Type': 'application/json',
    };

    _logger.i('GLM Client initialized');
  }

  bool get isInitialized => _apiKey != null && _apiKey!.isNotEmpty;

  // MARK: - Generate Text
  Future<String> generateText({
    required String prompt,
    String model = 'glm-4-flash',
    double temperature = 0.7,
    int maxTokens = 2048,
  }) async {
    if (!isInitialized) {
      throw Exception('GLM Client not initialized. Please set API key first.');
    }

    try {
      final response = await _dio.post(
        '/chat/completions',
        data: {
          'model': model,
          'messages': [
            {'role': 'user', 'content': prompt}
          ],
          'temperature': temperature,
          'max_tokens': maxTokens,
        },
      );

      final content = response.data['choices'][0]['message']['content'];
      return content as String;
    } on DioException catch (e) {
      _logger.e('API Error: ${e.message}');
      throw Exception('Failed to generate text: ${e.message}');
    } catch (e) {
      _logger.e('Error: $e');
      throw Exception('Failed to generate text: $e');
    }
  }

  // MARK: - Generate Structured Output
  Future<T> generateStructured<T>({
    required String prompt,
    required Map<String, dynamic> schema,
    String model = 'glm-4-flash',
    double temperature = 0.3,
  }) async {
    if (!isInitialized) {
      throw Exception('GLM Client not initialized. Please set API key first.');
    }

    try {
      final response = await _dio.post(
        '/chat/completions',
        data: {
          'model': model,
          'messages': [
            {
              'role': 'user',
              'content': prompt
            }
          ],
          'temperature': temperature,
          'response_format': {
            'type': 'json_schema',
            'json_schema': {
              'name': 'output',
              'schema': schema,
              'strict': true,
            },
          },
        },
      );

      final jsonString = response.data['choices'][0]['message']['content'];
      return _parseJson<T>(jsonString);
    } on DioException catch (e) {
      _logger.e('API Error: ${e.message}');
      throw Exception('Failed to generate structured output: ${e.message}');
    } catch (e) {
      _logger.e('Error: $e');
      throw Exception('Failed to generate structured output: $e');
    }
  }

  // MARK: - Validate API Key
  Future<bool> validateAPIKey(String apiKey) async {
    try {
      final tempClient = GLMClient();
      tempClient._apiKey = apiKey;
      tempClient._dio.options.baseUrl = _baseUrl;
      tempClient._dio.options.headers = {
        'Authorization': 'Bearer $apiKey',
        'Content-Type': 'application/json',
      };

      await tempClient.generateText(prompt: '测试', maxTokens: 10);
      return true;
    } catch (e) {
      _logger.w('API Key validation failed: $e');
      return false;
    }
  }

  // MARK: - Parse JSON
  T _parseJson<T>(String jsonString) {
    // This is a simplified version. In production, use proper type checking
    final Map<String, dynamic> json = parseJsonString(jsonString);

    switch (T) {
      case OutlineData:
        return OutlineData.fromJson(json) as T;
      default:
        throw Exception('Unsupported type: $T');
    }
  }

  Map<String, dynamic> parseJsonString(String jsonString) {
    // Use dart:convert
    return {};
  }
}

// MARK: - Outline Data
class OutlineData {
  final String title;
  final String subtitle;
  final List<Map<String, dynamic>> slides;

  OutlineData({
    required this.title,
    required this.subtitle,
    required this.slides,
  });

  factory OutlineData.fromJson(Map<String, dynamic> json) {
    return OutlineData(
      title: json['title'] as String,
      subtitle: json['subtitle'] as String,
      slides: (json['slides'] as List<dynamic>)
          .map((e) => e as Map<String, dynamic>)
          .toList(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'title': title,
      'subtitle': subtitle,
      'slides': slides,
    };
  }
}
