import random
import time
import streamlit as st
import streamlit.components.v1 as components
import difflib
from audio_recorder_streamlit import audio_recorder
import io
from gtts import gTTS
import speech_recognition as sr

ALL_QUESTIONS = [
    # ── 簡単 (≤5語) ──────────────────────────────────────────
    "See you later.",
    "That's a great idea.",
    "How are you doing?",
    "I'll be right back.",
    "Nice to meet you.",
    "It's getting late.",
    "I'm so tired today.",
    "You're taller than he is.",
    "What time is it?",
    "I don't know.",
    "That sounds good.",
    "Let me think.",
    "Be careful, please.",
    "I'm on my way.",
    "See you tomorrow.",
    "That's very kind.",
    "Take your time.",
    "Good luck today.",
    "I'm almost ready.",
    "Not bad at all.",
    "That makes sense.",
    "I'll try again.",
    "You did great.",
    "No problem at all.",
    "What's going on?",
    "I'm feeling great.",
    "That's really nice.",
    "I need help.",
    "Have a great day.",
    "What do you think?",
    "Let's get started.",
    "Don't worry about it.",
    "I'm very sorry.",
    "You're so funny.",
    "That's not right.",
    "How about now?",
    "I can do it.",
    "Let's go home.",
    "I miss you.",
    "Call me later.",
    "Here you go.",
    "How was school?",
    "I'll be there.",
    "Are you ready?",
    "I feel sick.",
    "Let me know.",
    "What's your name?",
    "I like it.",
    "Yes, of course.",
    "I'm not sure.",
    "Thank you so much.",
    "I'm home now.",
    "Please sit down.",
    "Excuse me, please.",
    "I'm running late.",
    "I agree with you.",
    "How do you feel?",
    "That's wonderful news.",
    "I'll take it.",
    "Let's eat out.",
    "I love this.",
    "You're absolutely right.",
    "It's my fault.",
    "I changed my mind.",
    "Can you hear me?",
    "I'm doing fine.",
    "That was delicious.",
    "I'll figure it out.",
    "I forgot about it.",
    "Let's try again.",
    "It's not that bad.",
    "I'm proud of you.",
    "I'll get it.",
    "Are you serious?",
    "That's a deal.",
    "I'm just kidding.",
    "You look tired.",
    "I'll check it.",
    "It happened again.",
    "I'm almost done.",
    "You were right.",
    "Good job today.",
    "No, thank you.",
    "I'm on it.",
    "Tell me more.",
    "That's too bad.",
    "I'll explain later.",
    "I made a mistake.",
    "What's the matter?",
    "Keep it up.",
    "It's up to you.",
    "Hang in there.",
    "I'll be fine.",
    "That's all right.",
    "I'm with you.",
    "Good morning, everyone.",
    "Well done, everyone.",
    "Good night, everyone.",
    "Ready or not.",
    "I'll pass today.",
    # ── 普通 (6〜9語) ─────────────────────────────────────────
    "Could you please say that again?",
    "I'm not sure what time it starts.",
    "She said she would call back later.",
    "We've been waiting here for almost an hour.",
    "Do you know where the subway station is?",
    "I'd like to make a reservation, please.",
    "Can you help me find what I need?",
    "I didn't realize how difficult this would be.",
    "Would you mind if I opened the window?",
    "He's been working on that project for months.",
    "He wanted to know if breakfast was included.",
    "I think we should leave before it gets late.",
    "Could you tell me the way to the station?",
    "I'm looking forward to seeing you this weekend.",
    "What would you like to have for dinner?",
    "I've never been to that part of town.",
    "Do you have any plans for the weekend?",
    "I'd rather stay home than go out tonight.",
    "He said he would be there by six.",
    "Can you pass me the salt, please?",
    "I need to finish this before the deadline.",
    "She forgot to bring her umbrella this morning.",
    "Would you like some more coffee or tea?",
    "Have you ever tried Japanese food before?",
    "The weather has been terrible all week long.",
    "I'll give you a call when I arrive.",
    "Could you show me how to use this?",
    "They've been friends since they were in school.",
    "Please let me know if you need anything.",
    "He always stays late to finish his work.",
    "I need to make a phone call quickly.",
    "She told me the store was having a sale.",
    "Would you like to come with us tonight?",
    "I lost my wallet somewhere on the way here.",
    "Can you give me a hand with this?",
    "I'm looking for someone who speaks English well.",
    "Do you think the rain will stop soon?",
    "I was surprised to see you at the party.",
    "Would you mind waiting here for just a moment?",
    "I forgot to turn off the air conditioner.",
    "She asked if I was available on Saturday.",
    "I'm glad we finally had a chance to meet.",
    "He didn't know what to say at first.",
    "Could you speak a bit more slowly, please?",
    "I'm not feeling well, so I'm going home.",
    "Would you be able to come a bit earlier?",
    "She left the office before anyone else did.",
    "Do you happen to know what time it closes?",
    "I'd like to order the same thing as you.",
    "Can you recommend a good place to eat nearby?",
    "I'm sorry I missed your call this morning.",
    "He asked me to pick him up at five.",
    "Would you prefer coffee or tea this morning?",
    "She turned off the lights before leaving the room.",
    "Do you know when the next bus is coming?",
    "I was just about to call you right now.",
    "He said the restaurant was fully booked tonight.",
    "Could you tell me how to get there?",
    "I'm running a bit late, so please wait.",
    "She handed in her report before the deadline.",
    "I didn't sleep well at all last night.",
    "He sent me an email about the meeting.",
    "Can you show me the way to the hotel?",
    "I'm thinking about taking up a new hobby.",
    "She was surprised to hear the good news.",
    "Do you have a few minutes to talk?",
    "He seems to be getting better every day.",
    "I'm looking for a good English conversation class.",
    "Could you lend me your umbrella for today?",
    "She told me the store opens at nine.",
    "Would you like to come with me instead?",
    "I've been really busy with work this week.",
    "He promised to return the book by Friday.",
    "Can you help me with this math problem?",
    "I'm thinking of changing my hairstyle soon.",
    "She reminded me to buy milk on the way.",
    "Do you know what time the movie starts?",
    "I was hoping you could join us today.",
    "He needs to leave by seven at the latest.",
    "Could you please wait outside for a moment?",
    "I haven't talked to him in quite a while.",
    "She was excited to hear about the promotion.",
    "Would it be okay if I used your charger?",
    "I had such a great time at the concert.",
    "He told me to go straight and turn left.",
    "Can you help me figure out this problem?",
    "I'm not sure if I locked the door.",
    "She gave me some good advice about the job.",
    "I don't think I've ever been here before.",
    "He looks like he could use some rest.",
    "Could you bring me another glass of water?",
    "I just realized I left my keys at home.",
    "She's been learning to drive for about six months.",
    "Would you like some help with your luggage?",
    "I think I need to take a short break.",
    "He barely had time to eat his lunch today.",
    "Can I ask you a personal question?",
    "I'll try to finish it by this evening.",
    "She's always known exactly what she wanted to do.",
    "Do you need me to translate that for you?",
    # ── 難しい (10語〜) ────────────────────────────────────────
    "They're trying to fix the problem, but so far they've had no luck.",
    "I'll have to check my schedule and get back to you on that.",
    "It's been a long time since we last saw each other, hasn't it?",
    "Could you please repeat that a little more slowly so I can understand?",
    "I was wondering if you could give me some advice about this situation.",
    "By the time we arrived at the station, the train had already left.",
    "I didn't realize how much work was involved until we actually got started.",
    "She mentioned that she was thinking about looking for a new position abroad.",
    "If you ever need anything, please don't hesitate to let me know.",
    "The meeting was supposed to start at nine, but it got pushed back.",
    "I've been meaning to call you, but things have been really busy lately.",
    "He told me that the project was finally approved after months of delays.",
    "Would it be possible for us to reschedule the appointment to next week?",
    "I'm not sure whether we should take the highway or the back roads.",
    "She said she would send the documents over as soon as she could.",
    "We should probably leave a little earlier to avoid getting stuck in traffic.",
    "I'm afraid I won't be able to attend the conference due to a conflict.",
    "Could you let me know what time works best for you to meet?",
    "He's been studying really hard for his exams and could use some support.",
    "I just heard that the company is planning to expand into new markets.",
    "She apologized for the delay and promised it wouldn't happen again in the future.",
    "I didn't expect so many people to show up for the event last night.",
    "Could you please tell me where I can find the nearest convenience store?",
    "He explained that the reason for the cancellation was due to bad weather.",
    "I've been looking forward to this trip for the past several months now.",
    "Would you be interested in joining us for dinner after the presentation tonight?",
    "We've been trying to solve this issue for quite some time without any success.",
    "He mentioned that he was planning to take a few days off next week.",
    "I just wanted to let you know that the package has finally been delivered.",
    "She did an incredible job presenting the proposal to the board of directors.",
    "If everything goes according to plan, we should be finished by Friday afternoon.",
    "I'm a bit concerned about the weather forecast for the upcoming weekend trip.",
    "He said he would try his best to finish the report before the meeting.",
    "Could you do me a favor and double-check these figures before the presentation?",
    "I've never seen so many people at the station at this time of day.",
    "She's been working really hard to meet the deadline, and it's starting to show.",
    "Would you mind if I asked you a few questions about your experience here?",
    "I was hoping we could find some time to go over the details together.",
    "He didn't realize how important it was to submit the form before the deadline.",
    "I think the best approach would be to tackle the most urgent issues first.",
    "She told her team that they needed to be more careful with the data.",
    "We're planning to have a small get-together at our place this coming Saturday.",
    "He's been commuting for over two hours every day for the past several years.",
    "Would it be alright if we moved the meeting to a different time slot?",
    "I wasn't expecting the feedback to be so positive, but I'm really glad it was.",
    "She made sure that all the necessary arrangements were made well in advance.",
    "I'm trying to decide whether to take the train or drive to the airport.",
    "He's looking forward to presenting his ideas to the team at the next meeting.",
    "Could you please confirm whether the event is still scheduled for next Thursday?",
    "I had a really good time at the conference, and I learned a lot.",
    "She's been feeling a bit under the weather, so she decided to stay home.",
    "We should probably set aside some time to go over the budget together soon.",
    "He asked me to review the contract before sending it to the other party.",
    "I was relieved to hear that everyone made it home safely after the storm.",
    "Would you be willing to stay a bit late tonight to help finish the project?",
    "She's been doing a lot of research on the topic and is quite knowledgeable.",
    "I think we should reconsider our approach before we proceed any further with this.",
    "He reminded everyone that the deadline was approaching and that we needed to hurry.",
    "She said the new system would take some getting used to, but it's worth it.",
    "I'm not sure I fully understand the situation, so could you please explain it again?",
    "Could you please make sure that all the doors are locked before you leave tonight?",
    "I was surprised to find out that the store had already closed for the day.",
    "She decided to take a completely different route home because of the construction nearby.",
    "We're going to need everyone's cooperation if we want this project to succeed.",
    "I just wanted to check in and see how things are going on your end.",
    "He apologized for not responding sooner and promised to follow up right away.",
    "Would you mind reviewing this document and letting me know your thoughts on it?",
    "I'm planning to take some time off after finishing this big project next month.",
    "He said the interview went really well and that he felt good about his chances.",
    "She took great care to explain every detail so that no one would be confused.",
    "We ended up spending the entire afternoon trying to figure out what had gone wrong.",
    "He made it very clear that he wasn't happy with the way things were handled.",
    "Could you send me the agenda for the meeting so I can prepare in advance?",
    "I'm looking forward to the opportunity to work with such a talented group of people.",
    "She mentioned that she would be out of the office for the rest of the week.",
    "We appreciate your patience and apologize for any inconvenience this may have caused.",
    "I realize this is short notice, but I was wondering if you were available tomorrow.",
    "He worked through the night to make sure everything was ready for the morning meeting.",
    "I've been trying to get in touch with you, but I keep missing your calls.",
    "She managed to finish the presentation on time despite all the last-minute changes.",
    "Would it be possible to get an extension on the deadline for this particular assignment?",
    "I've been so busy lately that I haven't had much time for anything else at all.",
    "He was really impressed by the amount of effort everyone put into the project.",
    "She pointed out that there was an error in the report that needed to be corrected.",
    "We should schedule a follow-up meeting to discuss the results of the initial review.",
    "I appreciate everything you've done for me, and I'll never forget your kindness.",
    "He reminded us that we should always double-check our work before submitting it.",
    "I'm having second thoughts about the decision we made at yesterday's meeting.",
    "I hadn't realized until now just how much progress we've actually made together.",
    "She asked if we could reschedule the call because something urgent had come up.",
    "He said the new policy would take effect starting from the beginning of next month.",
    "I think we all need to take a step back and look at the bigger picture here.",
    "Could you please forward that email to me so I can take a look at it?",
    "She was glad to hear that the client was satisfied with the final result.",
    "We'll need to finalize the budget proposal before the end of the fiscal quarter.",
    "I don't think we've considered all the possible risks associated with this approach.",
    "He asked everyone to keep the details of the project strictly confidential for now.",
    "I'm not entirely comfortable with the direction things are heading at the moment.",
    "She was relieved to find out that the problem had already been taken care of.",
    "We should make sure that all team members are on the same page going forward.",
    "I just found out that the deadline has been moved up to next Monday morning.",
]

