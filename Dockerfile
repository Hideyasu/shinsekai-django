# ベースイメージとしてpython:3を使用
FROM python:3

EXPOSE 8080
# Whisperと音声処理のためにffmpegをインストール
RUN apt-get update && apt-get install -y ffmpeg

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