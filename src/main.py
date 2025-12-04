"""
主程序入口

集成并启动 Outfit Simulator Web 服务：
1. 初始化 Flask 应用
2. 加载 / 配置 AI 模型
3. 启动 Web 服务器
4. 提供命令行参数和配置管理
"""

import os
import sys
import argparse
import logging
from logging.handlers import RotatingFileHandler

# 确保项目根目录在 sys.path 中
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from src.web.app import app, init_models  # noqa: E402


def setup_logging(log_level: str = "INFO", log_file: str | None = None) -> None:
    """
    配置日志系统

    参数:
        log_level: 日志级别（DEBUG/INFO/WARNING/ERROR）
        log_file: 日志文件路径（可选）
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    # 基础格式
    log_format = "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

    if log_file:
        log_file_path = os.path.abspath(log_file)
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        handlers.append(file_handler)

    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format,
        handlers=handlers,
        force=True,  # 覆盖已有配置
    )

    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.info("日志系统已初始化，级别: %s", log_level.upper())


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Outfit Simulator 主程序")

    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="服务器绑定地址（默认: 0.0.0.0）",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="服务器端口（默认: 5000）",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用 Flask Debug 模式（仅开发环境使用）",
    )
    parser.add_argument(
        "--model-path",
        type=str,
        default=os.path.join(BASE_DIR, "models", "best_model.h5"),
        help="款式识别模型路径（默认: models/best_model.h5）",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="日志级别（默认: INFO）",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=os.path.join(BASE_DIR, "logs", "app.log"),
        help="日志文件路径（默认: logs/app.log）",
    )

    return parser.parse_args()


def main() -> None:
    """主函数：配置并启动 Web 服务器"""
    args = parse_args()

    # 配置日志
    setup_logging(args.log_level, args.log_file)
    logger = logging.getLogger("main")

    # 应用配置
    app.config.setdefault("MODEL_PATH", args.model_path)
    app.config.setdefault("HOST", args.host)
    app.config.setdefault("PORT", args.port)
    app.config.setdefault("DEBUG", args.debug)

    logger.info("启动参数: host=%s, port=%s, debug=%s", args.host, args.port, args.debug)
    logger.info("模型路径: %s", args.model_path)

    # 初始化模型（可失败但不中断服务）
    try:
        init_models(model_path=args.model_path)
    except Exception as exc:  # 记录错误但继续启动（允许无模型运行）
        logger.error("初始化模型失败: %s", exc, exc_info=True)

    # 启动 Flask 应用
    logger.info("Web 服务器启动中...")
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug,
    )


if __name__ == "__main__":
    main()


