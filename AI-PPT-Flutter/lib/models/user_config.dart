import 'package:json_annotation/json_annotation.dart';
import 'package:hive/hive.dart';

part 'user_config.g.dart';

@HiveType(typeId: 0)
@JsonSerializable()
class UserConfig {
  @HiveField(0)
  final String apiKey;

  @HiveField(1)
  final String baseUrl;

  @HiveField(2)
  final bool cacheEnabled;

  @HiveField(3)
  final bool autoSaveEnabled;

  @HiveField(4)
  final AppTheme theme;

  @HiveField(5)
  final int maxCacheSize;

  UserConfig({
    required this.apiKey,
    required this.baseUrl,
    required this.cacheEnabled,
    required this.autoSaveEnabled,
    required this.theme,
    required this.maxCacheSize,
  });

  factory UserConfig.fromJson(Map<String, dynamic> json) =>
      _$UserConfigFromJson(json);

  Map<String, dynamic> toJson() => _$UserConfigToJson(this);

  static UserConfig get defaultConfig => UserConfig(
        apiKey: '',
        baseUrl: 'https://open.bigmodel.cn/api/paas/v4',
        cacheEnabled: true,
        autoSaveEnabled: true,
        theme: AppTheme.system,
        maxCacheSize: 100,
      );

  UserConfig copyWith({
    String? apiKey,
    String? baseUrl,
    bool? cacheEnabled,
    bool? autoSaveEnabled,
    AppTheme? theme,
    int? maxCacheSize,
  }) {
    return UserConfig(
      apiKey: apiKey ?? this.apiKey,
      baseUrl: baseUrl ?? this.baseUrl,
      cacheEnabled: cacheEnabled ?? this.cacheEnabled,
      autoSaveEnabled: autoSaveEnabled ?? this.autoSaveEnabled,
      theme: theme ?? this.theme,
      maxCacheSize: maxCacheSize ?? this.maxCacheSize,
    );
  }
}

@HiveType(typeId: 1)
enum AppTheme {
  @HiveField(0)
  light,

  @HiveField(1)
  dark,

  @HiveField(2)
  system,
}

extension AppThemeExtension on AppTheme {
  String get displayName {
    switch (this) {
      case AppTheme.light:
        return '浅色';
      case AppTheme.dark:
        return '深色';
      case AppTheme.system:
        return '跟随系统';
    }
  }
}
