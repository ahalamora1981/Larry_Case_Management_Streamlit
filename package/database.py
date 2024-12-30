# db.py
import os
import time
import pandas as pd
import streamlit as st
from loguru import logger
from datetime import datetime
import pytz
from sqlalchemy import (
    create_engine, Column, Integer, String, distinct, func
)
from sqlalchemy import or_, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


CWD = os.getcwd()

# 创建数据库引擎，连接到 SQLite 数据库（如果数据库不存在，会自动创建)}
engine_lawsuit = create_engine('sqlite:///lawsuit.db', echo=True)

# 创建一个基类，用于定义表
Base = declarative_base()


class Case(Base):
    __tablename__ = 'cases'

    id = Column(Integer, primary_key=True)
    
    ### 【首次导入模版】 ###
    batch_id = Column(String)  # 批次ID YYYY-MM
    company_name = Column(String)  # 公司名称
    shou_bie = Column(String)  # 手别
    case_id = Column(String)  # 案件id
    user_id = Column(String)  # 用户ID
    user_name = Column(String)  # 用户名
    full_name = Column(String)  # 用户姓名 | 被告(开庭表)
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
    loan_date = Column(String)  # 放款日期
    last_due_date = Column(String)  # 最后一期应还款日
    loan_terms = Column(Integer)  # 借款期数
    interest_rate = Column(String)  # 原始类型：Column(Float)    # 利率
    overdue_start_date = Column(String)  # 逾期开始日期
    last_pay_date = Column(String)  # 上一个还款日期
    overdue_days = Column(String)  # 列表逾期天数
    outstanding_principal = Column(String)  # 原始类型：Column(Float)    # 待还本金 | 客户本金(开庭表)
    outstanding_charge = Column(String)  # 原始类型：Column(Float)    # 待还费用
    outstanding_amount = Column(String)  # 原始类型：Column(Float)    # 待还金额 | 标的金额(开庭表)
    data_collection_date = Column(String)  # 数据提取日
    total_repurchase_principal = Column(String)  # 原始类型：Column(Float)    # 代偿回购本金
    total_repurchase_interest = Column(String)  # 原始类型：Column(Float)    # 代偿回购利息
    total_repurchase_penalty = Column(String)  # 原始类型：Column(Float)    # 代偿回购罚息
    total_repurchase_all = Column(String)  # 原始类型：Column(Float)    # 代偿回购总额
    latest_repurchase_date = Column(String)  # 最晚代偿时间
    if_can_lawsuit = Column(String)  # 是否可诉
    law_firm = Column(String)  # 承办律所
    lawyer = Column(String)  # 承办律师
    province_city = Column(String)  # 所属省/市
    court = Column(String)  # 法院全称
    
    ### 其他 ###
    case_status = Column(String)  # 案件状态
    case_register_user = Column(String)  # 立案负责人
    case_express_user = Column(String)  # 快递负责人
    case_update_datetime = Column(String)  # 案件更新时间

    ### 【更新导入模版】新增 ###
    case_register_id = Column(String, default=None)  # 立案号
    case_register_date = Column(String, default=None)  # 立案日期
    update_remark = Column(String, default=None) # 更新备注
    express_number = Column(String, default=None) # 快递单号
    
    ### 【开庭时间表导入模版】新增 ###
    trial_date = Column(String, default=None)  # 开庭日期
    trial_time = Column(String, default=None)  # 开庭时间
    plaintiff_company = Column(String, default=None)  # 原告公司
    trial_law_firm = Column(String, default=None)  # 开庭律所
    court_phone_number = Column(String, default=None)  # 法院电话
    trial_status = Column(String, default=None)  # 开庭状态
    sentence_remark = Column(String, default=None)  # 判决备注
    if_case_closed = Column(String, default=None)  # 结案与否
    
    ### 【邮寄状态变更模版】新增 ###
    # 无
    
    ### 【案件还款计划导入模版】新增 ###
    repayment_plan = Column(String, default=None)  # 还款计划
    repayment_start_date = Column(String, default=None)  # 还款开始日期
    repayment_channel = Column(String, default=None)  # 还款渠道
    repayment_remark = Column(String, default=None)  # 还款备注
    
    ### 自定义字段(预留) ###
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


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)  # 用户名
    password = Column(String)  # 密码
    role = Column(String)  # 角色


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

