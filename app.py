import random
import time
import streamlit as st
import streamlit.components.v1 as components
import difflib
from audio_recorder_streamlit import audio_recorder
import io
from gtts import gTTS
import speech_recognition as sr

from questions import ALL_QUESTIONS


DIFFICULTY_CONFIG = {
    "簡単 (〜5語)": (0, 5),
    "普通 (6〜9語)": (6, 9),
    "難しい (10語〜)": (10, 999),
}
QUESTIONS_PER_CYCLE = 16
PROGRESSIVE_MODE = "だんだん難しくなる"


def word_count(s: str) -> int:
    return len(s.split())


def questions_by_difficulty(difficulty: str) -> list[str]:
    min_w, max_w = DIFFICULTY_CONFIG[difficulty]
    return [q for q in ALL_QUESTIONS if min_w <= word_count(q) <= max_w]


def build_fixed_questions(difficulty: str) -> list[str]:
    filtered = questions_by_difficulty(difficulty)
    return random.sample(filtered, min(QUESTIONS_PER_CYCLE, len(filtered)))


def build_progressive_questions() -> list[str]:
    quotas = [5, 5, QUESTIONS_PER_CYCLE - 10]
    selected = []

    for difficulty, quota in zip(DIFFICULTY_CONFIG.keys(), quotas):
        candidates = questions_by_difficulty(difficulty)
        selected.extend(random.sample(candidates, min(quota, len(candidates))))

    if len(selected) < QUESTIONS_PER_CYCLE:
        remaining = [q for q in ALL_QUESTIONS if q not in selected]
        selected.extend(random.sample(remaining, min(QUESTIONS_PER_CYCLE - len(selected), len(remaining))))

    return sorted(selected, key=word_count)


def build_questions(mode: str) -> list[str]:
    if mode == PROGRESSIVE_MODE:
        return build_progressive_questions()
    return build_fixed_questions(mode)


def make_tts_audio(text: str) -> bytes | None:
    for _ in range(2):
        try:
            tts = gTTS(text=text, lang="en")
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            return fp.read()
        except Exception:
            pass
    return None


def audio_duration_estimate(text: str) -> float:
    return len(text.split()) * 0.42 + 0.8


def reset_cycle(mode: str):
    st.session_state.update(
        page="test",
        selected_mode=mode,
        questions=build_questions(mode),
        q_index=0,
        phase="playing",
        recorder_started=False,
        recorded_audio=None,
        tts_audio=None,
        tts_for_q=-1,
        result_audio_for_q=-1,
        user_text="",
        score=0,
        do_stop_recording=False,
        playback_start=None,
        playback_wait=0.0,
        results=[],
    )


def retry_current_question():
    st.session_state.phase = "playing"
    st.session_state.recorder_started = False
    st.session_state.recorded_audio = None
    st.session_state.tts_audio = None
    st.session_state.tts_for_q = -1
    st.session_state.result_audio_for_q = -1
    st.session_state.user_text = ""
    st.session_state.score = 0
    st.session_state.do_stop_recording = False
    st.session_state.playback_start = None
    st.session_state.playback_wait = 0.0

    if len(st.session_state.results) > st.session_state.q_index:
        st.session_state.results = st.session_state.results[:st.session_state.q_index]


# ── フラグメント：time.sleep なしのカウントダウン ─────────────
@st.fragment(run_every=0.5)
def playback_countdown():
    if st.session_state.get("phase") != "playing":
        return
    if not st.session_state.get("playback_start"):
        return
    elapsed = time.time() - st.session_state.playback_start
    remaining = st.session_state.playback_wait - elapsed
    if remaining <= 0:
        st.session_state.phase = "recording"
        st.session_state.recorder_started = False
        st.session_state.playback_start = None
        st.rerun(scope="app")
    else:
        st.caption(f"⏱️ 録音開始まで {max(1, int(remaining))} 秒...")


