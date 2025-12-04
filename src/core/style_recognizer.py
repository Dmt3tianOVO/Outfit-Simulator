"""
款式识别模块主接口

提供统一的款式识别接口，方便其他模块调用。
"""

from .model_utils import (
    create_model,
    load_model,
    predict_image,
    preprocess_image,
    get_class_name,
    CLASS_NAMES,
    NUM_CLASSES,
    IMG_SIZE
)


class StyleRecognizer:
    """
    款式识别器类
    
    封装模型加载和预测功能，提供简洁的API接口。
    """
    
    def __init__(self, model_path: str = None):
        """
        初始化款式识别器
        
        参数:
            model_path: 模型文件路径，如果为None则需要后续调用load_model加载
        """
        self.model = None
        self.model_path = model_path
        
        if model_path:
            self.load_model(model_path)
    
    def load_model(self, model_path: str):
        """
        加载模型
        
        参数:
            model_path: 模型文件路径
        """
        self.model = load_model(model_path)
        self.model_path = model_path
        print(f"款式识别模型已加载: {model_path}")
    
    def predict(self, image_path: str, top_k: int = 3) -> list:
        """
        预测单张图像的款式
        
        参数:
            image_path: 图像文件路径
            top_k: 返回前k个预测结果
        
        返回:
            list: 预测结果列表，每个元素为{'class': 类别名, 'confidence': 置信度}
        
        示例:
            >>> recognizer = StyleRecognizer('models/outfit_classifier.h5')
            >>> results = recognizer.predict('image.jpg')
            >>> print(results[0]['class'])  # 输出: 'T恤'
        """
        if self.model is None:
            raise ValueError("模型未加载，请先调用load_model()或初始化时提供model_path")
        
        return predict_image(self.model, image_path, top_k)
    
    def predict_batch(self, image_paths: list, top_k: int = 3) -> list:
        """
        批量预测图像
        
        参数:
            image_paths: 图像文件路径列表
            top_k: 返回前k个预测结果
        
        返回:
            list: 预测结果列表，每个元素包含图像路径和预测结果
        """
        if self.model is None:
            raise ValueError("模型未加载，请先调用load_model()或初始化时提供model_path")
        
        results = []
        for image_path in image_paths:
            try:
                predictions = predict_image(self.model, image_path, top_k)
                results.append({
                    'image_path': image_path,
                    'predictions': predictions,
                    'success': True
                })
            except Exception as e:
                results.append({
                    'image_path': image_path,
                    'predictions': None,
                    'error': str(e),
                    'success': False
                })
        
        return results
    
    def get_class_names(self) -> list:
        """
        获取所有类别名称
        
        返回:
            list: 类别名称列表
        """
        return CLASS_NAMES.copy()
    
    def get_num_classes(self) -> int:
        """
        获取类别数量
        
        返回:
            int: 类别数量
        """
        return NUM_CLASSES


# 便捷函数
def create_recognizer(model_path: str) -> StyleRecognizer:
    """
    创建款式识别器实例
    
    参数:
        model_path: 模型文件路径
    
    返回:
        StyleRecognizer: 款式识别器实例
    
    示例:
        >>> recognizer = create_recognizer('models/outfit_classifier.h5')
        >>> results = recognizer.predict('image.jpg')
    """
    return StyleRecognizer(model_path)


# 导出主要接口
__all__ = [
    'StyleRecognizer',
    'create_recognizer',
    'CLASS_NAMES',
    'NUM_CLASSES',
    'IMG_SIZE',
    'load_model',
    'predict_image',
    'get_class_name'
]

