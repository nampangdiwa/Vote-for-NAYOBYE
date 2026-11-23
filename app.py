import html
import re
import secrets as pysecrets
from urllib.parse import quote

import requests
import streamlit as st

st.set_page_config(page_title="กระดานนโยบาย", page_icon="📣")

st.markdown("""
<style>
.avatar{width:32px;height:32px;border-radius:50%;background:#eee;flex-shrink:0}
.nick{font-weight:700;margin:0}
.idea{margin:4px 0 0 0;line-height:1.6}
.res{position:relative;border:1px solid rgba(128,128,128,.35);border-radius:10px;margin:8px 0;overflow:hidden}
.bar{position:absolute;left:0;top:0;bottom:0;background:rgba(59,111,212,.25)}
.rt{position:relative;padding:10px 12px;line-height:1.5}
</style>
""", unsafe_allow_html=True)

BASE = st.secrets["SUPABASE_URL"] + "/rest/v1/"
KEY = st.secrets["SUPABASE_KEY"]
try:
    ADMIN_PW = st.secrets["ADMIN_PASSWORD"]
except Exception:
    ADMIN_PW = None
try:
    PROPOSALS_OPEN = str(st.secrets["PROPOSALS_OPEN"]).lower() != "false"
except Exception:
    PROPOSALS_OPEN = True


STYLE = "fun-emoji"
ALPHABET = "abcdefghjkmnpqrstuvwxyz23456789"


def api(method, table, params=None, body=None, prefer=None):
    head = {"apikey": KEY, "Content-Type": "application/json"}
    if prefer:
        head["Prefer"] = prefer
    r = requests.request(method, BASE + table, headers=head, params=params, json=body, timeout=10)
    r.raise_for_status()
    return r.json() if r.text else []


def get_policies():
    return api("GET", "policies", {"select": "id,nick,idea", "order": "id.asc"})


def get_voter(code):
    rows = api("GET", "voters", {"select": "code,label,voted", "code": f"eq.{code}"})
    return rows[0] if rows else None


def avatar_url(name):
    return f"https://api.dicebear.com/9.x/{STYLE}/svg?seed={quote(name)}"


def new_code():
    return "".join(pysecrets.choice(ALPHABET) for _ in range(6))


def render_results():
    pols = get_policies()
    votes = api("GET", "votes", {"select": "policy_id"})
    counts = {}
    for v in votes:
        counts[v["policy_id"]] = counts.get(v["policy_id"], 0) + 1
    ranked = sorted(pols, key=lambda p: (-counts.get(p["id"], 0), p["id"]))
    top = counts.get(ranked[0]["id"], 0) if ranked else 0
    if top > 0:
        leaders = [p for p in ranked if counts.get(p["id"], 0) == top]
        if len(leaders) == 1:
            st.success(f"🏆 อันดับ 1 ตอนนี้: {leaders[0]['idea']}")
        else:
            st.success(f"🏆 ตอนนี้เสมอกันอันดับ 1 ({len(leaders)} นโยบาย)")
    else:
        st.info("ยังไม่มีใครโหวต")
    for n, p in enumerate(ranked, 1):
        c = counts.get(p["id"], 0)
        pct = int(100 * c / top) if top else 0
        medal = "🥇" if (top > 0 and c == top) else f"{n}."
        text = html.escape(p["idea"]).replace("\n", "<br>")
        st.markdown(
            f'<div class="res"><div class="bar" style="width:{pct}%"></div>'
            f'<div class="rt">{medal} {text} <b>({c} โหวต)</b></div></div>',
            unsafe_allow_html=True,
        )
    st.caption("ผลอัปเดตอัตโนมัติทุก 10 วินาที")


@st.fragment(run_every=10)
def live_results():
    try:
        render_results()
    except Exception as e:
        st.error(f"โหลดผลโหวตไม่สำเร็จ: {e}")


