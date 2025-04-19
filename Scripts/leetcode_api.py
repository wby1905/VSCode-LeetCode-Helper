#!/usr/bin/env python3
"""
LeetCode GraphQL API客户端
使用gql库实现与LeetCode API的交互，替代原来的字符串解析方式
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union
import requests

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("LeetCodeAPI")

# LeetCode GraphQL API端点
LEETCODE_CN_API_URL = "https://leetcode.cn/graphql"
LEETCODE_CN_PROBLEMS_URL = "https://leetcode.cn/api/problems/all/"


class LeetCodeAPI:
    """LeetCode API客户端类"""

    def __init__(self, use_cn: bool = True):
        """
        初始化LeetCode API客户端

        Args:
            use_cn: 是否使用中国区LeetCode (leetcode.cn)
        """
        # 选择API端点
        self.api_url = LEETCODE_CN_API_URL

        # 创建HTTP传输
        transport = RequestsHTTPTransport(
            url=self.api_url,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            },
            use_json=True,
        )

        # 创建GQL客户端
        self.client = Client(transport=transport, fetch_schema_from_transport=False)
        logger.info(f"LeetCode API客户端已初始化，使用端点: {self.api_url}")

    def get_daily_question(self) -> Dict[str, Any]:
        """
        获取LeetCode每日一题信息

        Returns:
            字典，包含题目ID、标题和难度
        """
        logger.info("正在获取每日一题...")

        # 定义GraphQL查询
        query = gql(
            """
        query questionOfToday {
            todayRecord {
                question {
                    questionFrontendId
                    title
                    titleSlug
                    difficulty
                }
            }
        }
        """
        )

        try:
            # 执行查询
            result = self.client.execute(query)

            # 提取题目信息
            question = result["todayRecord"][0]["question"]
            question_info = {
                "id": question["questionFrontendId"],
                "title": question["title"],
                "title_slug": question["titleSlug"],
                "difficulty": question["difficulty"],
            }

            logger.info(
                f"成功获取每日一题: {question_info['id']} - {question_info['title']}"
            )
            return question_info

        except Exception as e:
            logger.error(f"获取每日一题失败: {str(e)}")
            raise

    def get_problem_details(self, title_slug: str) -> Dict[str, Any]:
        """
        获取题目详情

        Args:
            title_slug: 题目的标题Slug

        Returns:
            字典，包含题目的详细信息
        """
        logger.info(f"正在获取题目详情: {title_slug}")

        # 定义GraphQL查询
        query = gql(
            """
        query questionData($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                questionId
                questionFrontendId
                title
                titleSlug
                difficulty
                topicTags {
                    name
                    slug
                    translatedName
                }
                content
                translatedTitle
                translatedContent
                codeSnippets {
                    lang
                    langSlug
                    code
                }
                sampleTestCase
                metaData
                exampleTestcases
            }
        }
        """
        )

        try:
            # 执行查询
            variables = {"titleSlug": title_slug}
            result = self.client.execute(query, variable_values=variables)

            question = result["question"]

            # 处理元数据
            meta_data = {}
            try:
                if question.get("metaData"):
                    meta_data = json.loads(question.get("metaData", "{}"))
            except Exception as e:
                logger.warning(f"解析元数据时出错: {str(e)}")

            # 构建题目信息字典
            problem_info = {
                "id": question["questionFrontendId"],
                "title": question["translatedTitle"] or question["title"],
                "title_slug": question["titleSlug"],
                "difficulty": question["difficulty"],
                "topics": [
                    tag["translatedName"] or tag["name"]
                    for tag in question["topicTags"]
                ],
                "content": question["translatedContent"] or question["content"],
                "code_snippets": {
                    snippet["langSlug"]: snippet["code"]
                    for snippet in question["codeSnippets"]
                },
                "test_cases": question.get("exampleTestcases", "")
                or question.get("sampleTestCase", ""),
                "meta_data": meta_data,
            }

            logger.info(
                f"成功获取题目详情: {problem_info['id']} - {problem_info['title']}"
            )
            return problem_info

        except Exception as e:
            logger.error(f"获取题目详情失败: {str(e)}")
            raise

    def get_problem_by_id(self, problem_id: str) -> Dict[str, Any]:
        """
        根据题号获取题目详情

        Args:
            problem_id: 题目ID

        Returns:
            字典，包含题目的详细信息
        """
        logger.info(f"正在获取题号为 {problem_id} 的题目信息")

        try:
            # LeetCode中国站的API与国际版不同，需要先通过problems/all接口获取titleSlug
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            }
            response = requests.get(LEETCODE_CN_PROBLEMS_URL, headers=headers)

            if response.status_code != 200:
                logger.error(f"获取题目列表失败，状态码: {response.status_code}")
                raise Exception(f"API请求失败，状态码: {response.status_code}")

            problems_data = response.json()
            title_slug = None

            # 在问题列表中找到对应题号的题目
            for problem in problems_data.get("stat_status_pairs", []):
                if str(problem["stat"]["frontend_question_id"]) == str(problem_id):
                    title_slug = problem["stat"]["question__title_slug"]
                    break

            if not title_slug:
                logger.error(f"找不到题号为 {problem_id} 的题目")
                raise ValueError(f"找不到题号为 {problem_id} 的题目")

            logger.info(f"找到题号 {problem_id} 对应的title_slug: {title_slug}")

            # 通过title_slug获取完整题目详情
            return self.get_problem_details(title_slug)

        except Exception as e:
            logger.error(f"获取题号 {problem_id} 的题目信息失败: {str(e)}")
            raise


# 使用示例
if __name__ == "__main__":
    api = LeetCodeAPI()

    # 获取每日一题
    try:
        daily_question = api.get_daily_question()
        print(f"每日一题: {daily_question['id']} - {daily_question['title']}")
    except Exception as e:
        print(f"获取每日一题失败: {str(e)}")

    # 根据题号获取题目详情
    try:
        problem_id = "1"  # 示例题号
        problem_info = api.get_problem_by_id(problem_id)
        print(f"题号 {problem_id} 的题目: {problem_info['title']}")
        print(f"难度: {problem_info['difficulty']}")
        print(f"标签: {', '.join(problem_info['topics'])}")
    except Exception as e:
        print(f"获取题目详情失败: {str(e)}")
