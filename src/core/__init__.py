"""
核心模块包

包含颜色分析和款式识别等核心功能。
"""

from .color_analyzer import (
    extract_dominant_colors,
    classify_color_type,
    evaluate_color_combo
)

from .style_recognizer import (
    StyleRecognizer,
    create_recognizer,
    CLASS_NAMES,
    NUM_CLASSES,
    IMG_SIZE
)

from .rule_engine import (
    RuleEvaluator,
    RuleLibrary,
    BaseRule,
    ColorRule,
    StyleRule,
    ContextRule,
    RuleResult,
    RuleSeverity,
    create_evaluator,
    evaluate_outfit
)

__all__ = [
    # 颜色分析
    'extract_dominant_colors',
    'classify_color_type',
    'evaluate_color_combo',
    # 款式识别
    'StyleRecognizer',
    'create_recognizer',
    'CLASS_NAMES',
    'NUM_CLASSES',
    'IMG_SIZE',
    # 规则引擎
    'RuleEvaluator',
    'RuleLibrary',
    'BaseRule',
    'ColorRule',
    'StyleRule',
    'ContextRule',
    'RuleResult',
    'RuleSeverity',
    'create_evaluator',
    'evaluate_outfit',
]

