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
        ALLURE_TEMP_DIR.mkdir(parents=True, exist_ok=True)
        exit_code = pytest.main(
            ['-s', '-v', f'--alluredir={ALLURE_TEMP_DIR}', str(PROJECT_ROOT / 'testcase'),
             '--clean-alluredir', f'--junitxml={REPORT_DIR / "results.xml"}'])

        shutil.copy(PROJECT_ROOT / 'environment.xml', ALLURE_TEMP_DIR)
        subprocess.run(
            [
                'allure', 'generate', str(ALLURE_TEMP_DIR),
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
