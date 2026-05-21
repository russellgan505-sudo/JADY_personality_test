import streamlit as st
import pandas as pd
import os
import plotly.express as px

st.set_page_config(page_title="JADY 测试结果后台", page_icon="📊", layout="wide")
st.title("📊 JADY 性格测试 - 智能数据看板")

file_path = "测试结果收集表.csv"

if os.path.exists(file_path):
    # 读取原始数据
    df = pd.read_csv(file_path)

    # 为了兼容旧数据（如果之前的测试数据没有耗时列，先补上0防止报错）
    if '答题耗时(秒)' not in df.columns:
        df['答题耗时(秒)'] = 999

        # ================= 侧边栏：数据清洗控制台 =================
    with st.sidebar:
        st.header("🧽 数据清洗控制台")
        st.write("开启以下规则，系统将自动过滤无效问卷：")

        # 规则 1：过滤耗时过短
        # 30道题，按每题至少2秒算，低于60秒基本上是乱填
        min_seconds = st.slider("1. 最短有效答题时间(秒)", min_value=0, max_value=300, value=60, step=10)

        # 规则 2：去重机制
        remove_duplicate = st.checkbox("2. 自动合并重复提交", value=True,
                                       help="如果同一姓名多次提交，仅保留最新一次的数据。")

        # 规则 3：直线作答检测 (选填项，供参考)
        anti_straight_line = st.checkbox("3. 过滤敷衍作答 (如全选A)", value=False,
                                         help="如果某个人超过 25 道题都选了同一个选项，将被判定为无效作答。")

    # ================= 数据清洗执行引擎 (Pandas) =================
    df_clean = df.copy()

    # 执行规则 1
    df_clean = df_clean[df_clean['答题耗时(秒)'] >= min_seconds]

    # 执行规则 2：利用 pandas 强大的去重功能，基于姓名去重，保留最后一次(last)
    if remove_duplicate:
        df_clean = df_clean.drop_duplicates(subset=['姓名'], keep='last')

    # 执行规则 3：计算敷衍作答
    if anti_straight_line:
        valid_indices = []
        for index, row in df_clean.iterrows():
            # 提取该行第1到30题的所有答案拼成一个列表
            answers_list = [str(row.get(f"第{i}题", "")) for i in range(1, 31)]
            # 统计最高频选项的数量
            max_same_answer = max(
                [answers_list.count("A"), answers_list.count("B"), answers_list.count("C"), answers_list.count("D")])
            # 如果没有一个选项超过 25 个，才算有效
            if max_same_answer < 25:
                valid_indices.append(index)
        df_clean = df_clean.loc[valid_indices]

    # ================= 核心指标看板 =================
    st.write("### 👥 数据概况")
    col1, col2, col3 = st.columns(3)
    col1.metric("原始收集总数", f"{len(df)} 份")
    col2.metric("清洗后有效总数", f"{len(df_clean)} 份", delta=f"-{len(df) - len(df_clean)} 份 (已过滤)",
                delta_color="inverse")

    # 如果清洗后还有数据，就展示图表
    if len(df_clean) > 0:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📈 主要性格分布")
            # 统计频次并转为 DataFrame 给 Plotly 用
            type_counts = df_clean['主要性格'].value_counts().reset_index()
            type_counts.columns = ['性格', '人数']

            # 画多彩柱状图：指定x轴、y轴，用不同颜色区分，并在柱子上显示具体数字
            fig1 = px.bar(type_counts, x='性格', y='人数', color='性格', text='人数',
                          color_discrete_sequence=px.colors.qualitative.Pastel)  # 使用柔和的马卡龙色系

            # 优化图表外观：文字强制横向，固定柱子间距(宽度一致)，隐藏图例
            fig1.update_layout(xaxis_tickangle=0, showlegend=False, bargap=0.4,
                               margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.subheader("💡 平均得分概览")
            # 提取平均分
            avg_scores = df_clean[['交流型(ZQ)', '完美型(TZ)', '力量型(WS)', '稳健型(ST)']].mean().round(1)

            # 把冗长的底层标签替换为简短的字母组合
            score_data = pd.DataFrame({
                '维度': ['ZQ', 'TZ', 'WS', 'ST'],
                '分数': avg_scores.values
            })

            # 画图并使用另一套配色
            fig2 = px.bar(score_data, x='维度', y='分数', color='维度', text='分数',
                          color_discrete_sequence=px.colors.qualitative.Set2)

            fig2.update_layout(xaxis_tickangle=0, showlegend=False, bargap=0.4,
                               margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig2, use_container_width=True)

            # 在图表正下方补充说明文字，解决拥挤问题
            st.caption("📌 **指标说明：** ZQ(交流型) | TZ(完美型) | WS(力量型) | ST(稳健型)")

        st.divider()

        st.subheader("📋 有效答题明细数据")
        st.write(f"当前表格展示的是经过侧边栏规则清洗后的 **{len(df_clean)} 条** 高质量数据。")
        # 把耗时列移到前面方便看
        cols = df_clean.columns.tolist()
        if '答题耗时(秒)' in cols:
            cols.insert(1, cols.pop(cols.index('答题耗时(秒)')))
            df_clean = df_clean[cols]

        st.dataframe(df_clean, use_container_width=True)
    else:
        st.warning("当前清洗规则过于严格，所有问卷都被过滤掉了，请调整左侧阈值。")

else:
    st.info("💡 目前还没有人提交测试结果，快去把答题链接发给朋友们吧！")