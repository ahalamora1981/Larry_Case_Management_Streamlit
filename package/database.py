# db.py
import os
import pandas as pd
import streamlit as st
from io import BytesIO
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, Boolean, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


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
    last_pay_date = Column(DateTime)  # 上一个还款日期
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
        if str(row['上一个还款日期']) == 'nan':
            last_pay_date = None
        else:
            last_pay_date = datetime.strptime(row['上一个还款日期'], "%Y-%m-%d %H:%M:%S.%f")
            
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
            company_name = row['公司名称'],
            shou_bie = row['手别'],
            case_id = row['案件id'],
            user_id = row['用户ID'],
            user_name = row['用户名'],
            full_name = row['用户姓名'],
            id_card = row['身份证号码'],
            gender = row['性别'],
            nationality = row['民族'],
            id_card_address = row['身份证地址'],
            mobile_phone = row['注册手机号'],
            list_id = row['列表ID'],
            rongdan_mode = row['融担模式'],
            contract_id = row['合同号'],
            capital_institution = row['资方机构'],
            rongdan_company = row['融担公司'],
            contract_amount = float(row['合同金额']),
            loan_date = datetime.strptime(row['放款日期'], "%Y-%m-%d").date(),
            last_due_date = datetime.strptime(row['最后一期应还款日'], "%Y-%m-%d").date(),
            loan_terms = int(row['借款期数']),
            interest_rate = float(row['利率']),
            overdue_start_date = datetime.strptime(row['逾期开始日期'], "%Y-%m-%d").date(),
            last_pay_date = last_pay_date,
            overdue_days = int(row['列表逾期天数']),
            outstanding_principal = float(row['待还本金']),
            outstanding_charge = float(row['待还费用']),
            outstanding_amount = float(row['待还金额']),
            data_collection_date = datetime.strptime(row['数据提取日'], "%Y-%m-%d").date(),
            total_repurchase_principal = float(row['代偿回购本金']),
            total_repurchase_interest = float(row['代偿回购利息']),
            total_repurchase_penalty = float(row['代偿回购罚息']),
            total_repurchase_all = float(row['代偿回购总额']),
            latest_repurchase_date = row['最晚代偿时间'],
            can_lawsuit = row['是否可诉'],
            law_firm = row['承办律所'],
            lawyer = row['承办律师'],
            province_city = row['所属省/市'],
            court = row['法院全称'],
            status_id = 1,
            case_register_user_id = 2,
        )
        session.add(new_case)
        session.commit()
        
        progress_percentage += (1 / df.shape[0])
        progress_bar.progress(progress_percentage, text=progress_text)
            
    session.close()

def get_case_by_id(id: int) -> Case | None:
    session = Session()
    case = session.query(Case).filter_by(id=str(id)).first()
    session.close()
    
    return case

def update_case(id: int, user_id: int, status_id: int) -> None:
    session = Session()
    case = session.query(Case).filter_by(id=str(id)).first()
    case.status_id = status_id
    case.case_register_user_id = user_id
    session.commit()
    session.close()

def get_all_users() -> list[User]:
    session = Session()
    users = session.query(User).all()
    session.close()

    return users

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
