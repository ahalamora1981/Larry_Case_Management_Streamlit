# views/case_update.py
import streamlit as st
from loguru import logger
from datetime import datetime

from package.database import (
    Session,
    Case,
    get_case_by_id, 
    get_all_batch_ids,
    read_case_from_sql, 
    update_case_court,
)

from views.sidebar import sidebar


sidebar("开庭更新 | 手动")

st.header("法诉案件管理系统 | 开庭更新 | 手动")

all_batch_ids = get_all_batch_ids()

# 对应的批次ID进行排序，先按年份降序，再按月份降序，由近到远。
all_batch_ids.sort(key=lambda x: int(x.split('-')[1]), reverse=True)
all_batch_ids.sort(key=lambda x: int(x.split('-')[0]), reverse=True)

if not all_batch_ids:
    st.warning("案件信息表为空")
    st.stop()

# 需要显示的数据库字段名和页面字段名对应关系
columns_pairs = [
    ('batch_id', '批次ID'),
    ('user_name', '用户名'),
    ('list_id', '列表ID'),
    ('full_name', '被告'),
    ('court_session_open_date', '开庭日期'),
    ('court_session_open_time', '开庭时间'),
    ('outstanding_amount', '标的金额'),
    ('outstanding_principal', '客户本金'),
    ('plaintiff_company', '原告公司'),
    ('court_law_firm', '开庭律所'),
    ('case_register_id', '立案号'),
    ('court', '法院全称'),
    ('court_phone', '法院电话'),
    ('court_status', '开庭状态'),
    ('judgement_remark', '判决备注'),
    ('is_case_closed', '结案与否'),
]

col_11, col_12, col_13, col_14, col_15, col_16 = st.columns(6)

with col_11:
    # 在页面中添加批次ID的下拉框
    batch_id_selected = st.selectbox(
        "批次ID",
        options=all_batch_ids,
        label_visibility="collapsed",
        placeholder="选择批次ID",
        index=0,
    )

with col_12:
    user_name_selected= st.text_input(
        "用户名",
        value=None,
        label_visibility="collapsed",
        placeholder="输入用户名",
    )

with col_13:
    # 在页面中添加开庭律所的输入框
    court_law_firm_selected = st.text_input(
        "开庭律所",
        value=None,
        label_visibility="collapsed",
        placeholder="输入开庭律所",
    )

with col_14:
    # 在页面中添加立案号的输入框
    case_register_id_selected = st.text_input(
        "立案号",
        value=None,
        label_visibility="collapsed",
        placeholder="输入立案号",
    )
    
with col_15:
    # 在页面中添加法院的输入框
    court_selected = st.text_input(
        "法院",
        value=None,
        label_visibility="collapsed",
        placeholder="输入法院",
    )
    
with col_16:
    # 在页面中添加开庭状态的输入框
    court_status_selected = st.text_input(
        "开庭状态",
        value=None,
        label_visibility="collapsed",
        placeholder="输入开庭状态",
    )
    
# with col_16:
#     # 在页面中添加结案与否的输入框
#     is_case_closed_selected = st.text_input(
#         "结案与否",
#         value=None,
#         label_visibility="collapsed",
#         placeholder="输入结案与否",
#     )
    
case_df = read_case_from_sql(batch_id_selected)

# 如选择了用户名，则针对该用户名进行筛选
if user_name_selected:
    case_df = case_df[case_df['user_name'].str.contains(user_name_selected, case=False, na=False)]

# 如选择了开庭律所，则针对该开庭律所进行筛选
if court_law_firm_selected:
    case_df = case_df[case_df['court_law_firm'].str.contains(court_law_firm_selected, case=False, na=False)]
    
# 如选择了立案号，则针对该立案号进行筛选
if case_register_id_selected:
    case_df = case_df[case_df['case_register_id'].str.contains(case_register_id_selected, case=False, na=False)]

# 如选择了法院，则针对该法院进行筛选
if court_selected:
    case_df = case_df[case_df['court'].str.contains(court_selected, case=False, na=False)]

# 如选择了开庭状态，则针对该开庭状态进行筛选
if court_status_selected:
    case_df = case_df[case_df['court_status'].str.contains(court_status_selected, case=False, na=False)]

# 如选择了结案与否，则针对该结案与否进行筛选
# if is_case_closed_selected:
#     case_df = case_df[case_df['is_case_closed'].str.contains(is_case_closed_selected, case=False, na=False)]

display_names = [item[1] for item in columns_pairs]
    
case_df_display = case_df[[item[0] for item in columns_pairs]]
case_df_display.columns = [item[1] for item in columns_pairs]

col_21, col_22, = st.columns([1, 1])