def get_all_batch_ids() -> list[str]:
    session = Session()
    # 查询所有非重复的 batch_id
    result = session.query(distinct(Case.batch_id)).all()
    all_batch_ids = [batch_id[0] for batch_id in result]
    
    # 自定义排序键函数，将“年-月”字符串转换为日期对象
    def sort_key(date_str):
        return datetime.strptime(date_str, "%Y-%m")

    # 使用 sorted 函数进行排序，reverse=True 表示从近期到早期
    sorted_batch_ids = sorted(all_batch_ids, key=sort_key, reverse=True)

    session.close()
    return sorted_batch_ids

@timer
def read_cases_from_sql(batch_id: str) -> pd.DataFrame:
    query = f"SELECT * FROM cases WHERE batch_id = '{batch_id}'"
    df = pd.read_sql_query(query, engine_lawsuit, index_col='id')
    return df

def read_users_from_sql() -> pd.DataFrame:
    df = pd.read_sql_table("users", engine_lawsuit, index_col='id')
    return df

def import_cases(df_import: pd.DataFrame, batch_id: str) -> str | None:
    progress_text = "案件导入中..."
    progress_percentage = 0
    progress_bar = st.progress(progress_percentage, text=progress_text)

    session = Session()
    
    shanghai_tz = pytz.timezone('Asia/Shanghai')
    shanghai_time = datetime.now(shanghai_tz)
    shanghai_time_str = shanghai_time.strftime('%Y-%m-%d %H:%M:%S')

    for _, row in df_import.iterrows():
        # 检查案件是否已存在、“用户名”+“列表ID”作为唯一键
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
            
            ### 【首次导入模版】 ###
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
            loan_date = row['放款日期'] if not pd.isna(row['放款日期']) else None,
            last_due_date = row['最后一期应还款日'] if not pd.isna(row['最后一期应还款日']) else None,
            loan_terms = row['借款期数'] if not pd.isna(row['借款期数']) else None,
            interest_rate = row['利率'] if not pd.isna(row['利率']) else None,
            overdue_start_date = row['逾期开始日期'] if not pd.isna(row['逾期开始日期']) else None,
            last_pay_date = row['上一个还款日期'] if not pd.isna(row['上一个还款日期']) else None,
            overdue_days = row['列表逾期天数'] if not pd.isna(row['列表逾期天数']) else None,
            outstanding_principal = row['待还本金'] if not pd.isna(row['待还本金']) else None,
            outstanding_charge = row['待还费用'] if not pd.isna(row['待还费用']) else None,
            outstanding_amount = row['待还金额'] if not pd.isna(row['待还金额']) else None,
            data_collection_date = row['数据提取日'] if not pd.isna(row['数据提取日']) else None,
            total_repurchase_principal = row['代偿回购本金'] if not pd.isna(row['代偿回购本金']) else None,
            total_repurchase_interest = row['代偿回购利息'] if not pd.isna(row['代偿回购利息']) else None,
            total_repurchase_penalty = row['代偿回购罚息'] if not pd.isna(row['代偿回购罚息']) else None,
            total_repurchase_all = row['代偿回购总额'] if not pd.isna(row['代偿回购总额']) else None,
            latest_repurchase_date = row['最晚代偿时间'] if not pd.isna(row['最晚代偿时间']) else None,
            if_can_lawsuit = row['是否可诉'] if not pd.isna(row['是否可诉']) else None,
            law_firm = row['承办律所'] if not pd.isna(row['承办律所']) else None,
            lawyer = row['承办律师'] if not pd.isna(row['承办律师']) else None,
            province_city = row['所属省/市'] if not pd.isna(row['所属省/市']) else None,
            court = row['法院全称'] if not pd.isna(row['法院全称']) else None,
            
            ### 其他 ###
            case_status = "案件初始导入",
            case_register_user = None,
            case_express_user = None,
            case_update_datetime = shanghai_time_str,
            
            ### 【更新导入模版】新增（仅作参考） ###
            # case_register_id = row['立案号'] if not pd.isna(row['立案号']) else None,
            # case_register_date = row['立案日期'] if not pd.isna(row['立案日期']) else None,
            # update_remark = row['更新备注'] if not pd.isna(row['更新备注']) else None,
            # express_number = row['快递单号'] if not pd.isna(row['快递单号']) else None,
            
            ### 【开庭时间表导入模版】新增（仅作参考） ###
            # trial_date = row['开庭日期'] if not pd.isna(row['开庭日期']) else None,
            # trial_time = row['开庭时间'] if not pd.isna(row['开庭时间']) else None,
            # plaintiff_company = row['原告公司'] if not pd.isna(row['原告公司']) else None,
            # trial_law_firm = row['开庭律所'] if not pd.isna(row['开庭律所']) else None,
            # court_phone_number = row['法院电话'] if not pd.isna(row['法院电话']) else None,
            # trial_status = row['开庭状态'] if not pd.isna(row['开庭状态']) else None,
            # sentence_remark = row['判决备注'] if not pd.isna(row['判决备注']) else None,
            # if_case_closed = row['是否结案'] if not pd.isna(row['是否结案']) else None,
            
            ### 【邮寄状态变更模版】新增（仅作参考） ###
            # 无
            
            ### 【案件还款计划导入模版】新增（仅作参考） ###
            # repayment_plan = row['还款计划'] if not pd.isna(row['还款计划']) else None,
            # repayment_start_date = row['开始还款日期'] if not pd.isna(row['开始还款日期']) else None,
            # repayment_channel = row['渠道'] if not pd.isna(row['渠道']) else None,
            # repayment_remark = row['还款备注'] if not pd.isna(row['还款备注']) else None,
        )
        session.add(new_case)
        session.commit()
        
        # 更新进度条
        progress_percentage += (1 / df_import.shape[0])
        progress_bar.progress(progress_percentage, text=progress_text)
            
    session.close()

