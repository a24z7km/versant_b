import streamlit as st
import difflib
from audio_recorder_streamlit import audio_recorder
import io
from gtts import gTTS
import speech_recognition as sr

# 問題リスト
QUESTIONS = [
    "You're taller than he is.",
    "He wanted to know if the price included breakfast.",
    "They're trying to fix the problem, but so far, they've had no luck.",
    "I'll have to check my schedule and get back to you.",
    "Could you please repeat that a little more slowly?",
    "I'm not sure what time the meeting starts.",
    "She said she would call back later this afternoon.",
    "We've been waiting here for almost an hour.",
    "Do you know where the nearest subway station is?",
    "I'd like to make a reservation for two people.",
    "Can you help me find what I'm looking for?",
    "It's been a long time since we last saw each other.",
    "I didn't realize how difficult this would be.",
    "Would you mind if I opened the window?",
    "He's been working on that project for three months.",
    "I think we should leave before it gets too late.",
]

def make_tts_audio(text: str) -> bytes:
    tts = gTTS(text=text, lang="en")
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp.read()

# アプリの状態管理
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "show_result" not in st.session_state:
    st.session_state.show_result = False
if "user_text" not in st.session_state:
    st.session_state.user_text = ""
if "recorded_audio" not in st.session_state:
    st.session_state.recorded_audio = None

st.title("Repeat the Sentence (音声テスト版)")

# 全問終了判定
if st.session_state.q_index >= len(QUESTIONS):
    st.success("🎉 全問終了しました！")
    if st.button("最初からリセット"):
        st.session_state.q_index = 0
        st.session_state.show_result = False
        st.rerun()
    st.stop()

# 現在の問題
target = QUESTIONS[st.session_state.q_index]

st.subheader(f"Question {st.session_state.q_index + 1} / {len(QUESTIONS)}")

# ==========================================
# フェーズ1：回答中（テキストは隠す）
# ==========================================
if not st.session_state.show_result:
    st.write("🎧 **1. 音声を聞く** (テキストは隠されています)")

    if st.button("▶️ 問題の音声を再生"):
        with st.spinner("音声を生成中..."):
            st.audio(make_tts_audio(target), format="audio/mp3")

    st.divider()

    st.write("🎙️ **2. 復唱して録音する** (マイクアイコンを押して開始 / 停止)")
    audio_bytes = audio_recorder()

    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")

        if st.button("この録音で採点する"):
            with st.spinner("音声を解析中..."):
                recognizer = sr.Recognizer()
                audio_file = io.BytesIO(audio_bytes)

                try:
                    with sr.AudioFile(audio_file) as source:
                        audio_data = recognizer.record(source)
                    user_transcription = recognizer.recognize_google(audio_data)
                except sr.UnknownValueError:
                    user_transcription = ""
                except sr.RequestError as e:
                    st.error(f"音声認識サービスに接続できませんでした: {e}")
                    st.stop()

                similarity = difflib.SequenceMatcher(
                    None, target.lower(), user_transcription.lower()
                ).ratio()

                st.session_state.score = int(similarity * 100)
                st.session_state.user_text = user_transcription
                st.session_state.recorded_audio = audio_bytes
                st.session_state.show_result = True
                st.rerun()

# ==========================================
# フェーズ2：結果表示
# ==========================================
else:
    st.metric("判定スコア", f"{st.session_state.score} / 100")

    if st.session_state.score > 90:
        st.success("完璧です！ネイティブに近い発音・リズムです。")
    elif st.session_state.score > 70:
        st.warning("惜しい！一部の単語が抜け落ちているか、発音が不明瞭です。")
    else:
        st.error("うまく認識されませんでした。もう一度チャレンジしてみましょう。")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.info(f"**【正解の文章】**\n\n{target}")
        if st.button("▶️ 正解の音声を再生"):
            with st.spinner("音声を生成中..."):
                st.audio(make_tts_audio(target), format="audio/mp3")

    with col2:
        st.error(f"**【AIが聞き取ったあなたの発声】**\n\n{st.session_state.user_text}")
        if st.session_state.recorded_audio:
            st.write("▶️ あなたの録音")
            st.audio(st.session_state.recorded_audio, format="audio/wav")

    st.divider()

    if st.button("Next Question ➡"):
        st.session_state.q_index += 1
        st.session_state.show_result = False
        st.session_state.recorded_audio = None
        st.rerun()
