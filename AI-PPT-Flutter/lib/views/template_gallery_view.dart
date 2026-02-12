import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/template_models.dart';

final templateProvider = StateNotifierProvider<TemplateNotifier, TemplateState>((ref) {
  return TemplateNotifier();
});

class TemplateState {
  final List<PPTTemplate> templates;
  final TemplateCategory? selectedCategory;
  final PPTTemplate? selectedTemplate;

  TemplateState({
    required this.templates,
    this.selectedCategory,
    this.selectedTemplate,
  });

  TemplateState copyWith({
    List<PPTTemplate>? templates,
    TemplateCategory? selectedCategory,
    PPTTemplate? selectedTemplate,
  }) {
    return TemplateState(
      templates: templates ?? this.templates,
      selectedCategory: selectedCategory ?? this.selectedCategory,
      selectedTemplate: selectedTemplate ?? this.selectedTemplate,
    );
  }

  List<PPTTemplate> get filteredTemplates {
    if (selectedCategory == null) {
      return templates;
    }
    return templates.where((t) => t.category == selectedCategory).toList();
  }
}

class TemplateNotifier extends StateNotifier<TemplateState> {
  TemplateNotifier() : super(TemplateState(templates: TemplateManager.templates)) {
    // Select first template by default
    if (templates.isNotEmpty) {
      state = state.copyWith(selectedTemplate: templates.first);
    }
  }

  void selectCategory(TemplateCategory? category) {
    state = state.copyWith(selectedCategory: category);
  }

  void selectTemplate(PPTTemplate template) {
    state = state.copyWith(selectedTemplate: template);
  }
}

class TemplateGalleryView extends ConsumerWidget {
  const TemplateGalleryView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(templateProvider);
    final notifier = ref.read(templateProvider.notifier);

    return Scaffold(
      appBar: AppBar(
        title: const Text('模板'),
      ),
      body: Column(
        children: [
          // Category Selector
          SizedBox(
            height: 60,
            child: ListView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              children: [
                _CategoryChip(
                  label: '全部',
                  isSelected: state.selectedCategory == null,
                  onTap: () => notifier.selectCategory(null),
                ),
                ...TemplateCategory.values.map(
                  (category) => _CategoryChip(
                    label: category.displayName,
                    isSelected: state.selectedCategory == category,
                    onTap: () => notifier.selectCategory(category),
                  ),
                ),
              ],
            ),
          ),
          const Divider(height: 1),
          // Template Grid
          Expanded(
            child: GridView.builder(
              padding: const EdgeInsets.all(16),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                childAspectRatio: 0.8,
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
              ),
              itemCount: state.filteredTemplates.length,
              itemBuilder: (context, index) {
                final template = state.filteredTemplates[index];
                return _TemplateCard(
                  template: template,
                  isSelected: state.selectedTemplate?.id == template.id,
                  onTap: () => notifier.selectTemplate(template),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _CategoryChip extends StatelessWidget {
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  const _CategoryChip({
    required this.label,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: FilterChip(
        label: Text(label),
        selected: isSelected,
        onSelected: (_) => onTap(),
        selectedColor: Colors.blue.shade100,
        checkmarkColor: Colors.blue,
        labelStyle: TextStyle(
          color: isSelected ? Colors.blue.shade700 : Colors.grey.shade700,
        ),
      ),
    );
  }
}

class _TemplateCard extends StatelessWidget {
  final PPTTemplate template;
  final bool isSelected;
  final VoidCallback onTap;

  const _TemplateCard({
    required this.template,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Card(
        elevation: isSelected ? 4 : 1,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: BorderSide(
            color: isSelected ? Colors.blue : Colors.transparent,
            width: 2,
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(12.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Preview Colors
              Wrap(
                spacing: 4,
                children: template.previewColors.take(4).map((color) {
                  return Container(
                    width: 16,
                    height: 16,
                    decoration: BoxDecoration(
                      color: _parseColor(color),
                      borderRadius: BorderRadius.circular(4),
                    ),
                  );
                }).toList(),
              ),
              const SizedBox(height: 12),
              // Template Name
              Text(
                template.name,
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 4),
              // Template Description
              Text(
                template.description,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.grey[600],
                    ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const Spacer(),
              // Category
              Chip(
                label: Text(
                  template.category.displayName,
                  style: const TextStyle(fontSize: 10),
                ),
                padding: const EdgeInsets.symmetric(horizontal: 8),
                visualDensity: VisualDensity.compact,
              ),
            ],
          ),
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
