import sqlite3
import html
from urllib.parse import quote
import streamlit as st

st.set_page_config(page_title="กระดานเสนอนโยบาย", page_icon="📣")

st.markdown("""
<style>
.avatar{width:48px;height:48px;border-radius:50%;background:#eee;flex-shrink:0}
.nick{font-weight:700;font-size:1.05rem;margin:0}
.idea{margin:6px 0 0 0;white-space:pre-wrap;line-height:1.6}
</style>
""", unsafe_allow_html=True)

conn = sqlite3.connect("policies.db", check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS policies (id INTEGER PRIMARY KEY AUTOINCREMENT, nick TEXT, idea TEXT)")
conn.commit()

STYLE = "fun-emoji"  # เปลี่ยนได้ เช่น adventurer, bottts, thumbs, lorelei

def avatar_url(name):
    return f"https://api.dicebear.com/9.x/{STYLE}/svg?seed={quote(name)}"

st.title("📣 เสนอนโยบายมาเยย 🥺🥺")
st.caption("ใส่ชื่อเล่น แล้วเขียนแนวคิดนโยบายได้เยย 👅💦🥺🤘")

with st.form("f", clear_on_submit=True):
    nick = st.text_input("ชื่อเล่น", max_chars=30)
    idea = st.text_area("แนวคิดนโยบาย", max_chars=500, height=110)
    ok = st.form_submit_button("ส่งนโยบาย", use_container_width=True)

if ok:
    if nick.strip() and idea.strip():
        conn.execute("INSERT INTO policies (nick, idea) VALUES (?, ?)", (nick.strip(), idea.strip()))
        conn.commit()
        st.success("ส่งแล้วงับ ✓")
    else:
        st.warning("กรอกให้ครบทั้งสองช่องนะเตง")

with st.expander("🔒 สำหรับน้ำแป้งหัวจ่ายเท่านั้น"):
    pw = st.text_input("รหัสผ่าน", type="password")

try:
    admin = pw != "" and pw == st.secrets["ADMIN_PASSWORD"]
except Exception:
    admin = False

rows = conn.execute("SELECT id, nick, idea FROM policies ORDER BY id DESC").fetchall()

st.subheader(f"นโยบายทั้งหมด ({len(rows)})")
if not rows:
    st.info("ยังไม่มีนโยบาย เสนอคนแรกมาเอา 5 บาท (ล้อเล่น) 🥺")

for i, n, t in rows:


    with st.container(border=True):
        st.markdown(
            f"""<div style="display:flex;gap:12px;align-items:flex-start">
            <img class="avatar" src="{html.escape(avatar_url(n))}" alt="">

            <div style="flex:1"><p class="nick">{html.escape(n)}</p>
            <p class="idea">{html.escape(t)}</p></div></div>""",
            unsafe_allow_html=True,
        )
        if admin and st.button("🗑️ ลบ", key=f"d{i}"):
            conn.execute("DELETE FROM policies WHERE id=?", (i,))
            conn.commit()
            st.rerun()
