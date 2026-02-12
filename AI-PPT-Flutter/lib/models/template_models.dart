import 'package:json_annotation/json_annotation.dart';

part 'template_models.g.dart';

@JsonSerializable()
class PPTTemplate {
  final String id;
  final String name;
  final String description;
  final TemplateCategory category;
  final String narrative;
  final int suggestedSlides;
  final StyleHints styleHints;
  final List<String> previewColors;

  PPTTemplate({
    required this.id,
    required this.name,
    required this.description,
    required this.category,
    required this.narrative,
    required this.suggestedSlides,
    required this.styleHints,
    required this.previewColors,
  });

  factory PPTTemplate.fromJson(Map<String, dynamic> json) =>
      _$PPTTemplateFromJson(json);

  Map<String, dynamic> toJson() => _$PPTTemplateToJson(this);
}

@JsonSerializable()
class StyleHints {
  final String background;
  final String typography;
  final String layout;
  final List<String> colors;
  final String visual;

  StyleHints({
    required this.background,
    required this.typography,
    required this.layout,
    required this.colors,
    required this.visual,
  });

  factory StyleHints.fromJson(Map<String, dynamic> json) =>
      _$StyleHintsFromJson(json);

  Map<String, dynamic> toJson() => _$StyleHintsToJson(this);
}

enum TemplateCategory {
  business,
  technology,
  academic,
  creative,
  minimalist,
  cyberpunk,
  xiaohongshu,
}

extension TemplateCategoryExtension on TemplateCategory {
  String get displayName {
    switch (this) {
      case TemplateCategory.business:
        return '商业路演';
      case TemplateCategory.technology:
        return '技术报告';
      case TemplateCategory.academic:
        return '学术演讲';
      case TemplateCategory.creative:
        return '产品发布';
      case TemplateCategory.minimalist:
        return '极简高级';
      case TemplateCategory.cyberpunk:
        return '赛博朋克';
      case TemplateCategory.xiaohongshu:
        return '小红书风';
    }
  }

  static TemplateCategory fromString(String value) {
    switch (value) {
      case 'business':
        return TemplateCategory.business;
      case 'technology':
        return TemplateCategory.technology;
      case 'academic':
        return TemplateCategory.academic;
      case 'creative':
        return TemplateCategory.creative;
      case 'minimalist':
        return TemplateCategory.minimalist;
      case 'cyberpunk':
        return TemplateCategory.cyberpunk;
      case 'xiaohongshu':
        return TemplateCategory.xiaohongshu;
      default:
        return TemplateCategory.business;
    }
  }
}

// Built-in Templates
class TemplateManager {
  static List<PPTTemplate> get templates => [
        // Business Template
        PPTTemplate(
          id: 'business_01',
          name: '专业商务',
          description: '适合商业计划、项目提案等正式场合',
          category: TemplateCategory.business,
          narrative: '问题-解决方案-结果',
          suggestedSlides: 12,
          styleHints: StyleHints(
            background: 'gradient_blue',
            typography: 'sans_serif_bold',
            layout: 'centered_title_left_content',
            colors: ['#003366', '#336699', '#6699CC', '#99CCFF'],
            visual: 'geometric_shapes',
          ),
          previewColors: ['#003366', '#336699', '#6699CC', '#99CCFF'],
        ),

        // Technology Template
        PPTTemplate(
          id: 'tech_01',
          name: '科技前沿',
          description: '适合技术报告、产品展示等科技主题',
          category: TemplateCategory.technology,
          narrative: '背景-技术-应用',
          suggestedSlides: 10,
          styleHints: StyleHints(
            background: 'dark_gradient',
            typography: 'modern_sans',
            layout: 'grid_layout',
            colors: ['#1a1a2e', '#16213e', '#0f3460', '#e94560'],
            visual: 'tech_icons',
          ),
          previewColors: ['#1a1a2e', '#16213e', '#0f3460', '#e94560'],
        ),

        // Academic Template
        PPTTemplate(
          id: 'academic_01',
          name: '学术经典',
          description: '适合学术演讲、研究报告等专业场合',
          category: TemplateCategory.academic,
          narrative: '引言-方法-结果-讨论',
          suggestedSlides: 15,
          styleHints: StyleHints(
            background: 'clean_white',
            typography: 'serif_academic',
            layout: 'two_column',
            colors: ['#000000', '#333333', '#666666', '#FFFFFF'],
            visual: 'minimalist_icons',
          ),
          previewColors: ['#000000', '#333333', '#666666', '#FFFFFF'],
        ),

        // Creative Template
        PPTTemplate(
          id: 'creative_01',
          name: '创意设计',
          description: '适合产品发布、品牌故事等创意主题',
          category: TemplateCategory.creative,
          narrative: '灵感-探索-呈现',
          suggestedSlides: 8,
          styleHints: StyleHints(
            background: 'vibrant_gradient',
            typography: 'display_font',
            layout: 'asymmetric',
            colors: ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'],
            visual: 'organic_shapes',
          ),
          previewColors: ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'],
        ),

        // Minimalist Template
        PPTTemplate(
          id: 'minimal_01',
          name: '极简主义',
          description: '高端简约，适合品牌展示、个人作品集',
          category: TemplateCategory.minimalist,
          narrative: '简约-聚焦-纯粹',
          suggestedSlides: 10,
          styleHints: StyleHints(
            background: 'solid_neutral',
            typography: 'ultra_light',
            layout: 'large_typography',
            colors: ['#FFFFFF', '#F5F5F5', '#E0E0E0', '#757575'],
            visual: 'none',
          ),
          previewColors: ['#FFFFFF', '#F5F5F5', '#E0E0E0', '#757575'],
        ),

        // Cyberpunk Template
        PPTTemplate(
          id: 'cyber_01',
          name: '赛博朋克',
          description: '未来科技感，适合前沿技术展示',
          category: TemplateCategory.cyberpunk,
          narrative: '未来-突破-变革',
          suggestedSlides: 12,
          styleHints: StyleHints(
            background: 'neon_gradient',
            typography: 'futuristic',
            layout: 'holographic',
            colors: ['#FF00FF', '#00FFFF', '#FFFF00', '#000000'],
            visual: 'glitch_effects',
          ),
          previewColors: ['#FF00FF', '#00FFFF', '#FFFF00', '#000000'],
        ),

        // Xiaohongshu Template
        PPTTemplate(
          id: 'xhs_01',
          name: '小红书风',
          description: '社交分享风格，适合内容创作、种草',
          category: TemplateCategory.xiaohongshu,
          narrative: '吸引-种草-行动',
          suggestedSlides: 8,
          styleHints: StyleHints(
            background: 'warm_gradient',
            typography: 'rounded_soft',
            layout: 'card_style',
            colors: ['#FF2442', '#FF6B6B', '#FFB6C1', '#FFF0F5'],
            visual: 'emoji_stickers',
          ),
          previewColors: ['#FF2442', '#FF6B6B', '#FFB6C1', '#FFF0F5'],
        ),
      ];
}
