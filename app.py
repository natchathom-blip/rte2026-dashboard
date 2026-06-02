import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="RTE 2026 Dashboard",
    page_icon="📊",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
  .kpi-box {
    background: white;
    border-radius: 12px;
    padding: 16px 18px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.08);
    border-top: 4px solid #2563eb;
    margin-bottom: 4px;
  }
  .kpi-label { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; color: #64748b; letter-spacing: 0.6px; }
  .kpi-value { font-size: 2rem; font-weight: 800; color: #1e293b; margin: 4px 0; }
  .kpi-sub   { font-size: 0.73rem; color: #94a3b8; }
  .section-title { font-size: 0.85rem; font-weight: 700; color: #1e293b; margin-bottom: 4px; }
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────
MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

plan_new   = [14, 11, 10, 10, 0, 0, 0, 0, 0, 0, 0, 0]
sold_new   = [14, 11, 10, 10, 0, 0, 0, 0, 0, 0, 0, 0]
success_pct= [100,100,100,100, 0, 0, 0, 0, 0, 0, 0, 0]
stop_unplan= [1,  0,  0,  8,  0, 0, 0, 0, 0, 0, 0, 0]
sales_m    = [66.19, 135.88, 298.51, 429.18, 0, 0, 0, 0, 0, 0, 0, 0]

all_products = pd.DataFrame([
  dict(no=1,  group='ข้าวเหนียว สเต็ก',       market='PMA08', quarter='Q1', month='Jan', code='90113352', name='BGข.น.เนื้อลาบแซ่บEZYGO137g',          type='New',     cm=29.29, alpha=100,  defect=0,    delay=False, sales_jan=4022504, sales_feb=2879629, sales_mar=1896352, sales_apr=1064995),
  dict(no=2,  group='เบอร์เกอร์ รองท้อง',     market='PMA08', quarter='Q1', month='Jan', code='90113351', name='ชีสซี่เบอร์เกอร์ไก่ทอดEZYGO142g',       type='New',     cm=25.31, alpha=89.4, defect=0,    delay=False, sales_jan=5503870, sales_feb=4687381, sales_mar=3878403, sales_apr=3344298),
  dict(no=3,  group='เบอร์เกอร์ รองท้อง',     market='PMA08', quarter='Q1', month='Jan', code='90113348', name='เบอร์เกอร์ไก่EZYGO101g phase2',          type='New',     cm=34.95, alpha=100,  defect=0.12, delay=False, sales_jan=2760860, sales_feb=1461202, sales_mar=1492843, sales_apr=975489),
  dict(no=4,  group='สลัด ยำ น้ำจิ้ม',        market='PMA16', quarter='Q1', month='Jan', code='90138875', name='สลัดปูอัดเเละเซเลอรีตราอีซี่เฟรช210g',  type='New',     cm=18.38, alpha=94,   defect=0,    delay=False, sales_jan=15037920,sales_feb=9982080, sales_mar=6558520, sales_apr=3778886),
  dict(no=5,  group='ข้าวเหนียว สเต็ก',       market='PMA08', quarter='Q1', month='Jan', code='90113350', name='BGข.น.ไก่ย่างEZYGO136g LV2026',          type='LevelUp', cm=42.91, alpha=100,  defect=0.11, delay=False, sales_jan=2077608, sales_feb=1670208, sales_mar=723725,  sales_apr=482878),
  dict(no=6,  group='เบอร์เกอร์ รองท้อง',     market='PMA08', quarter='Q1', month='Jan', code='90113356', name='เบอร์เกอร์ไก่ย่างและชีสEZYGO105g',       type='New',     cm=34.32, alpha=100,  defect=0,    delay=False, sales_jan=1817667, sales_feb=2117417, sales_mar=763756,  sales_apr=0),
  dict(no=7,  group='เบอร์เกอร์ รองท้อง',     market='PMA08', quarter='Q1', month='Jan', code='90113349', name='เบอร์เกอร์กุ้งชีส(ผสมไก่)EZYGO102g',     type='New',     cm=31.25, alpha=100,  defect=0,    delay=False, sales_jan=4603385, sales_feb=2061592, sales_mar=0,       sales_apr=0),
  dict(no=8,  group='ติ่มซำ (นึ่ง)',           market='PMA24', quarter='Q1', month='Jan', code='90113353', name='ขนมจีบหมูอีซี่โก 75g (4 ชิ้น)',          type='New',     cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=9,  group='ติ่มซำ (นึ่ง)',           market='PMA24', quarter='Q1', month='Jan', code='90113354', name='ซาลาเปาหมูสับอีซี่โก 72g (2 ชิ้น)',      type='New',     cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=10, group='ติ่มซำ (นึ่ง)',           market='PMA24', quarter='Q1', month='Jan', code='90113355', name='ติ่มซำกุ้งอีซี่โก 70g (3 ชิ้น)',         type='New',     cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=11, group='ติ่มซำ (นึ่ง)',           market='PMA24', quarter='Q1', month='Jan', code='90113357', name='ฮะเก๋าอีซี่โก 66g (3 ชิ้น)',             type='New',     cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=12, group='เบอร์เกอร์ รองท้อง',     market='PMA02', quarter='Q1', month='Jan', code='90113358', name='เบอร์เกอร์ไก่ทอด PMA02 2026',            type='New',     cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=13, group='ข้าวปั้น เครื่องเคียง',  market='PMA19', quarter='Q1', month='Jan', code='90113359', name='ข้าวปั้นสามเหลี่ยมไก่เทอริยากิ',         type='New',     cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=14, group='ข้าวและกับข้าว',         market='PMA19', quarter='Q1', month='Jan', code='90113360', name='ข้าวกะเพราไก่ไข่ดาว PMA19',              type='New',     cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=15, group='กับข้าว',                market='PMA19', quarter='Q1', month='Feb', code='90113361', name='แกงเขียวหวานไก่ PMA19',                  type='New',     cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=16, group='ติ่มซำ (นึ่ง)',           market='PMA24', quarter='Q1', month='Feb', code='90113362', name='บะหมี่เกี๊ยวกุ้ง อีซี่โก',               type='New',     cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=17, group='ติ่มซำ (นึ่ง)',           market='PMA24', quarter='Q1', month='Feb', code='90113363', name='ซาลาเปาไส้ถั่วแดง อีซี่โก',              type='New',     cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=18, group='ติ่มซำ (นึ่ง)',           market='PMA24', quarter='Q1', month='Feb', code='90113364', name='ขนมจีบกุ้ง อีซี่โก',                     type='New',     cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=19, group='ติ่มซำ (นึ่ง)',           market='PMA24', quarter='Q1', month='Feb', code='90113365', name='ซาลาเปาไส้ BBQ อีซี่โก',                 type='New',     cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=20, group='ข้าวเหนียว สเต็ก',       market='PMA08', quarter='Q1', month='Feb', code='90113366', name='BGข.น.หมูย่างEZYGO LV2026',               type='LevelUp', cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=21, group='ข้าวเหนียว สเต็ก',       market='PMA08', quarter='Q1', month='Feb', code='90113367', name='BGสเต็กหมูEZYGO LV2026',                  type='LevelUp', cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=22, group='ข้าวปั้น เครื่องเคียง',  market='PMA19', quarter='Q1', month='Feb', code='90113368', name='ข้าวปั้นสามเหลี่ยมทูน่ามายองเนส',        type='LevelUp', cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=23, group='ข้าวและกับข้าว',         market='PMA19', quarter='Q1', month='Feb', code='90113369', name='ข้าวผัดกระเพราหมูสับ PMA19',              type='LevelUp', cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=24, group='กับข้าว',                market='PMA06', quarter='Q1', month='Feb', code='90113370', name='ต้มยำกุ้ง PMA06',                        type='LevelUp', cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=25, group='เส้น (ข้าวไทย)',         market='PMA20', quarter='Q2', month='Mar', code='90113371', name='ผัดไทยกุ้งสด PMA20',                     type='New',     cm=0,     alpha=100,  defect=0,    delay=True,  sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=26, group='เส้น (ข้าวไทย)',         market='PMA20', quarter='Q2', month='Mar', code='90113372', name='ข้าวผัดปูอัด PMA20',                     type='New',     cm=0,     alpha=100,  defect=0,    delay=True,  sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=27, group='ติ่มซำ (นึ่ง)',           market='PMA24', quarter='Q2', month='Mar', code='90113373', name='ติ่มซำรวมมิตร อีซี่โก',                  type='New',     cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=28, group='ติ่มซำ (นึ่ง)',           market='PMA24', quarter='Q2', month='Mar', code='90113374', name='ซาลาเปาหมูสับชีส อีซี่โก',               type='New',     cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=29, group='ติ่มซำ (นึ่ง)',           market='PMA24', quarter='Q2', month='Mar', code='90113375', name='ขนมปังซาวโดว์ไก่อบ PMA24',               type='New',     cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=30, group='ติ่มซำ (นึ่ง)',           market='PMA24', quarter='Q2', month='Mar', code='90113376', name='ขนมปังซาวโดว์ทูน่า PMA24',               type='New',     cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=31, group='ข้าวเหนียว สเต็ก',       market='PMA08', quarter='Q2', month='Mar', code='90113377', name='BGข.น.ปลาหมึกย่างEZYGO',                 type='New',     cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=32, group='ข้าวเหนียว สเต็ก',       market='PMA08', quarter='Q2', month='Mar', code='90113378', name='BGข.น.หมูกรอบEZYGO LV2026',              type='LevelUp', cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=33, group='กับข้าว',                market='PMA19', quarter='Q2', month='Mar', code='90113379', name='ผัดกระเพราเนื้อไข่ดาว PMA19',            type='New',     cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=34, group='ข้าวและกับข้าว',         market='PMA19', quarter='Q2', month='Mar', code='90113380', name='ข้าวหมูทอดกระเทียม PMA19',               type='LevelUp', cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=35, group='ติ่มซำ (นึ่ง)',           market='Export',quarter='Q2', month='Apr', code='EXP-001',  name='Chicken Dim Sum Export',                 type='New',     cm=0,     alpha=100,  defect=0,    delay=True,  sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=36, group='ติ่มซำ (นึ่ง)',           market='Export',quarter='Q2', month='Apr', code='EXP-002',  name='Shrimp Har Gow Export',                  type='New',     cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=37, group='ติ่มซำ (นึ่ง)',           market='Export',quarter='Q2', month='Apr', code='EXP-003',  name='Pork Siu Mai Export',                    type='New',     cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=38, group='เส้น (ข้าวไทย)',         market='PMA20', quarter='Q2', month='Apr', code='90113381', name='ก๋วยเตี๋ยวคั่วไก่ PMA20',               type='New',     cm=0,     alpha=100,  defect=0,    delay=True,  sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=39, group='ข้าวปั้น เครื่องเคียง',  market='PMA19', quarter='Q2', month='Apr', code='90113382', name='ข้าวปั้นซีอิ๊วไข่หวาน PMA19',           type='LevelUp', cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=40, group='ข้าวและกับข้าว',         market='PMA19', quarter='Q2', month='Apr', code='90113383', name='ข้าวแกงกะหรี่ไก่ PMA19',                type='LevelUp', cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=41, group='กับข้าว',                market='PMA19', quarter='Q2', month='Apr', code='90113384', name='ต้มข่าไก่ PMA19',                        type='LevelUp', cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=42, group='เส้น (แป้งสาลี) ซุป',   market='PMA20', quarter='Q2', month='Apr', code='90113385', name='ราเม็งซุปมิโซะ PMA20',                   type='New',     cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=43, group='ติ่มซำ รองท้อง (ทอด)',  market='non-7', quarter='Q2', month='Apr', code='non7-001', name='ทอดมันกุ้ง non-7',                       type='New',     cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=44, group='ติ่มซำ (นึ่ง)',           market='non-7', quarter='Q2', month='Apr', code='non7-002', name='ติ่มซำรวมมิตร non-7',                   type='New',     cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
  dict(no=45, group='ข้าวและกับข้าว',         market='PMA22', quarter='Q2', month='Apr', code='90113386', name='ข้าวหน้าเป็ด PMA22',                     type='New',     cm=0,     alpha=100,  defect=0,    delay=False, sales_jan=0, sales_feb=0, sales_mar=0, sales_apr=0),
])
all_products['total_sales'] = all_products[['sales_jan','sales_feb','sales_mar','sales_apr']].sum(axis=1)

stop_df = pd.DataFrame([
  dict(group='ติ่มซำ รองท้อง (ทอด)', market='Export', customer='Ksiaa GmbH',         name='Tori Katsu',                   month='Jan', plan_type='นอกแผน', cause='Mer/ลูกค้าขอยกเลิก', reason='ราคา RM สูง ทำให้ราคาขายสูง'),
  dict(group='เส้น (แป้งสาลี) ซุป',  market='PMA20',  customer='-',                  name='อุด้งหมูผัดกิมจิ 240g',        month='May', plan_type='นอกแผน', cause='Mer/ลูกค้าขอยกเลิก', reason='ราคา RM สูง ทำให้ราคาขายสูง'),
  dict(group='ติ่มซำ รองท้อง (ทอด)', market='non-7',  customer='MAKRO',              name='ซาโมซ่าไส้เผือก',              month='Apr', plan_type='นอกแผน', cause='Mer/ลูกค้าขอยกเลิก', reason='ราคา RM สูง ทำให้ราคาขายสูง'),
  dict(group='ติ่มซำ รองท้อง (ทอด)', market='non-7',  customer='MAKRO',              name='ซาโมซ่าไส้ครีมชีส',            month='Apr', plan_type='นอกแผน', cause='Mer/ลูกค้าขอยกเลิก', reason='ราคา RM สูง ทำให้ราคาขายสูง'),
  dict(group='ติ่มซำ รองท้อง (ทอด)', market='non-7',  customer='MAKRO',              name='ซาโมซ่าไส้เผือกโมจิ',          month='Apr', plan_type='นอกแผน', cause='Mer/ลูกค้าขอยกเลิก', reason='ราคา RM สูง ทำให้ราคาขายสูง'),
  dict(group='ติ่มซำ รองท้อง (ทอด)', market='non-7',  customer='MAKRO',              name='ซาโมซ่าไส้เผือกกล้วย',         month='Apr', plan_type='นอกแผน', cause='Mer/ลูกค้าขอยกเลิก', reason='ราคา RM สูง ทำให้ราคาขายสูง'),
  dict(group='ติ่มซำ รองท้อง (ทอด)', market='Export', customer='Westbridge (TESCO)', name='Banana Cinnamon Parcel',        month='Apr', plan_type='นอกแผน', cause='Mer/ลูกค้าขอยกเลิก', reason='ราคา RM สูง ทำให้ราคาขายสูง'),
  dict(group='ติ่มซำ รองท้อง (ทอด)', market='Export', customer='Westbridge (TESCO)', name='Tofu-Wrapped Prawn',            month='Apr', plan_type='นอกแผน', cause='Mer/ลูกค้าขอยกเลิก', reason='ราคา RM สูง ทำให้ราคาขายสูง'),
  dict(group='ติ่มซำ รองท้อง (ทอด)', market='Export', customer='Westbridge (TESCO)', name='Mango Sticky Rice Spring Roll', month='Apr', plan_type='นอกแผน', cause='Mer/ลูกค้าขอยกเลิก', reason='ราคา RM สูง ทำให้ราคาขายสูง'),
  dict(group='ติ่มซำ รองท้อง (ทอด)', market='Export', customer='Westbridge (TESCO)', name='Sesame Prawn Toast',            month='Apr', plan_type='นอกแผน', cause='Mer/ลูกค้าขอยกเลิก', reason='ราคา RM สูง ทำให้ราคาขายสูง'),
])

# ── Header ───────────────────────────────────────────────────
st.markdown("## 📊 RTE 2026 — Product Development Dashboard")
st.caption("7-11 & Non 7-11 · ข้อมูล ณ เดือน พฤษภาคม 2026")
st.divider()

# ── Tabs ─────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 ภาพรวม", "📦 สินค้าทั้งหมด (45)", "🛑 หยุดพัฒนา (10)"])

# ════════════════════════════════════════
# TAB 1 — OVERVIEW
# ════════════════════════════════════════
with tab1:
    # KPIs
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("สินค้าพัฒนาทั้งหมด", "45", "Jan–Apr 2026")
    k2.metric("% Success New", "100%", "ขายได้ครบทุกตัว")
    k3.metric("หยุดพัฒนานอกแผน", "10", "ส่วนใหญ่ Apr (+8)")
    k4.metric("Delay Plan", "4", "Mar=2, Apr=2")
    k5.metric("ยอดขายสะสม", "429M บาท", "ณ เมษายน")

    st.divider()

    # Row 1
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Plan vs Sold New — รายเดือน**")
        fig = go.Figure()
        fig.add_bar(x=MONTHS, y=plan_new, name="Plan New", marker_color="#2563eb")
        fig.add_bar(x=MONTHS, y=sold_new, name="Sold New", marker_color="#93c5fd")
        fig.update_layout(barmode="group", height=260, margin=dict(l=0,r=0,t=10,b=0),
                          legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("**% Success New — รายเดือน**")
        fig2 = go.Figure()
        fig2.add_scatter(x=MONTHS, y=success_pct, mode="lines+markers",
                         fill="tozeroy", line_color="#16a34a",
                         fillcolor="rgba(22,163,74,0.12)", name="% Success")
        fig2.update_layout(height=260, margin=dict(l=0,r=0,t=10,b=0),
                           yaxis=dict(range=[0,120], ticksuffix="%"))
        st.plotly_chart(fig2, use_container_width=True)

    # Row 2
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("**ยอดขายสะสม (ล้านบาท) — รายเดือน**")
        fig3 = go.Figure()
        fig3.add_scatter(x=MONTHS[:4], y=sales_m[:4], mode="lines+markers",
                         fill="tozeroy", line_color="#7c3aed",
                         fillcolor="rgba(124,58,237,0.10)", name="ยอดขาย")
        fig3.update_layout(height=260, margin=dict(l=0,r=0,t=10,b=0),
                           yaxis=dict(ticksuffix="M"))
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        st.markdown("**สินค้าหยุดพัฒนานอกแผน — รายเดือน**")
        colors = ["#dc2626" if v>5 else "#d97706" if v>0 else "#e2e8f0" for v in stop_unplan]
        fig4 = go.Figure()
        fig4.add_bar(x=MONTHS, y=stop_unplan, marker_color=colors, name="หยุดพัฒนา")
        fig4.update_layout(height=260, margin=dict(l=0,r=0,t=10,b=0), showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

    # Row 3
    c5, c6, c7 = st.columns(3)
    with c5:
        st.markdown("**Top 10 กลุ่มสินค้า (Plan New)**")
        group_df = pd.DataFrame([
            dict(กลุ่มสินค้า='ติ่มซำ (นึ่ง)', plan=17),
            dict(กลุ่มสินค้า='เบอร์เกอร์ รองท้อง', plan=9),
            dict(กลุ่มสินค้า='ข้าวเหนียว สเต็ก', plan=5),
            dict(กลุ่มสินค้า='กับข้าว', plan=3),
            dict(กลุ่มสินค้า='เส้น (ข้าวไทย)', plan=3),
            dict(กลุ่มสินค้า='ข้าวปั้น เครื่องเคียง', plan=2),
            dict(กลุ่มสินค้า='ข้าวและกับข้าว', plan=2),
            dict(กลุ่มสินค้า='ติ่มซำ รองท้อง (ทอด)', plan=2),
            dict(กลุ่มสินค้า='สลัด ยำ น้ำจิ้ม', plan=1),
            dict(กลุ่มสินค้า='เส้น (แป้งสาลี) ซุป', plan=1),
        ])
        fig5 = px.bar(group_df.sort_values('plan'), x='plan', y='กลุ่มสินค้า',
                      orientation='h', color='plan',
                      color_continuous_scale='Blues')
        fig5.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
                           showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig5, use_container_width=True)

    with c6:
        st.markdown("**สัดส่วนตามตลาด**")
        fig6 = go.Figure(go.Pie(
            labels=['PMA08','PMA24','Export','PMA19','PMA20','non-7','PMA02','PMA16','PMA06','PMA22'],
            values=[11,10,7,6,3,3,2,1,1,1],
            hole=0.55,
            marker_colors=px.colors.qualitative.Set2
        ))
        fig6.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig6, use_container_width=True)

    with c7:
        st.markdown("**New vs Level Up ตามตลาด**")
        mkts = ['PMA08','PMA24','Export','PMA19','PMA20','non-7','PMA02','PMA16']
        fig7 = go.Figure()
        fig7.add_bar(x=mkts, y=[11,10,7,6,3,3,2,1], name="New",      marker_color="#2563eb")
        fig7.add_bar(x=mkts, y=[0, 0, 0,6,0,3,0,0], name="Level Up", marker_color="#0d9488")
        fig7.update_layout(barmode="stack", height=300, margin=dict(l=0,r=0,t=10,b=0),
                           legend=dict(orientation="h",y=1.1))
        st.plotly_chart(fig7, use_container_width=True)


# ════════════════════════════════════════
# TAB 2 — ALL PRODUCTS
# ════════════════════════════════════════
with tab2:
    st.markdown("### 📦 สินค้าทั้งหมด")

    col_f1, col_f2, col_f3, col_f4 = st.columns([3,2,2,2])
    with col_f1:
        search = st.text_input("🔍 ค้นหา", placeholder="ชื่อสินค้า / รหัส / กลุ่ม")
    with col_f2:
        groups = ["ทั้งหมด"] + sorted(all_products['group'].unique().tolist())
        sel_group = st.selectbox("กลุ่มสินค้า", groups)
    with col_f3:
        markets = ["ทั้งหมด"] + sorted(all_products['market'].unique().tolist())
        sel_market = st.selectbox("ตลาด", markets)
    with col_f4:
        months_opt = ["ทั้งหมด"] + ['Jan','Feb','Mar','Apr']
        sel_month = st.selectbox("เดือน", months_opt)

    filtered = all_products.copy()
    if sel_group  != "ทั้งหมด": filtered = filtered[filtered['group']  == sel_group]
    if sel_market != "ทั้งหมด": filtered = filtered[filtered['market'] == sel_market]
    if sel_month  != "ทั้งหมด": filtered = filtered[filtered['month']  == sel_month]
    if search:
        q = search.lower()
        filtered = filtered[
            filtered['name'].str.lower().str.contains(q) |
            filtered['group'].str.lower().str.contains(q) |
            filtered['code'].str.lower().str.contains(q)
        ]

    st.caption(f"แสดง {len(filtered)} รายการ")

    display_df = filtered[['no','month','name','group','market','type','cm','total_sales']].copy()
    display_df['cm'] = display_df['cm'].apply(lambda x: f"{x:.2f}%" if x > 0 else "-")
    display_df['total_sales'] = display_df['total_sales'].apply(
        lambda x: f"{x/1e6:.2f}M" if x > 0 else "-")
    display_df.columns = ['#','เดือน','ชื่อสินค้า','กลุ่มสินค้า','ตลาด','ประเภท','%CM','ยอดขายรวม']
    st.dataframe(display_df, use_container_width=True, height=500, hide_index=True)

    # Detail expander
    if len(filtered) > 0:
        st.markdown("---")
        st.markdown("**🔎 ดูรายละเอียดสินค้า**")
        product_names = filtered['name'].tolist()
        sel_product = st.selectbox("เลือกสินค้า", product_names)
        if sel_product:
            row = filtered[filtered['name'] == sel_product].iloc[0]
            with st.expander(f"📋 {row['name']}", expanded=True):
                d1, d2 = st.columns(2)
                with d1:
                    st.markdown("**ข้อมูลทั่วไป**")
                    st.write(f"รหัส: `{row['code']}`")
                    st.write(f"กลุ่ม: {row['group']}")
                    st.write(f"ตลาด: {row['market']}")
                    st.write(f"ไตรมาส: {row['quarter']} | เดือน: {row['month']}")
                    st.write(f"ประเภท: {row['type']}")
                with d2:
                    st.markdown("**Quality & Sales**")
                    st.write(f"%αβ: {row['alpha']}%")
                    st.write(f"%Defect: {row['defect']}%")
                    st.write(f"%CM เกิดจริง: {row['cm']:.2f}%" if row['cm'] > 0 else "%CM: -")
                    st.write(f"Delay: {'⚠️ มี' if row['delay'] else '✅ ไม่มี'}")
                    total = row['total_sales']
                    st.write(f"ยอดขายรวม: {total/1e6:.2f}M บาท" if total > 0 else "ยอดขายรวม: -")
                if row['total_sales'] > 0:
                    fig_s = go.Figure(go.Bar(
                        x=['Jan','Feb','Mar','Apr'],
                        y=[row['sales_jan'],row['sales_feb'],row['sales_mar'],row['sales_apr']],
                        marker_color='#2563eb'
                    ))
                    fig_s.update_layout(title="ยอดขายรายเดือน (บาท)", height=200,
                                        margin=dict(l=0,r=0,t=30,b=0))
                    st.plotly_chart(fig_s, use_container_width=True)


# ════════════════════════════════════════
# TAB 3 — STOPPED PRODUCTS
# ════════════════════════════════════════
with tab3:
    st.markdown("### 🛑 สินค้าหยุดพัฒนานอกแผน")

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("ทั้งหมด", "10 รายการ")
    s2.metric("นอกแผน", "10 (100%)")
    s3.metric("Export", "5 รายการ")
    s4.metric("non-7 / PMA20", "5 รายการ")

    st.divider()

    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown("**หยุดพัฒนาแยกตามกลุ่ม**")
        fig_sg = px.bar(
            x=[9, 1],
            y=['ติ่มซำ รองท้อง (ทอด)', 'เส้น (แป้งสาลี) ซุป'],
            orientation='h',
            color=[9, 1],
            color_continuous_scale=[[0,'#d97706'],[1,'#dc2626']]
        )
        fig_sg.update_layout(height=200, margin=dict(l=0,r=0,t=10,b=0),
                             showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_sg, use_container_width=True)

    with sc2:
        st.markdown("**หยุดพัฒนาแยกตามเดือน**")
        fig_sm = go.Figure(go.Pie(
            labels=['Jan (1)','Apr (8)','May (1)'],
            values=[1, 8, 1],
            hole=0.5,
            marker_colors=['#93c5fd','#dc2626','#d97706']
        ))
        fig_sm.update_layout(height=200, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig_sm, use_container_width=True)

    st.markdown("**รายการสินค้า**")
    mkt_filter = st.radio("Filter ตลาด", ["ทั้งหมด","Export","non-7","PMA20"], horizontal=True)
    stop_filtered = stop_df if mkt_filter == "ทั้งหมด" else stop_df[stop_df['market'] == mkt_filter]

    st.dataframe(
        stop_filtered.rename(columns={
            'group':'กลุ่มสินค้า','market':'ตลาด','customer':'ลูกค้า',
            'name':'ชื่อสินค้า','month':'เดือน','plan_type':'ประเภท',
            'cause':'สาเหตุ','reason':'เหตุผล'
        }),
        use_container_width=True,
        hide_index=True,
        height=400
    )

    st.info("💰 สาเหตุหลักของทุกรายการ: **ราคา RM สูง ทำให้ราคาขายสูง** → Mer / ลูกค้าขอยกเลิก")
