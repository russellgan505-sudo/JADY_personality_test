import streamlit as st
import pandas as pd
import os
import plotly.express as px

# ================= 1. 页面与 UI 设置 =================
st.set_page_config(page_title="JADY 测试结果后台", page_icon="📊", layout="wide")

# 🌟 高级美化：注入 CSS 代码，隐藏右上角的默认菜单和底部的 Streamlit 水印
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

st.title("📊 JADY 性格测试 - 智能数据看板")

file_path = "测试结果收集表.csv"

if os.path.exists(file_path):
    # 读取原始数据
    df = pd.read_csv(file_path)

    # 为了兼容旧数据
    if '答题耗时(秒)' not in df.columns:
        df['答题耗时(秒)'] = 999

    # ================= 2. 侧边栏：控制中心 =================
    with st.sidebar:
        st.header("🧽 数据清洗控制台")
        st.write("开启以下规则，系统将自动过滤无效问卷：")

        # 规则 1：过滤耗时过短
        min_seconds = st.slider("1. 最短有效答题时间(秒)", min_value=0, max_value=300, value=60, step=10)

        # 规则 2：去重机制
        remove_duplicate = st.checkbox("2. 自动合并重复提交", value=True,
                                       help="如果同一姓名多次提交，仅保留最新一次的数据。")

        # 规则 3：直线作答检测
        anti_straight_line = st.checkbox("3. 过滤敷衍作答 (如全选A)", value=False,
                                         help="如果某个人超过 25 道题都选了同一个选项，将被判定为无效作答。")

        # ---------------- 危险操作区域 ----------------
        st.divider()
        st.markdown("### 🚨 数据删除控制台")

        # 功能 A：精准删除指定数据
        st.write("**1. 删除单条/多条数据**")
        if len(df) > 0:
            delete_options = df.apply(lambda row: f"[行号:{row.name}] {row['姓名']} - {row['提交时间']}",
                                      axis=1).tolist()
            selected_to_delete = st.multiselect("请选择要永久删除的记录：", delete_options)

            if st.button("🗑️ 删除选中的记录", disabled=len(selected_to_delete) == 0):
                indices_to_drop = [int(opt.split("]")[0].split(":")[1]) for opt in selected_to_delete]
                df_updated = df.drop(index=indices_to_drop)
                df_updated.to_csv(file_path, index=False, encoding='utf-8-sig')
                st.sidebar.success("✅ 选中的记录已永久删除！")
                st.rerun()
        else:
            st.info("当前暂无数据可删。")

        st.write("---")

        # 功能 B：一键清空全部数据
        st.write("**2. 清空全部历史数据**")
        confirm_delete = st.checkbox("我已知晓此操作不可逆，确认全部清空", value=False)

        if st.button("💥 清空所有数据", type="primary", disabled=not confirm_delete):
            if os.path.exists(file_path):
                os.remove(file_path)
                st.sidebar.success("💥 数据已全部清空！")
                st.rerun()

    # ================= 3. 数据清洗执行引擎 =================
    df_clean = df.copy()

    df_clean = df_clean[df_clean['答题耗时(秒)'] >= min_seconds]

    if remove_duplicate:
        df_clean = df_clean.drop_duplicates(subset=['姓名'], keep='last')

    if anti_straight_line:
        valid_indices = []
        for index, row in df_clean.iterrows():
            answers_list = [str(row.get(f"第{i}题", "")) for i in range(1, 31)]
            max_same_answer = max(
                [answers_list.count("A"), answers_list.count("B"), answers_list.count("C"), answers_list.count("D")])
            if max_same_answer < 25:
                valid_indices.append(index)
        df_clean = df_clean.loc[valid_indices]

    # ================= 4. 核心指标与图表看板 =================
    st.write("### 👥 数据概况")
    col1, col2, col3 = st.columns(3)
    col1.metric("原始收集总数", f"{len(df)} 份")
    col2.metric("清洗后有效总数", f"{len(df_clean)} 份", delta=f"-{len(df) - len(df_clean)} 份 (已过滤)",
                delta_color="inverse")

    if len(df_clean) > 0:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📈 主要性格分布")
            type_counts = df_clean['主要性格'].value_counts().reset_index()
            type_counts.columns = ['性格', '人数']

            fig1 = px.bar(type_counts, x='性格', y='人数', color='性格', text='人数',
                          color_discrete_sequence=px.colors.qualitative.Pastel)

            fig1.update_layout(xaxis_tickangle=0, showlegend=False, bargap=0.4,
                               margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.subheader("💡 平均得分概览")
            avg_scores = df_clean[['交流型(ZQ)', '完美型(TZ)', '力量型(WS)', '稳健型(ST)']].mean().round(1)

            score_data = pd.DataFrame({
                '维度': ['ZQ', 'TZ', 'WS', 'ST'],
                '分数': avg_scores.values
            })

            fig2 = px.bar(score_data, x='维度', y='分数', color='维度', text='分数',
                          color_discrete_sequence=px.colors.qualitative.Set2)

            fig2.update_layout(xaxis_tickangle=0, showlegend=False, bargap=0.4,
                               margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig2, use_container_width=True)

            st.caption("📌 **指标说明：** ZQ(交流型) | TZ(完美型) | WS(力量型) | ST(稳健型)")

        st.divider()

        st.subheader("📋 有效答题明细数据")
        st.write(f"当前表格展示的是经过侧边栏规则清洗后的 **{len(df_clean)} 条** 高质量数据。")

        cols = df_clean.columns.tolist()
        if '答题耗时(秒)' in cols:
            cols.insert(1, cols.pop(cols.index('答题耗时(秒)')))
            df_clean = df_clean[cols]

        st.dataframe(df_clean, use_container_width=True)
    else:
        st.warning("当前清洗规则过于严格，所有问卷都被过滤掉了，请调整左侧阈值。")

else:
    st.info("💡 目前还没有人提交测试结果，快去把答题链接发给朋友们吧！")