# ── トップページ ───────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":
    st.title("Repeat the Sentence")
    st.caption("音声を聞いて、聞こえた英文をそのまま復唱する練習です。")

    mode_options = list(DIFFICULTY_CONFIG.keys()) + [PROGRESSIVE_MODE]
    mode = st.radio("テストの種類", mode_options, index=0)

    if mode == PROGRESSIVE_MODE:
        st.info("序盤は短い文章から始まり、後半にかけて長い文章が出ます。")
    else:
        min_w, max_w = DIFFICULTY_CONFIG[mode]
        label = f"{min_w}〜{max_w}語" if max_w < 999 else f"{min_w}語以上"
        st.info(f"{mode} の文章だけで練習します。（{label}）")

    if st.button("スタート", type="primary"):
        reset_cycle(mode)
        st.rerun()

    st.stop()


# ── サイドバー ─────────────────────────────────────────────────
with st.sidebar:
    st.title("設定")
    st.write(f"**現在のテスト:** {st.session_state.get('selected_mode', '-')}")
    if st.button("トップに戻る"):
        st.session_state.page = "home"
        st.rerun()

# デフォルト値の保証
defaults = dict(
    selected_mode=list(DIFFICULTY_CONFIG.keys())[0],
    questions=[],
    q_index=0, phase="playing", recorder_started=False,
    recorded_audio=None, tts_audio=None, tts_for_q=-1, result_audio_for_q=-1,
    user_text="", score=0, do_stop_recording=False,
    playback_start=None, playback_wait=0.0,
    results=[],
)
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if not st.session_state.questions:
    reset_cycle(st.session_state.selected_mode)

questions = st.session_state.questions

# ── メイン ────────────────────────────────────────────────────
st.title("Repeat the Sentence")

if st.session_state.q_index >= len(questions):
    results = st.session_state.results
    avg = sum(r["score"] for r in results) / len(results) if results else 0

    st.title("🎉 お疲れ様でした！")

    # 平均スコア
    col_avg, col_hi, col_lo = st.columns(3)
    with col_avg:
        st.metric("平均スコア", f"{avg:.1f} / 100")
    with col_hi:
        best = max(results, key=lambda r: r["score"]) if results else None
        st.metric("最高スコア", f"{best['score']} / 100" if best else "-")
    with col_lo:
        worst = min(results, key=lambda r: r["score"]) if results else None
        st.metric("最低スコア", f"{worst['score']} / 100" if worst else "-")

    st.divider()

    # 全問結果一覧
    st.subheader("全問結果")
    for i, r in enumerate(results, 1):
        score = r["score"]
        if score > 90:
            color = "🟢"
        elif score > 70:
            color = "🟡"
        else:
            color = "🔴"

        with st.expander(f"{color} Q{i}. {r['question']}　→　**{score} 点**"):
            st.write(f"**正解:** {r['question']}")
            st.write(f"**あなたの発声:** {r['user_text'] if r['user_text'] else '（認識できませんでした）'}")
            st.progress(score / 100)

    st.divider()
    if st.button("もう一度（シャッフル）", type="primary"):
        reset_cycle(st.session_state.selected_mode)
        st.rerun()
    st.stop()

target = questions[st.session_state.q_index]
st.subheader(f"Question {st.session_state.q_index + 1} / {len(questions)}")

# ══════════════════════════════════════════════════════
# Phase: playing
# ══════════════════════════════════════════════════════
if st.session_state.phase == "playing":

    # TTS 生成（問題が変わったときだけ）
    if st.session_state.tts_for_q != st.session_state.q_index:
        with st.spinner("音声を生成中..."):
            audio = make_tts_audio(target)
        if audio is None:
            st.error("音声の生成に失敗しました。")
            col_r, col_s = st.columns(2)
            with col_r:
                if st.button("🔄 リトライ"):
                    st.rerun()
            with col_s:
                if st.button("⏭️ この問題をスキップ"):
                    st.session_state.q_index += 1
                    st.session_state.tts_for_q = -1
                    st.rerun()
            st.stop()

        st.session_state.tts_audio = audio
        st.session_state.tts_for_q = st.session_state.q_index
        st.session_state.playback_start = time.time()
        st.session_state.playback_wait = audio_duration_estimate(target) + 2.0

    st.info("🎧 音声を聞いてください。テキストは隠されています。")
    st.audio(st.session_state.tts_audio, format="audio/mp3", autoplay=True)
    playback_countdown()  # 0.5秒ごとに独立して再実行されるフラグメント

