#简历提取器
#生成一段代码，用于提取一个目录下所有pdf简历中的文本信息,并进行单独归档
#该代码采用的阿里千问的大模型，具体的大模型是可以替换的

import os
import PyPDF2
import broadscope_bailian
import json

def calculate_score(text):
   
    #此提示词可以根据岗位JD 进行提取，先手动提取吧,以下是我原始的岗位JD,提取完毕后为我们的自己的提示词，该段也可以封装，感兴趣小伙伴自己处理吧
    """
    岗位职责：
    1、根据公司品牌战略和定位，策划并负责公司级重大品牌发布、合作活动，提升行业影响力，塑造公司品牌；
    2、负责媒体活动策划项目的整体管理，包括项目计划制定、进度控制、预算管理，包括协调人和资源有效利用和高效执行，及时发现处理项目中出现的问题，确保项目按时按质完成；
    3、紧跟热点，洞察市场和用户，持续挖掘符合品牌、产品传播需求的策划和创意，策划事件、内容。分析竞品的新媒体策略和活动案例，提炼优点和不足，为品牌提供参考和借鉴；
    4、统筹集团自媒体矩阵管理，负责品牌自媒体平台的内容创意和运营。
    5、追踪和分析各类媒体平台的数据评估策略的有效性，并以结果为导向，持续迭代调整策略；
    6、完成领导交办的其它工作。
    任职要求：
    1、第一学历，统招本科以上学历，新闻、传播、广告、营销专业优先，5年以上品牌策划、项目管理经验优先；
    2、品牌营销策略功底扎实，展现前瞻视野和敏锐的市场洞察力，准确把握市场趋势与行业需求；
    3、拥有体系化的传播策略与全案策划执行能力,擅长整合内外部资源，具备从策略规划到项目落地的全过程推动力，确保品牌项目按时按质完成；
    4、具备扎实的文字功底和创新文案创作能力，良好的品牌感知力与美学素养；
    5、出色的跨部门沟通协调能力，善于快速建立合作关系，适应快节奏工作环境；
    """
    prompts="""
    你是一个资深的人力资源经理，现在要进行简历筛选,
    
    # 岗位名称：品牌策划与项目管理人员
    
    ## 候选人角色概述
    - 负责公司品牌战略的执行和媒体活动的策划与项目管理。
    ## 筛选标准
    ### 教育背景
    - 必须具有统招本科及以上学历。
    - 新闻、传播、广告、营销等相关专业优先。
    
    ### 工作经验
    - 至少5年品牌策划和项目管理经验。
    - 有成功策划大型品牌活动和媒体活动案例者优先。
    
    ### 专业技能
    - 强大的品牌营销策略制定和执行能力。
    - 出色的市场洞察力和内容创意能力。
    - 熟练的数据分析和媒体平台效果评估技能。
    
    ### 个人素质
    - 良好的文字功底和创新文案创作能力。
    - 出色的跨部门沟通协调能力和团队合作精神。
    - 能够适应快节奏的工作环境。
    ## 筛选流程
    1. **简历审查**: 检查候选人的教育背景和工作经验是否符合基本要求。
    2. **技能匹配**: 评估候选人的专业技能和个人素质是否满足岗位需求。
    3. **案例分析**: 审查候选人过往的品牌策划和项目案例，验证其实际操作能力。
    4. **优先级排序**: 根据候选人的综合条件进行排序，筛选出最符合条件的候选人，分为：高度合适，合适，不合适三个级别
    5. **面试推荐**: 为符合条件的候选人安排面试，进一步评估其适应性和潜力。
    ## 操作指令
    严格按照以下格式返回数据
    {
        "优先级排序":
        "总体评价":
    }
    ## 简历信息为:
    """
    access_key_id = ""
    access_key_secret = ""
    agent_key = ""
    appid = ""
    client = broadscope_bailian.AccessTokenClient(access_key_id=access_key_id, access_key_secret=access_key_secret,
                                                      agent_key=agent_key)
    token = client.get_token()
    resp = broadscope_bailian.Completions(token=token).create(
            app_id=appid,
            prompt=prompts+text,
            # 返回文档检索的文档引用数据, 传入为simple或indexed
            doc_reference_type="simple",
            # 文档标签code列表
            doc_tag_codes=[],
            stream=False,
        )
    if resp['Success'] == True:
                return resp['Data']['Text']
    else:
        return "error"
# 指定简历所在目录
directory = '--简历存在的目录--'
csvfile= open('--输出文件的目录--', 'a') 
num=1
# 遍历目录下所有pdf文件
for filename in os.listdir(directory):
    if filename.endswith('.pdf'):
        # 打开并读取PDF文件
        with open(os.path.join(directory, filename), 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            # 初始化文本变量
            text = ''
            # 遍历PDF文件中的所有页面
            for page_num in range(len(pdf_reader.pages)):
                # 提取每一页的文本
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
        res = calculate_score(text)
        if res != "error":
            try:
             #将res字典中的每一项写入csv文件
                res=json.loads(res)
                csvfile.write(str(filename)+',')
                for key, value in res.items():
                    #判断是否为数字
                    if isinstance(value, (int, float)):
                        csvfile.write(str(value)+',')
                    else:
                        csvfile.write(value+',')
                csvfile.write('\n')
                print(f"是个快乐的打工仔，🤖正在为你打工，🥰 +"+str(num))
                num += 1
            except json.JSONDecodeError as e:
                # 打印json错误信息
                print(res)
                print(f"发生错误：{filename}")
            
        # 将提取的文本写入对应的TXT文件
        # output_filename = f'{os.path.splitext(filename)[0]}.txt'
        # with open(os.path.join(directory, output_filename), 'w') as output_file:
        #     output_file.write(text)

