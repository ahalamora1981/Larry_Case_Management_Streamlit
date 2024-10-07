import streamlit as st
from datetime import date
from views.sidebar import sidebar
from package.database import get_case_by_batch_id, get_all_cases


sidebar("案件统计")

st.header("法诉案件管理系统")

year = date.today().year
month = date.today().month

last_month = month - 1 if month > 1 else 12
year_of_last_month = year if last_month > 1 else year - 1

num_all_cases = len(get_all_cases())
num_cases_last_month = len(get_case_by_batch_id(f"{year_of_last_month}-{last_month}"))
num_cases_this_month = len(get_case_by_batch_id(f"{year}-{month}"))

if num_cases_last_month != 0:
    percent_change_by_month = (num_cases_this_month - num_cases_last_month) / num_cases_last_month * 100
    percent_change_by_month_str = f"+{percent_change_by_month:.1f}%" if percent_change_by_month > 0 else f"{percent_change_by_month:.1f}%"
else:
    percent_change_by_month = 0
    percent_change_by_month_str = "0%"

st.write(date.today().strftime("今天日期：%Y 年 %m 月 %d 日"))

col1, col2, col3, col4, _, _ = st.columns(6)

with col1:
    st.error("案件总数")
    st.html(f"<p style='font-size: 36px;'>{num_all_cases}</p>")
    
with col2:
    st.info(f"{month}月案件数")
    st.html(f"<p style='font-size: 36px;'>{num_cases_this_month}</p>")
    
with col3:
    st.warning(f"{last_month}月案件数")
    st.html(f"<p style='font-size: 36px;'>{num_cases_last_month}</p>")
    
with col4:
    st.success("环比增长率")
    color = "gray" if percent_change_by_month <= 0 else "green"
    st.html(f"<p style='color: {color}; font-size: 36px;'>{percent_change_by_month_str}</p>")
