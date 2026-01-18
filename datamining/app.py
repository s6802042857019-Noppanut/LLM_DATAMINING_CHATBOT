import os
import streamlit as st
import google.generativeai as genai
import dotenv
from prompt import PROMPT_DATA_MINING
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# CSS
st.markdown(
    """
    <style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
        background-attachment: fixed;
        background-size: cover;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.4) !important;
        backdrop-filter: blur(20px); /* เบลอฉากหลัง */
        border-right: 1px solid rgba(255, 255, 255, 0.6);
        box-shadow: 5px 0 15px rgba(0,0,0,0.05);
    }

    /* Chat Input */
    .stChatInput {
        background-color: transparent !important;
    }
    
    /* Button */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #a18cd1 0%, #8ec5fc 100%);
        color: white !important;
        border: none !important;
        border-radius: 30px !important;
        padding: 12px 45px !important;
        font-weight: 600 !important;
        letter-spacing: 1px;
        box-shadow: 0 5px 15px rgba(161, 140, 209, 0.4) !important;
        transition: transform 0.2s, box-shadow 0.2s !important;
    }

    /* Button Hover */
    div.stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(161, 140, 209, 0.6) !important;
        background: linear-gradient(90deg, #b79deb 0%, #9ed1ff 100%) !important; /* สีสว่างขึ้นตอนชี้ */
    }

    /* Sidebar */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #5a4b81 !important; /* ม่วงเทาเข้ม อ่านง่าย */
        font-weight: 500;
    }

    /* Hide Header */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    
    
    /* หากต้องการปรับส่วน Secondary Background อื่นๆ อาจจะต้องระบุ Class เพิ่มเติม */
    </style>
    """,
    unsafe_allow_html=True
)

dotenv.load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# Configuration settings
generation_config = {
    "temperature": 0.1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 2048,
    "response_mime_type": "text/plain",
}

SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
}

#PDF_FILE_PATH = r"Data-Mining-E-Book.pdf"
PDF_FILE_PATH = r"Chapter-4-6-8_Data-Mining.pdf"

# cache_resource to avoid re-uploading
@st.cache_resource
def get_uploaded_file(path):
    if not os.path.exists(path):
        st.error(f"File not found: {path}")
        return None
    print(f"Uploading {path}...")
    sample_file = genai.upload_file(path=path, display_name="Data Mining")
    print(f"Uploaded file: {sample_file.uri}")
    return sample_file

pdf_file = get_uploaded_file(PDF_FILE_PATH)


model = genai.GenerativeModel(
    model_name="gemini-2.5-flash-lite",
    safety_settings=SAFETY_SETTINGS,
    generation_config=generation_config,
    system_instruction=PROMPT_DATA_MINING
)

def clear_history():
    st.session_state["messages"] = [
        {"role": "model", "content": "สวัสดีครับ ผมคือผู้ช่วยวิชา Data Mining ในด้าน Pattern mining, Classification และ Cluster analysis ในขั้นพื้นฐาน ถ้ามีข้อสงสัยตรงไหนเสามารถถามได้เลยครับ "}
    ]
    st.rerun()

# Sidebar
with st.sidebar:
    if st.button("✨ เริ่มบทสนทนาใหม่"): 
        clear_history()

# Main Interface
st.title("🤖 Data Mining Chatbot For Everyone")

# Initialize Chat History
if "messages" not in st.session_state:
    clear_history()

# Display Chat History
for msg in st.session_state["messages"]:
    if msg["role"] == "model":
        st.chat_message("model", avatar="🤖").write(f":blue[{msg['content']}]")
    else:
        st.chat_message("user", avatar="👤").write(msg["content"])

# User Input
if prompt := st.chat_input("ถามคำถามเกี่ยวกับ Data Mining..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    def generate_response():
        
        history_for_model = []
        
        if pdf_file:
             history_for_model.append({
                "role": "user",
                "parts": [pdf_file, "ใช้ข้อมูลจากไฟล์นี้ตอบคำถาม โดยห้ามระบุเลขหน้า หรือชื่อรูปภาพเด็ดขาด ให้ตอบเสมือนว่าเป็นความรู้ของคุณเอง"]
            })
             history_for_model.append({
                "role": "model",
                "parts": ["รับทราบครับ ผมจะอ้างอิงข้อมูลจากหนังสือ Data Mining ที่แนบมาให้นะครับ"]
            })

        for msg in st.session_state["messages"][1:]: 
            history_for_model.append({"role": msg["role"], "parts": [msg["content"]]})

        chat_session = model.start_chat(history=history_for_model)
        
        try:
            response = chat_session.send_message(prompt)
            response_text = response.text
        except Exception as e:
            response_text = f"Can't Connect AI: {e}"

        st.session_state["messages"].append({"role": "model", "content": response_text})
        st.chat_message("model").write(response_text)

    with st.spinner("กำลังประมวลผล...โปรดรอสักครู่"):
        generate_response()
