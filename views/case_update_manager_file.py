import streamlit as st
import pandas as pd
from loguru import logger
from datetime import datetime

from package.database import (
    get_all_batch_ids,
    read_case_from_sql, 
    update_cases,
    load_status_list,
)
from package.utils import get_case_df_display
from views.sidebar import sidebar


sidebar("案件更新 | 文件更新")

st.header("法诉案件管理系统 | 案件更新 | 文件更新")

all_batch_ids = get_all_batch_ids()

# 获取当前日期和月份
today = datetime.now()
year_of_today = today.year
month_of_today = today.month

case_status_df = load_status_list()

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
        ('status_id', '状态序号'),
        ('case_register_id', '立案号'),
        ('case_register_date', '立案日期'),
        ('court_session_open_date', '开庭日期'),
        ('case_register_user_id', '立案负责人ID'),
        ('case_print_user_id', '打印负责人ID'),
        ('case_update_datetime', '案件更新时间')
    ]
    
    display_names = [item[1] for item in columns_pairs] + [
        '案件阶段',
        '案件状态',
    ]

    col_11, _, _, _ = st.columns(4)

    with col_11:
        # 在页面中添加批次ID的下拉框
        batch_id = st.selectbox(
            "批次ID",
            options=all_batch_ids[::-1],
            label_visibility="collapsed",
            placeholder="选择批次ID",
            index=0,
        )
        
    # 如选择了批次ID，则针对该批次ID进行筛选
    if batch_id is not None:
        case_df = read_case_from_sql(batch_id)
        case_df_display = get_case_df_display(case_df, case_status_df, columns_pairs)
        
    st.dataframe(case_df_display)

xlsx_file = st.file_uploader("请上传案件更新信息Excel文件", type=["xlsx"])

if xlsx_file is not None:
    df_update = pd.read_excel(xlsx_file)

    for col in df_update.columns:
        if col not in display_names:
            raise Exception(f"Excel文件中存在未定义的字段：{col}") 

# 在页面中添加“导入案件”的按钮，并进行错误处理
if xlsx_file is not None:
    if st.button("更新案件", use_container_width=True, type="primary"):
        try:
            result = update_cases(xlsx_file, batch_id)
            if result is not None:
                logger.error(result)
                st.error(result)
            else:
                st.rerun()
        except Exception as e:
            logger.error(e)
            st.write(e)