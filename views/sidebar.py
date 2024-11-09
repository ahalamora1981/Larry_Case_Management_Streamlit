import streamlit as st
from package.utils import hash_password
from package.database import reset_password


@st.dialog("修改个人账号密码")
def change_password() -> None:
    new_password = st.text_input("新密码", type="password")
    repeat_password = st.text_input("重复密码", type="password")
    
    if new_password == "":
        disable_btn = True
        st.error("请输入新密码")
    elif new_password!= repeat_password:
        disable_btn = True
        st.error("两次输入密码不一致")
    else:
        disable_btn = False
    
    new_hashed_password = None if new_password == "" else hash_password(new_password)
    
    col_1, col_2 = st.columns(2)
    with col_1:
        if st.button("确认", use_container_width=True, type="primary", disabled=disable_btn):
            if new_hashed_password is not None:
                reset_password(
                    st.session_state.user_id, 
                    new_hashed_password
                )
            else:
                st.error("请输入新密码")
                st.stop()
                
            st.rerun()
    with col_2:
        if st.button("取消", use_container_width=True, disabled=disable_btn):
            st.rerun()

def sidebar(title) -> None:
    with st.sidebar:
        st.title(title)
        
        # 登录状态显示
        if st.session_state.logged_in:
            st.success(
                f"{st.session_state.username} ({st.session_state.role}) 已登录",
                icon=":material/account_circle:",
            )
            
            if st.sidebar.button("修改个人账号密码", use_container_width=True):
                change_password()

            # 退出按钮
            if st.sidebar.button("退出", use_container_width=True, type="primary"):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.rerun()