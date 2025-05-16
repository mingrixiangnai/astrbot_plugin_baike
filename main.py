import aiohttp
import json
from urllib.parse import quote
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api.message_components import Plain

@register("astrbot_plugin_baike", "mingrixiangnai", "百科查询插件", "1.0", "https://github.com/mingrixiangnai/astrbot_plugin_baike")
class WikiPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        #添加请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Referer': 'https://free.wqwlkj.cn/'
        }

    @filter.command("百科")
    async def query_wiki(self, event: AstrMessageEvent):
        '''查询百科词条'''
        args = event.message_str.split(maxsplit=1)
        if len(args) < 2:
            return event.plain_result("请输入查询词条，例如：/百科 丁真")

        keyword = args[1]
        try:
            encoded_keyword = quote(keyword, safe='')#需要输入的文字
            api_url = f"https://free.wqwlkj.cn/wqwlapi/baidu_bk.php?msg={encoded_keyword}&type=json"#接口
            
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(api_url) as resp:
                    raw_response = await resp.text()
                    json_data = json.loads(raw_response)
                    
                    # 直接访问 data.info 字段
                    if "data" not in json_data:
                        #logger.error("响应缺少data字段")
                        return event.plain_result("百科数据格式异常：响应缺少data字段")
                        
                    data_obj = json_data["data"]
                    if "info" not in data_obj:
                        #logger.error("data对象缺少info字段")
                        return event.plain_result("百科内容格式异常：data对象缺少info字段")
                        
                    info_content = data_obj["info"]
                    
                    # 内容类型验证
                    if not isinstance(info_content, str):
                        logger.error(f"info字段类型错误：{type(info_content)}")
                        return event.plain_result("百科内容格式异常：info字段类型错误")
                    
                    # 清理与格式化，“1000”可以修改（防止机器人刷屏），改的话改两个，保持一致
                    cleaned_content = " ".join(info_content.strip().split())
                    if len(cleaned_content) > 1000: #改这里
                        cleaned_content = cleaned_content[:1000] + "……" #这里也改
                        
                    return event.plain_result(
                        f"📚 {keyword}\n\n{cleaned_content}\n\n数据来源：百度百科（请自行鉴别真假）"
                    )

        except aiohttp.ClientError as e:
            logger.error(f"请求失败：{str(e)}")
            return event.plain_result("百科服务暂时不可用：请求失败")
        except json.JSONDecodeError:
            #logger.error("JSON解析失败")
            return event.plain_result("百科数据解析错误：JSON解析失败")
        except Exception as e:
            logger.error(f"未捕获异常：{str(e)}", exc_info=True)
            return event.plain_result("查询出现未知错误：未捕获异常")

    async def terminate(self):
        pass