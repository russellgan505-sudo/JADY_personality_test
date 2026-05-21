import streamlit as st
import pandas as pd
import os
from datetime import datetime
import time # 新增：用于计算耗时

# ================= 1. 页面设置 =================
st.set_page_config(page_title="JADY 性格测试", page_icon="📝", layout="centered")

# 新增：隐形秒表。用户一打开网页，就记录下当前时间存入缓存
if 'start_time' not in st.session_state:
    st.session_state['start_time'] = time.time()

st.title("JADY 个人性格度测试")
st.info(
    "填写须知：\n1. 每道题只能够选择 1 个答案，不能够多选。\n2. 所有问题的答案都不存在好坏或者对错之分，请不要犹豫，你的真实最重要。\n3. 请顺从你的内心世界而非你的脑袋思考，选择你最真实最本能的反应，否则最终结果会失真。")

# ================= 2. 完整题库录入 (1-30题) =================
questions = [
    {"id": 1, "text": "我的人生观是：", "options": ["A. 人生的体验越多越好，所以想法很多，有可能就应该多尝试。",
                                                   "B. 深度比宽度更重要，目标要谨慎，一旦确定就坚持到底。",
                                                   "C. 人生必须有所成。", "D. 没必要太辛苦，好好活着就行。"]},
    {"id": 2, "text": "如果野外旅游，在下山返回的路线上，我更在乎：",
     "options": ["A. 要好玩有趣，不愿重复，所以宁愿走新路线。", "B. 要安全稳妥，担心危险，所以宁愿走原路线。",
                 "C. 要挑战自我，喜欢冒险，所以宁愿走新路线。", "D. 要方便省心，害怕麻烦，所以宁愿走原路线。"]},
    {"id": 3, "text": "在表达一件事上，别人认为我：",
     "options": ["A. 总是给人感受到强烈印象。", "B. 总是表述极其准确。", "C. 总能围绕最终目的。", "D. 总能让大家很舒服。"]},
    {"id": 4, "text": "在生命多数时候，我其实更希望：", "options": ["A. 刺激", "B. 安全", "C. 挑战", "D. 稳定"]},
    {"id": 5, "text": "我认为自己在感情上的基本特点是：",
     "options": ["A. 情绪多变，情绪波动大。", "B. 外表抑制强，但内心起伏大，一旦挫伤难以平复。", "C. 感情不拖泥带水，较直接。",
                 "D. 天性四平八稳。"]},
    {"id": 6, "text": "我认为自己除了工作以外，在人生的控制欲上，我：",
     "options": ["A. 谈不上控制欲，却有强烈地能感染带动他人的欲望，但自控能力不强。",
                 "B. 用规则来保持我的自控和对他人的要求。", "C. 内心有控制欲，希望别人服从我。",
                 "D. 从不愿去管别人，也不愿别人来管我。"]},
    {"id": 7, "text": "当与情人交往时，我倾向于：",
     "options": ["A. 在一起时就要尽情地欢乐，爱意常会溢于言表。", "B. 体贴入微关怀细腻，于对方的需求变化很敏感。",
                 "C. 帮助对方成长是我最大的责任。", "D. 迁就顺从的陪伴者和绝佳的聆听者。"]},
    {"id": 8, "text": "在人际交往时，我：",
     "options": ["A. 心态放开，可快速建立起人际关系。", "B. 非常审慎缓慢地深入，一旦认为是朋友便会长久。",
                 "C. 希望在人际交往中占据主导地位。", "D. 顺其自然，不温不火，相对被动。"]},
    {"id": 9, "text": "我认为自己的为人：",
     "options": ["A. 可爱而生机。", "B. 深沉而内敛。", "C. 果断而自信。", "D. 平静而和气。"]},
    {"id": 10, "text": "我完成任务的方式是：",
     "options": ["A. 常赶在最后期限前的一刻完成。", "B. 自己精确地做，不麻烦别人。", "C. 最快速做完，再找下一个任务。",
                 "D. 该怎么做就怎么做，需要时从他人处得到帮忙。"]},
    {"id": 11, "text": "如果有人深深惹恼我时，我：",
     "options": ["A. 内心受伤，当时认为不可原谅，但最终常会原谅对方。", "B. 如此之深的愤怒无法忘记，同时未来避开那个家伙。",
                 "C. 每个人都要为他的错误付出相应的代价，内心期望有机会要狠狠地回应。",
                 "D. 尽量不摊牌，因为还不到那个地步。"]},
    {"id": 12, "text": "在人际关系中，我最在意的是：", "options": ["A. 欢迎。", "B. 理解。", "C. 尊敬。", "D. 接纳。"]},
    {"id": 13, "text": "在工作上，我表现出更多的是：",
     "options": ["A. 热枕，有很多想法且很有灵性。", "B. 完美精确且承诺可靠。", "C. 坚强而推有动力。",
                 "D. 有耐心且适应性强。"]},
    {"id": 14, "text": "我过往的老师最有可能对我的评价是：",
     "options": ["A. 善于表达和抒发情感。", "B. 严格保护自己的私密，有时会显得孤独或不合群。",
                 "C. 动作敏捷独立，且喜欢自己做事情。", "D. 反应度偏低，比较温和。"]},
    {"id": 15, "text": "朋友对我的评价最有可能的是：",
     "options": ["A. 喜欢对朋友倾述事情，是开心果。", "B. 能提出很多问题，且需要许多精细的解说。", "C. 解决问题的高手。",
                 "D. 总是多听少说。"]},
    {"id": 16, "text": "在帮助他人的问题上，我倾向于：",
     "options": ["A. 我不主动，旦若他来找我，那我一定帮。", "B. 值得帮助的人就帮。", "C. 无关者何必帮，但我若承诺，必完成。",
                 "D. 虽无英雄打虎胆，常有自告奋勇心。"]},
    {"id": 17, "text": "面对他人对自己的赞美，我的本能反应是：",
     "options": ["A. 没有赞美也无所谓，得到了也不至于欣喜。", "B. 我无须那些没用的赞美，宁可欣赏我的能力。",
                 "C. 有点怀疑对方是否认真或立即回避很多人的关注。", "D. 能得到赞美，总归是一件令人愉悦的事。"]},
    {"id": 18, "text": "面对生活的现状，我更倾向于：", "options": ["A. 外面怎样与我无关，我觉得自己这样就行。",
                                                                 "B. 这个世界如果我不进步，别人就会进步，所以我需要不停地前进。",
                                                                 "C. 在所有的问题未发生前，就该尽量想好所有的可能性。",
                                                                 "D. 每天的生活，只有开心快乐最重要。"]},
    {"id": 19, "text": "对于规则，我内心的态度是：",
     "options": ["A. 不愿违反规则，但可能因为松散而无法到规则要求。", "B. 打破规则，希望由自己来制定，而不是遵守规则。",
                 "C. 严格遵守规则，且竭力全力做到规则内的最好。", "D. 不喜欢被规则束缚，不按规则出牌，会觉得有趣。"]},
    {"id": 20, "text": "我认为自己做事上：",
     "options": ["A. 慢条斯理，按部就班，能与周围协调一致。", "B. 目标明确，聚焦为实现目标而努力，善于抓住核心。",
                 "C. 慎重小心，为做好预防及善后，会尽心操劳。", "D. 丰富跃动，灵活反应。"]},
    {"id": 21, "text": "在面对压力时，我比较倾向于选用：",
     "options": ["A. 眼不见为净。", "B. 压力越大，抵抗力越大。", "C. 在自己的内心慢慢地咀嚼消化压力。",
                 "D. 本能地回避压力，避不掉就用各种方法宣泄出去。"]},
    {"id": 22, "text": "当结束一段刻骨铭心的感情是，我会：",
     "options": ["A. 日子总要过，时间会冲淡一切。", "B. 虽然受伤，一旦决定就会努力把过去的影子甩掉。",
                 "C. 深陷悲伤，长时间难以自拔，也不接受新的人。", "D. 痛不欲生，需要找朋友倾诉，寻求化解之道。"]},
    {"id": 23, "text": "面对他人的痛苦倾诉，我回顾自己大多数时候本能上倾向于：",
     "options": ["A. 静静地听，认同对方的感受。", "B. 作出判断，痛苦没用，要帮助对方解决问题。",
                 "C. 给予分析，帮助他分析，安抚他的情绪。", "D. 发表自己的评论意见，与对方的情绪共起落。"]},
    {"id": 24, "text": "我在以下哪个群体中较感满足？",
     "options": ["A. 能心平气和，只要大家达成一致。", "B. 能简单扼要有结果地彼此展开充分的辩论。",
                 "C. 能就一件事情有规则、有条理、有步骤地详细讨论。", "D. 能随意无拘束地、开心地自由谈话。"]},
    {"id": 25, "text": "我觉得工作：",
     "options": ["A. 最好没有压力，让我做我熟悉的工作就不错。", "B. 是达成人生目标和成就最重要的途径。",
                 "C. 要么不做，要做就做到最好。", "D. 最喜欢工作与乐趣合一，做不喜欢的工作实在没劲。"]},
    {"id": 26, "text": "如果我是领导，我内心更希望在部属的心目中，我是：",
     "options": ["A. 可以亲近的和善于为他们着想。", "B. 有很强的能力和富有领导力的。", "C. 公平公正且足以信赖的。",
                 "D. 被他们喜欢并且觉得富有感召力的。"]},
    {"id": 27, "text": "我希望得到的认同方式是：",
     "options": ["A. 有无认同都不影响我。", "B. 精英的认同最重要。", "C. 我认同的人或我在乎的人认同就可。",
                 "D. 希望大家都能认同我。"]},
    {"id": 28, "text": "当我还是个孩子时，我：",
     "options": ["A. 不太会积极尝试新事物，通常比较喜欢旧有的和熟悉的。", "B. 是孩子王，大家经常听我的决定。",
                 "C. 害羞生人，有意识地回避。", "D. 调皮可爱，大部分的情况下是多动且热心的。"]},
    {"id": 29, "text": "如果我是父母，我也许是：",
     "options": ["A. 不愿干涉子女或易被说动的。", "B. 严厉的或直接给予方向指点的。",
                 "C. 用行动代替语言来表示关爱或高要求的。", "D. 愿意陪孩子一起玩，孩子的朋友们所喜欢和欢迎的。"]},
    {"id": 30, "text": "以下有四组格言，哪组里符合我感觉的数目最多？", "options": [
        "A. 最深刻的真理是最简单和最平凡的。 / 要在人世间取得成功必须大智若愚。 / 好脾气是一个人再社交中所能穿着的最佳服饰。 / 知足是人生在世最大的幸福。",
        "B. 走自己的路，让人家去说吧。 / 虽然世界充满了苦难总能被战胜。 / 有所成就是人生唯一的真正的乐趣。 / 对我而言，解决一个问题和享受一个假期一样好。",
        "C. 一个不注意小事的人，永远不会成就大事。 / 理性是灵魂中最高的因素。 / 切忌浮夸，与其说得过分，不如说得不全。 / 谨慎比大胆要有力量得多。",
        "D. 与其临死很多钱，还不如活时花着痛快。 / 任何时候都要最真实地对待你自己，这比什么都重要。 / 使生活变成幻想，再把幻想化为现实。 / 和喜欢的人在一起做喜欢的事是莫大的快乐。"]}
]