# 左侧信息栏
with col_21:
    index_selected = st.dataframe(
        case_df_display,
        on_select="rerun",  # 选择行时重新运行页面
        selection_mode="single-row",
        use_container_width=True,
        hide_index=True,  # 隐藏索引号
    )
    st.write(f"案件总数: {len(case_df_display)}")

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
    new_full_name = case_selected.full_name
    new_court_session_open_date = case_selected.court_session_open_date
    new_court_session_open_time = case_selected.court_session_open_time
    new_outstanding_amount = case_selected.outstanding_amount
    new_outstanding_principal = case_selected.outstanding_principal
    new_plaintiff_company = case_selected.plaintiff_company
    new_court_law_firm = case_selected.court_law_firm
    new_case_register_id = case_selected.case_register_id
    new_court = case_selected.court
    new_court_phone = case_selected.court_phone
    new_court_status = case_selected.court_status
    new_judgement_remark = case_selected.judgement_remark
    new_is_case_closed = case_selected.is_case_closed

    update_button_disabled = False
# 如未选择案件或案件对象为空，则启用“更新按钮”禁用(即按钮不可点击)
else:
    new_full_name = None
    new_court_session_open_date = None
    new_court_session_open_time = None
    new_outstanding_amount = None
    new_outstanding_principal = None
    new_plaintiff_company = None
    new_court_law_firm = None
    new_case_register_id = None
    new_court = None
    new_court_phone = None
    new_court_status = None
    new_judgement_remark = None
    new_is_case_closed = None

    update_button_disabled = True

# 右侧表单栏
with col_22:
    col_221, col_222 = st.columns([1, 1])
    
    with col_221:                
        # 如为选择案件，则禁用表单输入
        if case_selected is None:
            disable_form_input = True
        else:
            disable_form_input = False
        
        # 姓名
        st.text_input(
            "姓名", 
            value=new_full_name, 
            disabled=True,
        )
        
        # 开庭日期
        court_session_open_date = st.date_input(
            "开庭日期",
            value=new_court_session_open_date,
            disabled=disable_form_input,
        )
        
        # 开庭时间
        court_session_open_time = st.time_input(
            "开庭时间",
            value=new_court_session_open_time,
            disabled=disable_form_input,
        )
        
        # 标的金额
        outstanding_amount = st.text_input(
            "标的金额",
            value=new_outstanding_amount,
            disabled=disable_form_input,
        )
        
        # 客户本金
        outstanding_principal = st.text_input(
            "客户本金",
            value=new_outstanding_principal,
            disabled=disable_form_input,
        )
        
        # 原告公司
        plaintiff_company = st.text_input(
            "原告公司",
            value=new_plaintiff_company,
            disabled=disable_form_input,
        )
        
        # 开庭律所
        court_law_firm = st.text_input(
            "开庭律所",
            value=new_court_law_firm,
            disabled=disable_form_input,
        )
    
    with col_222:
        # 立案号
        case_register_id = st.text_input(
            "立案号",
            value=new_case_register_id,
            disabled=disable_form_input,
        )
        
        # 法院
        court = st.text_input(
            "法院",
            value=new_court,
            disabled=disable_form_input,
        )
        
        # 法院电话
        court_phone = st.text_input(
            "法院电话",
            value=new_court_phone,
            disabled=disable_form_input,
        )
        
        # 开庭状态
        court_status_options = [
            '待开庭',
            '待排庭',
            '已开庭',
        ]
        
        if new_court_status is None:
            court_status_index = 0
        else:
            court_status_index = court_status_options.index(new_court_status)
            
        court_status = st.selectbox(
            "开庭状态",
            options=court_status_options,
            index=court_status_index,
            disabled=disable_form_input,
        )
        
        # 判决备注
        judgement_remark = st.text_input(
            "判决备注",
            value=new_judgement_remark,
            disabled=disable_form_input,
        )
        
        # 结案与否
        is_case_closed_options = [
            '是',
            '否',
            '延期判决',
        ]
        
        if new_is_case_closed is None:
            is_case_closed_index = 0
        else:
            is_case_closed_index = is_case_closed_options.index(new_is_case_closed)
            
        is_case_closed = st.selectbox(
            "结案与否",
            options=is_case_closed_options,
            index=is_case_closed_index,
            disabled=disable_form_input,
        )
        
    # 提交按钮
    if st.button(
        "更新案件", 
        use_container_width=True, 
        type="primary",
        disabled=update_button_disabled,
    ):
        # 更新案件，输入参数为案件ID、新立案负责人ID、新状态序号
        session = Session()
        update_case_court(
            session, 
            id=case_selected.id, 
            court_session_open_date=court_session_open_date,
            court_session_open_time=court_session_open_time,
            outstanding_amount=outstanding_amount,
            outstanding_principal=outstanding_principal,
            plaintiff_company=plaintiff_company,
            court_law_firm=court_law_firm,
            case_register_id=case_register_id,
            court=court,
            court_phone=court_phone,
            court_status=court_status,
            judgement_remark=judgement_remark,
            is_case_closed=is_case_closed,
        )
        session.commit()
        session.close()
        
        logger.info(f"用户: {st.session_state.username} 把案件 {case_selected.id} 的法院开庭日期、开庭时间、标的金额、客户本金、原告公司、开庭律所、立案号、法院、法院电话、开庭状态、判决备注、结案与否更新为 {court_session_open_date}、{court_session_open_time}、{outstanding_amount}、{outstanding_principal}、{plaintiff_company}、{court_law_firm}、{case_register_id}、{court}、{court_phone}、{court_status}、{judgement_remark}、{is_case_closed}")
        st.rerun()
