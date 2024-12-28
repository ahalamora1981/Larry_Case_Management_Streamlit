import os
import time
import hashlib
import pandas as pd
from loguru import logger
import streamlit as st

from package.database import get_all_users_df


CWD = os.getcwd()

# Timer decorator
def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Function {func.__name__} took {execution_time:.6f} seconds to execute.")
        return result
    return wrapper

def hash_password(password: str, salt: str = "2024"):
    # 将密码和盐组合在一起
    salted_password = password.encode('utf-8') + salt.encode('utf-8')

    # 使用 SHA-256 进行哈希
    hashed_password = hashlib.sha256(salted_password).hexdigest()

    # 返回哈希后的密码
    return hashed_password

@st.cache_data
def get_case_df_display(
    case_df: pd.DataFrame,
    status_df: pd.DataFrame,    
    columns_pairs: list[tuple],
) -> pd.DataFrame:
    if case_df.empty:
        return case_df
    
    # 过滤需要显示的数据库字段，并将其列名修改为页面字段名
    case_df_display = case_df[[item[0] for item in columns_pairs]].copy()
    case_df_display.rename(columns={item[0]: item[1] for item in columns_pairs}, inplace=True)
    # case_df_display.columns = [item[1] for item in columns_pairs]
    
    all_users_df = get_all_users_df()
    all_users_df.set_index('id', inplace=True)
    
    case_df_display['立案负责人'] = case_df_display['立案负责人ID'].map(all_users_df['username'])
    case_df_display['打印负责人'] = case_df_display['打印负责人ID'].map(all_users_df['username'])
    case_df_display['案件阶段'] = case_df_display['状态序号'].map(status_df['案件阶段'])
    case_df_display['案件状态'] = case_df_display['状态序号'].map(status_df['案件状态'])

    # 在 case_df_to_display 中添加 '立案负责人' 、'打印负责人'、'案件阶段'、和 '案件状态' 列
    # for case_id, register_user_id, print_user_id, status_id in zip(
    #     case_df_display.index, 
    #     case_df_display['立案负责人ID'], 
    #     case_df_display['打印负责人ID'],
    #     case_df_display['状态序号']
    # ):
    #     case_df_display.loc[case_id, '立案负责人'] = all_users_df.loc[register_user_id, 'username']
    #     case_df_display.loc[case_id, '打印负责人'] = all_users_df.loc[print_user_id, 'username']
    #     case_df_display.loc[case_id, '案件阶段'] = status_df.loc[status_id, '案件阶段']
    #     case_df_display.loc[case_id, '案件状态'] = status_df.loc[status_id, '案件状态']
    
    # 获取要插入的列索引（把“立案负责人”、“打印负责人”、“案件阶段”、“案件状态”放到前面）
    # index_to_insert = case_df_display.columns.tolist().index("身份证号码")
    
    # 将 '立案负责人' 、'案件阶段'、和 '案件状态' 列从df中弹出后插入到指定位置
    # case_df_display.insert(index_to_insert, "案件状态", case_df_display.pop("案件状态"))
    # case_df_display.insert(index_to_insert, "案件阶段", case_df_display.pop("案件阶段"))
    # case_df_display.insert(index_to_insert, "打印负责人", case_df_display.pop("打印负责人"))
    # case_df_display.insert(index_to_insert, "立案负责人", case_df_display.pop("立案负责人"))
        
    # 将 '立案负责人ID' 和 '状态序号' 列删除
    case_df_display.drop(columns=['立案负责人ID', '打印负责人ID', '状态序号'], inplace=True)
    
    return case_df_display

if __name__ == "__main__":
    pass