import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/template_models.dart';
import '../services/ppt_generation_engine.dart';
import 'template_gallery_view.dart';

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
    // Select first template by default
    if (TemplateManager.templates.isNotEmpty) {
      state = state.copyWith(selectedTemplate: TemplateManager.templates.first);
    }
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
    state = state.copyWith(
      isGenerating: true,
      progress: 0.0,
      currentStep: '准备中...',
      errorMessage: null,
    );

    try {
      final engine = PPTGenerationEngine();
      final outputDir = await PPTGenerationEngine.getOutputDirectory();

      PPTResult result;

      if (state.selectedMode == 0) {
        // Text mode
        if (state.inputText.isEmpty) {
          throw Exception('请输入 PPT 文案');
        }

        result = await engine.generatePPTFromText(
          text: state.inputText,
          styleTemplate: state.selectedTemplate!,
          outputDir: outputDir,
          progressHandler: (progress) {
            state = state.copyWith(
              progress: progress,
              currentStep: '生成中... ${(progress * 100).toInt()}%',
            );
          },
        );
      } else {
        // Web search mode
        if (state.topic.isEmpty) {
          throw Exception('请输入主题');
        }

        result = await engine.generatePPTFromWebSearch(
          topic: state.topic,
          styleTemplate: state.selectedTemplate!,
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
        currentStep: '完成',
        generationResult: result,
      );
    } catch (e) {
      state = state.copyWith(
        isGenerating: false,
        progress: 0.0,
        currentStep: '失败',
        errorMessage: e.toString(),
      );
    }
  }

  void resetError() {
    state = state.copyWith(errorMessage: null);
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
      body: Column(
        children: [
          // Mode selector
          _buildModeSelector(state, notifier),
          const Divider(height: 1),

          // Input area
          Expanded(
            child: _buildInputArea(state, notifier),
          ),

          // Bottom action
          _buildBottomAction(state, notifier, context),
        ],
      ),
    );
  }

  Widget _buildModeSelector(GenerationState state, GenerationNotifier notifier) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Expanded(
            child: InkWell(
              onTap: () => notifier.setMode(0),
              borderRadius: BorderRadius.circular(8),
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 12),
                decoration: BoxDecoration(
                  color: state.selectedMode == 0
                      ? Colors.blue.shade50
                      : Colors.transparent,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: state.selectedMode == 0
                        ? Colors.blue
                        : Colors.grey.shade300,
                  ),
                ),
                child: Text(
                  '文案模式',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: state.selectedMode == 0
                        ? Colors.blue.shade700
                        : Colors.grey.shade600,
                    fontWeight: state.selectedMode == 0
                        ? FontWeight.bold
                        : FontWeight.normal,
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: InkWell(
              onTap: () => notifier.setMode(1),
              borderRadius: BorderRadius.circular(8),
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 12),
                decoration: BoxDecoration(
                  color: state.selectedMode == 1
                      ? Colors.blue.shade50
                      : Colors.transparent,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: state.selectedMode == 1
                        ? Colors.blue
                        : Colors.grey.shade300,
                  ),
                ),
                child: Text(
                  '搜索模式',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: state.selectedMode == 1
                        ? Colors.blue.shade700
                        : Colors.grey.shade600,
                    fontWeight: state.selectedMode == 1
                        ? FontWeight.bold
                        : FontWeight.normal,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInputArea(GenerationState state, GenerationNotifier notifier) {
    if (state.selectedMode == 0) {
      // Text mode
      return Container(
        padding: const EdgeInsets.all(16),
        child: TextField(
          maxLines: null,
          minLines: 10,
          decoration: const InputDecoration(
            border: OutlineInputBorder(),
            labelText: '请输入 PPT 文案',
          ),
          onChanged: (value) => notifier.setInputText(value),
        ),
      );
    } else {
      // Web search mode
      return Container(
        padding: const EdgeInsets.all(16),
        child: TextField(
          decoration: const InputDecoration(
            border: OutlineInputBorder(),
            labelText: '请输入主题',
            hintText: '例如：人工智能发展趋势',
          ),
          onChanged: (value) => notifier.setTopic(value),
        ),
      );
    }
  }

  Widget _buildBottomAction(
    GenerationState state,
    GenerationNotifier notifier,
    BuildContext context,
  ) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        border: Border(top: BorderSide(color: Colors.grey.shade300)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Template selector
          _TemplateSelector(
            selectedTemplate: state.selectedTemplate,
            onTemplateSelected: (template) =>
                notifier.setSelectedTemplate(template),
          ),
          const SizedBox(height: 16),

          // Progress indicator
          if (state.isGenerating)
            Column(
              children: [
                LinearProgressIndicator(value: state.progress),
                const SizedBox(height: 8),
                Text(
                  state.currentStep,
                  style: const TextStyle(fontSize: 12),
                ),
              ],
            ),

          // Error message
          if (state.errorMessage != null)
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.red.shade50,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  Icon(Icons.error, color: Colors.red.shade700, size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      state.errorMessage!,
                      style: TextStyle(color: Colors.red.shade700),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, size: 16),
                    onPressed: () => notifier.resetError(),
                  ),
                ],
              ),
            ),

          // Generate button
          if (!state.isGenerating)
            ElevatedButton(
              onPressed: () => notifier.generatePPT(),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: const Text('生成 PPT'),
            ),

          // Result view
          if (state.generationResult != null && !state.isGenerating)
            Padding(
              padding: const EdgeInsets.only(top: 16),
              child: PPTResultView(result: state.generationResult!),
            ),
        ],
      ),
    );
  }
}

