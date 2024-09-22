from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import tempfile
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import whisper
from openai import OpenAI
import os
# Importing other libraries
import joblib
import numpy as np

# Audio Imports
import pyaudio
import wave
import librosa
# Whisperモデルのロード
model = whisper.load_model('base')
# Opening Model
MLP = joblib.load("apiv1/assets/MLP.joblib")

# Audio Capture Parameters
CHUNKSIZE = 1024
RATE = 44100
p = pyaudio.PyAudio()
def start_stream(index=1):
    """Initializing PyAudio Capture Stream"""
    global stream
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE,
                    input=True, frames_per_buffer=CHUNKSIZE,
                    input_device_index=index)
def stop_stream():
    """Terminate stream."""
    stream.stop_stream()
    stream.close()
def get_emotion(filename: str):
    """Predict emotion."""
    global stream
    start_stream()
    frames = []
    for _ in range(0, int(RATE / CHUNKSIZE * 1)):
        data = stream.read(CHUNKSIZE)
        frames.append(data)
    with wave.open(filename, 'wb') as file:
        file.setnchannels(1)
        file.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        file.setframerate(RATE)
        file.writeframes(b''.join(frames))
    features = get_features(filename)
    emotion=MLP.predict(features)[0]
    stop_stream()
    p.terminate()
    return emotion
def get_features(filename: str):
    """
    Extract features from audio required for model training.

    return in required format.
    """
    # Reading the file in and extracting required data
    raw_data, sr = librosa.load(filename)

    # Creating an empty numpy array to add data later on
    data = np.array([])

    # Calculating & Appending mfcc
    mfcc = np.mean(librosa.feature.mfcc(
        y=raw_data, sr=sr, n_mfcc=40).T, axis=0)
    data = np.hstack((data, mfcc))

    # Calculating & Appending chroma
    stft = np.abs(librosa.stft(raw_data))
    chroma = np.mean(librosa.feature.chroma_stft(
        S=stft, sr=sr,).T, axis=0)
    data = np.hstack((data, chroma))

    # Calculating & Appending mel
    mel = np.mean(librosa.feature.melspectrogram(
        y=raw_data, sr=sr).T,axis=0)
    data = np.hstack((data, mel))

    x = []
    x.append(data)
    return np.array(x)

@csrf_exempt
def emotion(request):
    if request.method == 'POST':
        audio_file = request.FILES.get('audio')
        if not audio_file:
            return JsonResponse({'error': '音声ファイルが提供されていません。'}, status=400)

        # 一時ファイルを作成し、そのパスを取得
        _, temp_file_path = tempfile.mkstemp(suffix='.wav')
        
        # ファイルに書き込み
        with open(temp_file_path, 'wb') as temp_file:
            for chunk in audio_file.chunks():
                temp_file.write(chunk)
            print(temp_file_path)

        # 音波から感情を推測
        try:
            emotion = get_emotion(temp_file_path)
        except Exception as e:
            return JsonResponse({'error': f'音声認識中にエラーが発生しました: {str(e)}'}, status=500)
        finally:
            temp_file.close()

    #ChatGPTにテキストを送信して本当の感情を推測
        try:
            prompt = f"あなたの心の内の感情は{emotion}です。この時、あなたが心の中で思っていることを漫画の吹き出し風の一言を発して。"
            print("openai:client")
            print(os.environ.get("OPENAI_API_KEY"))
            client = OpenAI(
            #This is the default and can be omitted
                api_key=os.environ.get("OPENAI_API_KEY"),
            )
            print("openai")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "あなたはかぐや様は告らせたいに登場する四宮かぐやです"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7,
            )
            gpt_response = response.choices[0].message.content.strip()
        except Exception as e:
            print(e)
            return JsonResponse({'error': f'ChatGPT API呼び出し中にエラーが発生しました: {str(e)}'}, status=500)
"""
    #     # return JsonResponse({'text': text, 'gpt_response': gpt_response}, json_dumps_params={'ensure_ascii': False})
    #     return JsonResponse({'emotion': "AAAAA"})
    # else:
    #     return JsonResponse({'error': '無効なリクエストメソッドです。'}, status=405)