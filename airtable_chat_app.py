import streamlit as st
import openai
import requests

AIRTABLE_API_KEY = st.secrets["AIRTABLE_API_KEY"]
AIRTABLE_BASE_ID = st.secrets["AIRTABLE_BASE_ID"]
AIRTABLE_TABLE_NAME = st.secrets["AIRTABLE_TABLE_NAME"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

openai.api_key = OPENAI_API_KEY

st.set_page_config(page_title="พนักงาน กปภ. แชทบอท", page_icon="💬")
st.title("RTD1-bot: แชทถามข้อมูลพนักงาน กปภ.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("สอบถามข้อมูล เช่น 'สายงานผลิต', 'สาขาแม่สอด', 'คุณวุฒิวิศวกรรมศาสตร์' ...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    def query_airtable(keyword):
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
        headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}
        fields_to_search = [
            'ชื่อ-นามสกุล',
            'รหัส',
            'ตำแหน่ง',
            'สังกัด',
            'สาขา',
            'ผช.เขต',
            'เขต',
            'สายงาน',
            'ลำดับ',
            'ชั้น',
            'ตำแหน่งรักษาการ',
            'วดป.ดำรงตำแหน่ง',
            'วดป.บรรจุ',
            'วดป.เกิด',
            'ปีเกษียณ',
            'คุณวุฒิสุงสุด',
            'สาขาสูงสุด',
            'NO.ID Card',
            'คุณวุฒิแรกบรรจุ',
            'สาขาแรกบรรจุ',
        ]
        filter_formula = "OR(" + ",".join([f"FIND('{keyword}', {{{f}}})" for f in fields_to_search]) + ")"
        params = {"filterByFormula": filter_formula}
        res = requests.get(url, headers=headers, params=params)
        return res.json().get("records", [])

    records = query_airtable(prompt)
    if records:
        info = records[0]["fields"]
        reply = f"""พบข้อมูลพนักงาน

**ลำดับ:** {info.get('ลำดับ', '-')}
**รหัส:** {info.get('รหัส', '-')}
**ชื่อ-นามสกุล:** {info.get('ชื่อ-นามสกุล', '-')}
**ตำแหน่ง:** {info.get('ตำแหน่ง', '-')}
**ชั้น:** {info.get('ชั้น', '-')}
**ตำแหน่งรักษาการ:** {info.get('ตำแหน่งรักษาการ', '-')}
**สังกัด:** {info.get('สังกัด', '-')}
**สาขา:** {info.get('สาขา', '-')}
**ผช.เขต:** {info.get('ผช.เขต', '-')}
**เขต:** {info.get('เขต', '-')}
**สายงาน:** {info.get('สายงาน', '-')}
**วดป.ดำรงตำแหน่ง:** {info.get('วดป.ดำรงตำแหน่ง', '-')}
**วดป.บรรจุ:** {info.get('วดป.บรรจุ', '-')}
**วดป.เกิด:** {info.get('วดป.เกิด', '-')}
**ปีเกษียณ:** {info.get('ปีเกษียณ', '-')}
**คุณวุฒิสุงสุด:** {info.get('คุณวุฒิสุงสุด', '-')}
**สาขาสูงสุด:** {info.get('สาขาสูงสุด', '-')}
**NO.ID Card:** {info.get('NO.ID Card', '-')}
**คุณวุฒิแรกบรรจุ:** {info.get('คุณวุฒิแรกบรรจุ', '-')}
**สาขาแรกบรรจุ:** {info.get('สาขาแรกบรรจุ', '-')}
"""
    else:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "คุณคือผู้ช่วยค้นหาข้อมูลพนักงานจากองค์กร กปภ."},
                *st.session_state.messages,
            ]
        )
        reply = response.choices[0].message.content

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
