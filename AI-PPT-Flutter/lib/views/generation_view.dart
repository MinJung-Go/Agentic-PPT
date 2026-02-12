import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/template_models.dart';
import '../services/ppt_generation_engine.dart';
import '../services/user_config_manager.dart';
import '../models/ppt_models.dart';

final generationProvider = StateNotifierProvider<GenerationNotifier, GenerationState>((ref) {
  return GenerationNotifier();
});

class GenerationState {
  final int selectedMode; // 0: Text, 1: Web Search
  final String inputText;
  final String topic;
  final PPTTemplate? selectedTemplate;
  final bool isGenerating;
  final double progress;
  final String currentStep;
  final PPTResult? generationResult;
  final String? errorMessage;

  GenerationState({
    this.selectedMode = 0,
    this.inputText = '',
    this.topic = '',
    this.selectedTemplate,
    this.isGenerating = false,
    this.progress = 0.0,
    this.currentStep = '',
    this.generationResult,
    this.errorMessage,
  });

  GenerationState copyWith({
    int? selectedMode,
    String? inputText,
    String? topic,
    PPTTemplate? selectedTemplate,
    bool? isGenerating,
    double? progress,
    String? currentStep,
    PPTResult? generationResult,
    String? errorMessage,
  }) {
    return GenerationState(
      selectedMode: selectedMode ?? this.selectedMode,
      inputText: inputText ?? this.inputText,
      topic: topic ?? this.topic,
      selectedTemplate: selectedTemplate ?? this.selectedTemplate,
      isGenerating: isGenerating ?? this.isGenerating,
      progress: progress ?? this.progress,
      currentStep: currentStep ?? this.currentStep,
      generationResult: generationResult ?? this.generationResult,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }
}

class GenerationNotifier extends StateNotifier<GenerationState> {
  GenerationNotifier() : super(GenerationState()) {
    _init();
  }

  void _init() {
    final templates = TemplateManager.templates;
    state = state.copyWith(selectedTemplate: templates.first);
  }

  void setMode(int mode) {
    state = state.copyWith(selectedMode: mode);
  }

  void setInputText(String text) {
    state = state.copyWith(inputText: text);
  }

  void setTopic(String topic) {
    state = state.copyWith(topic: topic);
  }

  void setSelectedTemplate(PPTTemplate template) {
    state = state.copyWith(selectedTemplate: template);
  }

  Future<void> generatePPT() async {
    final configManager = UserConfigManager();
    if (configManager.config.apiKey.isEmpty) {
      state = state.copyWith(errorMessage: '请先配置 API Key');
      return;
    }

    final template = state.selectedTemplate;
    if (template == null) {
      state = state.copyWith(errorMessage: '请选择模板');
      return;
    }

    state = state.copyWith(
      isGenerating: true,
      progress: 0.0,
      currentStep: '开始生成...',
      errorMessage: null,
    );

    try {
      final engine = PPTGenerationEngine();
      final outputDir = await PPTGenerationEngine.getOutputDirectory();

      PPTResult result;
      if (state.selectedMode == 0) {
        // Generate from text
        result = await engine.generatePPTFromText(
          text: state.inputText,
          styleTemplate: template,
          outputDir: outputDir,
          progressHandler: (progress) {
            state = state.copyWith(
              progress: progress,
              currentStep: '生成中... ${(progress * 100).toInt()}%',
            );
          },
        );
      } else {
        // Generate from topic
        result = await engine.generatePPTFromTopic(
          topic: state.topic,
          styleTemplate: template,
          outputDir: outputDir,
          progressHandler: (progress) {
            state = state.copyWith(
              progress: progress,
              currentStep: '生成中... ${(progress * 100).toInt()}%',
            );
          },
        );
      }

      state = state.copyWith(
        isGenerating: false,
        progress: 1.0,
        currentStep: '生成完成！',
        generationResult: result,
      );
    } catch (e) {
      state = state.copyWith(
        isGenerating: false,
        errorMessage: '生成失败: $e',
      );
    }
  }

  void reset() {
    state = state.copyWith(
      inputText: '',
      topic: '',
      progress: 0.0,
      currentStep: '',
      generationResult: null,
      errorMessage: null,
    );
  }
}

class GenerationView extends ConsumerWidget {
  const GenerationView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(generationProvider);
    final notifier = ref.read(generationProvider.notifier);

