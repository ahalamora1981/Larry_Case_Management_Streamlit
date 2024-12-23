# db.py
import os
import time
import pandas as pd
import streamlit as st
from io import BytesIO
from loguru import logger
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, ForeignKey, Float, Date, DateTime, Time, distinct
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm import Session as SessionClass


CWD = os.getcwd()

STATUS_FILE_PATH = os.path.join(CWD, "data", "status.xlsx")

# 创建数据库引擎，连接到 SQLite 数据库（如果数据库不存在，会自动创建）
engine_lawsuit = create_engine('sqlite:///lawsuit.db', echo=True)

# 创建一个基类，用于定义表
Base = declarative_base()


class Case(Base):
    __tablename__ = 'cases'

    id = Column(Integer, primary_key=True)
    batch_id = Column(String)  # 批次ID YYYY-MM
    batch_date = Column(Date)  # 批次日期
    company_name = Column(String)  # 公司名称
    shou_bie = Column(String)  # 手别
    case_id = Column(String)  # 案件id
    user_id = Column(String)  # 用户ID
    user_name = Column(String)  # 用户名
    full_name = Column(String)  # 用户姓名
    id_card = Column(String)  # 身份证号码
    gender = Column(String)  # 性别
    nationality = Column(String)  # 民族
    id_card_address = Column(String)  # 身份证地址
    mobile_phone = Column(String)  # 注册手机号
    list_id = Column(String)  # 列表ID
    rongdan_mode = Column(String)  # 融担模式
    contract_id = Column(String)  # 合同号
    capital_institution = Column(String)  # 资方机构
    rongdan_company = Column(String)  # 融担公司
    contract_amount = Column(String)  # 原始类型：Column(Float)    # 合同金额
    loan_date = Column(Date)  # 放款日期
    last_due_date = Column(Date)  # 最后一期应还款日
    loan_terms = Column(Integer)  # 借款期数
    interest_rate = Column(String)  # 原始类型：Column(Float)    # 利率
    overdue_start_date = Column(Date)  # 逾期开始日期
    last_pay_date = Column(Date)  # 上一个还款日期
    overdue_days = Column(Integer)  # 列表逾期天数
    outstanding_principal = Column(String)  # 原始类型：Column(Float)    # 待还本金
    outstanding_charge = Column(String)  # 原始类型：Column(Float)    # 待还费用
    outstanding_amount = Column(String)  # 原始类型：Column(Float)    # 待还金额
    data_collection_date = Column(Date)  # 数据提取日
    total_repurchase_principal = Column(String)  # 原始类型：Column(Float)    # 代偿回购本金
    total_repurchase_interest = Column(String)  # 原始类型：Column(Float)    # 代偿回购利息
    total_repurchase_penalty = Column(String)  # 原始类型：Column(Float)    # 代偿回购罚息
    total_repurchase_all = Column(String)  # 原始类型：Column(Float)    # 代偿回购总额
    latest_repurchase_date = Column(String)  # 最晚代偿时间
    can_lawsuit = Column(String)  # 是否可诉
    law_firm = Column(String, default=None)  # 承办律所
    lawyer = Column(String, default=None)  # 承办律师
    province_city = Column(String, default=None)  # 所属省/市
    court = Column(String, default=None)  # 法院全称
    status_id = Column(Integer, default=1)  # 状态序号

    case_register_id = Column(String, default=None)  # 立案号
    case_register_date = Column(Date, default=None)  # 立案日期
    repayment_plan = Column(String, default=None) # 还款计划
    update_remark = Column(String, default=None) # 更新备注
    
    court_session_open_date = Column(Date, default=None)  # 开庭日期
    court_session_open_time = Column(Time, default=None)  # 开庭时间
    plaintiff_company = Column(String, default=None)  # 原告公司
    court_law_firm = Column(String, default=None)  # 开庭律所
    court_phone = Column(String, default=None)  # 法院电话
    court_status = Column(String, default=None)  # 开庭状态
    judgement_remark = Column(String, default=None) # 判决备注
    is_case_closed = Column(String, default=None) # 结案与否
    
    custom_data_1 = Column(String, default=None) # 自定义数据1
    custom_data_2 = Column(String, default=None) # 自定义数据2
    custom_data_3 = Column(String, default=None) # 自定义数据3    
    custom_data_4 = Column(String, default=None) # 自定义数据4
    custom_data_5 = Column(String, default=None) # 自定义数据5
    custom_data_6 = Column(String, default=None) # 自定义数据6
    custom_data_7 = Column(String, default=None) # 自定义数据7
    custom_data_8 = Column(String, default=None) # 自定义数据8
    custom_data_9 = Column(String, default=None) # 自定义数据9
    custom_data_10 = Column(String, default=None) # 自定义数据10
    
    case_register_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # 立案负责人ID
    case_print_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # 打印负责人ID
    
    case_register_user = relationship("User", foreign_keys=[case_register_user_id], back_populates="register_cases")
    case_print_user = relationship("User", foreign_keys=[case_print_user_id], back_populates="print_cases")
    
    case_update_datetime = Column(DateTime, default=None)  # 立案日期


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)  # 用户名
    password = Column(String)  # 密码
    role = Column(String)  # 角色

    register_cases = relationship("Case", foreign_keys=[Case.case_register_user_id], back_populates="case_register_user")
    print_cases = relationship("Case", foreign_keys=[Case.case_print_user_id], back_populates="case_print_user")