st.title("📣 กระดานนโยบาย")
tab_prop, tab_vote, tab_admin = st.tabs(["💡 เสนอนโยบาย", "🗳️ โหวต", "🔒 เฉพาะพี่น้ำแป้ง"])

# ---------- เสนอนโยบาย ----------
with tab_prop:
    st.caption("ใส่ชื่อเล่น แล้วเขียนแนวคิดนโยบายของคุณ")
    if not PROPOSALS_OPEN:
        st.warning("ปิดรับนโยบายแล้ว ไปโหวตได้ที่แท็บ 🗳️ โหวต")
    with st.form("propose", clear_on_submit=True):
        nick = st.text_input("ชื่อเล่น", max_chars=30)
        idea = st.text_area("แนวคิดนโยบาย", max_chars=500, height=110)
        ok = st.form_submit_button("ส่งนโยบาย", use_container_width=True, disabled=not PROPOSALS_OPEN)
    if ok:
        if nick.strip() and idea.strip():
            try:
                api("POST", "policies", body={"nick": nick.strip(), "idea": idea.strip()})
                st.success("ส่งแล้ว ✓")
            except Exception:
                st.error("ส่งไม่สำเร็จ ลองใหม่อีกครั้งนะ")
        else:
            st.warning("กรอกให้ครบทั้งสองช่องนะ")



# ---------- โหวต ----------
with tab_vote:
    code = st.text_input("รหัสโหวตของคุณ", key="vcode").strip().lower()
    if not code:
        st.info("ใส่รหัสที่ได้รับจากน้ำแป้งหัวจ่ายก่อนนะ")
    else:
        try:
            voter = get_voter(code)
            pols = get_policies()
        except Exception as e:
            voter, pols = None, []
            st.error(f"เชื่อมต่อไม่สำเร็จ: {e}")
        if voter is None:
            st.error("ไม่พบรหัสนี้")
        elif voter["voted"]:
            if st.session_state.pop("just_voted", False):
                st.success("โหวตเรียบร้อยแล้ว ขอบคุณนะ ✓")
            else:
                st.info("รหัสนี้โหวตไปแล้ว")
            live_results()
        elif not pols:
            st.info("ยังไม่มีนโยบายให้โหวต")
        else:
            st.write("เลือกได้หลายข้อ **ยืนยันได้ครั้งเดียว แก้ไขภายหลังไม่ได้**")
            with st.form("vote"):
                picks = [p["id"] for p in pols if st.checkbox(p["idea"], key=f"c{p['id']}")]
                go = st.form_submit_button("ยืนยันการโหวต", use_container_width=True)
            if go:
                if not picks:
                    st.warning("เลือกอย่างน้อย 1 ข้อก่อนนะ")
                else:
                    try:
                        got = api("PATCH", "voters", {"code": f"eq.{code}", "voted": "eq.false"},
                                  body={"voted": True}, prefer="return=representation")
                        if not got:
                            st.error("รหัสนี้โหวตไปแล้ว")
                        else:
                            try:
                                api("POST", "votes", body=[{"voter_code": code, "policy_id": i} for i in picks])
                                st.session_state["just_voted"] = True
                                st.rerun()
                            except requests.HTTPError:
                                api("PATCH", "voters", {"code": f"eq.{code}"}, body={"voted": False})
                                st.error("บันทึกโหวตไม่สำเร็จ ลองใหม่อีกครั้ง")
                    except requests.HTTPError as e:
                        st.error(f"เกิดข้อผิดพลาด: {e}")