class _TemplateSelector extends StatelessWidget {
  final PPTTemplate? selectedTemplate;
  final Function(PPTTemplate) onTemplateSelected;

  const _TemplateSelector({
    super.key,
    required this.selectedTemplate,
    required this.onTemplateSelected,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey.shade300),
        borderRadius: BorderRadius.circular(8),
      ),
      padding: const EdgeInsets.all(12),
      child: Row(
        children: [
          // Selected template preview
          Expanded(
            child: InkWell(
              onTap: () {
                if (selectedTemplate != null) {
                  onTemplateSelected(selectedTemplate!);
                }
              },
              child: Container(
                height: 60,
                decoration: BoxDecoration(
                  color: selectedTemplate?.previewColors.isNotEmpty ?? false
                      ? Color(int.parse(selectedTemplate!.previewColors.first
                              .replaceAll('#', 'FF')))
                      : Colors.grey.shade200,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: selectedTemplate != null
                    ? Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            selectedTemplate!.name,
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(width: 8),
                          Icon(
                            Icons.check_circle,
                            color: Colors.white,
                            size: 20,
                          ),
                        ],
                      )
                    : Center(
                        child: Text(
                          '请选择模板',
                          style: TextStyle(color: Colors.grey.shade600),
                        ),
                      ),
              ),
            ),
          ),
          const SizedBox(width: 16),
          // Browse templates button
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (_) => const TemplateGalleryView(),
                ),
              );
            },
            child: const Text('浏览模板'),
          ),
        ],
      ),
    );
  }
}

// MARK: - PPT Result View
class PPTResultView extends StatelessWidget {
  final PPTResult result;

  const PPTResultView({super.key, required this.result});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.green.shade50,
        border: Border.all(color: Colors.green.shade300),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.check_circle, color: Colors.green.shade700),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'PPT 生成成功！',
                  style: TextStyle(
                    color: Colors.green.shade700,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            '标题：${result.title}',
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 4),
          Text('模板：${result.templateUsed}'),
          const SizedBox(height: 4),
          Text('幻灯片数：${result.totalSlides}'),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: () {
              // TODO: Implement sharing/export
            },
            icon: const Icon(Icons.share),
            label: const Text('分享'),
          ),
        ],
      ),
    );
  }
}
