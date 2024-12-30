import streamlit as st
from datetime import datetime
import pytz
import pandas as pd
from views.sidebar import sidebar
from package.database import (
    get_count_by_batch_id, 
    get_count_by_year,
    get_count_all_cases,
    get_count_by_batch_id_and_registered,
    get_count_by_batch_id_and_repayment
)


sidebar("案件统计")

st.header("法诉案件管理系统 | 案件统计")

# 获取当前日期和月份
shanghai_tz = pytz.timezone('Asia/Shanghai')
shanghai_time = datetime.now(shanghai_tz)
year_today = shanghai_time.year
month_today = shanghai_time.month

st.write(shanghai_time.strftime("今天日期:%Y 年 %m 月 %d 日"))

col_11, col_12, _, _, _, _ = st.columns(6)

with col_11:
    # 在页面中添加批次年份的下拉框
    year_selected = st.selectbox(
        "批次年份",
        [year for year in range(2024, 2034)],
        index=(year_today-2024),
        label_visibility="collapsed",
    )

with col_12:
    # 在页面中添加批次月份的下拉框
    month_selected = st.selectbox(
        "批次月份",
        [month for month in range(1, 13)],
        index=(month_today-1),
        label_visibility="collapsed",
    )
    
previous_month = month_selected - 1 if month_selected > 1 else 12
year_of_previous_month = year_selected if previous_month > 1 else year_selected - 1

num_all_cases = get_count_all_cases()
num_cases_this_year = get_count_by_year(year_selected)
num_cases_last_month = get_count_by_batch_id(f"{year_of_previous_month}-{previous_month}")
num_cases_this_month = get_count_by_batch_id(f"{year_selected}-{month_selected}")

if num_cases_last_month != 0:
    percent_change_by_month = (num_cases_this_month - num_cases_last_month) / num_cases_last_month * 100
    percent_change_by_month_str = f"+{percent_change_by_month:.1f}%" if percent_change_by_month > 0 else f"{percent_change_by_month:.1f}%"
else:
    percent_change_by_month = 0
    percent_change_by_month_str = "0%"

### 案件数量 ###
st.subheader("案件数量")

df_cases_number = pd.DataFrame({
    "年份": [year_selected],
    "月份": [month_selected],
    "本年案件数量": [num_cases_this_year],
    "上月案件数量": [num_cases_last_month],
    "本月案件数量": [num_cases_this_month],
    "环比增长率": [percent_change_by_month_str]
}, dtype=str)

st.dataframe(df_cases_number, width=600, hide_index=True)

### 立案比例 ###
st.subheader("立案比例")

if num_cases_this_month == 0:
    register_rate = "0%"
else:
    register_rate = f"{get_count_by_batch_id_and_registered(f'{year_selected}-{month_selected}') / num_cases_this_month * 100:.1f}%"

df_registered = pd.DataFrame({
    "年份": [year_selected],
    "月份": [month_selected],
    "立案数": [get_count_by_batch_id_and_registered(f'{year_selected}-{month_selected}')],
    "立案比例": [register_rate]
}, dtype=str)

st.dataframe(df_registered, width=600, hide_index=True)

### 还款意向比例 ###
st.subheader("还款意向比例")

if num_cases_this_month == 0:
    repayment_rate = "0%"
else:
    repayment_rate = f"{get_count_by_batch_id_and_repayment(f'{year_selected}-{month_selected}') / num_cases_this_month * 100:.1f}%"

df_repayment = pd.DataFrame({
    "年份": [year_selected],
    "月份": [month_selected],
    "还款数": [get_count_by_batch_id_and_repayment(f'{year_selected}-{month_selected}')],
    "还款比例": [repayment_rate]
}, dtype=str)

st.dataframe(df_repayment, width=600, hide_index=True)
