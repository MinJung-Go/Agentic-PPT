import 'package:hive_flutter/hive_flutter.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user_config.dart';

class UserConfigManager {
  static final UserConfigManager _instance = UserConfigManager._internal();
  factory UserConfigManager() => _instance;
  UserConfigManager._internal();

  static const String _configBoxName = 'userConfig';
  static const String _apiKeyKey = 'apiKey';
  static const String _baseUrlKey = 'baseUrl';
  static const String _cacheEnabledKey = 'cacheEnabled';
  static const String _autoSaveEnabledKey = 'autoSaveEnabled';
  static const String _themeKey = 'theme';
  static const String _maxCacheSizeKey = 'maxCacheSize';

  late Box<UserConfig> _configBox;
  UserConfig? _cachedConfig;

  // MARK: - Initialize
  Future<void> initialize() async {
    await Hive.initFlutter();
    Hive.registerAdapter(UserConfigAdapter());
    Hive.registerAdapter(AppThemeAdapter());

    _configBox = await Hive.openBox<UserConfig>(_configBoxName);
  }

  // MARK: - Get Config
  UserConfig get config {
    if (_cachedConfig != null) {
      return _cachedConfig!;
    }

    final storedConfig = _configBox.get('config');
    if (storedConfig != null) {
      _cachedConfig = storedConfig;
      return storedConfig;
    }

    _cachedConfig = UserConfig.defaultConfig;
    return _cachedConfig!;
  }

  // MARK: - Save Config
  Future<void> saveConfig(UserConfig config) async {
    await _configBox.put('config', config);
    _cachedConfig = config;
  }

  // MARK: - Update API Key
  Future<void> updateAPIKey(String apiKey) async {
    final currentConfig = config;
    final updatedConfig = currentConfig.copyWith(apiKey: apiKey);
    await saveConfig(updatedConfig);
  }

  // MARK: - Update Base URL
  Future<void> updateBaseUrl(String baseUrl) async {
    final currentConfig = config;
    final updatedConfig = currentConfig.copyWith(baseUrl: baseUrl);
    await saveConfig(updatedConfig);
  }

  // MARK: - Update Theme
  Future<void> updateTheme(AppTheme theme) async {
    final currentConfig = config;
    final updatedConfig = currentConfig.copyWith(theme: theme);
    await saveConfig(updatedConfig);
  }

  // MARK: - Toggle Cache
  Future<void> toggleCache(bool enabled) async {
    final currentConfig = config;
    final updatedConfig = currentConfig.copyWith(cacheEnabled: enabled);
    await saveConfig(updatedConfig);
  }

  // MARK: - Toggle Auto Save
  Future<void> toggleAutoSave(bool enabled) async {
    final currentConfig = config;
    final updatedConfig = currentConfig.copyWith(autoSaveEnabled: enabled);
    await saveConfig(updatedConfig);
  }

  // MARK: - Validate API Key
  Future<bool> validateAPIKey(String apiKey) async {
    // TODO: Implement actual API key validation
    // For now, just check if it's not empty
    return apiKey.isNotEmpty;
  }

  // MARK: - Clear Config
  Future<void> clearConfig() async {
    await _configBox.clear();
    _cachedConfig = null;
  }

  // MARK: - Migration from SharedPreferences
  Future<void> migrateFromSharedPreferences() async {
    try {
      final prefs = await SharedPreferences.getInstance();

      final apiKey = prefs.getString(_apiKeyKey);
      final baseUrl = prefs.getString(_baseUrlKey);
      final cacheEnabled = prefs.getBool(_cacheEnabledKey);
      final autoSaveEnabled = prefs.getBool(_autoSaveEnabledKey);
      final theme = prefs.getString(_themeKey);
      final maxCacheSize = prefs.getInt(_maxCacheSizeKey);

      if (apiKey != null && apiKey.isNotEmpty) {
        await saveConfig(UserConfig(
          apiKey: apiKey,
          baseUrl: baseUrl ?? 'https://open.bigmodel.cn/api/paas/v4',
          cacheEnabled: cacheEnabled ?? true,
          autoSaveEnabled: autoSaveEnabled ?? true,
          theme: AppTheme.values.firstWhere(
            (t) => t.name == theme,
            orElse: () => AppTheme.system,
          ),
          maxCacheSize: maxCacheSize ?? 100,
        ));

        // Clear old preferences
        await prefs.clear();
      }
    } catch (e) {
      // Migration failed, but that's okay
      print('Migration failed: $e');
    }
  }
}

// MARK: - Hive Adapters
class UserConfigAdapter extends TypeAdapter<UserConfig> {
  @override
  final typeId = 0;

  @override
  UserConfig read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return UserConfig(
      apiKey: fields[0] as String,
      baseUrl: fields[1] as String,
      cacheEnabled: fields[2] as bool,
      autoSaveEnabled: fields[3] as bool,
      theme: fields[4] as AppTheme,
      maxCacheSize: fields[5] as int,
    );
  }

  @override
  void write(BinaryWriter writer, UserConfig obj) {
    writer.writeByte(6);
    writer.writeByte(0);
    writer.write(obj.apiKey);
    writer.writeByte(1);
    writer.write(obj.baseUrl);
    writer.writeByte(2);
    writer.write(obj.cacheEnabled);
    writer.writeByte(3);
    writer.write(obj.autoSaveEnabled);
    writer.writeByte(4);
    writer.write(obj.theme);
    writer.writeByte(5);
    writer.write(obj.maxCacheSize);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      other is UserConfigAdapter && other.typeId == typeId;
}

class AppThemeAdapter extends TypeAdapter<AppTheme> {
  @override
  final typeId = 1;

  @override
  AppTheme read(BinaryReader reader) {
    return AppTheme.values[reader.readByte()];
  }

  @override
  void write(BinaryWriter writer, AppTheme obj) {
    writer.writeByte(obj.index);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      other is AppThemeAdapter && other.typeId == typeId;
}
