"""
这是一个日志记录模块，基于标准库 logging，实现了：

日志按天分文件、按大小滚动备份；

自动清理 30 天前的过期日志；

同时输出到文件和控制台；

通过模块级 logs 对象全局使用。
"""

import sys
import logging
import time
from pathlib import Path
from logging.handlers import RotatingFileHandler  # 按文件大小滚动备份
import datetime

from conf import setting

log_path = Path(setting.FILE_PATH["LOG"])
log_path.mkdir(parents=True, exist_ok=True)
logfile_name = log_path / "test.{}.log".format(time.strftime("%Y%m%d"))


class RecordLog:
    """日志模块"""

    def __init__(self):
        self.handle_overdue_log()

    def handle_overdue_log(self):
        """处理过期日志文件"""
        # 获取系统的当前时间
        now_time = datetime.datetime.now()
        # 日期偏移30天，最多保留30的日志文件，超过自动清理
        offset_date = datetime.timedelta(days=-30)
        # 获取前一天时间戳
        before_date = (now_time + offset_date).timestamp()
        # 找到目录下的文件
        for filepath in log_path.iterdir():
            if filepath.is_file() and filepath.suffix:
                # mtime 在 macOS、Linux 和 Windows 上含义一致，适合按日志年龄清理。
                file_create_time = filepath.stat().st_mtime
                # dateArray = datetime.datetime.fromtimestamp(file_createtime) #标准时间格式
                # print(dateArray.strftime("%Y--%m--%d %H:%M:%S"))
                if file_create_time < before_date:
                    filepath.unlink()
                else:
                    continue

    def output_logging(self):
        """获取logger对象"""
        logger = logging.getLogger(__name__)
        # 防止重复打印日志
        if not logger.handlers:
            logger.setLevel(setting.LOG_LEVEL)
            log_format = logging.Formatter(
                '%(levelname)s - %(asctime)s - %(filename)s:%(lineno)d -[%(module)s:%(funcName)s] - %(message)s')
            # 日志输出到指定文件，滚动备份日志
            fh = RotatingFileHandler(filename=logfile_name, mode='a', maxBytes=5242880,
                                     backupCount=7,
                                     encoding='utf-8')  # maxBytes:控制单个日志文件的大小，单位是字节,backupCount:用于控制日志文件的数量

            fh.setLevel(setting.LOG_LEVEL)
            fh.setFormatter(log_format)
            # 将相应的handler添加在logger对象中
            logger.addHandler(fh)

            # 输出到控制台
            sh = logging.StreamHandler()
            sh.setLevel(setting.STREAM_LOG_LEVEL)
            sh.setFormatter(log_format)
            logger.addHandler(sh)
        return logger


apilog = RecordLog()
logs = apilog.output_logging()
