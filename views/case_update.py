# views/case_update.py
import streamlit as st
from loguru import logger

from package.database import (
    Session,
    Case,
    get_case_by_id, 
    get_all_users,
    get_user_by_id,
    get_all_batch_ids,
    read_case_from_sql, 
    update_case,
    delete_case_by_id,
    load_status_list,
)
from package.utils import get_case_df_display
from views.sidebar import sidebar


sidebar("案件更新")

st.header("法诉案件管理系统")

# 更新确认弹窗
@st.dialog("确认更新案件")
def confirm_update_cases(
    cases: list[Case], 
    new_user_id: int | None, 
    new_status_id: int | None
) -> None:
    col_1, col_2 = st.columns(2)
    with col_1:
        confirm_btn = st.button("确认", use_container_width=True, type="primary")
    with col_2:
        if st.button("取消", use_container_width=True):
            st.rerun()
    if confirm_btn:
        progress_text = "批量更新中..."
        progress_percentage = 0
        progress_bar = st.progress(progress_percentage, text=progress_text)
        
        session = Session()
        for i, this_case in enumerate(cases):
            update_case(session, this_case.id, new_user_id, new_status_id)
            # 更新进度条
            progress_percentage = i / len(cases)
            progress_bar.progress(progress_percentage, text=progress_text)
        session.commit()
        session.close()
        st.rerun()
            
# 确认弹窗
@st.dialog("确认删除案件")
def confirm_delete_cases(cases: list[Case]) -> None:
    col_1, col_2 = st.columns(2)
    with col_1:
        confirm_btn = st.button("确认", use_container_width=True, type="primary")
    with col_2:
        if st.button("取消", use_container_width=True):
            st.rerun()
    if confirm_btn:
        progress_text = "批量删除中..."
        progress_percentage = 0
        progress_bar = st.progress(progress_percentage, text=progress_text)
        
        session = Session()
        for i, this_case in enumerate(cases):
            delete_case_by_id(session, this_case.id)
            # 更新进度条
            progress_percentage = i / len(cases)
            progress_bar.progress(progress_percentage, text=progress_text)
        session.commit()
        session.close()
        st.rerun()

all_batch_ids = get_all_batch_ids()

status_df = load_status_list()

if not all_batch_ids:
    st.warning("案件信息表为空")
    st.stop()

# 需要显示的数据库字段名和页面字段名对应关系
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
    ('case_register_user_id', '立案负责人ID')
]
    
col_1, col_2 = st.columns([3, 1])

# 左侧信息栏
with col_1:
    col_11, col_12, col_13, col_14 = st.columns(4)
    
    with col_11:
        multi_select = st.selectbox(
            "是否多选", 
            ['单选(案件更新)', '多选(批量更新或删除)'], 
            index=0, 
            key="multi_select",
            placeholder="选择单选或多选",
            label_visibility="collapsed",
        )
        
        multi_select = True if multi_select == '多选(批量更新或删除)' else False
        
        if multi_select:
            selection_mode = "multi-row"
        else:
            selection_mode = "single-row"
    
    with col_12:
        # 在页面中添加批次ID的下拉框
        batch_id = st.selectbox(
            "批次ID",
            options=get_all_batch_ids(),
            label_visibility="collapsed",
            placeholder="选择批次ID",
            index=0,
        )
    
    with col_13:
        # 在页面中添加用户名的输入框
        user_name = st.text_input(
            "用户名",
            label_visibility="collapsed",
            placeholder="输入用户名",
        )
        
    # 如选择了批次ID，则针对该批次ID进行筛选
    if batch_id is not None:
        case_df = read_case_from_sql(batch_id)
        case_df_display = get_case_df_display(case_df, status_df, columns_pairs)

    # 如输入了用户名，则针对该用户名进行筛选
    if user_name:
        case_df_display = case_df_display[case_df_display['用户名'] == user_name]
    
    # 如登录角色为员工(staff)，则针对登录用户名进行筛选
    if st.session_state.role == "staff":
        case_df_display = case_df_display[case_df_display['立案负责人'] == st.session_state.username]

    index_selected = st.dataframe(
        case_df_display,
        on_select="rerun",  # 选择行时重新运行页面
        selection_mode=selection_mode,  # 选择模式：单行 or 多行
        use_container_width=True,
        hide_index=True,  # 隐藏索引号
    )

id_selected = None
case_selected = None

# 如选择了行，则获取该行的行ID和案件对象
if len(index_selected['selection']['rows']) > 0:
    id_selected = case_df.reset_index()['id'][index_selected['selection']['rows'][0]]
    session = Session()
    case_selected = get_case_by_id(session, id_selected)
    session.close()

# 如选择了案件且案件对象不为空，则获取案件的姓名、律师、立案负责人、和案件状态，并取消“更新按钮”禁用(即按钮可点击)
if case_selected is not None:
    full_name = case_selected.full_name
    lawyer = case_selected.lawyer
    case_register_user_id = case_selected.case_register_user_id
    status_id = case_selected.status_id
    update_button_disabled = False