    return Scaffold(
      appBar: AppBar(
        title: const Text('生成 PPT'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Mode Selection
            SegmentedButton<int>(
              segments: const [
                ButtonSegment(
                  value: 0,
                  label: Text('文案生成'),
                  icon: Icon(Icons.description),
                ),
                ButtonSegment(
                  value: 1,
                  label: Text('研报生成'),
                  icon: Icon(Icons.search),
                ),
              ],
              selected: {state.selectedMode},
              onSelectionChanged: (Set<int> newSelection) {
                notifier.setMode(newSelection.first);
              },
            ),
            const SizedBox(height: 24),

            // Input Area
            if (state.selectedMode == 0) ...[
              TextField(
                maxLines: 10,
                decoration: const InputDecoration(
                  labelText: '请输入 PPT 文案',
                  hintText: '在这里输入你的文案...',
                  border: OutlineInputBorder(),
                ),
                onChanged: notifier.setInputText,
              ),
            ] else ...[
              TextField(
                decoration: const InputDecoration(
                  labelText: '请输入研究主题',
                  hintText: '例如：AI技术发展趋势',
                  border: OutlineInputBorder(),
                ),
                onChanged: notifier.setTopic,
              ),
            ],
            const SizedBox(height: 24),

            // Template Preview
            if (state.selectedTemplate != null)
              _TemplatePreviewCard(
                template: state.selectedTemplate!,
              ),
            const SizedBox(height: 24),

            // Generation Button
            if (state.isGenerating) ...[
              const LinearProgressIndicator(),
              const SizedBox(height: 8),
              Text(
                state.currentStep,
                style: Theme.of(context).textTheme.bodySmall,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
            ] else if (state.generationResult != null) ...[
              ElevatedButton.icon(
                onPressed: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => PPTResultView(
                        result: state.generationResult!,
                      ),
                    ),
                  );
                },
                icon: const Icon(Icons.visibility),
                label: const Text('查看结果'),
              ),
              const SizedBox(height: 8),
              OutlinedButton.icon(
                onPressed: notifier.reset,
                icon: const Icon(Icons.refresh),
                label: const Text('重新生成'),
              ),
            ] else
              ElevatedButton.icon(
                onPressed: state.selectedTemplate == null
                    ? null
                    : () => notifier.generatePPT(),
                icon: const Icon(Icons.play_arrow),
                label: const Text('生成 PPT'),
              ),

            if (state.errorMessage != null) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.red.shade300),
                ),
                child: Row(
                  children: [
                    Icon(Icons.error_outline, color: Colors.red.shade700),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        state.errorMessage!,
                        style: TextStyle(color: Colors.red.shade700),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _TemplatePreviewCard extends StatelessWidget {
  final PPTTemplate template;

  const _TemplatePreviewCard({required this.template});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: template.previewColors.take(4).map((color) {
                return Container(
                  margin: const EdgeInsets.only(right: 8),
                  width: 20,
                  height: 20,
                  decoration: BoxDecoration(
                    color: _parseColor(color),
                    shape: BoxShape.circle,
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 12),
            Text(
              template.name,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 4),
            Text(
              template.description,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.grey[600],
                  ),
            ),
          ],
        ),
      ),
    );
  }

  Color _parseColor(String hexColor) {
    final hex = hexColor.replaceAll('#', '');
    final colorInt = int.parse('FF$hex', radix: 16);
    return Color(colorInt);
  }
}

// MARK: - PPT Result View
class PPTResultView extends StatelessWidget {
  final PPTResult result;

  const PPTResultView({super.key, required this.result});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('生成结果'),
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: result.slides.length,
        itemBuilder: (context, index) {
          final slide = result.slides[index];
          return Card(
            margin: const EdgeInsets.only(bottom: 16),
            child: ListTile(
              leading: CircleAvatar(
                child: Text('${slide.slideNumber}'),
              ),
              title: Text(slide.title),
              subtitle: Text(
                slide.isStyleAnchor ? '风格锚定页' : '普通页面',
                style: TextStyle(
                  color: slide.isStyleAnchor ? Colors.blue : Colors.grey[600],
                ),
              ),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {
                Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (_) => SlideDetailView(slide: slide),
                  ),
                );
              },
            ),
          );
        },
      ),
    );
  }
}

class SlideDetailView extends StatelessWidget {
  final GeneratedSlide slide;

  const SlideDetailView({super.key, required this.slide});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('幻灯片 #${slide.slideNumber}'),
      ),
      body: FutureBuilder<String>(
        future: slide.fileUrl.readAsString(),
        builder: (context, snapshot) {
          if (!snapshot.hasData) {
            return const Center(child: CircularProgressIndicator());
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Text(
              snapshot.data!,
              style: const TextStyle(fontFamily: 'monospace'),
            ),
          );
        },
      ),
    );
  }
}