# 创建所有定义的表
Base.metadata.create_all(engine_lawsuit)

# 创建一个会话类
Session = sessionmaker(bind=engine_lawsuit)

# 计时装饰器
def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"函数 {func.__name__} 执行时间: {end_time - start_time} 秒")
        return result
    return wrapper

def load_status_list() -> pd.DataFrame:
    df = pd.read_excel(
        STATUS_FILE_PATH,
        index_col=0,
    )
    
    if df.shape[0] != df.案件状态.shape[0]:
        raise ValueError("案件状态存在重复")
    
    return df

def get_all_batch_ids() -> list[str]:
    session = Session()
    # 查询所有非重复的 batch_id
    result = session.query(distinct(Case.batch_id)).all()
    all_batch_ids = [batch_id[0] for batch_id in result]
    session.close()
    return all_batch_ids

@timer
def read_case_from_sql(batch_id: str) -> pd.DataFrame:
    query = f"SELECT * FROM cases WHERE batch_id = '{batch_id}'"
    df = pd.read_sql_query(query, engine_lawsuit, index_col='id')
    return df

def read_case_from_sql_court() -> pd.DataFrame:
    query = f"SELECT * FROM cases WHERE court_status IS NOT NULL"
    df = pd.read_sql_query(query, engine_lawsuit, index_col='id')
    return df

def read_user_from_sql() -> pd.DataFrame:
    df = pd.read_sql_table("users", engine_lawsuit, index_col='id')
    return df

