import os
import time
import shutil
from datetime import datetime
from zoneinfo import ZoneInfo


# 获取上海时区
shanghai_tz = ZoneInfo('Asia/Shanghai')

# 备份目录
db_backup_dir = "/app/backup/db"

# 数据库文件路径
db_file = "/app/lawsuit.db"

while True:
    # 获取当前时间
    current_time = datetime.now(shanghai_tz).strftime("%Y%m%d_%H%M%S")

    # 备份文件名
    db_backup_file = os.path.join(db_backup_dir, f"lawsuit_{current_time}.db")
    
    # 执行备份
    shutil.copy2(db_file, db_backup_file)
    
    # 等待一天
    time.sleep(24*60*60)