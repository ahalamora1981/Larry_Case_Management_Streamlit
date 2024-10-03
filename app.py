# app.py
import os
import yaml
import streamlit as st
from datetime import datetime
from loguru import logger

from package.database import (
    get_case_by_id, 
    get_all_users,
    get_user_by_username, 
    get_user_by_id,
    read_from_sql, 
    import_cases,
    add_user,
    delete_user,
    update_case_status,
    load_status_list,
)
from package.utils import hash_password


######################
### Initialization ###
######################

CWD = os.getcwd()

# Initialize logger
logger.remove()
logger.add(
    os.path.join(CWD, "logs", "app.log"), 
    rotation="10 MB", 
    compression="zip"
)

# Load config
with open(os.path.join(CWD, "config.yaml"), "r") as f:
    config = yaml.safe_load(f)

# 初始化管理员账户
ADMIN_PASSWORD = config['admin']['password']

if get_user_by_username('admin') is None:
    add_user('admin', hash_password(ADMIN_PASSWORD), 'admin')
    
# with open(os.path.join(CWD, "config.yaml"), "w") as f:
#     yaml.dump(config, f)

# 初始化用户登录状态
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

#############################
### End of Initialization ###
#############################

def sidebar() -> None:
    with st.sidebar:
        st.title("案件管理系统")
        
        if st.session_state.role == "admin":
            page_options = ["案件上传", "案件更新", "用户管理"]
            default_page = 1
        elif st.session_state.role == "manager":
            page_options = ["案件更新", "用户管理"]
            default_page = 0
        elif st.session_state.role == "staff":
            page_options = ["案件更新"]
            default_page = 0
        else:
            st.error("未知角色")
            logger.error(f"未知角色: {st.session_state.role}")
        
        st.session_state.page = st.selectbox(
            "请选择页面",
            options=page_options,
            index=default_page,
        )
        
        if st.session_state.logged_in:
            st.success(
                f"{st.session_state.username} ({st.session_state.role}) 已登录",
                icon=":material/account_circle:",
            )

            if st.sidebar.button("退出", use_container_width=True, type="primary"):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.rerun()

def ui_case_upload() -> None:
    st.header("案件上传")
    
    today = datetime.now()
    year_of_today = today.year
    month_of_today = today.month
    
    case_df = read_from_sql('case')
    status_df = load_status_list()
    
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
        ('register_user_id', '立案负责人ID')
    ]
    
    case_df_to_display = case_df[[item[0] for item in columns_pairs]]
    case_df_to_display.columns = [item[1] for item in columns_pairs]
    
    for case_id, user_id, status_id in zip(case_df_to_display.index, case_df_to_display['立案负责人ID'], case_df_to_display['状态序号']):
        case_df_to_display.loc[case_id, '立案负责人'] = get_user_by_id(user_id).username
        case_df_to_display.loc[case_id, '案件阶段'] = status_df.loc[status_id, '案件阶段']
        case_df_to_display.loc[case_id, '案件状态'] = status_df.loc[status_id, '案件状态']
    
    
    case_df_to_display = case_df_to_display.drop(columns=['立案负责人ID', '状态序号'])

    st.dataframe(case_df_to_display, use_container_width=True)
    
    xlsx_file = st.file_uploader("请上传案件信息Excel文件", type=["xlsx"])
    
    col_1, col_2, _, _ = st.columns(4)
    
    with col_1:
        batch_year = st.selectbox(
            "批次年份",
            [year for year in range(2024, 2034)],
            index=(year_of_today-2024),
        )
    
    with col_2:
        batch_month = st.selectbox(
            "批次月份",
            [month for month in range(1, 13)],
            index=(month_of_today-1),
        )
    
    batch_id = f"{batch_year}-{batch_month}"

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
                    
