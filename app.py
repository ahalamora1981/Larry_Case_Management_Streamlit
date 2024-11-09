# app.py
import os
import yaml
import streamlit as st
from loguru import logger

from package.database import (
    get_user_by_username, 
    add_user,
)
from package.utils import hash_password

        
def ui_login() -> None:
    with st.form("login_form"):
        st.header("法诉案件管理系统")
        username = st.text_input("用户名").strip()
        password = st.text_input("密码", type="password")

        if st.form_submit_button("登录", use_container_width=True):
            user = get_user_by_username(username=username)

            if user is not None:
                if user.password == hash_password(password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.user_id = user.id
                    st.session_state.role = user.role
                    logger.info(f"用户: {username} 尝试登录")
                    st.rerun()
                else:
                    st.error("密码错误")
            else:
                st.error("用户名错误")
                    
def ui_main() -> None:
    st.set_page_config(
        page_title="案件管理系统",
        layout="wide",
        initial_sidebar_state="expanded",
        page_icon=":memo:", 
    )
    
    if st.session_state.role in ["admin", "manager"]:
        pg = st.navigation([
            st.Page(os.path.join(CWD, "views", "main_view.py"), title="案件统计"),
            st.Page(os.path.join(CWD, "views", "case_upload.py"), title="案件上传"),
            st.Page(os.path.join(CWD, "views", "case_assignment.py"), title="案件分配"),
            st.Page(os.path.join(CWD, "views", "case_update_manager_manual.py"), title="案件更新 | 手动更新"),
            st.Page(os.path.join(CWD, "views", "case_update_manager_file.py"), title="案件更新 | 文件更新"),
            st.Page(os.path.join(CWD, "views", "user_management.py"),  title="用户管理"),
        ])
    elif st.session_state.role == "staff":
        pg = st.navigation([
            st.Page(os.path.join(CWD, "views", "case_update_register.py"), title="立案 - 案件更新"),
            st.Page(os.path.join(CWD, "views", "case_update_print.py"), title="打印 - 案件更新"),
        ])
    else:
        raise Exception("Invalid role")
        
    pg.run()


def initialization():
    # 加载 Config 文件
    with open(os.path.join(CWD, "config.yaml"), "r") as f:
        config = yaml.safe_load(f)

    # 初始化管理员账户
    admin_password = config['admin']['password']

    # 创建管理员账号, id=1
    if get_user_by_username('admin') is None:
        add_user('admin', hash_password(admin_password), 'admin')

    # 创建“无立案负责人”账号, id=2
    if get_user_by_username('none') is None:
        add_user('none', hash_password('none'), 'staff')
        
    # 初始化用户登录状态
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    # 保存 Config 到文件    
    # with open(os.path.join(CWD, "config.yaml"), "w") as f:
    #     yaml.dump(config, f)


if __name__ == "__main__":
    CWD = os.getcwd()

    # 每次Streamlit Rerun时，先Remove现有logger，再Add新logger，防止重复log。
    logger.remove()
    logger.add(
        os.path.join(CWD, "logs", "app.log"), 
        rotation="10 MB", 
        compression="zip"
    )

    initialization()

    if st.session_state.logged_in:
        ui_main()
    else:
        ui_login()