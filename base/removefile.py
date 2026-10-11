# 删除报告、临时文件等清理工具根,conftest.py 有导入，但目前没有实际调用

import shutil
from pathlib import Path

from common.recordlog import logs


def remove_file(filepath, endlst):
    """
    删除文件
    :param filepath: 路径
    :param endlst: 删除的后缀，例如：['json','txt','attach']
    :return:
    """
    try:
        if not isinstance(endlst, list):
            raise TypeError('file Type error,must is list')

        directory = Path(filepath).expanduser()
        directory.mkdir(parents=True, exist_ok=True)
        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.name.endswith(tuple(endlst)):
                file_path.unlink()
    except Exception as e:
        logs.error(e)


def remove_directory(path):
    try:
        target = Path(path).expanduser()
        if target.is_dir() and not target.is_symlink():
            shutil.rmtree(target)
        elif target.exists() or target.is_symlink():
            target.unlink()
    except Exception as e:
        logs.error(e)