def ui_case_update() -> None:    
    st.header("案件更新")
    
    case_df = read_from_sql('case')
    status_df = load_status_list()
    
    columns_pairs = [ 
        ('batch_id', '批次ID'),
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
        ('overdue_days', '列表逾期天数'),
        ('outstanding_principal', '待还本金'),
        ('outstanding_charge', '待还费用'),
        ('outstanding_amount', '待还金额'),
        ('can_lawsuit', '是否可诉'),
        ('law_firm', '承办律所'),
        ('lawyer', '承办律师'),
        ('province_city', '所属省/市'),
        ('court', '法院全称'),
        ('status_id', '状态序号'),
        ('register_user_id', '立案负责人ID')
    ]

    case_df_to_display = case_df[[item[0] for item in columns_pairs]]
    case_df_to_display.columns = [item[1] for item in columns_pairs]
    
    for case_id, user_id, status_id in zip(case_df_to_display.index, case_df_to_display['立案负责人ID'], case_df_to_display['状态序号']):
        case_df_to_display.loc[case_id, '立案负责人'] = get_user_by_id(user_id).username
        case_df_to_display.loc[case_id, '案件阶段'] = status_df.loc[status_id, '案件阶段']
        case_df_to_display.loc[case_id, '案件状态'] = status_df.loc[status_id, '案件状态']
    
    case_df_to_display = case_df_to_display.drop(columns=['立案负责人ID', '状态序号'])
    
    col_11, col_12, col_13, col_14, col_15 = st.columns(5)
    
    with col_11:
        batch_id = st.selectbox(
            "批次ID",
            options=case_df_to_display['批次ID'].unique(),
            label_visibility="collapsed",
            placeholder="选择批次ID",
            index=None,
        )
    
    with col_12:
        user_name = st.text_input(
            "用户名",
            label_visibility="collapsed",
            placeholder="输入用户名",
        )
    
    if batch_id is not None:
        case_df_to_display = case_df_to_display[case_df_to_display['批次ID'] == batch_id]
        
    if user_name:
        case_df_to_display = case_df_to_display[case_df_to_display['用户名'] == user_name]
    
    if st.session_state.role == "staff":
        case_df_to_display = case_df_to_display[case_df_to_display['立案负责人'] == st.session_state.username]

    col_21, col_22 = st.columns([3, 1])
    
    with col_21:
        index_selected = st.dataframe(
            case_df_to_display,
            on_select="rerun",
            selection_mode="single-row",
            use_container_width=True,
            hide_index=True,
        )
    
    id_selected = None
    case_selected = None
    
    if len(index_selected['selection']['rows']) > 0:
        id_selected = case_df.reset_index()['id'][index_selected['selection']['rows'][0]]
        case_selected = get_case_by_id(id_selected)
    
    if case_selected is not None:
        full_name = case_selected.full_name
        lawyer = case_selected.lawyer
        register_user_id = case_selected.register_user_id
        status_id = case_selected.status_id
        update_button_disabled = False
    else:
        full_name = None
        lawyer = None
        register_user_id = None
        status_id = None
        update_button_disabled = True
        
    all_users = get_all_users()
    all_usernames = [user.username for user in all_users]
        
    with col_22:
        with st.form("case_update_form"):
            st.subheader("案件详情1")
            
            if case_selected is None:
                disable_form_input = True
            else:
                disable_form_input = False
            
            st.text_input(
                "姓名", 
                value=full_name, 
                disabled=True,
            )

            st.text_input(
                "律师",
                value=lawyer,
                disabled=True,
            )
            
            # 立案负责人
            if register_user_id is None:
                register_user_index = None
            else:
                register_user_index = all_usernames.index(get_user_by_id(register_user_id).username)
                
            new_username = st.selectbox(
                "立案负责人",
                options=all_usernames,
                index=register_user_index,
                disabled=disable_form_input,
            )
            
            if register_user_index is None:
                new_user_id = None
            else:
                new_user_id = all_users[all_usernames.index(new_username)].id
            
            # 案件状态 
            if status_id is None:
                status_index = None
            else:
                status_index = status_df['案件状态'].tolist().index(status_df.loc[status_id, '案件状态'])
            
            new_status = st.selectbox(
                "案件状态",
                options=status_df['案件状态'], 
                index=status_index,
                disabled=disable_form_input,
            )
            
            status_df_reset_index = status_df.reset_index()
            
            if status_id is None:
                new_status_id = None
            else:
                new_status_id = int(status_df_reset_index[status_df_reset_index['案件状态'] == new_status]['序号'].tolist()[0])
            
            # 提交按钮
            if st.form_submit_button(
                "更新案件", 
                use_container_width=True, 
                type="primary",
                disabled=update_button_disabled,
            ):
                update_case_status(case_selected.id, new_user_id, new_status_id)
                
                logger.info(f"用户: {st.session_state.username} 把案件 {case_selected.user_name_and_list_id} 的状态从 {case_selected.status_id} 更新为 {new_status_id}")
                    
                st.rerun()

def ui_user_management() -> None:
    st.header("用户管理")

    user_df = read_from_sql('user')
    
    col_1, col_2 = st.columns([3, 1])

    with col_1:
        index_selected = st.dataframe(
            user_df[['username', 'role']], 
            on_select="rerun",
            selection_mode="single-row",
            use_container_width=True,
        )
    
    id_selected = None
    user_selected = None
    
    if len(index_selected['selection']['rows']) > 0:
        id_selected = user_df.reset_index()['id'][index_selected['selection']['rows'][0]]
        user_selected = get_user_by_id(id_selected)
    
    with col_2:
        if user_selected is not None:
            with st.form("delete_user_form"):
                st.subheader("删除用户")
                
                st.text_input(
                    "用户名", 
                    value=user_selected.username, 
                    disabled=True,
                )

                st.text_input(
                    "角色", 
                    value=user_selected.role, 
                    disabled=True,
                )

                if st.form_submit_button("删除用户", use_container_width=True, type="primary"):
                    confirm_delete_user(user_selected.id)
        else:
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
                    ["admin", "manager", "staff"],
                    placeholder="请选择角色",
                )

                if st.form_submit_button("添加用户", use_container_width=True, type="primary"):
                    result = add_user(username=username, hashed_password=hashed_password, role=role)
                    if result is not None:
                        st.error(result)
                    else:
                        st.rerun()

@st.dialog("确认删除用户")
def confirm_delete_user(user_id) -> None:
    col_1, col_2 = st.columns(2)
    with col_1:
        if st.button("确认", use_container_width=True, type="primary"):
            delete_user(user_id)
            st.rerun()
    with col_2:
        if st.button("取消", use_container_width=True):
            st.rerun()

def login_ui() -> None:
    with st.form("login_form"):
        st.header("登录")
        username = st.text_input("用户名").strip()
        password = st.text_input("密码", type="password")

        if st.form_submit_button("登录", use_container_width=True):
            user = get_user_by_username(username=username)

            if user is not None:
                if user.password == hash_password(password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = user.role
                    logger.info(f"用户: {username} 尝试登录")
                    st.rerun()
                else:
                    st.error("密码错误")
            else:
                st.error("用户名错误")
                    
def main_ui() -> None:
    st.set_page_config(
        page_title="案件管理系统",
        layout="wide",
        initial_sidebar_state="expanded",
        page_icon=":memo:", 
    )
    
    sidebar()
    
    if "page" in st.session_state:
        match st.session_state.page:
            case "案件上传":
                ui_case_upload()
            case "案件更新":
                ui_case_update()
            case "用户管理":
                ui_user_management()
             
if st.session_state.logged_in:
    main_ui()
else:
    login_ui()