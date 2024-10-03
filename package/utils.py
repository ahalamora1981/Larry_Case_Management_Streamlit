import os
import hashlib
import pandas as pd


CWD = os.getcwd()

def hash_password(password: str, salt: str = "2024"):
    # 将密码和盐组合在一起
    salted_password = password.encode('utf-8') + salt.encode('utf-8')

    # 使用 SHA-256 进行哈希
    hashed_password = hashlib.sha256(salted_password).hexdigest()

    # 返回哈希后的密码
    return hashed_password


if __name__ == "__main__":
    pass