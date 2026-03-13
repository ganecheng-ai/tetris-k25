"""日志系统模块"""

import logging
import logging.handlers
import sys
from pathlib import Path

from .config import LOG_FILE, LOG_LEVEL, LOG_FORMAT, LOG_MAX_BYTES, LOG_BACKUP_COUNT


def setup_logger(name: str = "tetris") -> logging.Logger:
    """
    设置并返回一个配置好的日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))

    # 避免重复添加处理器
    if logger.handlers:
        return logger

    # 创建格式化器
    formatter = logging.Formatter(LOG_FORMAT)

    # 文件处理器（带轮转）
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.debug(f"日志系统初始化完成，日志文件: {LOG_FILE}")
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    获取日志记录器

    Args:
        name: 子模块名称，如果不提供则返回根日志记录器

    Returns:
        日志记录器
    """
    if name:
        return logging.getLogger(f"tetris.{name}")
    return logging.getLogger("tetris")
