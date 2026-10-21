# API_test

一个基于 **Pytest + YAML** 的接口自动化测试项目。测试数据与执行代码分离，覆盖用户管理单接口、商品下单与支付流程，以及物流订单业务链路；运行时支持参数提取、接口关联、断言和测试报告。

## 主要功能

- 使用 YAML 定义请求、测试数据、预期结果和响应字段提取规则。
- 支持 `params`、`data`、`json` 请求参数，以及文件上传和 Cookie 传递。
- 通过 `extract.yaml` 保存运行中提取的变量，在后续接口中以 `${get_extract_data(...)}` 引用。
- 使用 Pytest 参数化组织单接口用例和业务场景用例，并通过 Allure 展示结果。
- 可选启用 DeepSeek：测试失败时生成中文分析建议并附加到 Allure 结果。
- 提供接口测试用例生成工具 `base/new_testcase_tools.py`，以及 `flaskServer/` 下的辅助程序。

## 项目结构

| 路径 | 作用 |
| --- | --- |
| `testcase/` | 用户管理、商品管理、业务场景和物流场景测试 |
| `base/` | 单接口与业务场景的请求、提取和断言封装 |
| `common/` | YAML、请求、日志、数据库连接等公共模块 |
| `conf/` | 运行常量与接口环境配置 |
| `data/` | 登录、CSV、Excel、SQL 等测试数据 |
| `run.py` | 执行测试并生成报告的入口 |
| `report/`、`logs/` | 测试报告与运行日志 |
| `flaskServer/` | 辅助服务源码及 Windows 打包文件 |

更详细的用例字段说明可见 [使用前请阅读此文件.md](使用前请阅读此文件.md)。

## 快速开始

建议在测试环境中运行：现有用例会调用真实接口，部分业务链路包含创建订单、支付、派车等操作。

1. 克隆仓库，创建虚拟环境并安装依赖：

   ```bash
   git clone https://github.com/MRhdy2/API_test.git
   cd API_test
   python -m venv venv
   source venv/bin/activate       # Windows: venv\Scripts\activate
   python -m pip install -r requirements.txt
   ```

2. 在 `conf/config.ini` 中设置测试环境的接口地址及所需服务连接信息；按目标环境检查 `data/loginName.yaml` 中的登录用例和 `testcase/` 中的测试数据。

3. 从项目根目录运行：

   ```bash
   python -m pytest testcase -v
   ```

`testcase/conftest.py` 会在测试会话开始时清空 `extract.yaml`，然后执行 `data/loginName.yaml` 中的登录用例。目标接口不可访问或登录失败时，后续用例无法正常运行。根目录的 `test_llm_analyzer.py` 是主动触发异常的失败分析演示文件，不属于上述 `testcase/` 执行范围。

## 报告

`conf/setting.py` 中的 `REPORT_TYPE` 默认是 `allure`。安装 [Allure 命令行工具](https://allurereport.org/docs/install/) 并确保 `allure` 命令可用后，运行：

```bash
python run.py
```

脚本会执行 `testcase/`，将原始结果写入 `report/temp/`、JUnit 结果写入 `report/results.xml`，并生成 `report/allureReport/index.html`。在 Jenkins 环境中，Allure 原始结果写入 `allure-results/`，供流水线使用。

如需使用 TM 报告，可将 `REPORT_TYPE` 改为 `tm`，并安装对应的 Pytest 报告插件；输出路径为 `report/tmreport/testReport.html`。

## YAML 用例格式

测试文件以 `baseInfo` 描述接口，以 `testCase` 描述用例。以下为简化示例：

```yaml
- baseInfo:
    api_name: 查询商品
    url: /api/products
    method: get
    header:
      Content-Type: application/json
  testCase:
    - case_name: 查询商品列表
      params:
        page: 1
      validation:
        - contains: { 'status_code': 200 }
      extract:
        product_id: $.data[0].id
```

接口主机地址来自 `conf/config.ini` 的 `[api_envi] host`；后续用例可通过 `${get_extract_data(product_id)}` 使用提取值。业务场景用例可参考 `testcase/Business interface/` 和 `testcase/Logistics/`。

## 可选的失败分析

根目录 `conftest.py` 会读取本地 `.env` 或系统环境变量。设置 `DEEPSEEK_API_KEY` 后，测试失败时会调用配置的模型生成建议；还可设置 `DEEPSEEK_BASE_URL` 和 `DEEPSEEK_MODEL`。未配置密钥时，普通测试仍可运行。

```dotenv
DEEPSEEK_API_KEY=your-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=your-model-name
```

`.env` 与 `venv/` 已列入 `.gitignore`。运行前请检查仓库内的配置和测试数据是否适合目标环境。
