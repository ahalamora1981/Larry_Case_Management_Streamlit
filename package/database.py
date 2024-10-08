# db.py
import os
import pandas as pd
import streamlit as st
from io import BytesIO
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, Date, DateTime
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
    __tablename__ = 'case'

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
    contract_amount = Column(Float)  # 合同金额
    loan_date = Column(Date)  # 放款日期
    last_due_date = Column(Date)  # 最后一期应还款日
    loan_terms = Column(Integer)  # 借款期数
    interest_rate = Column(Float)  # 利率
    overdue_start_date = Column(Date)  # 逾期开始日期
    last_pay_date = Column(Date)  # 上一个还款日期
    overdue_days = Column(Integer)  # 列表逾期天数
    outstanding_principal = Column(Float)  # 待还本金
    outstanding_charge = Column(Float)  # 待还费用
    outstanding_amount = Column(Float)  # 待还金额
    data_collection_date = Column(Date)  # 数据提取日
    total_repurchase_principal = Column(Float)  # 代偿回购本金
    total_repurchase_interest = Column(Float)  # 代偿回购利息
    total_repurchase_penalty = Column(Float)  # 代偿回购罚息
    total_repurchase_all = Column(Float)  # 代偿回购总额
    latest_repurchase_date = Column(String)  # 最晚代偿时间
    can_lawsuit = Column(String)  # 是否可诉
    law_firm = Column(String)  # 承办律所
    lawyer = Column(String)  # 承办律师
    province_city = Column(String)  # 所属省/市
    court = Column(String)  # 法院全称
    status_id = Column(Integer, default=1)  # 状态序号

    case_register_user_id = Column(Integer, ForeignKey('user.id'), nullable=False)  # 立案负责人ID
    case_register_user = relationship("User", back_populates="cases", cascade="save-update")  # 立案负责人


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)  # 用户名
    password = Column(String)  # 密码
    role = Column(String)  # 角色

    cases = relationship("Case", back_populates="case_register_user", cascade="save-update")


# 创建所有定义的表
Base.metadata.create_all(engine_lawsuit)

# 创建一个会话类
Session = sessionmaker(bind=engine_lawsuit)

def load_status_list() -> pd.DataFrame:
    df = pd.read_excel(
        STATUS_FILE_PATH,
        index_col=0,
    )
    
    return df

def read_from_sql(table_name: str) -> pd.DataFrame:
    df = pd.read_sql_table(table_name, engine_lawsuit, index_col='id')
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

        if case_selected is not None:
            return f"【错误】案件 - 用户名: {row['用户名']} - 列表ID: {row['列表ID']} 已存在"
            
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
            contract_amount = float(row['合同金额']) if not pd.isna(row['合同金额']) else None,
            loan_date = datetime.strptime(row['放款日期'][:10], "%Y-%m-%d").date() if not pd.isna(row['放款日期']) else None,
            last_due_date = datetime.strptime(row['最后一期应还款日'][:10], "%Y-%m-%d").date() if not pd.isna(row['最后一期应还款日']) else None,
            loan_terms = int(row['借款期数']) if not pd.isna(row['借款期数']) else None,
            interest_rate = float(row['利率']) if not pd.isna(row['利率']) else None,
            overdue_start_date = datetime.strptime(row['逾期开始日期'][:10], "%Y-%m-%d").date() if not pd.isna(row['逾期开始日期']) else None,
            last_pay_date = datetime.strptime(row['上一个还款日期'][:10], "%Y-%m-%d") if not pd.isna(row['上一个还款日期']) else None,
            overdue_days = int(row['列表逾期天数']) if not pd.isna(row['列表逾期天数']) else None,
            outstanding_principal = float(row['待还本金']) if not pd.isna(row['待还本金']) else None,
            outstanding_charge = float(row['待还费用']) if not pd.isna(row['待还费用']) else None,
            outstanding_amount = float(row['待还金额']) if not pd.isna(row['待还金额']) else None,
            data_collection_date = datetime.strptime(row['数据提取日'][:10], "%Y-%m-%d").date() if not pd.isna(row['数据提取日']) else None,
            total_repurchase_principal = float(row['代偿回购本金']) if not pd.isna(row['代偿回购本金']) else None,
            total_repurchase_interest = float(row['代偿回购利息']) if not pd.isna(row['代偿回购利息']) else None,
            total_repurchase_penalty = float(row['代偿回购罚息']) if not pd.isna(row['代偿回购罚息']) else None,
            total_repurchase_all = float(row['代偿回购总额']) if not pd.isna(row['代偿回购总额']) else None,
            latest_repurchase_date = row['最晚代偿时间'] if not pd.isna(row['最晚代偿时间']) else None,
            can_lawsuit = row['是否可诉'] if not pd.isna(row['是否可诉']) else None,
            law_firm = row['承办律所'] if not pd.isna(row['承办律所']) else None,
            lawyer = row['承办律师'] if not pd.isna(row['承办律师']) else None,
            province_city = row['所属省/市'] if not pd.isna(row['所属省/市']) else None,
            court = row['法院全称'] if not pd.isna(row['法院全称']) else None,
            status_id = 1,
            case_register_user_id = 2,
        )
        session.add(new_case)
        session.commit()
        
        # 更新进度条
        progress_percentage += (1 / df.shape[0])
        progress_bar.progress(progress_percentage, text=progress_text)
            
    session.close()

def get_all_cases() -> list[Case]:
    session = Session()
    cases = session.query(Case).all()
    session.close()

    return cases

def get_case_by_id(session: SessionClass, id: int) -> Case | None:
    case = session.query(Case).filter_by(id=str(id)).first()
    
    return case

def get_case_by_batch_id(batch_id: str) -> list[Case]:
    session = Session()
    cases = session.query(Case).filter_by(batch_id=batch_id).all()
    session.close()

    return cases

def update_case(session: SessionClass, id: int, user_id: int | None, status_id: int | None) -> None:
    case = session.query(Case).filter_by(id=str(id)).first()
    if user_id is not None:
        case.case_register_user_id = user_id
    if status_id is not None:
        case.status_id = status_id

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

def reset_password(id: int, hashed_password: str) -> None:
    session = Session()
    user = session.query(User).filter_by(id=id).first()
    user.password = hashed_password
    session.commit()
    session.close()