# ================= 3. 表单收集区 =================
answers = {}

with st.form("survey_form"):
    # 遍历 30 道选择题
    for q in questions:
        st.markdown(f"**第 {q['id']} 题：{q['text']}**")
        # index=None 保证默认不选中任何选项
        choice = st.radio("请选择", q['options'], key=f"q_{q['id']}", label_visibility="collapsed", index=None)

        if choice:
            answers[q['id']] = choice[0]  # 提取 A, B, C 或 D
        st.divider()

    # 附加信息区：基本信息
    st.markdown("### 📋 基本信息填写")
    col1, col2 = st.columns(2)
    with col1:
        user_name = st.text_input("姓名 (必填) *")
        user_age = st.text_input("年龄")
    with col2:
        user_gender = st.selectbox("性别", ["男", "女", "保密"], index=None)
        user_position = st.text_input("岗位职务")

    st.divider()

    # 附加信息区：自我评价
    st.markdown("### 🪞 自我评价")
    st.write("请列举您性格中最大的 **3 个缺点**（一直为您所控）：")
    c1, c2, c3 = st.columns(3)
    weak1 = c1.text_input("缺点 1")
    weak2 = c2.text_input("缺点 2")
    weak3 = c3.text_input("缺点 3")

    st.write("请列举您性格中最大的 **3 个优点**（未来您选其所用）：")
    c4, c5, c6 = st.columns(3)
    str1 = c4.text_input("优点 1")
    str2 = c5.text_input("优点 2")
    str3 = c6.text_input("优点 3")

    st.write("")  # 留点空隙
    submitted = st.form_submit_button("提交并计算我的性格特质", type="primary")

