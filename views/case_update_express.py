import streamlit as st
import pandas as pd
from loguru import logger
from datetime import datetime
import pytz

from package.database import (
    get_all_batch_ids,
    read_cases_from_sql, 
    update_cases
)
from package.utils import get_cases_df_display
from views.sidebar import sidebar


sidebar("邮寄状态变更")

st.header("法诉案件管理系统 (邮寄状态变更)")

# 获取当前日期和月份
shanghai_tz = pytz.timezone('Asia/Shanghai')
shanghai_time = datetime.now(shanghai_tz)
year_of_today = shanghai_time.year
month_of_today = shanghai_time.month

all_batch_ids = get_all_batch_ids()

if not all_batch_ids:
    st.warning("案件信息表为空")
else:
    # 需要显示的数据库字段名和页面字段名对应关系
    columns_pairs = [
        ('batch_id', '批次ID'),
        ('shou_bie', '手别'),
        ('user_name', '用户名'),
        ('full_name', '用户姓名'),
        ('list_id', '列表ID'),
        ('outstanding_principal', '待还本金'),
        ('law_firm', '承办律所'),
        ('lawyer', '承办律师'),
        ('province_city', '所属省/市'),
        ('court', '法院全称'),
        ('express_number', '快递单号')
    ]

    col_11, _, _, _ = st.columns(4)

    with col_11:
        # 在页面中添加批次ID的下拉框
        batch_id = st.selectbox(
            "批次ID",
            options=all_batch_ids,
            label_visibility="collapsed",
            placeholder="选择批次ID",
            index=0,
        )
        
    # 如选择了批次ID，则针对该批次ID进行筛选
    if batch_id is not None:
        case_df = read_cases_from_sql(batch_id)
        case_df_display = get_cases_df_display(case_df, columns_pairs)
        
    st.dataframe(case_df_display, hide_index=True)
    st.write(f"案件总数: {len(case_df)}")
    
if st.session_state.role == "staff":
    st.stop()

xlsx_file = st.file_uploader("请上传案件更新信息Excel文件", type=["xlsx"])

# Excel样例下载
st.download_button(
    label="下载Excel样例 - 邮寄状态变更模版.xlsx",
    data=open("data/3_邮寄状态变更模版.xlsx", "rb").read(),
    file_name="邮寄状态变更模版.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

# 在页面中添加“导入案件”的按钮，并进行错误处理
if xlsx_file is not None:
    df_update = pd.read_excel(xlsx_file, dtype=str)
    df_update_standard = pd.read_excel("data/3_邮寄状态变更模版.xlsx", dtype=str)
    
    if df_update.columns.tolist() != df_update_standard.columns.tolist():
        logger.error("Excel文件的字段与“邮寄状态变更模版”不匹配，请检查")
        raise ValueError("Excel文件的字段与“邮寄状态变更模版”不匹配，请检查")
    
    if st.button("更新案件", use_container_width=True, type="primary"):
        try:
            result = update_cases(df_update, ['快递单号'])
            if result is not None:
                st.text_area("错误信息", value=result, height=300, disabled=True)
            else:
                st.rerun()  
        except Exception as e:
            logger.error(e)
            st.text_area("错误信息", value=e, height=300, disabled=True)