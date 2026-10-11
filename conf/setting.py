# 定义代码级常量：项目根目录、日志级别、接口超时、Excel 工作表编号、报告类型和各类文件路径。

import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIR_BASE = str(PROJECT_ROOT)
if DIR_BASE not in sys.path:
    sys.path.insert(0, DIR_BASE)

# log日志输出级别
LOG_LEVEL = logging.DEBUG  # 文件
STREAM_LOG_LEVEL = logging.DEBUG  # 控制台

# 接口超时时间，单位/s
API_TIMEOUT = 60

# excel文件的sheet页，默认读取第一个sheet页的数据，int类型，第一个sheet为0，以此类推0.....9
SHEET_ID = 0

# 生成的测试报告类型，可以生成两个风格的报告，allure或tm
REPORT_TYPE = 'allure'

# 是否发送钉钉消息
dd_msg = False

# 文件路径
FILE_PATH = {
    'CONFIG': str(PROJECT_ROOT / 'conf' / 'config.ini'),
    'LOG': str(PROJECT_ROOT / 'logs'),
    'YAML': str(PROJECT_ROOT),
    'TEMP': str(PROJECT_ROOT / 'report' / 'temp'),
    'TMR': str(PROJECT_ROOT / 'report' / 'tmreport'),
    'EXTRACT': str(PROJECT_ROOT / 'extract.yaml'),
    'XML': str(PROJECT_ROOT / 'data' / 'sql'),
    'RESULTXML': str(PROJECT_ROOT / 'report'),
    'EXCEL': str(PROJECT_ROOT / 'data' / '测试数据.xls')
}

# 默认请求头信息
LOGIN_HEADER = {
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive'
}
