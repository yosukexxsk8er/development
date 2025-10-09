import sounddevice as sd
import numpy as np
import pyperclip
import tkinter as tk
from threading import Thread
import openai
import tempfile
import wave
import keyboard

# ======================
# OpenAI APIキー設定
# ======================
openai.api_key = "YOUR_OPENAI_API_KEY"  # ←自分のキーに置き換え

# ======================
# 音声録音パラメータ
# ======================
FS = 16000   # サンプリング周波数
DURATION = 5 # 録音秒数（必要に応じて変更）

# ======================
# Tkinter GUI設定
# ======================
root = tk.Tk()
root.title("AI音声入力ログ")
text_box = tk.Text(root, height=20, width=60)
text_box.pack()

# ======================
# 音声録音＆文字起こし処理
# ======================
def record_and_transcribe():
    try:
        text_box.insert(tk.END, "🎙 録音開始...\n")
        text_box.see(tk.END)

        # 音声録音
        audio = sd.rec(int(FS * DURATION), samplerate=FS, channels=1)
        sd.wait()

        # 一時WAVファイルに保存
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wav_file = f.name
            audio_int16 = (audio * 32767).astype(np.int16)
            with wave.open(wav_file, 'w') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(FS)
                wf.writeframes(audio_int16.tobytes())

        # Whisper APIで文字起こし
        with open(wav_file, "rb") as audio_file:
            response = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        text = response.text.strip()

        # 結果表示＆コピー
        text_box.insert(tk.END, f"✅ 認識結果: {text}\n")
        text_box.see(tk.END)
        pyperclip.copy(text)
        text_box.insert(tk.END, "📋 クリップボードにコピーしました\n\n")
        text_box.see(tk.END)

    except Exception as e:
        text_box.insert(tk.END, f"⚠️ エラー: {e}\n")
        text_box.see(tk.END)

# ======================
# グローバルショートカット設定
# ======================
def setup_global_shortcut():
    keyboard.add_hotkey('ctrl+shift+r', lambda: Thread(target=record_and_transcribe, daemon=True).start())
    keyboard.wait()  # 無限待機（常駐）

Thread(target=setup_global_shortcut, daemon=True).start()

# ======================
# Tkinterメインループ
# ======================
root.mainloop()