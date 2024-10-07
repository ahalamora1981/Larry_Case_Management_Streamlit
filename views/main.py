import streamlit as st
from views.sidebar import sidebar


sidebar("主页")

st.header("法诉案件管理系统")

col1, col2, col3, _, _, _ = st.columns(6)

col1.metric("案件总数", "1234")
col2.metric("上月案件数(10月)", "789")
col3.metric("本月案件数(11月)", "1000", "20%")