def update_cases(
    df_update: pd.DataFrame, 
    update_fields: list[str],
    case_status: str | None = None
) -> str | None:
    shanghai_tz = pytz.timezone('Asia/Shanghai')
    shanghai_time = datetime.now(shanghai_tz)
    shanghai_time_str = shanghai_time.strftime('%Y-%m-%d %H:%M:%S')
    
    progress_text = "案件更新中..."
    progress_percentage = 0
    progress_bar = st.progress(progress_percentage, text=progress_text)

    session = Session()
    error_msg_all = ""

    for _, row in df_update.iterrows():
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
            progress_percentage += (1 / df_update.shape[0])
            progress_bar.progress(progress_percentage, text=progress_text)
            
            continue
        
        try:
            # 更新案件
            if '公司名称' in update_fields:
                case_selected.company_name = row['公司名称'] if not pd.isna(row['公司名称']) else None
            if '手别' in update_fields:
                case_selected.shou_bie = row['手别'] if not pd.isna(row['手别']) else None
            if '案件id' in update_fields:
                case_selected.case_id = row['案件id'] if not pd.isna(row['案件id']) else None
            if '用户ID' in update_fields:
                case_selected.user_id = row['用户ID'] if not pd.isna(row['用户ID']) else None
            if '用户名' in update_fields:
                case_selected.user_name = row['用户名'] if not pd.isna(row['用户名']) else None
            
            # “用户姓名”为原始字段，则“被告”为开庭表中相同字段的别名
            if '用户姓名' in update_fields:
                case_selected.full_name = row['用户姓名'] if not pd.isna(row['用户姓名']) else None
            elif '被告' in update_fields:
                case_selected.full_name = row['被告'] if not pd.isna(row['被告']) else None
                
            if '身份证号码' in update_fields:
                case_selected.id_card = row['身份证号码'] if not pd.isna(row['身份证号码']) else None
            if '性别' in update_fields:
                case_selected.gender = row['性别'] if not pd.isna(row['性别']) else None
            if '民族' in update_fields:
                case_selected.nationality = row['民族'] if not pd.isna(row['民族']) else None
            if '身份证地址' in update_fields:
                case_selected.id_card_address = row['身份证地址'] if not pd.isna(row['身份证地址']) else None
            if '注册手机号' in update_fields:
                case_selected.mobile_phone = row['注册手机号'] if not pd.isna(row['注册手机号']) else None
            if '列表ID' in update_fields:
                case_selected.list_id = row['列表ID'] if not pd.isna(row['列表ID']) else None
            if '融担模式' in update_fields:
                case_selected.rongdan_mode = row['融担模式'] if not pd.isna(row['融担模式']) else None
            if '合同号' in update_fields:
                case_selected.contract_id = row['合同号'] if not pd.isna(row['合同号']) else None
            if '资方机构' in update_fields:
                case_selected.capital_institution = row['资方机构'] if not pd.isna(row['资方机构']) else None
            if '融担公司' in update_fields:
                case_selected.rongdan_company = row['融担公司'] if not pd.isna(row['融担公司']) else None
            if '合同金额' in update_fields:
                case_selected.contract_amount = row['合同金额'] if not pd.isna(row['合同金额']) else None
            if '放款日期' in update_fields:
                case_selected.loan_date = row['放款日期'] if not pd.isna(row['放款日期']) else None
            if '最后一期应还款日' in update_fields:
                case_selected.last_due_date = row['最后一期应还款日'] if not pd.isna(row['最后一期应还款日']) else None
            if '借款期数' in update_fields:
                case_selected.loan_terms = row['借款期数'] if not pd.isna(row['借款期数']) else None
            if '利率' in update_fields:
                case_selected.interest_rate = row['利率'] if not pd.isna(row['利率']) else None
            if '逾期开始日期' in update_fields:
                case_selected.overdue_start_date = row['逾期开始日期'] if not pd.isna(row['逾期开始日期']) else None
            if '上一个还款日期' in update_fields:
                case_selected.last_pay_date = row['上一个还款日期'] if not pd.isna(row['上一个还款日期']) else None
            if '列表逾期天数' in update_fields:
                case_selected.overdue_days = row['列表逾期天数'] if not pd.isna(row['列表逾期天数']) else None
            
            # “待还本金”为原始字段，则“客户本金”为开庭表中相同字段的别名
            if '待还本金' in update_fields:
                case_selected.outstanding_principal = row['待还本金'] if not pd.isna(row['待还本金']) else None
            elif '客户本金' in update_fields:
                case_selected.outstanding_principal = row['客户本金'] if not pd.isna(row['客户本金']) else None
                
            if '待还费用' in update_fields:
                case_selected.outstanding_charge = row['待还费用'] if not pd.isna(row['待还费用']) else None
            
            # “待还金额”为原始字段，则“标的金额”为开庭表中相同字段的别名
            if '待还金额' in update_fields:
                case_selected.outstanding_amount = row['待还金额'] if not pd.isna(row['待还金额']) else None
            elif '标的金额' in update_fields:
                case_selected.outstanding_amount = row['标的金额'] if not pd.isna(row['标的金额']) else None
                
            if '数据提取日' in update_fields:
                case_selected.data_collection_date = row['数据提取日'] if not pd.isna(row['数据提取日']) else None
            if '代偿回购本金' in update_fields:
                case_selected.total_repurchase_principal = row['代偿回购本金'] if not pd.isna(row['代偿回购本金']) else None
            if '代偿回购利息' in update_fields:
                case_selected.total_repurchase_interest = row['代偿回购利息'] if not pd.isna(row['代偿回购利息']) else None
            if '代偿回购罚息' in update_fields:
                case_selected.total_repurchase_penalty = row['代偿回购罚息'] if not pd.isna(row['代偿回购罚息']) else None
            if '代偿回购总额' in update_fields:
                case_selected.total_repurchase_all = row['代偿回购总额'] if not pd.isna(row['代偿回购总额']) else None
            if '最晚代偿时间' in update_fields:
                case_selected.latest_repurchase_date = row['最晚代偿时间'] if not pd.isna(row['最晚代偿时间']) else None
            if '是否可诉讼' in update_fields:
                case_selected.if_can_lawsuit = row['是否可诉讼'] if not pd.isna(row['是否可诉讼']) else None
            if '承办律所' in update_fields:
                case_selected.law_firm = row['承办律所'] if not pd.isna(row['承办律所']) else None
            if '承办律师' in update_fields:
                case_selected.lawyer = row['承办律师'] if not pd.isna(row['承办律师']) else None
            if '所属省/市' in update_fields:
                case_selected.province_city = row['所属省/市'] if not pd.isna(row['所属省/市']) else None    
            if '法院全称' in update_fields:
                case_selected.court = row['法院全称'] if not pd.isna(row['法院全称']) else None
            if '案件状态' in update_fields:
                case_selected.case_status = row['案件状态'] if not pd.isna(row['案件状态']) else None
            if '立案号' in update_fields:
                case_selected.case_register_id = row['立案号'] if not pd.isna(row['立案号']) else None
            if '立案日期' in update_fields:
                case_selected.case_register_date = row['立案日期'] if not pd.isna(row['立案日期']) else None
            if '更新备注' in update_fields:
                case_selected.update_remark = row['更新备注'] if not pd.isna(row['更新备注']) else None
            if '快递单号' in update_fields:
                case_selected.express_number = row['快递单号'] if not pd.isna(row['快递单号']) else None
            if '开庭日期' in update_fields:
                case_selected.trial_date = row['开庭日期'] if not pd.isna(row['开庭日期']) else None
            if '开庭时间' in update_fields:
                case_selected.trial_time = row['开庭时间'] if not pd.isna(row['开庭时间']) else None
            if '标的金额' in update_fields:
                case_selected.target_amount = row['标的金额'] if not pd.isna(row['标的金额']) else None
            if '客户本金' in update_fields:
                case_selected.customer_principal = row['客户本金'] if not pd.isna(row['客户本金']) else None
            if '原告公司' in update_fields:
                case_selected.plaintiff_company = row['原告公司'] if not pd.isna(row['原告公司']) else None
            if '开庭律所' in update_fields:
                case_selected.trial_law_firm = row['开庭律所'] if not pd.isna(row['开庭律所']) else None
            if '法院电话' in update_fields:
                case_selected.court_phone_number = row['法院电话'] if not pd.isna(row['法院电话']) else None
            if '开庭状态' in update_fields:
                case_selected.trial_status = row['开庭状态'] if not pd.isna(row['开庭状态']) else None
            if '判决备注' in update_fields:
                case_selected.sentence_remark = row['判决备注'] if not pd.isna(row['判决备注']) else None
            if '是否结案' in update_fields:
                case_selected.if_case_closed = row['是否结案'] if not pd.isna(row['是否结案']) else None
            if '还款计划' in update_fields:
                case_selected.repayment_plan = row['还款计划'] if not pd.isna(row['还款计划']) else None
            if '开始还款日期' in update_fields:
                case_selected.repayment_start_date = row['开始还款日期'] if not pd.isna(row['开始还款日期']) else None
            if '渠道' in update_fields:
                case_selected.repayment_channel = row['渠道'] if not pd.isna(row['渠道']) else None
            if '还款备注' in update_fields:
                case_selected.repayment_remark = row['还款备注'] if not pd.isna(row['还款备注']) else None
                
            if case_status is not None:
                case_selected.case_status = case_status
            
            case_selected.case_update_datetime = shanghai_time_str
            
            session.commit()
        except Exception as e:
            logger.error(e)
            raise Exception(e)
        
        # 更新进度条
        progress_percentage += (1 / df_update.shape[0])
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

