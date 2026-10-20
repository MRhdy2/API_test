import shutil
import pytest
import os
import subprocess
import sys
import webbrowser
from pathlib import Path
from conf.setting import REPORT_TYPE


PROJECT_ROOT = Path(__file__).resolve().parent
REPORT_DIR = PROJECT_ROOT / 'report'
ALLURE_TEMP_DIR = REPORT_DIR / 'temp'
ALLURE_REPORT_DIR = REPORT_DIR / 'allureReport'
TM_REPORT_DIR = REPORT_DIR / 'tmreport'
IS_JENKINS = bool(os.environ.get('JENKINS_URL') or
                  (os.environ.get('WORKSPACE') and os.environ.get('BUILD_NUMBER')))
ALLURE_RESULTS_DIR = PROJECT_ROOT / 'allure-results' if IS_JENKINS else ALLURE_TEMP_DIR


def configure_utf8_output():
    """统一主进程、pytest 和报告子进程的输出编码。"""
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, 'reconfigure', None)
        if callable(reconfigure):
            reconfigure(encoding='utf-8', errors='replace')

configure_utf8_output()

if __name__ == '__main__':

    if REPORT_TYPE == 'allure':
        ALLURE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        exit_code = pytest.main(
            ['-s', '-v', f'--alluredir={ALLURE_RESULTS_DIR}', str(PROJECT_ROOT / 'testcase'),
             '--clean-alluredir', f'--junitxml={REPORT_DIR / "results.xml"}'])

        shutil.copy(PROJECT_ROOT / 'environment.xml', ALLURE_RESULTS_DIR)
        if IS_JENKINS:
            print(f'Allure 原始结果已保存到：{ALLURE_RESULTS_DIR}')
            raise SystemExit(exit_code)

        subprocess.run(
            [
                'allure', 'generate', str(ALLURE_RESULTS_DIR),
                '-o', str(ALLURE_REPORT_DIR), '--clean', '--single-file',
            ],
            check=True,
        )
        report_file = ALLURE_REPORT_DIR / 'index.html'
        print(f'Allure 离线报告已保存到：{report_file}')
        webbrowser.open_new_tab(report_file.as_uri())
        raise SystemExit(exit_code)

    elif REPORT_TYPE == 'tm':
        TM_REPORT_DIR.mkdir(parents=True, exist_ok=True)
        pytest.main([
            '-vs', '--pytest-tmreport-name=testReport.html',
            f'--pytest-tmreport-path={TM_REPORT_DIR}', str(PROJECT_ROOT / 'testcase'),
        ])
        webbrowser.open_new_tab((TM_REPORT_DIR / 'testReport.html').as_uri())