# ══════════════════════════════════════════════════════
# Phase: recording
# ══════════════════════════════════════════════════════
elif st.session_state.phase == "recording":
    st.error("🔴 **録音中です。文章を復唱してください。**")

    col_stop, col_replay, col_retry = st.columns([1, 1, 1])
    with col_stop:
        if st.button("✅ 録音完了", type="primary"):
            st.session_state.do_stop_recording = True
            st.rerun()
    with col_replay:
        if st.button("🔊 もう一度聞く"):
            if st.session_state.tts_audio:
                st.audio(st.session_state.tts_audio, format="audio/mp3", autoplay=True)
    with col_retry:
        if st.button("問題に戻る"):
            retry_current_question()
            st.rerun()

    # 完了ボタン押下時に JS でマイクボタンをクリック
    if st.session_state.do_stop_recording:
        st.session_state.do_stop_recording = False
        components.html("""
        <script>
        setTimeout(function() {
            var frames = window.parent.document.querySelectorAll('iframe');
            for (var i = 0; i < frames.length; i++) {
                try {
                    var btn = frames[i].contentDocument.querySelector('button[aria-label="Record"]');
                    if (btn) { btn.click(); break; }
                } catch(e) {}
            }
        }, 300);
        </script>
        """, height=0)

    # 初回マウント時のみ auto_start=True（rerun で再起動しない）
    auto_start = not st.session_state.recorder_started
    audio_bytes = audio_recorder(
        text="",
        auto_start=auto_start,
        pause_threshold=4.0,
        sample_rate=44_100,
        key="main_recorder",
    )
    st.session_state.recorder_started = True

    if audio_bytes:
        with st.spinner("音声を解析中..."):
            recognizer = sr.Recognizer()
            try:
                with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
                    audio_data = recognizer.record(source)
                user_transcription = recognizer.recognize_google(audio_data)
            except sr.UnknownValueError:
                user_transcription = ""
            except sr.RequestError:
                user_transcription = ""

        similarity = difflib.SequenceMatcher(
            None, target.lower(), user_transcription.lower()
        ).ratio()

        score = int(similarity * 100)
        st.session_state.score = score
        st.session_state.user_text = user_transcription
        st.session_state.recorded_audio = audio_bytes

        # 重複防止: この問題の結果がまだ未登録なら追加
        if len(st.session_state.results) == st.session_state.q_index:
            st.session_state.results.append({
                "question": target,
                "user_text": user_transcription,
                "score": score,
            })

        st.session_state.phase = "result"
        st.rerun()

# ══════════════════════════════════════════════════════
# Phase: result
# ══════════════════════════════════════════════════════
elif st.session_state.phase == "result":
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
        if st.session_state.result_audio_for_q != st.session_state.q_index:
            audio = st.session_state.tts_audio
            if audio is None:
                with st.spinner("正解の音声を生成中..."):
                    audio = make_tts_audio(target)
            if audio:
                st.audio(audio, format="audio/mp3", autoplay=True)
            st.session_state.result_audio_for_q = st.session_state.q_index

    with col2:
        st.error(f"**【AIが聞き取った発声】**\n\n{st.session_state.user_text}")
        if st.session_state.recorded_audio:
            st.write("▶️ あなたの録音")
            st.audio(st.session_state.recorded_audio, format="audio/wav")

    st.divider()
    col_retry_result, col_next = st.columns(2)
    with col_retry_result:
        if st.button("この問題をやり直す"):
            retry_current_question()
            st.rerun()
    with col_next:
        next_label = "Next Question ➡"
        if st.button(next_label, type="primary"):
            st.session_state.q_index += 1
            st.session_state.phase = "playing"
            st.session_state.recorder_started = False
            st.session_state.recorded_audio = None
            st.session_state.tts_audio = None
            st.session_state.tts_for_q = -1
            st.session_state.result_audio_for_q = -1
            st.rerun()