DIFFICULTY_CONFIG = {
    "簡単 (〜5語)": (0, 5),
    "普通 (6〜9語)": (6, 9),
    "難しい (10語〜)": (10, 999),
}

QUESTIONS_PER_CYCLE = 16


def word_count(s: str) -> int:
    return len(s.split())


def make_tts_audio(text: str) -> bytes:
    tts = gTTS(text=text, lang="en")
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp.read()


def audio_duration_estimate(text: str) -> float:
    """単語数から再生時間を推定（秒）"""
    return len(text.split()) * 0.42 + 0.8


def reset_for_new_cycle(filtered: list):
    st.session_state.questions = random.sample(filtered, min(QUESTIONS_PER_CYCLE, len(filtered)))
    st.session_state.q_index = 0
    st.session_state.phase = "playing"
    st.session_state.recorder_started = False
    st.session_state.recorded_audio = None
    st.session_state.tts_audio = None
    st.session_state.tts_for_q = -1
    st.session_state.user_text = ""
    st.session_state.score = 0


# ── サイドバー ────────────────────────────────────────────────
with st.sidebar:
    st.title("設定")
    difficulty = st.selectbox("難易度", list(DIFFICULTY_CONFIG.keys()), key="difficulty_select")

min_w, max_w = DIFFICULTY_CONFIG[difficulty]
filtered = [q for q in ALL_QUESTIONS if min_w <= word_count(q) <= max_w]

