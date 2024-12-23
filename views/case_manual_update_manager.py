import streamlit as st
from views.case_manual_update_template import case_update_staff_page
from views.sidebar import sidebar


sidebar("案件更新 | 手动")

st.header("法诉案件管理系统 | 案件更新 | 手动")
    
case_update_staff_page(user_type="manager")