# 如未选择案件或案件对象为空，则启用“更新按钮”禁用(即按钮不可点击)
else:
    full_name = None
    lawyer = None
    case_register_user_id = None
    status_id = None
    update_button_disabled = True

# 获取所有用户名
all_users = [user for user in get_all_users() if user.username != "admin"]
all_usernames = [user.username for user in all_users]

# 右侧表单栏
with col_2:
    if not multi_select:  # 单选
        # 更新案件的表单
        with st.form("case_update_form"):
            st.subheader("案件详情")
            
            # 如为选择案件，则禁用表单输入
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
            
            # 根据立案负责人ID，获取立案负责人在所有用户中的索引位置；如立案负责人ID为None，则设置索引位置为None
            if case_register_user_id is None:
                case_register_user_index = None
            else:
                case_register_user_index = all_usernames.index(get_user_by_id(case_register_user_id).username)
            
            # 如登录角色为员工(staff)，则不能更改立案负责人(即新立案负责人与原立案负责人相同)
            if st.session_state.role == "staff":
                new_user_id = case_register_user_id
            else:
                new_username = st.selectbox(
                    "立案负责人",
                    options=all_usernames,
                    index=case_register_user_index,
                    disabled=disable_form_input,
                )
                
                # 立案负责人ID为None，则新立案负责人ID为None
                # 否则，先通过新用户名确定其在所有用户名中的索引，然后通过其在所有用户名中的索引确定其ID
                if case_register_user_id is None:
                    new_user_id = None
                else:
                    new_user_id = all_users[all_usernames.index(new_username)].id
            
            # 如未选择案件或案件对象为空，则状态序号为None
            # 否则，通过状态序号确定其状态名称，然后通过状态名称确定其状态序号 
            if status_id is None:
                status_index = None
            else:
                status_index = status_df['案件状态'].tolist().index(status_df.loc[status_id, '案件状态'])
            
            # 案件状态的下拉框
            new_status = st.selectbox(
                "案件状态",
                options=status_df['案件状态'], 
                index=status_index,
                disabled=disable_form_input,
            )
            
            # 重置状态表的索引，以便通过“序号”列确定状态序号
            status_df_reset_index = status_df.reset_index()
            
            # 如未选择案件或案件对象为空，则状态序号为None
            # 否则，通过状态名称确定其状态序号
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
                # 更新案件，输入参数为案件ID、新立案负责人ID、新状态序号
                session = Session()
                update_case(session, case_selected.id, new_user_id, new_status_id)
                session.commit()
                session.close()
                
                logger.info(f"用户: {st.session_state.username} 把案件 {case_selected.id} 的状态从 {case_selected.status_id} 更新为 {new_status_id}")
                    
                st.rerun()
    else:  # 多选
        cases_selected = []
            
        # 如选择了行，则获取该行的行ID和案件对象
        if len(index_selected['selection']['rows']) > 0:
            case_df_reset_index = case_df.reset_index()
            
            session = Session()
            for index in index_selected['selection']['rows']:
                case_id = case_df_reset_index.loc[index, 'id']
                cases_selected.append(get_case_by_id(session, case_id))
            session.close()
            update_button_disabled = False
        else:
            update_button_disabled = True
            
        st.text_input(
            "已选案件数量",
            value=f"已选择案件数量: {len(cases_selected)}",
            disabled=True,
            label_visibility="collapsed",
        )
        
        # 如为未选择案件，则禁用表单更新
        if cases_selected == []:
            disable_form_input = True
        else:
            disable_form_input = False
            
        # 批量更新立案负责人
        with st.form("cases_register_user_update_form"):
            st.subheader("批量更新")
            
            if st.session_state.role != "staff":
                # 立案负责人下拉框
                new_username = st.selectbox(
                    "立案负责人",
                    options=all_usernames,
                    index=None,
                )
            else:
                new_username = None
                
            if new_username is not None:
                new_user_id = all_users[all_usernames.index(new_username)].id
            else:
                new_user_id = None
            
            # 案件状态的下拉框
            new_status = st.selectbox(
                "案件状态",
                options=status_df['案件状态'], 
                index=None,
            )
            
            if new_status is not None:
                # 重置状态表的索引，以便通过“序号”列确定状态序号
                status_df_reset_index = status_df.reset_index()
                
                # 通过状态名称确定其状态序号
                new_status_id = int(status_df_reset_index[status_df_reset_index['案件状态'] == new_status]['序号'].tolist()[0])
            else:
                new_status_id = None
            
            if st.form_submit_button(
                "更新所选案件",
                use_container_width=True,
                type="primary",
                disabled=update_button_disabled,
            ):
                confirm_update_cases(cases_selected, new_user_id, new_status_id)
                
        # 批量删除
        if st.session_state.role != "staff":
            with st.form("cases_delete_form"):
                st.subheader("批量删除")
            
                if st.form_submit_button(
                    "删除所选案件",
                    use_container_width=True,
                    type="primary",
                    disabled=update_button_disabled,
                ):
                    confirm_delete_cases(cases_selected)