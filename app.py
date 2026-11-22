import sqlite3
import html
import streamlit as st

st.set_page_config(page_title="กระดานเสนอนโยบาย", page_icon="📣")

st.markdown("""
<style>
.avatar{width:42px;height:42px;border-radius:50%;color:#fff;font-weight:700;
display:flex;align-items:center;justify-content:center;font-size:1.2rem}
.nick{font-weight:700;font-size:1.05rem;margin:0}
.idea{margin:6px 0 0 0;white-space:pre-wrap;line-height:1.6}
</style>
""", unsafe_allow_html=True)

conn = sqlite3.connect("policies.db", check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS policies (id INTEGER PRIMARY KEY AUTOINCREMENT, nick TEXT, idea TEXT)")
conn.commit()

COLORS = ["#e76f51", "#2a9d8f", "#3b6fd4", "#9b5de5", "#f4a261", "#d6336c", "#2b9348"]

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
    st.info("ยังไม่มีนโยบาย เสนอคนแรกมาเอา 5 บาท ( ล้อเล่น ) 🥺")

for i, n, t in rows:
    color = COLORS[sum(map(ord, n)) % len(COLORS)]
    with st.container(border=True):
        st.markdown(
            f"""<div style="display:flex;gap:12px;align-items:flex-start">
            <div class="avatar" style="background:{color}">{html.escape(n[:1].upper())}</div>
            <div style="flex:1"><p class="nick">{html.escape(n)}</p>
            <p class="idea">{html.escape(t)}</p></div></div>""",
            unsafe_allow_html=True,
        )
        if admin and st.button("🗑️ ลบ", key=f"d{i}"):
            conn.execute("DELETE FROM policies WHERE id=?", (i,))
            conn.commit()
            st.rerun()
