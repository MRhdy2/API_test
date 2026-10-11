"""
这是一个极简的 CSV 读取工具，基于 pandas 实现，

用于从 CSV 文件中读取指定列并返回列表。
"""

import pandas as pd
from common.recordlog import logs
import traceback


def read_csv(filepath, col_name):
    """
    :param filepath: csv目录
    :param col_name: 取值的列名
    usecols：需要读取的列，可以是列的位置编号，也可以是列的名称
    error_bad_lines = False  当某行数据有问题时，不报错，直接跳过，处理脏数据时使用
    :return:
    """
    try:
        df = pd.read_csv(filepath, encoding="utf-8")
        data = df[col_name].tolist()
        return data
    except Exception:
        logs.error(str(traceback.format_exc()))