def import_cases(xlsx_file: BytesIO, batch_id: str) -> str | None:
    progress_text = "案件导入中..."
    progress_percentage = 0
    progress_bar = st.progress(progress_percentage, text=progress_text)

    session = Session()

    # 从 Excel 文件中读取数据
    df = pd.read_excel(xlsx_file, dtype=str)

    for _, row in df.iterrows():
        # 检查案件是否已存在，“用户名”+“列表ID”作为唯一键
        case_selected = session.query(Case).filter_by(
            user_name = row['用户名']
        ).filter_by(
            list_id = row['列表ID']
        ).first()

        # 检查案件是否已存在
        if case_selected is not None:
            # return f"【错误】案件 - 用户名: {row['用户名']} - 列表ID: {row['列表ID']} 已存在"
            session.delete(case_selected)
            session.commit()
            
        # 创建新的案件
        new_case = Case(
            batch_id=batch_id,
            batch_date=datetime.strptime(batch_id, "%Y-%m").date(),
            company_name = row['公司名称'] if not pd.isna(row['公司名称']) else None,
            shou_bie = row['手别'] if not pd.isna(row['手别']) else None,
            case_id = row['案件id'] if not pd.isna(row['案件id']) else None,
            user_id = row['用户ID'] if not pd.isna(row['用户ID']) else None,
            user_name = row['用户名'] if not pd.isna(row['用户名']) else None,
            full_name = row['用户姓名'] if not pd.isna(row['用户姓名']) else None,
            id_card = row['身份证号码'] if not pd.isna(row['身份证号码']) else None,
            gender = row['性别'] if not pd.isna(row['性别']) else None,
            nationality = row['民族'] if not pd.isna(row['民族']) else None,
            id_card_address = row['身份证地址'] if not pd.isna(row['身份证地址']) else None,
            mobile_phone = row['注册手机号'] if not pd.isna(row['注册手机号']) else None,
            list_id = row['列表ID'] if not pd.isna(row['列表ID']) else None,
            rongdan_mode = row['融担模式'] if not pd.isna(row['融担模式']) else None,
            contract_id = row['合同号'] if not pd.isna(row['合同号']) else None,
            capital_institution = row['资方机构'] if not pd.isna(row['资方机构']) else None,
            rongdan_company = row['融担公司'] if not pd.isna(row['融担公司']) else None,
            contract_amount = row['合同金额'] if not pd.isna(row['合同金额']) else None,
            loan_date = datetime.strptime(row['放款日期'][:10], "%Y-%m-%d").date() if not pd.isna(row['放款日期']) else None,
            last_due_date = datetime.strptime(row['最后一期应还款日'][:10], "%Y-%m-%d").date() if not pd.isna(row['最后一期应还款日']) else None,
            loan_terms = int(row['借款期数']) if not pd.isna(row['借款期数']) else None,
            interest_rate = row['利率'] if not pd.isna(row['利率']) else None,
            overdue_start_date = datetime.strptime(row['逾期开始日期'][:10], "%Y-%m-%d").date() if not pd.isna(row['逾期开始日期']) else None,
            last_pay_date = datetime.strptime(row['上一个还款日期'][:10], "%Y-%m-%d") if not pd.isna(row['上一个还款日期']) else None,
            overdue_days = int(row['列表逾期天数']) if not pd.isna(row['列表逾期天数']) else None,
            outstanding_principal = row['待还本金'] if not pd.isna(row['待还本金']) else None,
            outstanding_charge = row['待还费用'] if not pd.isna(row['待还费用']) else None,
            outstanding_amount = row['待还金额'] if not pd.isna(row['待还金额']) else None,
            data_collection_date = datetime.strptime(row['数据提取日'][:10], "%Y-%m-%d").date() if not pd.isna(row['数据提取日']) else None,
            total_repurchase_principal = row['代偿回购本金'] if not pd.isna(row['代偿回购本金']) else None,
            total_repurchase_interest = row['代偿回购利息'] if not pd.isna(row['代偿回购利息']) else None,
            total_repurchase_penalty = row['代偿回购罚息'] if not pd.isna(row['代偿回购罚息']) else None,
            total_repurchase_all = row['代偿回购总额'] if not pd.isna(row['代偿回购总额']) else None,
            latest_repurchase_date = row['最晚代偿时间'] if not pd.isna(row['最晚代偿时间']) else None,
            can_lawsuit = row['是否可诉'] if not pd.isna(row['是否可诉']) else None,
            law_firm = row['承办律所'] if not pd.isna(row['承办律所']) else None,
            lawyer = row['承办律师'] if not pd.isna(row['承办律师']) else None,
            province_city = row['所属省/市'] if not pd.isna(row['所属省/市']) else None,
            court = row['法院全称'] if not pd.isna(row['法院全称']) else None,
            status_id = 1,
            # case_register_id = None,
            # case_register_date = None,
            # court_session_open_date = None,
            case_register_user_id = 2,
            case_print_user_id = 2,
            # case_update_datetime = None,
            # remark = None
        )
        session.add(new_case)
        session.commit()
        
        # 更新进度条
        progress_percentage += (1 / df.shape[0])
        progress_bar.progress(progress_percentage, text=progress_text)
            
    session.close()

def update_cases_court(xlsx_file: BytesIO) -> str | None:
    progress_text = "案件导入中..."
    progress_percentage = 0
    progress_bar = st.progress(progress_percentage, text=progress_text)

    session = Session()

    # 从 Excel 文件中读取数据
    df = pd.read_excel(xlsx_file, dtype=str)
    
    error_msg_all = ""

    for _, row in df.iterrows():
        case_selected = session.query(Case).filter_by(
            user_name = row['用户名']
        ).filter_by(
            list_id = row['列表ID']
        ).first()

        if case_selected is None:
            error_msg = f"【告警】 - 用户名: {row['用户名']} - 列表ID: {row['列表ID']} 不存在"
            error_msg_all += error_msg + "\n"
            logger.warning(error_msg)
            
            # 更新进度条
            progress_percentage += (1 / df.shape[0])
            progress_bar.progress(progress_percentage, text=progress_text)
            
            continue
        
        try:
            # 更新案件
            case_selected.court_session_open_date = datetime.strptime(row['开庭日期'], "%Y-%m-%d").date() if not pd.isna(row['开庭日期']) else None
            case_selected.court_session_open_time = datetime.strptime(row['开庭时间'], "%H:%M:%S").time() if not pd.isna(row['开庭时间']) else None
            case_selected.plaintiff_company = row['原告公司'] if not pd.isna(row['原告公司']) else None
            case_selected.court_law_firm = row['开庭律所'] if not pd.isna(row['开庭律所']) else None
            case_selected.case_register_id = row['立案号'] if not pd.isna(row['立案号']) else None
            case_selected.court = row['法院全称'] if not pd.isna(row['法院全称']) else None
            case_selected.court_phone = row['法院电话'] if not pd.isna(row['法院电话']) else None
            case_selected.court_status = row['开庭状态'] if not pd.isna(row['开庭状态']) else None
            case_selected.judgement_remark = row['判决备注'] if not pd.isna(row['判决备注']) else None
            case_selected.is_case_closed = row['结案与否'] if not pd.isna(row['结案与否']) else None

            session.commit()
        except Exception as e:
            logger.error(e)
        
        # 更新进度条
        progress_percentage += (1 / df.shape[0])
        progress_bar.progress(progress_percentage, text=progress_text)
            
    session.close()
    
    if error_msg_all == "":
        return None
    else:
        return error_msg_all

