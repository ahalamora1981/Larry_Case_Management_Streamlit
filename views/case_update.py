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
    update_case,
    load_status_list,
)
from package.utils import get_case_df_display
from views.sidebar import sidebar

def case_update_staff_page(user_type: str = None):
    # 更新确认弹窗
    @st.dialog("确认更新案件")
    def confirm_update_cases(
        cases: list[Case], 
        new_status_id: int | None = None,
        case_register_date: datetime | None = None
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
                update_case(
                    session, 
                    id=this_case.id, 
                    status_id=new_status_id,
                    case_register_date=case_register_date,
                )
                # 更新进度条
                progress_percentage = i / len(cases)
                progress_bar.progress(progress_percentage, text=progress_text)
            session.commit()
            session.close()
            st.rerun()

    all_batch_ids = get_all_batch_ids()
    
    # 对应的批次ID进行排序，先按年份降序，再按月份降序，由近到远。
    all_batch_ids.sort(key=lambda x: int(x.split('-')[1]), reverse=True)
    all_batch_ids.sort(key=lambda x: int(x.split('-')[0]), reverse=True)
    
    case_status_df = load_status_list()    
    status_to_id = {df[1]['案件状态']: df[0] for df in case_status_df.iterrows()}
    id_to_status = {df[0]: df[1]['案件状态'] for df in case_status_df.iterrows()}
    unique_stage_list = case_status_df['案件阶段'].unique().tolist()

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
        ('case_register_id', '立案号'),
        ('case_register_date', '立案日期'),
        ('court_session_open_date', '开庭日期'),
        ('case_register_user_id', '立案负责人ID'),
        ('case_print_user_id', '打印负责人ID'),
        ('case_update_datetime', '案件更新时间')
    ]
    
    col_11, col_12, col_13, col_14, col_15, col_16 = st.columns(6)

    with col_11:
        multi_selection = st.toggle(
                "批量处理",
                key="selection",
            )
        
        if not multi_selection:
            selection_mode = "single-row"
        else:
            selection_mode = "multi-row"

    with col_12:
        # 在页面中添加批次ID的下拉框
        batch_id_selected = st.selectbox(
            "批次ID",
            options=all_batch_ids,
            label_visibility="collapsed",
            placeholder="选择批次ID",
            index=0,
        )

    with col_13:
        # 在页面中添加用户名的输入框
        user_name_selected= st.text_input(
            "用户名",
            value=None,
            label_visibility="collapsed",
            placeholder="输入用户名",
        )

    # 如选择了批次ID，则针对该批次ID进行筛选
    if batch_id_selected is not None:
        case_df = read_case_from_sql(batch_id_selected)

    lawyer_list = case_df['lawyer'].unique().tolist()
    if None in lawyer_list:
        lawyer_list.remove(None) 
        
    with col_14:
        # 在页面中添加律师的输入框
        lawyer_selected = st.selectbox(
            "承办律师",
            lawyer_list,
            label_visibility="collapsed",
            placeholder="选择律师",
            index=None
        )

    with col_15:
        # 在页面中添加法院的下拉框
        court_selected = st.text_input(
            "法院",
            value=None,
            label_visibility="collapsed",
            placeholder="选择法院",
        )
        
    with col_16:
        # 在页面中添加案件状态的输入框
        status_selected = st.selectbox(
            "案件状态",
            options=case_status_df['案件状态'].tolist(),
            label_visibility="collapsed",
            placeholder="选择案件状态",
            index=None
        )
        
    # 如选择了批次ID，则针对该批次ID进行筛选
    if batch_id_selected is not None:
        case_df = read_case_from_sql(batch_id_selected)

    # 如选择了用户名，则针对该用户名进行筛选
    if user_name_selected:
        case_df = case_df[case_df['user_name'].str.contains(user_name_selected, case=False, na=False)]
    
    # 如选择了律师，则针对该律师进行筛选
    if lawyer_selected:
        case_df = case_df[case_df['lawyer'].str.contains(lawyer_selected, case=False, na=False)]
    
    # 如选择了法院，则针对该法院进行筛选
    if court_selected:
        case_df = case_df[case_df['court'].str.contains(court_selected, case=False, na=False)]
    
    # 如选择了案件状态，则针对该案件状态进行筛选
    if status_selected:
        case_df = case_df[case_df['status_id'] == status_to_id[status_selected]]
    
    # 根据登录用户名进行筛选
    if user_type == "register":
        case_df = case_df[case_df['case_register_user_id'] == st.session_state.user_id]
    elif user_type == "print":
        case_df = case_df[case_df['case_print_user_id'] == st.session_state.user_id]
    elif user_type == "manager":
        pass
    else:
        raise ValueError("user_type must be 'register', 'print' or 'manager'")
    
    case_df_display = get_case_df_display(case_df, case_status_df, columns_pairs)

    col_21, col_22 = st.columns([3, 1])

    # 左侧信息栏
    with col_21:
        index_selected = st.dataframe(
            case_df_display,
            on_select="rerun",  # 选择行时重新运行页面
            selection_mode=selection_mode,  # 选择模式：单行 or 多行
            use_container_width=True,
            hide_index=True,  # 隐藏索引号
        )
        st.write(f"案件数量：{len(case_df_display)}")

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
        status_id = case_selected.status_id
        update_button_disabled = False
    # 如未选择案件或案件对象为空，则启用“更新按钮”禁用(即按钮不可点击)
    else:
        full_name = None
        status_id = None
        update_button_disabled = True

    # 右侧表单栏
    with col_22:
        if not multi_selection:  # 单选
            # 更新案件
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
                "当前案件阶段",
                value=case_status_df.loc[status_id, '案件阶段'] if status_id is not None else None,
                disabled=True,
            )
            
            st.text_input(
                "当前案件状态",
                value=case_status_df.loc[status_id, '案件状态'] if status_id is not None else None,
                disabled=True,
            )
        
            # 案件阶段的下拉框
            new_case_stage = st.selectbox(
                "新的案件阶段",
                options=unique_stage_list,
                index=None,
                disabled=disable_form_input,
            )
            
            current_status_list = case_status_df[case_status_df['案件阶段'] == new_case_stage]['案件状态'].tolist()
            
            # 案件状态的下拉框
            new_case_status = st.selectbox(
                "新的案件状态",
                options=current_status_list, 
                index=None,
                disabled=disable_form_input,
            )
            
            if new_case_status is not None:
                new_status_id = status_to_id[new_case_status]
            
            if st.toggle("是否更新立案信息"):
                case_register_id = st.text_input(
                    "立案号",
                    disabled=disable_form_input,
                )
                case_register_date = st.date_input(
                    "立案日期",
                    value=datetime.now(),
                    disabled=disable_form_input,
                )
            else:
                case_register_id = None
                case_register_date = None
            
            # 提交按钮
            if st.button(
                "更新案件", 
                use_container_width=True, 
                type="primary",
                disabled=update_button_disabled,
            ):
                # 更新案件，输入参数为案件ID、新立案负责人ID、新状态序号
                session = Session()
                update_case(
                    session, 
                    id=case_selected.id, 
                    status_id=new_status_id,
                    case_register_id=case_register_id,
                    case_register_date=case_register_date,
                )
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
            
            # 如为未选择案件，则禁用表单更新
            if cases_selected == []:
                disable_form_input = True
            else:
                disable_form_input = False
                
            # 批量更新立案负责人
            st.subheader("批量更新")
            
            st.text_input(
                "已选案件数量",
                value=f"已选择案件数量: {len(cases_selected)}",
                disabled=True,
                label_visibility="collapsed",
            )
            
            # 案件阶段的下拉框
            new_case_stage = st.selectbox(
                "新的案件阶段",
                options=unique_stage_list,
                index=None,
                disabled=disable_form_input,
            )
            
            current_status_list = case_status_df[case_status_df['案件阶段'] == new_case_stage]['案件状态'].tolist()
            
            # 案件状态的下拉框
            new_case_status = st.selectbox(
                "新的案件状态",
                options=current_status_list, 
                index=None,
                disabled=disable_form_input,
            )
            
            if new_case_status is not None:
                # 重置状态表的索引，以便通过“序号”列确定状态序号
                status_df_reset_index = case_status_df.reset_index()
                
                # 通过状态名称确定其状态序号
                new_status_id = int(status_df_reset_index[status_df_reset_index['案件状态'] == new_case_status]['序号'].tolist()[0])
            else:
                new_status_id = None
                
            if st.button(
                "更新所选案件",
                use_container_width=True,
                type="primary",
                disabled=update_button_disabled,
            ):
                confirm_update_cases(cases_selected, new_status_id)