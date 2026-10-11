"""
这是一个 YAML 数据读写模块，用于：

读取测试用例 YAML 文件（testcase 格式）；

读写接口关联提取变量文件（extract.yaml）；

获取请求方法、请求参数等。

是 httprunner 风格测试框架的数据层核心。
"""

import traceback
from pathlib import Path

import yaml

from common.recordlog import logs
from conf.operationConfig import OperationConfig
from conf.setting import FILE_PATH


PROJECT_ROOT = Path(FILE_PATH['YAML'])


def _resolve_path(file):
    """将相对路径稳定地解析到项目根目录，避免依赖启动时的工作目录。"""
    path = Path(file).expanduser()
    if path.is_absolute():
        return path

    current_path = Path.cwd() / path
    if current_path.exists():
        return current_path
    return PROJECT_ROOT / path


def get_testcase_yaml(file):
    testcase_list = []
    yaml_path = _resolve_path(file)
    try:
        with yaml_path.open('r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            if len(data) <= 1:
                yam_data = data[0]
                base_info = yam_data.get('baseInfo')
                for ts in yam_data.get('testCase'):
                    param = [base_info, ts]
                    testcase_list.append(param)
                return testcase_list
            else:
                return data
    except UnicodeDecodeError:
        logs.error(f"[{yaml_path}]文件编码格式错误，--尝试使用utf-8编码解码YAML文件时发生了错误，请确保你的yaml文件是UTF-8格式！")
    except FileNotFoundError:
        logs.error(f'[{yaml_path}]文件未找到，请检查路径是否正确')
    except Exception as e:
        logs.error(f'获取【{yaml_path}】文件数据时出现未知错误: {str(e)}')


class ReadYamlData:
    """读写接口的YAML格式测试数据"""

    def __init__(self, yaml_file=None):
        if yaml_file is not None:
            self.yaml_file = yaml_file
        else:
            pass
        self.conf = OperationConfig()
        self.yaml_data = None

    @property
    def get_yaml_data(self):
        """
        获取测试用例yaml数据
        :param file: YAML文件
        :return: 返回list
        """
        # Loader=yaml.FullLoader表示加载完整的YAML语言，避免任意代码执行，无此参数控制台报Warning
        try:
            with _resolve_path(self.yaml_file).open('r', encoding='utf-8') as f:
                self.yaml_data = yaml.safe_load(f)
                return self.yaml_data
        except Exception:
            logs.error(str(traceback.format_exc()))

    def write_yaml_data(self, value):
        """
        写入数据需为dict，allow_unicode=True表示写入中文，sort_keys按顺序写入
        写入YAML文件数据,主要用于接口关联
        :param value: 写入数据，必须用dict
        :return:
        """

        file_path = Path(FILE_PATH['EXTRACT'])
        file_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            if not isinstance(value, dict):
                logs.info('写入[extract.yaml]的数据必须为dict格式')
                return
            with file_path.open('a', encoding='utf-8') as file:
                write_data = yaml.dump(value, allow_unicode=True, sort_keys=False)
                file.write(write_data)
        except Exception:
            logs.error(str(traceback.format_exc()))

    def clear_yaml_data(self):
        """
        清空extract.yaml文件数据
        :param filename: yaml文件名
        :return:
        """
        extract_path = Path(FILE_PATH['EXTRACT'])
        extract_path.parent.mkdir(parents=True, exist_ok=True)
        extract_path.write_text('', encoding='utf-8')

    def get_extract_yaml(self, node_name, second_node_name=None):
        """
        用于读取接口提取的变量值
        :param node_name:
        :return:
        """
        extract_path = Path(FILE_PATH['EXTRACT'])
        if not extract_path.exists():
            logs.error('extract.yaml不存在')
            extract_path.parent.mkdir(parents=True, exist_ok=True)
            extract_path.touch()
            logs.info('extract.yaml创建成功！')
        try:
            with extract_path.open('r', encoding='utf-8') as rf:
                ext_data = yaml.safe_load(rf)
                if second_node_name is None:
                    return ext_data[node_name]
                else:
                    return ext_data[node_name][second_node_name]
        except Exception as e:
            logs.error(f"【extract.yaml】没有找到：{node_name},--%s" % e)

    def get_testCase_baseInfo(self, case_info):
        """
        获取testcase yaml文件的baseInfo数据
        :param case_info: yaml数据，dict类型
        :return:
        """
        pass

    def get_method(self):
        """
        :param self:
        :return:
        """
        yal_data = self.get_yaml_data()
        metd = yal_data[0].get('method')
        return metd

    def get_request_parame(self):
        """
        获取yaml测试数据中的请求参数
        :return:
        """
        data_list = []
        yaml_data = self.get_yaml_data()
        del yaml_data[0]
        for da in yaml_data:
            data_list.append(da)
        return data_list
