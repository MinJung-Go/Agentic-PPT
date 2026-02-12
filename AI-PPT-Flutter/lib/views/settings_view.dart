import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hive_flutter/hive_flutter.dart';
import '../models/user_config.dart';
import '../services/user_config_manager.dart';

class SettingsView extends ConsumerWidget {
  const SettingsView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final configManager = UserConfigManager();
    final config = configManager.config;

    return Scaffold(
      appBar: AppBar(
        title: const Text('设置'),
      ),
      body: ListView(
        children: [
          // API Configuration
          _buildSectionHeader('API 配置'),
          ListTile(
            title: const Text('API Key'),
            subtitle: Text(
              config.apiKey.isEmpty ? '未配置' : '已配置',
              style: TextStyle(
                color: config.apiKey.isEmpty ? Colors.red : Colors.green,
              ),
            ),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (_) => const APIConfigView(),
                ),
              );
            },
          ),
          const Divider(height: 1),

          // General Settings
          _buildSectionHeader('通用设置'),
          SwitchListTile(
            title: const Text('启用缓存'),
            subtitle: const Text('缓存生成结果，提升加载速度'),
            value: config.cacheEnabled,
            onChanged: (value) {
              configManager.toggleCache(value);
            },
          ),
          SwitchListTile(
            title: const Text('自动保存'),
            subtitle: const Text('自动保存生成的 PPT'),
            value: config.autoSaveEnabled,
            onChanged: (value) {
              configManager.toggleAutoSave(value);
            },
          ),
          const Divider(height: 1),

          // Appearance
          _buildSectionHeader('外观'),
          ListTile(
            title: const Text('主题'),
            subtitle: Text(config.theme.displayName),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (_) => const ThemeSelectionView(),
                ),
              );
            },
          ),
          const Divider(height: 1),

          // Storage
          _buildSectionHeader('存储管理'),
          ListTile(
            title: const Text('清除缓存'),
            subtitle: const Text('释放存储空间'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => _showClearCacheDialog(context),
          ),
          const Divider(height: 1),

          // About
          _buildSectionHeader('关于'),
          ListTile(
            title: const Text('版本'),
            subtitle: const Text('1.0.0'),
          ),
          ListTile(
            title: const Text('用户协议'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              // TODO: Open user agreement
            },
          ),
          ListTile(
            title: const Text('隐私政策'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              // TODO: Open privacy policy
            },
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 24, 16, 8),
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.bold,
          color: Colors.grey,
        ),
      ),
    );
  }

  void _showClearCacheDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('清除缓存'),
        content: const Text('确定要清除所有缓存吗？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              // TODO: Implement cache clearing
              Navigator.of(context).pop();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('缓存已清除')),
              );
            },
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('清除'),
          ),
        ],
      ),
    );
  }
}

// MARK: - API Config View
class APIConfigView extends StatefulWidget {
  const APIConfigView({super.key});

  @override
  State<APIConfigView> createState() => _APIConfigViewState();
}

class _APIConfigViewState extends State<APIConfigView> {
  late TextEditingController _apiKeyController;
  late TextEditingController _baseUrlController;
  bool _isValidating = false;

  @override
  void initState() {
    super.initState();
    final configManager = UserConfigManager();
    final config = configManager.config;
    _apiKeyController = TextEditingController(text: config.apiKey);
    _baseUrlController = TextEditingController(text: config.baseUrl);
  }

  @override
  void dispose() {
    _apiKeyController.dispose();
    _baseUrlController.dispose();
    super.dispose();
  }

  Future<void> _saveConfig() async {
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
        cacheEnabled: UserConfigManager().config.cacheEnabled,
        autoSaveEnabled: UserConfigManager().config.autoSaveEnabled,
        theme: UserConfigManager().config.theme,
        maxCacheSize: UserConfigManager().config.maxCacheSize,
      ));

      if (mounted) {
        Navigator.of(context).pop();
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('配置已保存')),
        );
      }
    } else {
      setState(() {
        _isValidating = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('API Key 无效')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('API 配置'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _apiKeyController,
              decoration: const InputDecoration(
                labelText: 'API Key',
                hintText: '请输入 GLM API Key',
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
                    : _saveConfig,
                child: _isValidating
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('保存'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// MARK: - Theme Selection View
class ThemeSelectionView extends StatefulWidget {
  const ThemeSelectionView({super.key});

  @override
  State<ThemeSelectionView> createState() => _ThemeSelectionViewState();
}

class _ThemeSelectionViewState extends State<ThemeSelectionView> {
  @override
  Widget build(BuildContext context) {
    final configManager = UserConfigManager();
    final currentTheme = configManager.config.theme;

    return Scaffold(
      appBar: AppBar(
        title: const Text('主题'),
      ),
      body: ListView(
        children: AppTheme.values.map((theme) {
          return RadioListTile<AppTheme>(
            title: Text(theme.displayName),
            value: theme,
            groupValue: currentTheme,
            onChanged: (value) {
              if (value != null) {
                configManager.updateTheme(value);
                setState(() {});
              }
            },
          );
        }).toList(),
      ),
    );
  }
}
