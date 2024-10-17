# views/ui_case_upload.py
import pandas as pd
import streamlit as st
from loguru import logger
from datetime import datetime

from package.database import (
    get_all_batch_ids,
    read_case_from_sql, 
    import_cases,
    load_status_list,
)
from package.utils import get_case_df_display
from views.sidebar import sidebar


sidebar("案件上传")

st.header("法诉案件管理系统")

all_batch_ids = get_all_batch_ids()

# 获取当前日期和月份
today = datetime.now()
year_of_today = today.year
month_of_today = today.month

status_df = load_status_list()

if not all_batch_ids:
    st.warning("案件信息表为空")
else:
    # 需要显示的数据库字段名和页面字段名对应关系
    columns_pairs = [
        ('batch_id', '批次ID'),
        ('company_name', '公司名称'),
        ('shou_bie', '手别'),
        ('case_id', '案件id'),
        ('user_id', '用户ID'),
        ('user_name', '用户名'),
        ('full_name', '用户姓名'),
        ('id_card', '身份证号码'),
        ('gender', '性别'),
        ('nationality', '民族'),
        ('id_card_address', '身份证地址'),
        ('mobile_phone', '注册手机号'),
        ('list_id', '列表ID'),
        ('rongdan_mode', '融担模式'),
        ('contract_id', '合同号'),
        ('capital_institution', '资方机构'),
        ('rongdan_company', '融担公司'),
        ('contract_amount', '合同金额'),
        ('loan_date', '放款日期'),
        ('last_due_date', '最后一期应还款日'),
        ('loan_terms', '借款期数'),
        ('interest_rate', '利率'),
        ('overdue_start_date', '逾期开始日期'),
        ('last_pay_date', '上一个还款日期'),
        ('overdue_days', '列表逾期天数'),
        ('outstanding_principal', '待还本金'),
        ('outstanding_charge', '待还费用'),
        ('outstanding_amount', '待还金额'),
        ('data_collection_date', '数据提取日'),
        ('total_repurchase_principal', '代偿回购本金'),
        ('total_repurchase_interest', '代偿回购利息'),
        ('total_repurchase_penalty', '代偿回购罚息'),
        ('total_repurchase_all', '代偿回购总额'),
        ('latest_repurchase_date', '最晚代偿时间'),
        ('can_lawsuit', '是否可诉'),
        ('law_firm', '承办律所'),
        ('lawyer', '承办律师'),
        ('province_city', '所属省/市'),
        ('court', '法院全称'),
        ('status_id', '状态序号'),
        ('case_register_user_id', '立案负责人ID'),
        ('case_register_id', '立案号')
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
        case_df = read_case_from_sql(batch_id)
        case_df_display = get_case_df_display(case_df, status_df, columns_pairs)
        
    st.dataframe(case_df_display)

xlsx_file = st.file_uploader("请上传案件信息Excel文件", type=["xlsx"])

col_21, col_22, _, _ = st.columns(4)

with col_21:
    # 在页面中添加批次年份的下拉框
    batch_year = st.selectbox(
        "批次年份",
        [year for year in range(2024, 2034)],
        index=(year_of_today-2024),
    )

with col_22:
    # 在页面中添加批次月份的下拉框
    batch_month = st.selectbox(
        "批次月份",
        [month for month in range(1, 13)],
        index=(month_of_today-1),
    )

# 将批次年份和批次月份拼接成批次ID
batch_id = f"{batch_year}-{batch_month}"

# 在页面中添加“导入案件”的按钮，并进行错误处理
if xlsx_file is not None:
    if st.button("导入案件", use_container_width=True, type="primary"):
        try:
            result = import_cases(xlsx_file, batch_id)
            if result is not None:
                logger.error(result)
                st.error(result)
            else:
                st.rerun()
        except Exception as e:
            logger.error(e)
            st.write(e)