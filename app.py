import html
from urllib.parse import quote

import requests
import streamlit as st

st.set_page_config(page_title="กระดานเสนอนโยบาย", page_icon="📣")

st.markdown("""
<style>
.avatar{width:30px;height:30px;border-radius:50%;background:#eee;flex-shrink:0}
.nick{font-weight:700;font-size:1.05rem;margin:0}
.idea{margin:4px 0 0 0;line-height:1.6}
</style>
""", unsafe_allow_html=True)

URL = st.secrets["SUPABASE_URL"] + "/rest/v1/policies"
KEY = st.secrets["SUPABASE_KEY"]
HEAD = {"apikey": KEY, "Authorization": "Bearer " + KEY, "Content-Type": "application/json"}

def get_rows():
    r = requests.get(URL, headers=HEAD, params={"select": "id,nick,idea", "order": "id.desc"}, timeout=10)
    r.raise_for_status()
    return [(x["id"], x["nick"], x["idea"]) for x in r.json()]

def add_row(n, t):
    requests.post(URL, headers=HEAD, json={"nick": n, "idea": t}, timeout=10).raise_for_status()

def del_row(i):
    requests.delete(URL, headers=HEAD, params={"id": f"eq.{i}"}, timeout=10).raise_for_status()

STYLE = "fun-emoji"  # เปลี่ยนได้ เช่น adventurer, bottts, thumbs, lorelei

def avatar_url(name):
    return f"https://api.dicebear.com/9.x/{STYLE}/svg?seed={quote(name)}"

st.title("📣 เสนอนโยบายมาเยย 🥺🥺")
st.caption("ใส่ชื่อเล่น แล้วเขียนแนวคิดนโยบายมาเยย 👅💦🤘🥺")

with st.form("f", clear_on_submit=True):
    nick = st.text_input("ชื่อเล่น", max_chars=30)
    idea = st.text_area("แนวคิดนโยบาย", max_chars=500, height=110)
    ok = st.form_submit_button("ส่งนโยบาย", use_container_width=True)

if ok:
    if nick.strip() and idea.strip():
        try:
            add_row(nick.strip(), idea.strip())
            st.success("ส่งแล้วงับ ✓")
        except Exception:
            st.error("ส่งไม่สำเร็จง่ะ ลองใหม่อีกครั้งนะ")
    else:
        st.warning("กรอกให้ครบทั้งสองช่องนะเตง")

with st.expander("🔒 สำหรับน้ำแป้งหัวจ่ายเท่านั้น"):
    pw = st.text_input("รหัสผ่าน", type="password")

try:
    admin = pw != "" and pw == st.secrets["ADMIN_PASSWORD"]
except Exception:
    admin = False



st.subheader(f"นโยบายทั้งหมด ({len(rows)})")
if not rows:
    st.info("ยังไม่มีนโยบาย ใครอยากเปิด")

for i, n, t in rows:
    idea_html = html.escape(t).replace("\n", "<br>")
    with st.container(border=True):
        st.markdown(
            f'<div style="display:flex;gap:10px;align-items:flex-start">'
            f'<img class="avatar" src="{html.escape(avatar_url(n))}" alt="">'
            f'<div style="flex:1"><p class="nick">{html.escape(n)}</p>'
            f'<p class="idea">{idea_html}</p></div></div>',
            unsafe_allow_html=True,
        )
        if admin and st.button("🗑️ ลบ", key=f"d{i}"):
            del_row(i)
            st.rerun()
