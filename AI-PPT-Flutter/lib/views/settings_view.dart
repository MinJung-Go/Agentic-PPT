import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
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
            title: const Text('缓存大小'),
            subtitle: const Text('查看和管理缓存'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              // TODO: Implement cache management
            },
          ),
          ListTile(
            title: const Text('清除缓存'),
            subtitle: const Text('删除所有缓存数据'),
            trailing: const Icon(Icons.delete_outline),
            onTap: () async {
              final confirmed = await showDialog<bool>(
                context: context,
                builder: (context) => AlertDialog(
                  title: const Text('确认清除'),
                  content: const Text('确定要清除所有缓存吗？'),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.of(context).pop(false),
                      child: const Text('取消'),
                    ),
                    TextButton(
                      onPressed: () => Navigator.of(context).pop(true),
                      child: const Text('清除'),
                    ),
                  ],
                ),
              );

              if (confirmed == true) {
                configManager.clearConfig();
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('缓存已清除')),
                );
              }
            },
          ),
          const Divider(height: 1),

          // About
          _buildSectionHeader('关于'),
          ListTile(
            title: const Text('版本'),
            subtitle: const Text('1.0.0'),
            trailing: const Icon(Icons.info_outline),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
      child: Text(
        title,
        style: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.bold,
          color: Colors.grey.shade600,
        ),
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
  final TextEditingController _apiKeyController = TextEditingController();
  final TextEditingController _baseUrlController = TextEditingController();

  @override
  void initState() {
    super.initState();
    final configManager = UserConfigManager();
    final config = configManager.config;
    _apiKeyController.text = config.apiKey;
    _baseUrlController.text = config.baseUrl;
  }

  @override
  void dispose() {
    _apiKeyController.dispose();
    _baseUrlController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('API 配置'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          TextField(
            controller: _apiKeyController,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              labelText: 'API Key',
              hintText: '输入您的 API Key',
            ),
            obscureText: true,
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _baseUrlController,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              labelText: 'Base URL',
              hintText: 'https://open.bigmodel.cn/api/paas/v4',
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: () async {
              final configManager = UserConfigManager();
              await configManager.updateAPIKey(_apiKeyController.text);
              await configManager.updateBaseUrl(_baseUrlController.text);
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('配置已保存')),
                );
                Navigator.of(context).pop();
              }
            },
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 16),
            ),
            child: const Text('保存'),
          ),
        ],
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
      body: RadioGroup<AppTheme>(
        value: currentTheme,
        onChanged: (value) {
          if (value != null) {
            configManager.updateTheme(value);
            setState(() {});
          }
        },
        child: ListView(
          children: AppTheme.values.map((theme) {
            return ListTile(
              title: Text(theme.displayName),
              leading: Radio<AppTheme>(
                value: theme,
              ),
              onTap: () {
                configManager.updateTheme(theme);
                setState(() {});
              },
            );
          }).toList(),
        ),
      ),
    );
  }
}
