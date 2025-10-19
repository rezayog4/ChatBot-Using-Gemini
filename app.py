import streamlit as st
import os
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="Chatbot Kesehatan - Gemini",
    page_icon="💬",
    layout="centered"
)

# --- Header dan Deskripsi ---
st.markdown(
    """
    <h2 style='text-align: center; color: #2E86C1;'>💬 Chatbot Kesehatan Gemini</h2>
    <p style='text-align: center; color: gray;'>
    Asisten virtual yang siap membantu menjawab pertanyaan seputar <b>kesehatan umum</b>.<br>
    ⚠️ <i>Catatan: Jawaban bersifat informatif dan tidak menggantikan konsultasi langsung dengan dokter.</i>
    </p>
    <hr>
    """,
    unsafe_allow_html=True
)

# --- Seksi: Panduan Mendapatkan API Key ---
with st.expander("🔑 Panduan: Cara Mendapatkan Google API Key (Gemini)"):
    st.markdown(
        """
        Untuk menggunakan chatbot ini, Anda memerlukan **Google API Key** dari [Google AI Studio](https://aistudio.google.com/app/apikey).

        **Langkah-langkah mendapatkan API Key:**
        1. Buka situs [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
        2. Login menggunakan akun Google Anda.
        3. Klik tombol **"Create API key"**.
        4. Setelah key muncul, **salin** API key tersebut.
        5. Tempelkan API key Anda pada kolom di bawah ini.

        🔒 *API Key bersifat pribadi, disimpan hanya di sesi ini dan tidak akan dikirim ke pihak lain.*
        """,
        unsafe_allow_html=True
    )

# --- Input API Key ---
api_key = st.text_input("Google API Key", type="password", help="Diperlukan untuk mengakses model Gemini.")
if not api_key:
    st.info("Silakan masukkan API key Anda terlebih dahulu untuk memulai percakapan.")
    st.stop()

# --- Setup Model ---
os.environ["GOOGLE_API_KEY"] = api_key
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# --- Inisialisasi Riwayat Chat ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        SystemMessage(content=(
            "Kamu adalah asisten kesehatan yang ramah dan informatif. "
            "Fokus hanya pada topik kesehatan, gizi, olahraga, kesehatan mental, penyakit umum, dan gaya hidup sehat. "
            "Jika pengguna menanyakan hal di luar konteks kesehatan, jawab dengan sopan bahwa kamu hanya dapat menjawab seputar kesehatan. "
            "Berikan jawaban berdasarkan pengetahuan medis umum, dan selalu ingatkan pengguna untuk konsultasi ke tenaga medis profesional."
        ))
    ]

# --- Area Chat ---
st.subheader("💬 Ruang Konsultasi Kesehatan")
chat_container = st.container()

# Menampilkan percakapan sebelumnya
for msg in st.session_state.chat_history[1:]:
    if isinstance(msg, HumanMessage):
        with chat_container.chat_message("user", avatar="👤"):
            st.markdown(f"**Anda:** {msg.content}")
    elif isinstance(msg, AIMessage) or isinstance(msg, SystemMessage):
        with chat_container.chat_message("assistant", avatar="🩺"):
            st.markdown(msg.content)

# --- Input Pengguna ---
prompt = st.chat_input("Tanyakan sesuatu seputar kesehatan Anda...")

if prompt:
    # Tambahkan pesan pengguna
    st.session_state.chat_history.append(HumanMessage(content=prompt))
    
    # Tampilkan pesan pengguna
    with chat_container.chat_message("user", avatar="👤"):
        st.markdown(f"**Anda:** {prompt}")

    # --- Panggilan Model ---
    with chat_container.chat_message("assistant", avatar="🩺"):
        with st.spinner("🧠 Asisten sedang memproses jawaban..."):
            # Pemeriksaan konteks topik
            context_check = (
                "Tentukan apakah pertanyaan berikut masih dalam konteks kesehatan: "
                f"'{prompt}'. Jika tidak, jawab hanya dengan kata 'NON-KESEHATAN'."
            )
            check_response = llm.invoke([HumanMessage(content=context_check)])

            if "NON-KESEHATAN" in check_response.content.upper():
                response_text = (
                    "⚠️ Maaf, saya hanya dapat membantu menjawab pertanyaan seputar **kesehatan, gizi, olahraga, "
                    "atau gaya hidup sehat**. Silakan ajukan pertanyaan lain dalam topik tersebut ya. 😊"
                )
            else:
                # Jika dalam konteks kesehatan, lanjutkan dengan jawaban utama
                response = llm.invoke(st.session_state.chat_history)
                response_text = response.content

            st.markdown(response_text)

    # Simpan balasan ke riwayat
    st.session_state.chat_history.append(AIMessage(content=response_text))

# --- Footer ---
st.markdown(
    """
    <hr>
    <p style='text-align: center; color: gray; font-size: 0.9em;'>
    Developed by rejaayp using <b>Streamlit</b> and <b>Gemini API</b>.<br>
    — Health Chatbot — .
    </p>
    """,
    unsafe_allow_html=True
)