def update_cases(xlsx_file: BytesIO, batch_id: str) -> str | None:
    case_status_df = load_status_list()    
    status_to_id = {df[1]['案件状态']: df[0] for df in case_status_df.iterrows()}
    # id_to_status = {df[0]: df[1]['案件状态'] for df in case_status_df.iterrows()}
    
    progress_text = "案件更新中..."
    progress_percentage = 0
    progress_bar = st.progress(progress_percentage, text=progress_text)

    session = Session()

    # 从 Excel 文件中读取数据
    df = pd.read_excel(xlsx_file, dtype=str)
    
    error_msg_all = ""

    for _, row in df.iterrows():
        case_selected = session.query(Case).filter_by(
            user_name = row['用户名']
        ).filter_by(
            list_id = row['列表ID']
        ).first()
        
        # print("##################\n")
        # print(status_to_id[row['案件状态']])
        # print(type(status_to_id[row['案件状态']]))
        # print("\n##################")

        if case_selected is None:
            error_msg = f"【告警】 - 用户名: {row['用户名']} - 列表ID: {row['列表ID']} 不存在"
            error_msg_all += error_msg + "\n"   
            logger.warning(error_msg)
            
            # 更新进度条
            progress_percentage += (1 / df.shape[0])
            progress_bar.progress(progress_percentage, text=progress_text)
            
            continue

        # if case_selected.batch_id != batch_id:
        #     return f"【告警】 - 用户名: {row['用户名']} - 列表ID: {row['列表ID']} 不属于批次: {batch_id}"
        
        try:
            # 更新案件
            case_selected.shou_bie = row['手别'] if not pd.isna(row['手别']) else None
            case_selected.user_name = row['用户名'] if not pd.isna(row['用户名']) else None
            case_selected.full_name = row['用户姓名'] if not pd.isna(row['用户姓名']) else None
            case_selected.list_id = row['列表ID'] if not pd.isna(row['列表ID']) else None
            case_selected.outstanding_principal = row['待还本金'] if not pd.isna(row['待还本金']) else None
            case_selected.law_firm = row['承办律所'] if not pd.isna(row['承办律所']) else None
            case_selected.lawyer = row['承办律师'] if not pd.isna(row['承办律师']) else None
            case_selected.province_city = row['所属省/市'] if not pd.isna(row['所属省/市']) else None
            case_selected.court = row['法院全称'] if not pd.isna(row['法院全称']) else None
            case_selected.status_id = status_to_id[row['案件状态']] if not pd.isna(row['案件状态']) else None
            case_selected.case_register_id = row['立案号'] if not pd.isna(row['立案号']) else None
            case_selected.case_register_date = datetime.strptime(row['立案日期'], "%Y-%m-%d").date() if not pd.isna(row['立案日期']) else None
            case_selected.court_session_open_date = datetime.strptime(row['开庭日期'], "%Y-%m-%d").date() if not pd.isna(row['开庭日期']) else None
            case_selected.remark = row['更新备注'] if not pd.isna(row['更新备注']) else None
            case_selected.repayment_plan = row['还款计划'] if not pd.isna(row['还款计划']) else None
            case_selected.case_update_datetime = datetime.now()

            session.commit()
        except Exception as e:
            logger.error(e)
        
        # 更新进度条
        progress_percentage += (1 / df.shape[0])
        progress_bar.progress(progress_percentage, text=progress_text)
            
    session.close()
    
    if error_msg_all == "":
        return None
    else:
        return error_msg_all

def get_all_cases() -> list[Case]:
    session = Session()
    cases = session.query(Case).all()
    session.close()

    return cases

def get_case_by_id(session: SessionClass, id: int) -> Case | None:
    this_case = session.query(Case).filter_by(id=str(id)).first()
    
    return this_case

def get_case_by_batch_id(batch_id: str) -> list[Case]:
    session = Session()
    cases = session.query(Case).filter_by(batch_id=batch_id).all()
    session.close()

    return cases