def get_count_all_cases() -> int:
    session = Session()
    count = session.query(func.count(Case.id)).scalar()
    session.close()
    return count

def get_case_by_id(id: int) -> Case | None:
    session = Session()
    this_case = session.query(Case).filter_by(id=str(id)).first()
    session.close()
    return this_case

def get_cases_by_batch_id(batch_id: str) -> list[Case]:
    session = Session()
    cases = session.query(Case).filter_by(batch_id=batch_id).all()
    session.close()
    return cases

def get_count_by_batch_id(batch_id: str) -> int:
    session = Session()
    count = session.query(func.count(Case.id)).filter_by(batch_id=batch_id).scalar()
    session.close()
    return count

def get_count_by_batch_id_and_registered(batch_id: str) -> int:
    """
    获取指定批次下符合条件的案件数量
    
    过滤案件状态为网上立案成功、邮寄材料、诉前调解，或者快递单号不为空
    """
    session = Session()
    count = session.query(
        func.count(Case.id)
    ).filter_by(
        batch_id=batch_id
    ).filter(
        or_(
            Case.case_status == "网上立案成功",
            Case.case_status == "邮寄材料",
            Case.case_status == "诉前调解",
            and_(
                Case.express_number.isnot(None),
                Case.express_number != ""
            )
        )
    ).scalar()
    return count