# ── 初期化 / 難易度変更 ─────────────────────────────────────────
if "active_difficulty" not in st.session_state or st.session_state.active_difficulty != difficulty:
    reset_for_new_cycle(filtered)
    st.session_state.active_difficulty = difficulty

for key, default in [
    ("q_index", 0),
    ("phase", "playing"),
    ("recorder_started", False),
    ("recorded_audio", None),
    ("tts_audio", None),
    ("tts_for_q", -1),
    ("user_text", ""),
    ("score", 0),
    ("do_stop_recording", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

questions = st.session_state.questions

# ── タイトル ───────────────────────────────────────────────────
st.title("Repeat the Sentence")

# ── 全問終了 ───────────────────────────────────────────────────
if st.session_state.q_index >= len(questions):
    st.success("🎉 16問終了しました！")
    if st.button("もう一度（シャッフル）", type="primary"):
        reset_for_new_cycle(filtered)
        st.rerun()
    st.stop()

target = questions[st.session_state.q_index]
st.subheader(f"Question {st.session_state.q_index + 1} / {len(questions)}")

# ══════════════════════════════════════════════════════════════
# Phase: playing  ── 音声自動再生 → 待機 → 録音フェーズへ
# ══════════════════════════════════════════════════════════════
if st.session_state.phase == "playing":
    # TTS 生成（問題が変わったときだけ）
    if st.session_state.tts_for_q != st.session_state.q_index:
        with st.spinner("音声を生成中..."):
            audio = make_tts_audio(target)
        st.session_state.tts_audio = audio
        st.session_state.tts_for_q = st.session_state.q_index

    est = audio_duration_estimate(target)
    wait = est + 2.0  # 音声終了後 2 秒待ってから録音開始

    st.info("🎧 音声を聞いてください。テキストは隠されています。")
    st.audio(st.session_state.tts_audio, format="audio/mp3", autoplay=True)
    st.caption(f"⏱️ 約 {int(wait)} 秒後に録音が自動的に開始されます...")

    time.sleep(wait)  # ブラウザで音声が再生される間 Python が待機

    st.session_state.phase = "recording"
    st.session_state.recorder_started = False
    st.rerun()

# ══════════════════════════════════════════════════════════════
# Phase: recording  ── 自動録音開始・完了ボタン
# ══════════════════════════════════════════════════════════════
elif st.session_state.phase == "recording":
    st.error("🔴 **録音中です。文章を復唱してください。**")

    col_btn, col_hint = st.columns([1, 3])
    with col_btn:
        if st.button("✅ 録音完了", type="primary"):
            st.session_state.do_stop_recording = True
            st.rerun()
    with col_hint:
        st.caption("マイクボタンを押して止めることもできます。")

    # 完了ボタン押下時: JS でマイクボタンをクリック
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

    # 初回マウント時のみ auto_start=True
    auto_start = not st.session_state.recorder_started
    audio_bytes = audio_recorder(
        text="",
        auto_start=auto_start,
        pause_threshold=4.0,   # 4 秒の沈黙で自動停止
        sample_rate=44_100,
        key="main_recorder",
    )
    st.session_state.recorder_started = True  # 次回以降 auto_start しない

    if audio_bytes:
        with st.spinner("音声を解析中..."):
            recognizer = sr.Recognizer()
            try:
                with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
                    audio_data = recognizer.record(source)
                user_transcription = recognizer.recognize_google(audio_data)
            except sr.UnknownValueError:
                user_transcription = ""
            except sr.RequestError as e:
                st.error(f"音声認識エラー: {e}")
                st.stop()

        similarity = difflib.SequenceMatcher(
            None, target.lower(), user_transcription.lower()
        ).ratio()

        st.session_state.score = int(similarity * 100)
        st.session_state.user_text = user_transcription
        st.session_state.recorded_audio = audio_bytes
        st.session_state.phase = "result"
        st.rerun()

# ══════════════════════════════════════════════════════════════
# Phase: result  ── スコア表示
# ══════════════════════════════════════════════════════════════
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
        if st.button("▶️ 正解の音声を再生"):
            with st.spinner("生成中..."):
                audio = make_tts_audio(target)
            st.audio(audio, format="audio/mp3", autoplay=True)

    with col2:
        st.error(f"**【AIが聞き取った発声】**\n\n{st.session_state.user_text}")
        if st.session_state.recorded_audio:
            st.write("▶️ あなたの録音")
            st.audio(st.session_state.recorded_audio, format="audio/wav")

    st.divider()
    if st.button("Next Question ➡", type="primary"):
        st.session_state.q_index += 1
        st.session_state.phase = "playing"
        st.session_state.recorder_started = False
        st.session_state.recorded_audio = None
        st.session_state.tts_audio = None
        st.session_state.tts_for_q = -1
        st.rerun()
