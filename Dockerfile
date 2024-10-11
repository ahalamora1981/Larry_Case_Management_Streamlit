# 使用 Python 3.12.7-slim-bookworm 作为基础镜像
FROM python:3.12.7-slim-bookworm

# 设置工作目录
WORKDIR /app

# 创建并激活虚拟环境
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 更新 pip
RUN pip install --upgrade pip

# 复制 requirements.txt 到容器中并安装依赖
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 8501

# 运行 Streamlit 应用
CMD ["streamlit", "run", "app.py"]