import allure
import pytest

from base.apiutil_business import RequestBase
from base.generateId import c_id, m_id
from common.readyaml import get_testcase_yaml


LOGISTICS_CASES = get_testcase_yaml(
    './testcase/Logistics/logistics_scenario.yml'
)


@allure.feature(next(m_id) + '物流项目接口')
class TestLogisticsScenario:

    @allure.story(next(c_id) + '物流订单完整业务链路')
    @pytest.mark.parametrize(
        'case_info',
        LOGISTICS_CASES,
        ids=[case['baseInfo']['api_name'] for case in LOGISTICS_CASES],
    )
    def test_logistics_scenario(self, case_info):
        allure.dynamic.title(case_info['baseInfo']['api_name'])
        RequestBase().specification_yaml(case_info)
