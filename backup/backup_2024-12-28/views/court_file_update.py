import streamlit as st
import pandas as pd
from loguru import logger

from package.database import (
    get_all_batch_ids,
    read_case_from_sql_court, 
    update_cases_court,
)
from views.sidebar import sidebar


sidebar("开庭更新 | 文件")

st.header("法诉案件管理系统 | 开庭更新 | 文件")

all_batch_ids = get_all_batch_ids()

if not all_batch_ids:
    st.warning("案件信息表为空")
    st.stop()
    
# 需要显示的数据库字段名和页面字段名对应关系
columns_pairs = [
    ('batch_id', '批次ID'),
    ('user_name', '用户名'),
    ('list_id', '列表ID'),
    ('full_name', '被告'),
    ('court_session_open_date', '开庭日期'),
    ('court_session_open_time', '开庭时间'),
    ('outstanding_amount', '标的金额'),
    ('outstanding_principal', '客户本金'),
    ('plaintiff_company', '原告公司'),
    ('court_law_firm', '开庭律所'),
    ('case_register_id', '立案号'),
    ('court', '法院全称'),
    ('court_phone', '法院电话'),
    ('court_status', '开庭状态'),
    ('judgement_remark', '判决备注'),
    ('is_case_closed', '结案与否'),
]

display_names = [item[1] for item in columns_pairs]
    
case_df = read_case_from_sql_court()
case_df_display = case_df[[item[0] for item in columns_pairs]]
case_df_display.columns = [item[1] for item in columns_pairs]
    
st.dataframe(case_df_display, hide_index=True)
st.write(f"案件总数: {len(case_df)}")

xlsx_file = st.file_uploader("请上传案件更新信息Excel文件", type=["xlsx"])

# Excel样例下载
st.download_button(
    label="下载Excel样例",
    data=open("data/开庭时间表导入模版-v1.0.xlsx", "rb").read(),
    file_name="开庭时间表导入模版-v1.0.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

if xlsx_file is not None:
    df_update = pd.read_excel(xlsx_file)

    for col in df_update.columns:
        if col not in display_names:
            raise Exception(f"Excel文件中存在未定义的字段：{col}") 

# 在页面中添加“导入案件”的按钮，并进行错误处理
if xlsx_file is not None:
    if st.button("更新案件", use_container_width=True, type="primary"):
        try:
            result = update_cases_court(xlsx_file)
            if result is not None:
                st.text_area("错误信息", value=result, height=300, disabled=True)
            else:
                st.rerun()
        except Exception as e:
            st.text_area("错误信息", value=e, height=300, disabled=True)