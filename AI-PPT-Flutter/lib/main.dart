import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'models/user_config.dart';
import 'services/user_config_manager.dart';
import 'services/glm_client.dart';
import 'views/main_view.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Load environment variables
  await dotenv.load(fileName: '.env');

  // Initialize Hive
  await Hive.initFlutter();
  Hive.registerAdapter(UserConfigAdapter());
  Hive.registerAdapter(AppThemeAdapter());

  // Initialize services
  await UserConfigManager().initialize();

  // Initialize GLM Client
  final configManager = UserConfigManager();
  if (configManager.config.apiKey.isNotEmpty) {
    GLMClient().initialize(
      apiKey: configManager.config.apiKey,
      baseUrl: configManager.config.baseUrl,
    );
  }

  runApp(
    ProviderScope(
      child: const MyApp(),
    ),
  );
}

class MyApp extends ConsumerWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final configManager = UserConfigManager();
    final config = configManager.config;

    final themeMode = config.theme == AppTheme.system
        ? ThemeMode.system
        : config.theme == AppTheme.dark
            ? ThemeMode.dark
            : ThemeMode.light;

    return MaterialApp(
      title: 'AI PPT Pro',
      debugShowCheckedModeBanner: false,
      theme: _lightTheme,
      darkTheme: _darkTheme,
      themeMode: themeMode,
      home: config.apiKey.isEmpty
          ? const ConfigurationView()
          : const MainView(),
    );
  }

  static final ThemeData _lightTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    colorScheme: ColorScheme.fromSeed(
      seedColor: Colors.blue,
      brightness: Brightness.light,
    ),
    fontFamily: 'GoogleSans',
    appBarTheme: const AppBarTheme(
      centerTitle: false,
      elevation: 0,
    ),
    cardTheme: CardTheme(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
    ),
  );

  static final ThemeData _darkTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    colorScheme: ColorScheme.fromSeed(
      seedColor: Colors.blue,
      brightness: Brightness.dark,
    ),
    fontFamily: 'GoogleSans',
    appBarTheme: const AppBarTheme(
      centerTitle: false,
      elevation: 0,
    ),
    cardTheme: CardTheme(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
    ),
  );
}

// MARK: - Configuration View
class ConfigurationView extends ConsumerStatefulWidget {
  const ConfigurationView({super.key});

  @override
  ConsumerState<ConfigurationView> createState() => _ConfigurationViewState();
}

class _ConfigurationViewState extends ConsumerState<ConfigurationView> {
  final _apiKeyController = TextEditingController();
  final _baseUrlController = TextEditingController();
  bool _isValidating = false;
  bool _showSuccess = false;

  @override
  void initState() {
    super.initState();
    _loadConfig();
  }

  Future<void> _loadConfig() async {
    final configManager = UserConfigManager();
    final config = configManager.config;
    _apiKeyController.text = config.apiKey;
    _baseUrlController.text = config.baseUrl;
  }

  Future<void> _saveConfiguration() async {
    setState(() {
      _isValidating = true;
    });

    final apiKey = _apiKeyController.text.trim();
    final baseUrl = _baseUrlController.text.trim();

    final isValid = await UserConfigManager().validateAPIKey(apiKey);

    if (isValid) {
      await UserConfigManager().saveConfig(UserConfig(
        apiKey: apiKey,
        baseUrl: baseUrl,
        cacheEnabled: true,
        autoSaveEnabled: true,
        theme: AppTheme.system,
        maxCacheSize: 100,
      ));

      GLMClient().initialize(apiKey: apiKey, baseUrl: baseUrl);

      setState(() {
        _isValidating = false;
        _showSuccess = true;
      });

      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const MainView()),
        );
      }
    } else {
      setState(() {
        _isValidating = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('API Key 无效，请检查后重试')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.insert_drive_file_outlined,
                size: 80,
                color: Colors.blue,
              ),
              const SizedBox(height: 20),
              Text(
                'AI PPT Pro',
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: 8),
              Text(
                '智能 PPT 生成应用',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: Colors.grey[600],
                    ),
              ),
              const SizedBox(height: 40),
              TextField(
                controller: _apiKeyController,
                decoration: const InputDecoration(
                  labelText: 'GLM API Key',
                  hintText: '请输入 API Key',
                  border: OutlineInputBorder(),
                ),
                obscureText: true,
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _baseUrlController,
                decoration: const InputDecoration(
                  labelText: 'Base URL (可选)',
                  hintText: 'https://open.bigmodel.cn/api/paas/v4',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _isValidating || _apiKeyController.text.isEmpty
                      ? null
                      : _saveConfiguration,
                  child: _isValidating
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('开始使用'),
                ),
              ),
              const SizedBox(height: 16),
              Text(
                '获取 API Key: https://open.bigmodel.cn/',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.grey[600],
                    ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _apiKeyController.dispose();
    _baseUrlController.dispose();
    super.dispose();
  }
}
