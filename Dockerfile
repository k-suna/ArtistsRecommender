# ベースイメージを指定
FROM python:3.11-slim

# 作業ディレクトリを作成（RUN，COPY，CMD等を実行するための作業用ディレクトリを指定）
WORKDIR /app

# 必要なパッケージをインストール（ベースイメージに対するコマンドの実行）
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコードをコピー（ホスト上のファイルのイメージへのコピー）
COPY . .

# ポートを指定
EXPOSE 5000

# アプリケーションを起動（イメージをもとに生成したコンテナ内でのコマンドの実行）
#CMD ["python", "app.py"]
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]