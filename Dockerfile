# ベースイメージを指定
FROM python:3.11-slim

# 作業ディレクトリを作成
WORKDIR /app

# 必要なパッケージをインストール
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコードをコピー
COPY . .

# ポートを指定
EXPOSE 5000

# アプリケーションを起動
#CMD ["python", "app.py"]
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]