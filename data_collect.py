import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

# ================= 1. 页面与 UI 设置 =================
st.set_page_config(page_title="JADY 测试结果后台", page_icon="📊", layout="wide")

# 🌟 高级美化：隐藏右上角的默认菜单和底部的 Streamlit 水印
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# 🚀 密码门禁已被无情拆除！直接进入智能大屏主界面
st.title("📊 JADY 性格测试 - 智能数据看板")

# ================= 2. 连接 Supabase 云端数据库 =================
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# 从云端数据库抓取所有记录
try:
    response = supabase.table("jady_results").select("*").execute()
    db_data = response.data
except Exception as e:
    st.error(f"❌ 无法连接到云端数据库，请检查网络或 Secrets 密钥配置。详细报错: {e}")
    st.stop()

# 如果云端没有数据，提示并终止加载图表
if not db_data:
    st.info("💡 目前云端数据库中还没有人提交测试结果，快去把答题链接发给朋友们吧！")
    st.stop()

# ================= 3. 数据处理与映射 =================
df = pd.DataFrame(db_data)

# 安全的时间转换与时区校准（防止空数据导致异常）
if 'created_at' in df.columns:
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    if df['created_at'].dt.tz is None:
        df['created_at'] = df['created_at'].dt.localize('UTC')
    df['created_at'] = df['created_at'].dt.tz_convert('Asia/Shanghai').dt.strftime('%Y-%m-%d %H:%M:%S')

# 完美映射回中文列名 (保留了核心的 'id'，用于后续精准删除)
column_mapping = {
    "id": "记录ID", "created_at": "提交时间", "duration": "答题耗时(秒)", "name": "姓名",
    "gender": "性别", "age": "年龄", "position": "岗位职务", "main_trait": "主要性格",
    "score_zq": "交流型(ZQ)", "score_tz": "完美型(TZ)", "score_ws": "力量型(WS)", "score_st": "稳健型(ST)",
    "weaknesses": "缺点", "strengths": "优点"
}
df = df.rename(columns=column_mapping)

# 将存放在 all_answers 里的 30 道题展开解压出来
if 'all_answers' in df.columns:
    for i in range(1, 31):
        df[f"第{i}题"] = df['all_answers'].apply(lambda x: x.get(f"第{i}题", "") if isinstance(x, dict) else "")
    # 从表格展示中剔除冗余的原始 JSON 列
    df = df.drop(columns=['all_answers'])

# ================= 4. 侧边栏：无需密码，直接开放控制中心 =================
with st.sidebar:
    st.header("🧽 数据清洗控制台")
    st.write("开启以下规则，系统将自动过滤无效问卷：")

    # 规则 1：过滤耗时过短
    min_seconds = st.slider("1. 最短有效答题时间(秒)", min_value=0, max_value=300, value=60, step=10)

    # 规则 2：去重机制
    remove_duplicate = st.checkbox("2. 自动合并重复提交", value=True, help="如果同一姓名多次提交，仅保留最新一次的数据。")

    # 规则 3：直线作答检测
    anti_straight_line = st.checkbox("3. 过滤敷衍作答 (如全选A)", value=False,
                                     help="如果某个人超过 25 道题都选了同一个选项，将被判定为无效作答。")

    # ---------------- 危险操作区域 (全面接入云端 API) ----------------
    st.divider()
    st.markdown("### 🚨 云端数据删除控制台")

    # 功能 A：精准删除指定数据
    st.write("**1. 删除单条/多条数据**")
    if "记录ID" in df.columns and "姓名" in df.columns:
        delete_options = df.apply(lambda row: f"[ID:{row['记录ID']}] {row['姓名']} - {row['提交时间']}", axis=1).tolist()
        selected_to_delete = st.multiselect("请选择要永久删除的记录：", delete_options)

        if st.button("🗑️ 从云端删除选中记录", disabled=len(selected_to_delete) == 0):
            ids_to_drop = [int(opt.split("]")[0].split(":")[1]) for opt in selected_to_delete]
            for record_id in ids_to_drop:
                supabase.table("jady_results").delete().eq("id", record_id).execute()
            st.sidebar.success("✅ 选中的记录已从云端永久删除！")
            st.rerun()

    st.write("---")

    # 功能 B：一键清空全部数据
    st.write("**2. 清空云端全部历史数据**")
    confirm_delete = st.checkbox("我已知晓此操作不可逆，确认清空云端所有数据", value=False)

    if st.button("💥 清空云端所有数据", type="primary", disabled=not confirm_delete):
        supabase.table("jady_results").delete().gt("id", -1).execute()
        st.sidebar.success("💥 云端数据已全部清空！")
        st.rerun()

# ================= 5. 数据清洗执行引擎 =================
df_clean = df.copy()

if '答题耗时(秒)' in df_clean.columns:
    df_clean = df_clean[df_clean['答题耗时(秒)'] >= min_seconds]

if remove_duplicate and '姓名' in df_clean.columns:
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

# ================= 6. 核心指标与图表看板 =================
st.write("### 👥 数据概况")
col1, col2, col3 = st.columns(3)
col1.metric("原始收集总数", f"{len(df)} 份")
col2.metric("清洗后有效总数", f"{len(df_clean)} 份", delta=f"-{len(df) - len(df_clean)} 份 (已过滤)",
            delta_color="inverse")

if len(df_clean) > 0:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 主要性格分布")
        if '主要性格' in df_clean.columns:
            type_counts = df_clean['主要性格'].value_counts().reset_index()
            type_counts.columns = ['性格', '人数']
            fig1 = px.bar(type_counts, x='性格', y='人数', color='性格', text='人数',
                          color_discrete_sequence=px.colors.qualitative.Pastel)
            fig1.update_layout(xaxis_tickangle=0, showlegend=False, bargap=0.4, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("💡 平均得分概览")
        available_scores = [c for c in ['交流型(ZQ)', '完美型(TZ)', '力量型(WS)', '稳健型(ST)'] if c in df_clean.columns]
        if available_scores:
            avg_scores = df_clean[available_scores].mean().round(1)
            score_data = pd.DataFrame({
                '维度': [c.split('(')[0] for c in available_scores],
                '分数': avg_scores.values
            })
            fig2 = px.bar(score_data, x='维度', y='分数', color='维度', text='分数',
                          color_discrete_sequence=px.colors.qualitative.Set2)
            fig2.update_layout(xaxis_tickangle=0, showlegend=False, bargap=0.4, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig2, use_container_width=True)
        st.caption("📌 **指标说明：** ZQ(交流型) | TZ(完美型) | WS(力量型) | ST(稳健型)")

    st.divider()

    st.subheader("📋 有效答题明细数据")
    st.write(f"当前表格展示的是经过侧边栏规则清洗后的 **{len(df_clean)} 条** 高质量数据。")

    # 优雅重新排序，核心信息排在最前
    cols = df_clean.columns.tolist()
    if '记录ID' in cols:
        cols.remove('记录ID')
    if '提交时间' in cols: cols.insert(0, cols.pop(cols.index('提交时间')))
    if '姓名' in cols: cols.insert(1, cols.pop(cols.index('姓名')))
    if '答题耗时(秒)' in cols: cols.insert(2, cols.pop(cols.index('答题耗时(秒)')))
    df_clean = df_clean[cols]

    st.dataframe(df_clean, use_container_width=True)
else:
    st.warning("当前清洗规则过于严格，所有问卷都被过滤掉了，请调整左侧阈值。")