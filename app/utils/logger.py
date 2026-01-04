"""ログ設定（個人情報ハッシュ化対応）"""
import hashlib
import logging
import os
from logging.handlers import TimedRotatingFileHandler
from typing import Optional


LOG_FORMAT = "[%(asctime)s.%(msecs)03d] [%(levelname)s] [%(name)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(level: str, log_file: Optional[str]) -> None:
    """ログ設定を構成"""
    logging.basicConfig(level=getattr(logging, level.upper(), logging.ERROR))
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

    root = logging.getLogger()
    root.handlers.clear()

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root.addHandler(console)

    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        # 週次ローテーション、90日保持（約13週）
        file_handler = TimedRotatingFileHandler(
            log_file,
            when="W0",  # 毎週月曜日
            backupCount=13,  # 約90日分
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """ロガーを取得"""
    return logging.getLogger(name)


def hash_pii(value: str) -> str:
    """個人情報をハッシュ化（先頭8文字のみ）"""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:8]


def hash_line_id(line_id: str) -> str:
    """LINE IDをハッシュ化（先頭8文字のみ）"""
    return hash_pii(line_id)


def hash_phone_number(phone_number: str) -> str:
    """電話番号をハッシュ化（先頭8文字のみ）"""
    return hash_pii(phone_number)