def update_case_court(
    session: SessionClass,
    id: int,
    court_session_open_date: Date | None = None,
    court_session_open_time: Time | None = None,
    outstanding_amount: str | None = None,
    outstanding_principal: str | None = None,
    plaintiff_company: str | None = None,
    court_law_firm: str | None = None,
    case_register_id: str | None = None,
    court: str | None = None,
    court_phone: str | None = None,
    court_status: str | None = None,
    judgement_remark: str | None = None,
    is_case_closed: str | None = None,
) -> None:
    this_case = session.query(Case).filter_by(id=str(id)).first()
    if this_case is None:
        raise Exception(f"【错误】案件 {id} 不存在")
    if court_session_open_date is not None:
        this_case.court_session_open_date = court_session_open_date
    if court_session_open_time is not None:
        this_case.court_session_open_time = court_session_open_time
    if outstanding_amount is not None:
        this_case.outstanding_amount = outstanding_amount
    if outstanding_principal is not None:
        this_case.outstanding_principal = outstanding_principal
    if plaintiff_company is not None:
        this_case.plaintiff_company = plaintiff_company
    if court_law_firm is not None:
        this_case.court_law_firm = court_law_firm
    if case_register_id is not None:
        this_case.case_register_id = case_register_id
    if court is not None:
        this_case.court = court
    if court_phone is not None:
        this_case.court_phone = court_phone
    if court_status is not None:
        this_case.court_status = court_status
    if judgement_remark is not None:
        this_case.judgement_remark = judgement_remark
    if is_case_closed is not None:
        this_case.is_case_closed = is_case_closed
    this_case.case_update_datetime = datetime.now()

def update_case(
    session: SessionClass, 
    id: int, 
    register_user_id: int | None = None,
    print_user_id: int | None = None,
    status_id: int | None = None,
    case_register_id: str | None = None,
    case_register_date: Date | None = None,
    court_session_open_date: Date | None = None,
) -> None:
    this_case = session.query(Case).filter_by(id=str(id)).first()
    if this_case is None:
        raise Exception(f"【错误】案件 {id} 不存在")
    if register_user_id is not None:
        this_case.case_register_user_id = register_user_id
    if print_user_id is not None:
        this_case.case_print_user_id = print_user_id
    if status_id is not None:
        this_case.status_id = status_id
    if case_register_id is not None:
        this_case.case_register_id = case_register_id
    if case_register_date is not None:
        this_case.case_register_date = case_register_date
    if court_session_open_date is not None:
        this_case.court_session_open_date = court_session_open_date
    this_case.case_update_datetime = datetime.now()

def delete_case_by_id(session: SessionClass, id: int | None) -> None:
    case_to_delete = session.query(Case).filter_by(id=id).first()
    session.delete(case_to_delete)

def get_all_users() -> list[User]:
    session = Session()
    users = session.query(User).all()
    session.close()

    return users

def get_all_users_df() -> pd.DataFrame:
    session = Session()
    users = session.query(User).all()
    session.close()

    df = pd.DataFrame([user.__dict__ for user in users])
    df = df.drop(columns=['_sa_instance_state'])

    return df

def get_user_by_username(username: str) -> User | None:
    session = Session()
    user = session.query(User).filter_by(username=username).first()
    session.close()

    return user

def get_user_by_id(id: int) -> User | None:
    session = Session()
    user = session.query(User).filter_by(id=str(id)).first()
    session.close()

    return user

def add_user(username: str, hashed_password: str, role: str) -> str | None:
    if get_user_by_username(username) is not None:
        return f"【错误】用户 {username} 已存在"
    
    session = Session()
    new_user = User(
        username=username,
        password=hashed_password,
        role=role,
    )
    session.add(new_user)
    session.commit()
    session.close()

def delete_user(id: int) -> None:
    session = Session()
    user_to_delete = session.query(User).filter_by(id=id).first()
    session.delete(user_to_delete)
    session.commit()
    session.close()

def reset_username(id: int, username: str) -> None:
    session = Session()
    user_with_username = session.query(User).filter_by(username=username).first()
            
    if user_with_username is None:
        user = session.query(User).filter_by(id=id).first()
        user.username = username
        session.commit()
        session.close()
    elif user_with_username.username == username:
        session.commit()
        session.close()
    else:
        session.commit()
        session.close()
        raise Exception(f"【错误】用户 {username} 已存在")

def reset_role(id: int, role: str) -> None:
    session = Session()
    user = session.query(User).filter_by(id=id).first()
    user.role = role
    session.commit()
    session.close()

def reset_password(id: int, hashed_password: str) -> None:
    session = Session()
    user = session.query(User).filter_by(id=id).first()
    user.password = hashed_password
    session.commit()
    session.close()