# ================= 4. 后台计算与保存 =================
if submitted:
    # 校验 30 道题是否全部做完，且填了名字
    if len(answers) < 30 or not user_name.strip():
        st.error("⚠️ 提交失败：请确保完成所有 30 道选择题，并填写您的姓名！")
    else:
        st.balloons()
        st.success(f"感谢提交，{user_name}！您的性格数据分析如下：")

        # 1. 统计选项分布 (甲区1-15，乙区16-30)
        jia_A = sum(1 for k, v in answers.items() if k <= 15 and v == 'A')
        jia_B = sum(1 for k, v in answers.items() if k <= 15 and v == 'B')
        jia_C = sum(1 for k, v in answers.items() if k <= 15 and v == 'C')
        jia_D = sum(1 for k, v in answers.items() if k <= 15 and v == 'D')

        yi_A = sum(1 for k, v in answers.items() if k > 15 and v == 'A')
        yi_B = sum(1 for k, v in answers.items() if k > 15 and v == 'B')
        yi_C = sum(1 for k, v in answers.items() if k > 15 and v == 'C')
        yi_D = sum(1 for k, v in answers.items() if k > 15 and v == 'D')

        # 2. 算分公式 (严格按照 Word 文档逻辑)
        score_ZQ = jia_A + yi_D  # 交流型
        score_TZ = jia_B + yi_C  # 完美型
        score_WS = jia_C + yi_B  # 力量型
        score_ST = jia_D + yi_A  # 稳健型

        # 3. 画出计分板
        st.subheader("📊 您的综合总计得分")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("交流型特质 (ZQ)", score_ZQ)
        col2.metric("完美型特质 (TZ)", score_TZ)
        col3.metric("力量型特质 (WS)", score_WS)
        col4.metric("稳健型特质 (ST)", score_ST)

        scores = {"ZQ 型 (交流型)": score_ZQ, "TZ 型 (完美型)": score_TZ, "WS 型 (力量型)": score_WS,
                  "ST 型 (稳健型)": score_ST}
        max_trait = max(scores, key=scores.get)

        st.markdown("---")
        st.markdown(f"### 🏆 您的主要性格特质是：**<span style='color:#FF4B4B'>{max_trait}</span>**",
                    unsafe_allow_html=True)
        st.caption("对于结果含义不明晰或者觉得与现实对自己性格判断不一致的，可以找助教/老师沟通。")

        end_time = time.time()
        duration_seconds = int(end_time - st.session_state['start_time'])

        # ================= 5. 将结果全面保存到本地 CSV 表格 =================
        result_data = {
            "提交时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "答题耗时(秒)": duration_seconds,  # 新增这一行，记录耗时
            "姓名": user_name,
            "性别": user_gender,
            "年龄": user_age,
            "岗位职务": user_position,
            "主要性格": max_trait,
            "交流型(ZQ)": score_ZQ,
            "完美型(TZ)": score_TZ,
            "力量型(WS)": score_WS,
            "稳健型(ST)": score_ST,
            "缺点1": weak1, "缺点2": weak2, "缺点3": weak3,
            "优点1": str1, "优点2": str2, "优点3": str3
        }
        # 把 1-30 题的具体选项追加进记录
        for k, v in answers.items():
            result_data[f"第{k}题"] = v

        # 转换为 Pandas 数据表并保存
        df = pd.DataFrame([result_data])
        file_path = "测试结果收集表.csv"

        # 自动追加写入表格
        if os.path.exists(file_path):
            df.to_csv(file_path, mode='a', header=False, index=False, encoding='utf-8-sig')
        else:
            df.to_csv(file_path, mode='w', header=True, index=False, encoding='utf-8-sig')