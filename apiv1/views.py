from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import tempfile
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import whisper
from openai import OpenAI
import os

# Whisperモデルのロード
model = whisper.load_model('base')

@csrf_exempt
def transcribe_audio(request):
    if request.method == 'POST':
        audio_file = request.FILES.get('audio')
        if not audio_file:
            return JsonResponse({'error': '音声ファイルが提供されていません。'}, status=400)

        # 音声ファイルを一時ファイルに保存
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            for chunk in audio_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        # Whisperで音声をテキストに変換
        try:
            result = model.transcribe(temp_file_path, language='ja')
            text = result.get('text')
        except Exception as e:
            return JsonResponse({'error': f'音声認識中にエラーが発生しました: {str(e)}'}, status=500)
        finally:
            temp_file.close()

        # ChatGPTにテキストを送信して本当の感情を推測
        try:
            prompt = f"以下の文章の話者が本当に感じている感情や意図を推測して、漫画の吹き出しのような一言を発言して：\n\n{text}"
            client = OpenAI(
                # This is the default and can be omitted
                api_key=os.environ.get("OPENAI_API_KEY"),
            )
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "あなたはかぐや様は告らせたいに登場する四宮かぐやです。本当は、好きな人に告白したいと思っています。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7,
                n=10,
            )
            gpt_responses = [choice.message.content.strip() for choice in response.choices]
        except Exception as e:
            print(e)
            return JsonResponse({'error': f'ChatGPT API呼び出し中にエラーが発生しました: {str(e)}'}, status=500)

        print(gpt_responses)
        return JsonResponse({'text': text, 'gpt_responses': gpt_responses}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse({'error': '無効なリクエストメソッドです。'}, status=405)

class HelloWorldAPIView(APIView):
    def get(self, request):
        return Response({"message": "hello"})