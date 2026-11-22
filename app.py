import sqlite3
import streamlit as st

conn = sqlite3.connect("policies.db", check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS policies (id INTEGER PRIMARY KEY AUTOINCREMENT, nick TEXT, idea TEXT)")
conn.commit()

st.title("📣 เสนอนโยบายมาเยย🥺🥺")

with st.form("f", clear_on_submit=True):
    nick = st.text_input("ชื่อเล่น", max_chars=30)
    idea = st.text_area("แนวคิดนโยบาย", max_chars=500)
    ok = st.form_submit_button("ส่งนโยบาย")

if ok:
    if nick.strip() and idea.strip():
        conn.execute("INSERT INTO policies (nick, idea) VALUES (?, ?)", (nick.strip(), idea.strip()))
        conn.commit()
        st.success("ส่งแล้วงับ ✓")
    else:
        st.warning("กรอกให้ครบทั้งสองช่องนะ")

with st.expander("🔒 สำหรับน้ำแป้งหัวจ่ายเท่านั้น"):
    pw = st.text_input("รหัสผ่าน", type="password")

try:
    admin = pw != "" and pw == st.secrets["ADMIN_PASSWORD"]
except Exception:
    admin = False

st.subheader("นโยบายทั้งหมด")
rows = conn.execute("SELECT id, nick, idea FROM policies ORDER BY id DESC").fetchall()
if not rows:
    st.write("ยังไม่มีนโยบาย เสนอเป็นคนแรกมาเอา 5 บาท ( ล้อเล่น)🥺🥺")
for i, n, t in rows:
    st.markdown(f"**{n}**")
    st.write(t)
    if admin and st.button("🗑️ ลบ", key=f"d{i}"):
        conn.execute("DELETE FROM policies WHERE id=?", (i,))
        conn.commit()
        st.rerun()
    st.divider()
