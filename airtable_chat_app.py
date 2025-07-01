import streamlit as st
st.write(st.secrets)
import streamlit as st
import openai
import requests

# ดึงค่าจาก secrets.toml
AIRTABLE_API_KEY = st.secrets["AIRTABLE_API_KEY"]
AIRTABLE_BASE_ID = st.secrets["AIRTABLE_BASE_ID"]
AIRTABLE_TABLE_NAME = st.secrets["AIRTABLE_TABLE_NAME"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

openai.api_key = OPENAI_API_KEY

# === GPT Setup ===
openai.api_key = st.secrets["OPENAI_API_KEY"]

# === Streamlit UI ===
st.set_page_config(page_title="พนักงาน กปภ. แชทบอท", page_icon="💬")
st.title("RTD1-bot: แชทถามข้อมูลพนักงาน กปภ.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# === Chat Display ===
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# === Chat Input ===
prompt = st.chat_input("สอบถามข้อมูล เช่น 'ใครคือผู้จัดการสาขาพิษณุโลก'")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Step 1: Query Airtable for name or keywords
    def query_airtable(keyword):
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
        headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}
        params = {"filterByFormula": f"FIND('{keyword}', {{ชื่อ - สกุล}})"}
        res = requests.get(url, headers=headers, params=params)
        return res.json().get("records", [])

    records = query_airtable(prompt)
    if records:
        info = records[0]["fields"]
        reply = f"พบข้อมูล: **{info.get('ชื่อ - สกุล', 'ไม่ทราบชื่อ')}**\n\nตำแหน่ง: {info.get('ตำแหน่ง', '-')}, เบอร์โทร: {info.get('เบอร์โทรติดต่อ', '-')}, สังกัด: {info.get('สังกัด', '-')}"
    else:
        # Step 2: ถ้า Airtable ไม่มีผลลัพธ์ → ให้ GPT ช่วยตอบ
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "คุณคือผู้ช่วยค้นหาข้อมูลพนักงานจากองค์กร กปภ."},
                *st.session_state.messages,
            ]
        )
        reply = response.choices[0].message.content

    # === Display reply ===
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
