import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'services/hive_adapters.dart';
import 'services/user_config_manager.dart';
import 'services/glm_client.dart';
import 'views/main_view.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Register Hive adapters
  await registerAdapters();

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

    final themeMode = config.theme.name == 'system'
        ? ThemeMode.system
        : config.theme.name == 'dark'
            ? ThemeMode.dark
            : ThemeMode.light;

    final lightTheme = ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: Colors.blue,
        brightness: Brightness.light,
      ),
      fontFamily: 'GoogleSans',
      appBarTheme: const AppBarTheme(
        centerTitle: false,
        elevation: 0,
      ),
      cardTheme: const CardThemeData(
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(12)),
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

    final darkTheme = ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: Colors.blue,
        brightness: Brightness.dark,
      ),
      fontFamily: 'GoogleSans',
      appBarTheme: const AppBarTheme(
        centerTitle: false,
        elevation: 0,
      ),
      cardTheme: const CardThemeData(
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(12)),
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

    return MaterialApp(
      title: 'AI PPT Pro',
      theme: lightTheme,
      darkTheme: darkTheme,
      themeMode: themeMode,
      home: const MainView(),
    );
  }
}