# ---------- แอดมิน ----------
with tab_admin:
    pw = st.text_input("รหัสผ่านของเทพ", type="password")
    if not (ADMIN_PW and pw == ADMIN_PW):
        st.caption("ใส่รหัสผ่านเพื่อจัดการ")
    else:
        try:
            pols = get_policies()
            voters = api("GET", "voters", {"select": "code,label,voted", "order": "label.asc"})
            allv = api("GET", "votes", {"select": "voter_code,policy_id"})
        except Exception as e:
            st.error(f"โหลดข้อมูลไม่สำเร็จ: {e}")
            st.stop()

        text_of = {p["id"]: p["idea"] for p in pols}
        picks_of = {}
        for v in allv:
            picks_of.setdefault(v["voter_code"], []).append(v["policy_id"])

        st.subheader("เพิ่มเพื่อน (สร้างรหัสโหวต)")
        with st.form("addvoter", clear_on_submit=True):
            label = st.text_input("ชื่อเพื่อน (เห็นเฉพาะน้ำแป้งหัวจ่าย)", max_chars=40)
            custom = st.text_input("รหัสที่ตั้งเอง (ไม่บังคับ เว้นว่าง = สุ่มให้)", max_chars=20)
            add = st.form_submit_button("เพิ่มเพื่อน", use_container_width=True)
        if add:
            c = custom.strip().lower() or new_code()
            if not label.strip():
                st.warning("ใส่ชื่อเพื่อนก่อน")
            elif not re.fullmatch(r"[a-z0-9_-]{3,20}", c):
                st.warning("รหัสใช้ได้เฉพาะ a-z 0-9 - _ ยาว 3-20 ตัว")
            else:
                try:
                    api("POST", "voters", body={"code": c, "label": label.strip()})
                    st.success(f"สร้างแล้ว: {label.strip()} → {c}")
                    voters.append({"code": c, "label": label.strip(), "voted": False})
                except requests.HTTPError:
                    st.error("รหัสนี้มีคนใช้แล้ว ลองรหัสอื่น")

        done = sum(1 for v in voters if v["voted"])
        st.subheader(f"เพื่อนทั้งหมด (โหวตแล้ว {done}/{len(voters)})")
        for v in voters:
            with st.container(border=True):
                status = "✅ โหวตแล้ว" if v["voted"] else "⏳ ยังไม่โหวต"
                st.markdown(f"**{html.escape(v['label'])}** · รหัส `{v['code']}` · {status}")
                if v["voted"]:
                    for i in picks_of.get(v["code"], []):
                        st.caption("• " + text_of.get(i, "(นโยบายถูกลบแล้ว)"))
                c1, c2 = st.columns(2)
                if c1.button("รีเซ็ตโหวต", key=f"r{v['code']}"):
                    api("DELETE", "votes", {"voter_code": f"eq.{v['code']}"})
                    api("PATCH", "voters", {"code": f"eq.{v['code']}"}, body={"voted": False})
                    st.rerun()
                if c2.button("🗑️ ลบ", key=f"dv{v['code']}"):
                    api("DELETE", "voters", {"code": f"eq.{v['code']}"})
                    st.rerun()

        st.subheader(f"นโยบายทั้งหมด ({len(pols)})")
        for p in pols:
            with st.container(border=True):
                idea_html = html.escape(p["idea"]).replace("\n", "<br>")
                st.markdown(
                    f'<div style="display:flex;gap:10px;align-items:flex-start">'
                    f'<img class="avatar" src="{html.escape(avatar_url(p["nick"]))}" alt="">'
                    f'<div style="flex:1"><p class="nick">{html.escape(p["nick"])}</p>'
                    f'<p class="idea">{idea_html}</p></div></div>',
                    unsafe_allow_html=True,
                )
                if st.button("🗑️ ลบนโยบายนี้", key=f"dp{p['id']}"):
                    api("DELETE", "policies", {"id": f"eq.{p['id']}"})
                    st.rerun()

        st.subheader("ล้างโหวตทั้งหมด")
        if st.checkbox("ยืนยันว่าจะล้างโหวตของทุกคน") and st.button("ล้างโหวตทั้งหมด"):
            api("DELETE", "votes", {"id": "gt.0"})
            api("PATCH", "voters", {"voted": "eq.true"}, body={"voted": False})
            st.rerun()

