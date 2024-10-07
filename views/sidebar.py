import streamlit as st


def sidebar(title) -> None:
    with st.sidebar:
        st.title(title)
        
        # 登录状态显示
        if st.session_state.logged_in:
            st.success(
                f"{st.session_state.username} ({st.session_state.role}) 已登录",
                icon=":material/account_circle:",
            )

            # 退出按钮
            if st.sidebar.button("退出", use_container_width=True, type="primary"):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.rerun()