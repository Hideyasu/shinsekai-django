# ベースイメージの選択
FROM python:3.9-slim

EXPOSE 8080
# 必要なシステムライブラリをインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    portaudio19-dev \
    libsndfile1-dev \
    && rm -rf /var/lib/apt/lists/*

# Pythonの出力がバッファリングされないように環境変数を設定
ENV PYTHONUNBUFFERED 1

# /codeディレクトリを作成して作業ディレクトリを設定
RUN mkdir /code
WORKDIR /code

# requirements.txtをコンテナに追加して必要なパッケージをインストール
ADD requirements.txt /code/
RUN pip install -r requirements.txt

# Whisperライブラリをインストール
RUN pip install openai-whisper

# プロジェクトファイルをコンテナにコピー
ADD . /code/

CMD python3 manage.py runserver 0.0.0.0:8080