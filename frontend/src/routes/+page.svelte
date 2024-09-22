<script>
	let isRecording = false;
	let mediaRecorder;
	let audioChunks = [];
	let audioBlob;

	// 音声キャプチャを開始する関数
	async function startRecording() {
		const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
		mediaRecorder = new MediaRecorder(stream);

		// 音声データを保存する
		mediaRecorder.ondataavailable = (event) => {
			audioChunks.push(event.data);
		};

		// 録音終了時にBlobとしてまとめる
		mediaRecorder.onstop = () => {
			audioBlob = new Blob(audioChunks, { type: 'audio/mp3' });
			audioChunks = [];
		};

		mediaRecorder.start();
		isRecording = true;
	}

	// 録音を停止する関数
	function stopRecording() {
		mediaRecorder.stop();
		isRecording = false;
	}

	// 録音した音声をダウンロードする関数
	function downloadAudio() {
		if (audioBlob) {
			const audioUrl = URL.createObjectURL(audioBlob);
			const a = document.createElement('a');
			a.href = audioUrl;
			a.download = 'recording.mp3';
			a.click();
		}
	}

	// バックエンドに音声ファイルを送信する関数
	async function sendAudio() {
		if (audioBlob) {
			const formData = new FormData();
			formData.append('audio', audioBlob, 'recording.mp3');

			try {
				const emotion_response = await fetch('http://127.0.0.1:8080/api/v1/emotion/',{
					method: 'POST',
					body: formData
				});

				if (emotion_response.ok) {
					console.log('音声ファイルが正常に送信されました');
				} else {
					console.error('ファイル送信に失敗しました');
				}
			} catch (error) {
				console.error('エラーが発生しました', error);
			}
		}
	}
</script>

<div>
	<button on:click={isRecording ? stopRecording : startRecording}>
		{isRecording ? '録音停止' : '録音開始'}
	</button>
	<button on:click={downloadAudio} disabled={!audioBlob}> ダウンロード </button>
	<button on:click={sendAudio} disabled={!audioBlob}> サーバーに送信 </button>
</div>

<style>
	button {
		margin: 5px;
		padding: 10px;
		font-size: 16px;
	}
</style>
