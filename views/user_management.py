# views/user_management.py
import streamlit as st

from package.database import (
    get_user_by_id,
    read_user_from_sql, 
    add_user,
    delete_user,
    reset_password,
    reset_username,
    reset_role,
)
from package.utils import hash_password
from views.sidebar import sidebar


sidebar("用户管理")

st.header("法诉案件管理系统 | 用户管理")

# 确认弹窗
@st.dialog("确认删除用户")
def confirm_delete_user(user_id: int) -> None:
    col_1, col_2 = st.columns(2)
    with col_1:
        if st.button("确认", use_container_width=True, type="primary"):
            delete_user(user_id)
            st.rerun()
    with col_2:
        if st.button("取消", use_container_width=True):
            st.rerun()

# 确认弹窗
@st.dialog("确认重置用户")
def confirm_reset_user(
    user_id: int, 
    username: str | None = None, 
    role: str | None = None,
    hashed_password: str | None = None
) -> None:
    col_1, col_2 = st.columns(2)
    with col_1:
        if st.button("确认", use_container_width=True, type="primary"):
            if username is not None:
                reset_username(user_id, username)
            if role is not None:
                reset_role(user_id, role)
            if hashed_password is not None:
                reset_password(user_id, hashed_password)
            if username is None and hashed_password is None:
                st.error("请输入新用户名或密码")
            st.rerun()
    with col_2:
        if st.button("取消", use_container_width=True):
            st.rerun()

user_df = read_user_from_sql()
user_df = user_df.loc[user_df['username'] != 'admin']
user_df = user_df.loc[user_df['username'] != 'jtao']
user_df = user_df.loc[user_df['username'] != st.session_state.username]

user_df_display = user_df[['username', 'role']]
user_df_display = user_df_display.rename(columns={'username': '用户名', 'role': '角色'})

col_1, col_2 = st.columns([3, 1])

with col_1:
    index_selected = st.dataframe(
        user_df_display, 
        on_select="rerun",
        selection_mode="single-row",
        use_container_width=True,
        hide_index=True,
    )

id_selected = None
user_selected = None

# 如选择行，则获取该行的ID，再通过ID获取用户对象
if len(index_selected['selection']['rows']) > 0:
    id_selected = user_df.reset_index()['id'][index_selected['selection']['rows'][0]]
    user_selected = get_user_by_id(id_selected)

with col_2:
    # 如没有选中的用户，则显示添加用户表单
    if user_selected is None:
        with st.form("add_user_form"):
            st.subheader("添加用户")
            
            username = st.text_input(
                "用户名", 
                placeholder="请输入用户名", 
            )

            password = st.text_input(
                "密码", 
                type="password", 
                placeholder="请输入密码", 
            )
            
            hashed_password = hash_password(password)

            role = st.selectbox(
                "角色",
                ["manager", "staff"],
                index=1,
                placeholder="请选择角色",
            )

            if st.form_submit_button("添加用户", use_container_width=True, type="primary"):
                result = add_user(username=username, hashed_password=hashed_password, role=role)
                if result is not None:
                    st.error(result)
                else:
                    st.rerun()
                    
    # 如有选中的用户，且id不为1(即用户不是admin)，则显示删除用户和重置密码表单
    elif user_selected is not None and id_selected != 1:
        if st.session_state.role == "admin":
            with st.form("delete_user_form"):
                st.subheader("删除用户")
                
                st.text_input(
                    "用户名", 
                    value=user_selected.username, 
                    disabled=True,
                )

                if st.form_submit_button("删除用户", use_container_width=True, type="primary"):
                    confirm_delete_user(user_selected.id)
                
        with st.form("reset_user_form"):
            st.subheader("重置用户")
            
            new_username = st.text_input(
                "用户名", 
                value=user_selected.username, 
            ).strip()
            
            new_username = None if new_username == "" else new_username
            
            new_role = st.selectbox(
                "角色", 
                options=['manager', 'staff'],
                index=0 if user_selected.role =='manager' else 1, 
            ).strip()

            new_password = st.text_input(
                "密码", 
                value="",
                type="password",
            ).strip()
            
            new_hashed_password = None if new_password == "" else hash_password(new_password)

            if st.form_submit_button("重置用户", use_container_width=True, type="primary"):
                if new_username is None and new_role is not None and new_hashed_password is None:
                    st.error("请输入新用户名、角色、或密码")
                else:
                    confirm_reset_user(user_selected.id, new_username, new_role, new_hashed_password)
                    
    # 其余情况(即有选中的用户，且id为1，是admin)，则不显示表单
    else:
        pass