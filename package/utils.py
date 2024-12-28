import os
import time
import hashlib
import pandas as pd
from loguru import logger
import streamlit as st


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
def get_cases_df_display(
    cases_df: pd.DataFrame,  
    columns_pairs: list[tuple],
) -> pd.DataFrame:
    if cases_df.empty:
        return cases_df
    
    # 过滤需要显示的数据库字段，并将其列名修改为页面字段名
    cases_df_display = cases_df[[item[0] for item in columns_pairs]].copy()
    cases_df_display.rename(columns={item[0]: item[1] for item in columns_pairs}, inplace=True)
    
    return cases_df_display

STATUS_FILE_PATH = os.path.join(CWD, "data", "0_案件状态.xlsx")

def load_status_list() -> pd.DataFrame:
    df = pd.read_excel(
        STATUS_FILE_PATH,
        index_col=0,
    )
    
    return df


if __name__ == "__main__":
    pass