def get_count_by_batch_id_and_repayment(batch_id: str) -> int:
    session = Session()
    count = session.query(
        func.count(Case.id)
    ).filter_by(
        batch_id=batch_id
    ).filter(
        and_(
            Case.repayment_plan.isnot(None),
            Case.repayment_plan != ""
        )
    ).scalar()
    return count

def get_count_by_year(year: int) -> int:
    session = Session()
    count = session.query(func.count(Case.batch_id)).filter(Case.batch_id.like(f'{year}-%')).scalar()
    session.close()
    return count

def delete_cases_by_batch_id(batch_id: str) -> None:
    session = Session()
    cases_to_delete = session.query(Case).filter_by(batch_id=batch_id).all()
    for case in cases_to_delete:
        session.delete(case)
    session.commit()
    session.close()
    return None

def delete_case_by_id(id: int | None) -> None:
    session = Session()
    case_to_delete = session.query(Case).filter_by(id=id).first()
    session.delete(case_to_delete)
    session.commit()
    return None

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
    return None

def delete_user(id: int) -> None:
    session = Session()
    user_to_delete = session.query(User).filter_by(id=id).first()
    session.delete(user_to_delete)
    session.commit()
    session.close()
    return None

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

    return None

def reset_role(id: int, role: str) -> None:
    session = Session()
    user = session.query(User).filter_by(id=id).first()
    user.role = role
    session.commit()
    session.close()
    return None

def reset_password(id: int, hashed_password: str) -> None:
    session = Session()
    user = session.query(User).filter_by(id=id).first()
    user.password = hashed_password
    session.commit()
    session.close()
    return None