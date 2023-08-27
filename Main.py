import os
from typing import List

from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_cloudapi20160714.client import Client
from alibabacloud_cloudapi20160714 import models as cloud_api20160714_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient


class AliyunUtils:
    """
        通过传递的group_name、app_name以及api_names(默认API_Name是唯一的) 获取到SetApisAuthorities 的参
        数group_id、app_id以及api_ids，同时读取环境变量中的AK/SK 获取阿里云的权限,减少secrets 的泄漏。
        给多个API添加APP访问权限 目前给的是永久权限，后续也可在set_apis_authorities 配置中添加其他参数。

    """

    # 初始化阿里云授权
    def __init__(self, endpoint, app_name, group_name, api_names):
        config = open_api_models.Config(
            access_key_id=os.getenv("access_key_id"),
            access_key_secret=os.getenv("access_key_secret")
        )
        config.endpoint = endpoint
        self.apiclient = Client(config=config)
        self.app_name = app_name
        self.group_name = group_name
        self.api_names = api_names

    def get_app_id_by_name(self) -> str:
        """
        通过APP name 获取到app_id
        :param app_name:
        :return: app_id
        """
        describe_app_attributes_request = cloud_api20160714_models.DescribeAppAttributesRequest(
            app_name=self.app_name
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            query_result = self.apiclient.describe_app_attributes_with_options(describe_app_attributes_request, runtime)
            return query_result["Apps"]["AppAttribute"][0]["AppId"]
        except Exception as error:
            # 如有需要，请打印 error
            UtilClient.assert_as_string(error.message)

    def get_group_id_by_name(self) -> str:
        """
        通过group 获取到API Group 的唯一标识符
        :param group_name: API组名称
        :return: API分组 ID，系统生成，全局唯一
        """
        describe_api_groups_request = cloud_api20160714_models.DescribeApiGroupsRequest(
            group_name=self.group_name
        )
        runtime = util_models.RuntimeOptions()
        try:
            query_result = self.apiclient.describe_api_groups_with_options(describe_api_groups_request, runtime)
            return query_result["ApiGroupAttributes"]["ApiGroupAttribute"][0]["GroupId"]
        except Exception as error:
            UtilClient.assert_as_string(error.message)

    def get_api_ids_by_name(self) -> List[str]:
        group_id = self.get_group_id_by_name()
        api_ids = []
        for item in api_names:
            describe_apis_request = cloud_api20160714_models.DescribeApisRequest(
                group_id=self.get_group_id_by_name(),
                api_name=item
            )
            runtime = util_models.RuntimeOptions()
            try:
                query_result = self.apiclient.describe_apis_with_options(describe_apis_request, runtime)
                api_id = query_result["ApiSummarys"]["ApiSummary"][0]["ApiId"]
                api_ids.append(api_id)
            except Exception as error:
                UtilClient.assert_as_string(error.message)

    def set_apis_authorities(self):
        """
        通过给定的 group_name, app_name, api_names 分别获取到group_id,app_id 以及api_ids
        :param group_name: Group name
        :param app_name: app name
        :param api_names: api names
        :return:
        """
        set_apis_authorities_request = cloud_api20160714_models.SetApisAuthoritiesRequest(
            group_id=self.get_group_id_by_name(),
            app_id=self.get_app_id_by_name(),
            api_ids=self.get_api_ids_by_name()
        )
        runtime = util_models.RuntimeOptions()
        try:
            return self.apiclient.set_apis_authorities_with_options(set_apis_authorities_request, runtime)
        except Exception as error:
            UtilClient.assert_as_string(error.message)


if __name__ == '__main__':
    """
        目前采用hardcode 方式提交相关信息，后续可以有用户输入相关参数执行
    """

    app_name = "app_ywzt"
    api_group_name = "ywzt_test"
    api_names = ["a", "b", "c", "d"]
    client = AliyunUtils("apigateway.cn-hangzhou.aliyuncs.com", app_name, api_group_name, api_names)
    client.set_apis_authorities()
