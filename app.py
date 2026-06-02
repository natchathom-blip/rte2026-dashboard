import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json, os

st.set_page_config(
    page_title="RTE 2026 Dashboard",
    page_icon="📊",
    layout="wide",
)

# ── Persistent storage ────────────────────────────────────────
DATA_FILE = "products_data.json"

def load_extra():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_extra(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'extra_products' not in st.session_state:
    st.session_state.extra_products = load_extra()

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Hide default Streamlit top padding */
  .block-container { padding-top: 0 !important; }
  header[data-testid="stHeader"] { display: none; }

  /* Dashboard header */
  .dash-header {
    background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%);
    color: white;
    padding: 18px 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-radius: 0 0 16px 16px;
    box-shadow: 0 2px 12px rgba(37,99,235,0.3);
    margin-bottom: 20px;
  }
  .dash-header h1 { font-size: 1.3rem; font-weight: 700; margin: 0; }
  .dash-header .sub { font-size: 0.8rem; opacity: 0.8; margin-top: 3px; }
  .dash-badge {
    background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.78rem;
    font-weight: 600;
  }

  /* KPI cards */
  .kpi-card {
    background: white;
    border-radius: 14px;
    padding: 16px 18px 13px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.07);
    border-top: 4px solid transparent;
    margin-bottom: 4px;
    height: 110px;
  }
  .kpi-card.blue   { border-top-color: #2563eb; }
  .kpi-card.green  { border-top-color: #16a34a; }
  .kpi-card.red    { border-top-color: #dc2626; }
  .kpi-card.amber  { border-top-color: #d97706; }
  .kpi-card.purple { border-top-color: #7c3aed; }
  .kpi-label {
    font-size: 0.66rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.6px; color: #64748b; margin-bottom: 5px;
  }
  .kpi-card.blue   .kpi-value { color: #2563eb; }
  .kpi-card.green  .kpi-value { color: #16a34a; }
  .kpi-card.red    .kpi-value { color: #dc2626; }
  .kpi-card.amber  .kpi-value { color: #d97706; }
  .kpi-card.purple .kpi-value { color: #7c3aed; }
  .kpi-value { font-size: 2rem; font-weight: 800; line-height: 1; }
  .kpi-sub   { font-size: 0.72rem; color: #94a3b8; margin-top: 5px; }

  /* Progress bar rows */
  .prog-row { display:flex; align-items:center; gap:8px; margin-bottom:8px; font-size:0.78rem; }
  .prog-label { width:148px; flex-shrink:0; color:#334155; font-weight:500; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .prog-bar-wrap { flex:1; background:#f1f5f9; border-radius:6px; height:18px; overflow:hidden; }
  .prog-bar { height:100%; border-radius:6px; display:flex; align-items:center; justify-content:flex-end; padding-right:6px; font-size:0.69rem; font-weight:700; color:white; }
  .prog-num { width:22px; text-align:right; font-weight:700; color:#1e293b; font-size:0.78rem; }

  /* Stop tab styled boxes */
  .cause-box { background:#fee2e2; border-radius:10px; padding:12px 14px; margin-bottom:10px; }
  .cause-box .ct { font-size:0.72rem; color:#dc2626; font-weight:700; margin-bottom:4px; }
  .cause-box .cn { font-size:1.5rem; font-weight:800; color:#dc2626; }
  .info-box { background:#fef9ec; border-radius:10px; padding:12px 14px; border-left:4px solid #f59e0b; margin-bottom:14px; }
  .info-box .it { font-size:0.77rem; color:#92400e; font-weight:700; margin-bottom:4px; }
  .info-box .id { font-size:0.74rem; color:#78350f; }

  /* Market tags in table */
  .tag { display:inline-block; padding:2px 8px; border-radius:10px; font-size:0.7rem; font-weight:600; }
  .tag-red   { background:#fee2e2; color:#dc2626; }
  .tag-blue  { background:#dbeafe; color:#2563eb; }
  .tag-amber { background:#fef3c7; color:#d97706; }
  .tag-gray  { background:#f1f5f9; color:#64748b; }
  .tag-green { background:#dcfce7; color:#16a34a; }

  /* Chart cards */
  .chart-card {
    background: white;
    border-radius: 14px;
    padding: 16px 18px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.07);
    margin-bottom: 4px;
  }
  .chart-card-title {
    font-size: 0.84rem; font-weight: 700; color: #1e293b; margin-bottom: 12px;
  }
</style>
""", unsafe_allow_html=True)

# ── Monthly stats (from Excel %success sheet) ─────────────────
MONTHLY_STATS = {
    'Jan': {'plan_new': 14, 'plan_lv': 8,  'sold_new': 14, 'sold_lv': 8,  'stop_unplan': 1},
    'Feb': {'plan_new': 11, 'plan_lv': 6,  'sold_new': 11, 'sold_lv': 6,  'stop_unplan': 0},
    'Mar': {'plan_new': 10, 'plan_lv': 12, 'sold_new': 10, 'sold_lv': 12, 'stop_unplan': 0},
    'Apr': {'plan_new': 10, 'plan_lv': 5,  'sold_new': 10, 'sold_lv': 5,  'stop_unplan': 8},
}

MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

plan_new    = [14, 11, 10, 10, 0, 0, 0, 0, 0, 0, 0, 0]
sold_new    = [14, 11, 10, 10, 0, 0, 0, 0, 0, 0, 0, 0]
success_pct = [100,100,100,100, 0, 0, 0, 0, 0, 0, 0, 0]
stop_unplan = [1,   0,  0,  8,  0, 0, 0, 0, 0, 0, 0, 0]
sales_m     = [66.19, 135.88, 298.51, 429.18, 0, 0, 0, 0, 0, 0, 0, 0]

# ── Base Data (76 products from Excel) ───────────────────────
BASE_PRODUCTS = [
  dict(no=1,  group='ข้าวเหนียว สเต็ก',      market='PMA08', quarter='Q1', month='Jan', code='90113352', name='BGข.น.เนื้อลาบแซ่บEZYGO137gIMP267-11',                     type='Level Up', alpha=100.0,  defect=0.0,  cm=29.29, cm_request=30.33, delay=False, sales_jan=4022504,  sales_feb=2879629,  sales_mar=1896352,  sales_apr=1064995),
  dict(no=2,  group='เบอร์เกอร์ รองท้อง',    market='PMA08', quarter='Q1', month='Jan', code='90113351', name='ชีสซี่เบอร์เกอร์ไก่ทอดEZYGO142gIMP2026',                    type='Level Up', alpha=89.4,   defect=0.0,  cm=25.31, cm_request=21.6,  delay=False, sales_jan=5503870,  sales_feb=4687381,  sales_mar=3878403,  sales_apr=3344298),
  dict(no=3,  group='เบอร์เกอร์ รองท้อง',    market='PMA08', quarter='Q1', month='Jan', code='90113348', name='เบอร์เกอร์ไก่EZYGO101g, 7-11 phase 2',                     type='Level Up', alpha=100.0,  defect=0.12, cm=34.95, cm_request=27.83, delay=False, sales_jan=2760860,  sales_feb=1461202,  sales_mar=1492843,  sales_apr=975489),
  dict(no=4,  group='สลัด ยำ น้ำจิ้ม',       market='PMA16', quarter='Q1', month='Jan', code='90138875', name='สลัดปูอัดเเละเซเลอรี พร้อมน้ำสลัดซาวเออร์ เมโย่ ตราอีซี่เฟรช 210 กรัม', type='New',      alpha=94.0,   defect=0.0,  cm=18.38, cm_request=16.49, delay=False, sales_jan=15037920, sales_feb=9982080,  sales_mar=6558520,  sales_apr=3778886),
  dict(no=5,  group='ข้าวเหนียว สเต็ก',      market='PMA08', quarter='Q1', month='Jan', code='90113350', name='BGข.น.ไก่ย่างEZYGO136gLV2026,7-11',                         type='New',      alpha=100.0,  defect=0.11, cm=42.91, cm_request=30.03, delay=False, sales_jan=2077608,  sales_feb=1670208,  sales_mar=723725,   sales_apr=482878),
  dict(no=6,  group='เบอร์เกอร์ รองท้อง',    market='PMA08', quarter='Q1', month='Jan', code='90113356', name='เบอร์เกอร์ไก่ย่างและชีสEZYGO105g,7-11',                    type='New',      alpha=100.0,  defect=0.0,  cm=34.32, cm_request=25.85, delay=False, sales_jan=1817667,  sales_feb=2117417,  sales_mar=763756,   sales_apr=0),
  dict(no=7,  group='เบอร์เกอร์ รองท้อง',    market='PMA08', quarter='Q1', month='Jan', code='90113349', name='เบอร์เกอร์กุ้งชีส(ผสมไก่)EZYGO102g,7-11',                  type='New',      alpha=100.0,  defect=0.0,  cm=31.25, cm_request=30.07, delay=False, sales_jan=4603385,  sales_feb=2061592,  sales_mar=0,        sales_apr=0),
  dict(no=8,  group='เบอร์เกอร์ รองท้อง',    market='PMA02', quarter='Q1', month='Jan', code='90101418', name='เกี๊ยวหมึก(หมึกผสมหมู)ซีฟู้ด107g,7-11',                   type='New',      alpha=100.0,  defect=0.13, cm=20.64, cm_request=17.03, delay=False, sales_jan=6961712,  sales_feb=3298219,  sales_mar=2185595,  sales_apr=1617363),
  dict(no=9,  group='ติ่มซำ (นึ่ง)',          market='PMA24', quarter='Q1', month='Jan', code='90108256', name='JBBPไก่กุ้งไข่นกกระทาEZYGO110g,7-11',                      type='New',      alpha=100.0,  defect=0.21, cm=52.79, cm_request=40.82, delay=False, sales_jan=1624628,  sales_feb=1287205,  sales_mar=562597,   sales_apr=19),
  dict(no=10, group='ติ่มซำ (นึ่ง)',          market='PMA24', quarter='Q1', month='Jan', code='90102093', name='สาหร่ายห่อหมูผสมไก่เนื้อปลาบดEZYGO69gคัพ',                type='New',      alpha=83.33,  defect=0.21, cm=20.65, cm_request=32.6,  delay=False, sales_jan=1446130,  sales_feb=2537560,  sales_mar=877397,   sales_apr=302588),
  dict(no=11, group='ติ่มซำ (นึ่ง)',          market='PMA24', quarter='Q1', month='Jan', code='90108259', name='แรบบิทถั่วแดง ตรา อีซี่โก 50 กรัม, 7-11',                  type='New',      alpha=83.33,  defect=0.68, cm=42.26, cm_request=39.7,  delay=False, sales_jan=773560,   sales_feb=1187552,  sales_mar=811619,   sales_apr=547221),
  dict(no=12, group='ติ่มซำ (นึ่ง)',          market='PMA24', quarter='Q1', month='Jan', code='90108254', name='เปาลาวาช็อกโกแลต ตรา อีซี่โก 80กรัม,7-11',                type='New',      alpha=100.0,  defect=0.0,  cm=30.48, cm_request=31.44, delay=False, sales_jan=568921,   sales_feb=1066129,  sales_mar=270317,   sales_apr=62483),
  dict(no=13, group='กับข้าว',               market='PMA06', quarter='Q1', month='Jan', code='90139687', name='พะแนงหมู ตราเซเว่นเฟรช IMP2025',                           type='Level Up', alpha=100.0,  defect=0.0,  cm=41.69, cm_request=35.06, delay=False, sales_jan=652356,   sales_feb=662050,   sales_mar=801638,   sales_apr=928716),
  dict(no=14, group='ข้าวปั้น เครื่องเคียง', market='PMA19', quarter='Q1', month='Jan', code='90138886', name='โอนิกิริซาบะย่างซีอิ๊ว 150g (big size)',                   type='New',      alpha=95.0,   defect=0.0,  cm=22.3,  cm_request=26.35, delay=False, sales_jan=101004,   sales_feb=107759,   sales_mar=7343377,  sales_apr=16597625),
  dict(no=15, group='ข้าวและกับข้าว',        market='PMA19', quarter='Q1', month='Jan', code='90138889', name='ข้าวผัดผักรวมมิตร+ไก่ทอด 300 กรัม',                        type='New',      alpha=100.0,  defect=0.0,  cm=16.71, cm_request=35.37, delay=False, sales_jan=550997,   sales_feb=523285,   sales_mar=281467,   sales_apr=120671),
  dict(no=16, group='ข้าวและกับข้าว',        market='PMA19', quarter='Q1', month='Jan', code='90138888', name='ข้าวแกงเขียวหวานไก่+หมูปั้นก้อนทอด 300 กรัม',              type='New',      alpha=100.0,  defect=0.0,  cm=23.69, cm_request=33.2,  delay=False, sales_jan=576432,   sales_feb=713559,   sales_mar=554583,   sales_apr=5334724),
  dict(no=17, group='ข้าวและกับข้าว',        market='PMA19', quarter='Q1', month='Jan', code='90138898', name='ข้าวหอมมันปูกะเพราอกไก่ LV 2026 270 กรัม',                 type='Level Up', alpha=100.0,  defect=0.0,  cm=35.95, cm_request=25.39, delay=False, sales_jan=2594574,  sales_feb=9161702,  sales_mar=10239514, sales_apr=9493328),
  dict(no=18, group='ข้าวและกับข้าว',        market='PMA19', quarter='Q1', month='Jan', code='90138896', name='ข้าวไรซ์เบอร์รี่ผสมข้าวหอมมะลิลาบอกไก่ LV 2026 270 กรัม', type='Level Up', alpha=100.0,  defect=0.0,  cm=31.94, cm_request=26.26, delay=False, sales_jan=2368040,  sales_feb=7604327,  sales_mar=8342388,  sales_apr=7360410),
  dict(no=19, group='ข้าวและกับข้าว',        market='PMA19', quarter='Q1', month='Jan', code='90138899', name='ข้าวหอมมันปูอกไก่ย่างจิ้มแจ่ว LV 2026',                   type='Level Up', alpha=100.0,  defect=0.0,  cm=37.54, cm_request=30.16, delay=False, sales_jan=5558327,  sales_feb=11992220, sales_mar=12905062, sales_apr=12133213),
  dict(no=20, group='กับข้าว',               market='PMA19', quarter='Q1', month='Jan', code='90138897', name='ต้มยำกุ้งน้ำข้น LV 2026 310 กรัม',                         type='Level Up', alpha=100.0,  defect=0.0,  cm=19.67, cm_request=20.52, delay=False, sales_jan=5304783,  sales_feb=7992490,  sales_mar=8679522,  sales_apr=8270337),
  dict(no=21, group='ติ่มซำ (นึ่ง)',          market='Export',quarter='Q1', month='Jan', code='90140510', name='FZN BBQ Chicken Chick Buns',                                type='New',      alpha=93.33,  defect=0.36, cm=39.18, cm_request=44.96, delay=False, sales_jan=711486,   sales_feb=0,        sales_mar=0,        sales_apr=0),
  dict(no=22, group='ติ่มซำ (นึ่ง)',          market='Export',quarter='Q1', month='Jan', code='90140509', name='FZN Sweet & Sour Hot Cross Buns',                           type='New',      alpha=95.24,  defect=0.71, cm=42.7,  cm_request=51.89, delay=False, sales_jan=577590,   sales_feb=0,        sales_mar=0,        sales_apr=0),
  dict(no=23, group='ข้าวและกับข้าว',        market='PMA19', quarter='Q1', month='Feb', code='90138904', name='ข้าวกะเพราหมู LV 2026',                                    type='Level Up', alpha=100.0,  defect=0.0,  cm=46.2,  cm_request=35.88, delay=False, sales_jan=0,        sales_feb=13641147, sales_mar=37190709, sales_apr=40016069),
  dict(no=24, group='กับข้าว',               market='PMA19', quarter='Q1', month='Feb', code='90138901', name='ไข่เจียวปู 270 กรัม',                                      type='New',      alpha=100.0,  defect=0.0,  cm=19.8,  cm_request=30.23, delay=False, sales_jan=0,        sales_feb=183183,   sales_mar=223369,   sales_apr=204),
  dict(no=25, group='ข้าวและกับข้าว',        market='PMA19', quarter='Q1', month='Mar', code='90138911', name='ข้าวหมกไก่ 280 กรัม',                                      type='Level Up', alpha=100.0,  defect=0.0,  cm=24.08, cm_request=24.27, delay=False, sales_jan=0,        sales_feb=0,        sales_mar=3797235,  sales_apr=12947612),
  dict(no=26, group='ข้าวและกับข้าว',        market='PMA19', quarter='Q1', month='Mar', code='90138906', name='แกงส้มชะอมกุ้ง 310 กรัม',                                 type='Level Up', alpha=100.0,  defect=0.0,  cm=14.42, cm_request=18.73, delay=False, sales_jan=0,        sales_feb=0,        sales_mar=7689311,  sales_apr=12157268),
  dict(no=27, group='เส้น (ข้าวไทย)',        market='PMA19', quarter='Q1', month='Feb', code='90138903', name='ก๋วยเตี๋ยวคั่วไก่ 250 กรัม',                              type='New',      alpha=100.0,  defect=0.0,  cm=33.13, cm_request=30.02, delay=False, sales_jan=0,        sales_feb=5514646,  sales_mar=12418231, sales_apr=11629431),
  dict(no=28, group='เส้น (ข้าวไทย)',        market='PMA20', quarter='Q1', month='Feb', code='90139663', name='ขนมจีนแกงเขียวหวานไก่ 290 กรัม',                          type='New',      alpha=100.0,  defect=0.0,  cm=31.76, cm_request=31.49, delay=False, sales_jan=0,        sales_feb=4354930,  sales_mar=2367257,  sales_apr=2624483),
  dict(no=29, group='กับข้าว',               market='PMA06', quarter='Q1', month='Feb', code='90139689', name='ไก่สับคั่วพริกเกลือพร้อมกระเทียมเจียว62g',               type='New',      alpha=100.0,  defect=0.0,  cm=42.37, cm_request=37.02, delay=False, sales_jan=0,        sales_feb=487077,   sales_mar=733618,   sales_apr=497171),
  dict(no=30, group='กับข้าว',               market='PMA20', quarter='Q1', month='Feb', code='90139674', name='แกงเห็ดรวมมิตร 225 กรัม IMP2026, Frozen',                 type='Level Up', alpha=100.0,  defect=0.0,  cm=35.09, cm_request=32.92, delay=False, sales_jan=0,        sales_feb=4024986,  sales_mar=6713483,  sales_apr=8036297),
  dict(no=31, group='เบอร์เกอร์ รองท้อง',    market='PMA08', quarter='Q1', month='Feb', code='90113354', name='เลิฟเวอร์BGไก่ทอดชีสEZYGO139g,7-11',                      type='New',      alpha=100.0,  defect=0.15, cm=32.18, cm_request=25.25, delay=False, sales_jan=0,        sales_feb=4512763,  sales_mar=1159764,  sales_apr=0),
  dict(no=32, group='เบอร์เกอร์ รองท้อง',    market='PMA08', quarter='Q1', month='Feb', code='90113357', name='BGกุ้งและไข่กุ้งEZYGO98g7-11IMP2026',                      type='Level Up', alpha=100.0,  defect=0.0,  cm=28.53, cm_request=29.65, delay=False, sales_jan=0,        sales_feb=2800165,  sales_mar=3233169,  sales_apr=2406599),
  dict(no=33, group='เบอร์เกอร์ รองท้อง',    market='PMA08', quarter='Q1', month='Feb', code='90113358', name='เบอร์เกอร์หมูEZGO93g(IMP2026,)7-11',                       type='Level Up', alpha=100.0,  defect=0.08, cm=35.01, cm_request=30.73, delay=False, sales_jan=0,        sales_feb=2002288,  sales_mar=12903828, sales_apr=14285232),
  dict(no=34, group='ข้าวเหนียว สเต็ก',      market='PMA08', quarter='Q1', month='Feb', code='90113353', name='เบอร์เกอร์ข้าวเหนียวหมูย่างEZYGO141g7-11',                 type='New',      alpha=100.0,  defect=0.0,  cm=64.57, cm_request=36.65, delay=False, sales_jan=0,        sales_feb=3518368,  sales_mar=2029084,  sales_apr=985173),
  dict(no=35, group='ข้าวเหนียว สเต็ก',      market='PMA22', quarter='Q1', month='Feb', code='90138905', name='ข้าวเหนียวไก่ย่างแดง อีซี่โก 170g, 7-11',                 type='New',      alpha=100.0,  defect=0.13, cm=27.69, cm_request=27.69, delay=False, sales_jan=0,        sales_feb=512010,   sales_mar=358015,   sales_apr=284820),
  dict(no=36, group='ติ่มซำ (นึ่ง)',          market='PMA24', quarter='Q1', month='Feb', code='90108281', name='แรบบิทครีม ตรา อีซี่โก 60 กรัม,7-11 Lv26',                type='Level Up', alpha=100.0,  defect=0.42, cm=49.0,  cm_request=36.94, delay=False, sales_jan=0,        sales_feb=724593,   sales_mar=5126676,  sales_apr=5106241),
  dict(no=37, group='ติ่มซำ (นึ่ง)',          market='PMA24', quarter='Q1', month='Feb', code='90108280', name='เปาเผือกโมจิ (ซาลาเปา) อีซี่โก 80g,7-11',                type='New',      alpha=100.0,  defect=0.52, cm=52.95, cm_request=39.89, delay=False, sales_jan=0,        sales_feb=896459,   sales_mar=2015552,  sales_apr=1281865),
  dict(no=38, group='ติ่มซำ (นึ่ง)',          market='PMA24', quarter='Q1', month='Feb', code='90106013', name='ไก่นุ่มหน้ากุ้ง(ผสมหมู)EZYGO67g,7-11คัพ',                 type='New',      alpha=100.0,  defect=0.0,  cm=28.46, cm_request=28.18, delay=False, sales_jan=0,        sales_feb=3016074,  sales_mar=1797353,  sales_apr=778885),
  dict(no=39, group='ข้าวปั้น เครื่องเคียง', market='PMA19', quarter='Q1', month='Feb', code='90138907', name='โอนิกิริไข่กุ้งมายองเนส 100 กรัม(LV2026)',                type='Level Up', alpha=100.0,  defect=0.0,  cm=52.09, cm_request=47.01, delay=False, sales_jan=0,        sales_feb=12169381, sales_mar=29670444, sales_apr=29722494),
  dict(no=40, group='ติ่มซำ (นึ่ง)',          market='Export',quarter='Q1', month='Feb', code='90140505', name='Frozen Fully Steamed Gochujang Chicken Bun',                type='New',      alpha=100.0,  defect=0.0,  cm=62.0,  cm_request=55.84, delay=False, sales_jan=0,        sales_feb=3235200,  sales_mar=0,        sales_apr=0),
  dict(no=41, group='ติ่มซำ (นึ่ง)',          market='Export',quarter='Q1', month='Feb', code='90140506', name='Frozen Fully Steamed Chicken Gyoza',                        type='New',      alpha=100.0,  defect=0.0,  cm=51.43, cm_request=57.69, delay=False, sales_jan=0,        sales_feb=1290914,  sales_mar=0,        sales_apr=0),
  dict(no=42, group='ข้าวและกับข้าว',        market='PMA20', quarter='Q1', month='Mar', code='90139668', name='ข้าวกะเพรามังสวิรัติ 210 G IMP2026 CHB',                  type='Level Up', alpha=100.0,  defect=0.0,  cm=35.51, cm_request=35.45, delay=True,  sales_jan=0,        sales_feb=0,        sales_mar=4619790,  sales_apr=6089509),
  dict(no=43, group='ข้าวปั้น เครื่องเคียง', market='PMA19', quarter='Q1', month='Mar', code='90138908', name='แคลิฟอร์เนียโรล 105 กรัม LV2026, Chilled',                type='Level Up', alpha=95.0,   defect=0.0,  cm=33.18, cm_request=31.92, delay=False, sales_jan=0,        sales_feb=0,        sales_mar=5949100,  sales_apr=9320202),
  dict(no=44, group='ข้าวปั้น เครื่องเคียง', market='PMA19', quarter='Q1', month='Mar', code='90138909', name='ซูชิเซ็ท 155 กรัม LV2026, Chilled',                       type='Level Up', alpha=100.0,  defect=0.0,  cm=31.71, cm_request=28.6,  delay=False, sales_jan=0,        sales_feb=0,        sales_mar=3672908,  sales_apr=13096653),
  dict(no=45, group='ติ่มซำ (นึ่ง)',          market='PMA24', quarter='Q1', month='Mar', code='90101430', name='ขนมจีบกุ้งและขนมจีบหมูไข่เค็มEZYGO112g',                  type='New',      alpha=100.0,  defect=0.0,  cm=43.35, cm_request=38.84, delay=False, sales_jan=0,        sales_feb=0,        sales_mar=1381716,  sales_apr=1887655),
  dict(no=46, group='ติ่มซำ (นึ่ง)',          market='PMA24', quarter='Q1', month='Mar', code='90101429', name='ขนมจีบหมูผสมไก่450g7-11 Frozen',                           type='New',      alpha=100.0,  defect=0.0,  cm=53.59, cm_request=40.85, delay=False, sales_jan=0,        sales_feb=0,        sales_mar=2291201,  sales_apr=1325912),
  dict(no=47, group='ติ่มซำ (นึ่ง)',          market='PMA24', quarter='Q1', month='Mar', code='90108284', name='แรบบิทฟักทอง ตรา อีซี่โก 50g,7-11',                       type='New',      alpha=83.33,  defect=0.42, cm=45.43, cm_request=36.99, delay=False, sales_jan=0,        sales_feb=0,        sales_mar=735992,   sales_apr=761235),
  dict(no=48, group='ข้าวเหนียว สเต็ก',      market='PMA08', quarter='Q1', month='Mar', code='90113366', name='BGข้าวเหนียวไก่ปลาร้า อีซี่โก 140g, 7-11',                type='New',      alpha=100.0,  defect=0.15, cm=28.1,  cm_request=31.11, delay=False, sales_jan=0,        sales_feb=0,        sales_mar=2511029,  sales_apr=3623664),
  dict(no=49, group='เบอร์เกอร์ รองท้อง',    market='PMA08', quarter='Q1', month='Mar', code='90113360', name='เบอร์เกอร์หมูชีสและแฮมEZYGO126g,7-11',                    type='New',      alpha=100.0,  defect=0.0,  cm=27.06, cm_request=28.98, delay=False, sales_jan=0,        sales_feb=0,        sales_mar=3914350,  sales_apr=2796272),
  dict(no=50, group='เบอร์เกอร์ รองท้อง',    market='PMA08', quarter='Q1', month='Mar', code='90113362', name='BGกุ้งย่างและชีส(ผสมไก่)EZYGO115g,7-11',                  type='New',      alpha=100.0,  defect=0.0,  cm=35.17, cm_request=32.57, delay=False, sales_jan=0,        sales_feb=0,        sales_mar=2619028,  sales_apr=2429581),
  dict(no=51, group='เบอร์เกอร์ รองท้อง',    market='PMA08', quarter='Q1', month='Mar', code='90113363', name='เบอร์เกอร์ไก่ทอดชีสEZYGO143g,7-11',                       type='New',      alpha=100.0,  defect=0.16, cm=25.16, cm_request=26.97, delay=False, sales_jan=0,        sales_feb=0,        sales_mar=571542,   sales_apr=3056553),
  dict(no=52, group='ข้าวเหนียว สเต็ก',      market='PMA08', quarter='Q1', month='Mar', code='90113359', name='เจ๊แดงBGข้าวเหนียวหมูน้ำตก141gIMP26,7-11',                type='Level Up', alpha=100.0,  defect=0.1,  cm=58.83, cm_request=41.0,  delay=False, sales_jan=0,        sales_feb=-237,     sales_mar=2784168,  sales_apr=2185825),
  dict(no=53, group='เบอร์เกอร์ รองท้อง',    market='PMA08', quarter='Q1', month='Mar', code='90113361', name='เบอร์เกอร์กุ้งEZYGO93g,7-11IMP2026',                       type='Level Up', alpha=100.0,  defect=0.1,  cm=29.25, cm_request=28.57, delay=False, sales_jan=0,        sales_feb=0,        sales_mar=5433350,  sales_apr=19814185),
  dict(no=54, group='ข้าวเหนียว สเต็ก',      market='PMA22', quarter='Q1', month='Mar', code='90138912', name='ข้าวเหนียวหมูทอดอีซี่โก125gIMP26,7-11',                   type='Level Up', alpha=100.0,  defect=0.0,  cm=45.23, cm_request=39.55, delay=False, sales_jan=0,        sales_feb=0,        sales_mar=12706191, sales_apr=16277561),
  dict(no=55, group='ติ่มซำ (นึ่ง)',          market='Export',quarter='Q1', month='Mar', code='90140511', name='Frozen Fully Steamed Pork Bun (Conan) 100 g',               type='New',      alpha=87.5,   defect=1.33, cm=58.13, cm_request=55.97, delay=False, sales_jan=0,        sales_feb=0,        sales_mar=896334,   sales_apr=0),
  dict(no=56, group='เส้น (ข้าวไทย)',        market='PMA20', quarter='Q1', month='Mar', code='90139644', name='แจ่วฮ้อนหม่ำแซ่บ 170 g (ซุปเข้มข้น)',                    type='Level Up', alpha=100.0,  defect=0.0,  cm=30.71, cm_request=35.0,  delay=False, sales_jan=0,        sales_feb=0,        sales_mar=3259764,  sales_apr=4779534),
  dict(no=57, group='เส้น (ข้าวไทย)',        market='PMA19', quarter='Q1', month='Mar', code='90138910', name='ผัดซีอิ๊วหมู 250g. LV 2026',                              type='Level Up', alpha=100.0,  defect=0.0,  cm=35.32, cm_request=31.34, delay=False, sales_jan=0,        sales_feb=0,        sales_mar=26566532, sales_apr=43371499),
  dict(no=58, group='เส้น (ข้าวไทย)',        market='PMA20', quarter='Q1', month='Mar', code='90139688', name='ขนมจีนน้ำยาป่าลูกชิ้นปลา 285 กรัม IMP2026',              type='Level Up', alpha=100.0,  defect=0.0,  cm=20.67, cm_request=14.3,  delay=False, sales_jan=0,        sales_feb=0,        sales_mar=2370986,  sales_apr=3259591),
  dict(no=59, group='เส้น (แป้งสาลี) ซุป',  market='PMA20', quarter='Q1', month='Mar', code='90139639', name='เกี๊ยวน้ำหมู 190 กรัม IMP2025, Frozen',                   type='Level Up', alpha=100.0,  defect=0.0,  cm=44.44, cm_request=30.84, delay=False, sales_jan=0,        sales_feb=0,        sales_mar=5400626,  sales_apr=10028358),
  dict(no=60, group='เส้น (แป้งสาลี) ซุป',  market='non-7', quarter='Q1', month='Mar', code='90139672', name='สปาเก็ตตี้ไส้กรอกผัดพริกแห้ง, เดลิกาเซีย',               type='New',      alpha=100.0,  defect=0.0,  cm=59.51, cm_request=50.28, delay=False, sales_jan=0,        sales_feb=0,        sales_mar=3600,     sales_apr=56400),
  dict(no=61, group='ข้าวปั้น เครื่องเคียง', market='PMA19', quarter='Q1', month='Mar', code='90138877', name='สาหร่ายวากาเมะน้ำมันงา 55 กรัม, Chilled',                type='New',      alpha=100.0,  defect=0.0,  cm=31.46, cm_request=30.79, delay=True,  sales_jan=0,        sales_feb=0,        sales_mar=8482102,  sales_apr=8820224),
  dict(no=62, group='ข้าวและกับข้าว',        market='PMA20', quarter='Q2', month='Apr', code='90139693', name='ข้าวไก่ย่างปลาร้าซอสจิ้มแจ่ว300g,IMP26',                 type='Level Up', alpha=100.0,  defect=0.0,  cm=21.31, cm_request=24.25, delay=False, sales_jan=0,        sales_feb=0,        sales_mar=2243955,  sales_apr=3492065),
  dict(no=63, group='กับข้าว',               market='PMA20', quarter='Q2', month='Apr', code='90139694', name='ซุปผักสไตล์ลาว 160 กรัม, Frozen',                         type='New',      alpha=100.0,  defect=0.0,  cm=36.62, cm_request=39.05, delay=False, sales_jan=0,        sales_feb=0,        sales_mar=0,        sales_apr=8669782),
  dict(no=64, group='ข้าวและกับข้าว',        market='PMA20', quarter='Q2', month='Apr', code='90139690', name='ข้าวกะเพราหมู 215 กรัม IMP2026',                          type='Level Up', alpha=100.0,  defect=0.0,  cm=42.1,  cm_request=35.22, delay=False, sales_jan=0,        sales_feb=0,        sales_mar=0,        sales_apr=18582372),
  dict(no=65, group='ข้าวเหนียว สเต็ก',      market='PMA08', quarter='Q2', month='Apr', code='90113364', name='BGข้าวเหนียวแหนมหมูทอด138g7-11',                          type='New',      alpha=100.0,  defect=0.0,  cm=39.77, cm_request=47.45, delay=False, sales_jan=0,        sales_feb=0,        sales_mar=0,        sales_apr=3584141),
  dict(no=66, group='เบอร์เกอร์ รองท้อง',    market='PMA08', quarter='Q2', month='Apr', code='90113365', name='BGหมูทอดทงคัตสึและชีสEZYGO121g,7-11',                     type='New',      alpha=90.5,   defect=0.1,  cm=32.41, cm_request=33.98, delay=False, sales_jan=0,        sales_feb=0,        sales_mar=0,        sales_apr=2837105),
  dict(no=67, group='เบอร์เกอร์ รองท้อง',    market='PMA02', quarter='Q2', month='Apr', code='90138915', name='ไก่ย่างสูตรเผ็ดเดลิกาเซียเชสเตอร์90g7-11',               type='New',      alpha=90.0,   defect=0.23, cm=24.35, cm_request=17.15, delay=False, sales_jan=0,        sales_feb=0,        sales_mar=0,        sales_apr=1856108),
  dict(no=68, group='เบอร์เกอร์ รองท้อง',    market='PMA08', quarter='Q2', month='Apr', code='90113355', name='ดับเบิ้ลชีสเบอร์เกอร์หมูEZYGO131g,IMP26',                type='Level Up', alpha=100.0,  defect=0.0,  cm=24.88, cm_request=15.93, delay=False, sales_jan=0,        sales_feb=0,        sales_mar=0,        sales_apr=7399346),
  dict(no=69, group='ข้าวเหนียว สเต็ก',      market='PMA08', quarter='Q2', month='Apr', code='90113367', name='BGข้าวเหนียวจัมโบ้หมูปิ้ง180gIMP26,7-11',                type='Level Up', alpha=100.0,  defect=0.0,  cm=35.27, cm_request=39.06, delay=False, sales_jan=0,        sales_feb=0,        sales_mar=1496738,  sales_apr=6958411),
  dict(no=70, group='ติ่มซำ รองท้อง (ทอด)',  market='Export',quarter='Q2', month='Apr', code='90147032', name='Frozen Fully Fried Veggie Wonton 15g',                     type='New',      alpha=100.0,  defect=0.0,  cm=3.8,   cm_request=37.5,  delay=False, sales_jan=0,        sales_feb=0,        sales_mar=0,        sales_apr=502347),
  dict(no=71, group='ติ่มซำ รองท้อง (ทอด)',  market='Export',quarter='Q2', month='Apr', code='90147032', name='Sweet & Sour Sauce 20 g',                                  type='New',      alpha=100.0,  defect=0.0,  cm=3.8,   cm_request=37.5,  delay=False, sales_jan=0,        sales_feb=0,        sales_mar=0,        sales_apr=0),
  dict(no=72, group='เส้น (ข้าวไทย)',        market='PMA20', quarter='Q2', month='Apr', code='90139686', name='ผัดหมี่โคราช 200 กรัม',                                   type='New',      alpha=100.0,  defect=0.0,  cm=22.34, cm_request=31.42, delay=True,  sales_jan=0,        sales_feb=0,        sales_mar=0,        sales_apr=3755920),
  dict(no=73, group='เส้น (ข้าวไทย)',        market='PMA19', quarter='Q2', month='Apr', code='90138913', name='เส้นใหญ่ราดหน้าหมูนุ่ม 395 กรัม',                        type='Level Up', alpha=100.0,  defect=0.0,  cm=34.61, cm_request=31.66, delay=True,  sales_jan=0,        sales_feb=0,        sales_mar=0,        sales_apr=1013890),
  dict(no=74, group='ติ่มซำ (นึ่ง)',          market='non-7', quarter='Q2', month='Apr', code='90108275', name='ซาลาเปาลาวาโอวัลติน เจดดราก้อน444g,Makro',               type='New',      alpha=100.0,  defect=0.0,  cm=53.63, cm_request=50.23, delay=False, sales_jan=0,        sales_feb=0,        sales_mar=0,        sales_apr=480473),
  dict(no=75, group='ติ่มซำ (นึ่ง)',          market='non-7', quarter='Q2', month='Apr', code='90103091', name='ฮะเก๋ากุ้งชีส(ผสมปลาและหมู)เจด360g,Non-7',               type='New',      alpha=100.0,  defect=0.0,  cm=34.78, cm_request=38.05, delay=False, sales_jan=0,        sales_feb=0,        sales_mar=0,        sales_apr=616593),
  dict(no=76, group='ติ่มซำ (นึ่ง)',          market='PMA24', quarter='Q2', month='Apr', code='90108288', name='เปาจี่ผักโขมไก่ผสมแฮมและชีสEZYGO110g7-11',               type='New',      alpha=90.91,  defect=0.62, cm=37.41, cm_request=41.36, delay=False, sales_jan=0,        sales_feb=0,        sales_mar=0,        sales_apr=1273235),
]

STOP_PRODUCTS = [
  dict(group='ติ่มซำ รองท้อง (ทอด)', market='Export', customer='Ksiaa GmbH',            name='Tori Katsu',                   plan_type='นอกแผน', month='Jan', cause='Mer/ลูกค้าขอยกเลิก', reason='ราคา RM สูง ทำให้ราคาขายสูง'),
  dict(group='เส้น (แป้งสาลี) ซุป',  market='PMA20',  customer='-',                     name='อุด้งหมูผัดกิมจิ 240 กรัม',  plan_type='นอกแผน', month='May', cause='Mer/ลูกค้าขอยกเลิก', reason='ราคา RM สูง ทำให้ราคาขายสูง'),
  dict(group='ติ่มซำ รองท้อง (ทอด)', market='non-7',  customer='MAKRO',                 name='ซาโมซ่าไส้เผือก',             plan_type='นอกแผน', month='Apr', cause='Mer/ลูกค้าขอยกเลิก', reason='ราคา RM สูง ทำให้ราคาขายสูง'),
  dict(group='ติ่มซำ รองท้อง (ทอด)', market='non-7',  customer='MAKRO',                 name='ซาโมซ่าไส้ครีมชีส',           plan_type='นอกแผน', month='Apr', cause='Mer/ลูกค้าขอยกเลิก', reason='ราคา RM สูง ทำให้ราคาขายสูง'),
  dict(group='ติ่มซำ รองท้อง (ทอด)', market='non-7',  customer='MAKRO',                 name='ซาโมซ่าไส้เผือกโมจิ',         plan_type='นอกแผน', month='Apr', cause='Mer/ลูกค้าขอยกเลิก', reason='ราคา RM สูง ทำให้ราคาขายสูง'),
  dict(group='ติ่มซำ รองท้อง (ทอด)', market='non-7',  customer='MAKRO',                 name='ซาโมซ่าไส้เผือกกล้วย',        plan_type='นอกแผน', month='Apr', cause='Mer/ลูกค้าขอยกเลิก', reason='ราคา RM สูง ทำให้ราคาขายสูง'),
  dict(group='ติ่มซำ รองท้อง (ทอด)', market='Export', customer='Westbridge (TESCO)',    name='Banana Cinnamon Parcel',       plan_type='นอกแผน', month='Apr', cause='Mer/ลูกค้าขอยกเลิก', reason='ราคา RM สูง ทำให้ราคาขายสูง'),
  dict(group='ติ่มซำ รองท้อง (ทอด)', market='Export', customer='Westbridge (TESCO)',    name='Tofu-Wrapped Prawn',           plan_type='นอกแผน', month='Apr', cause='Mer/ลูกค้าขอยกเลิก', reason='ราคา RM สูง ทำให้ราคาขายสูง'),
  dict(group='ติ่มซำ รองท้อง (ทอด)', market='Export', customer='Westbridge (TESCO)',    name='Mango Sticky Rice Spring Roll',plan_type='นอกแผน', month='Apr', cause='Mer/ลูกค้าขอยกเลิก', reason='ราคา RM สูง ทำให้ราคาขายสูง'),
  dict(group='ติ่มซำ รองท้อง (ทอด)', market='Export', customer='Westbridge for Aldi',   name='Crispy Stay Chicken Gyoza',   plan_type='นอกแผน', month='Apr', cause='Mer/ลูกค้าขอยกเลิก', reason='ราคา RM สูง ทำให้ราคาขายสูง'),
]

GROUP_LIST  = sorted(set(p['group'] for p in BASE_PRODUCTS)) + ['อื่นๆ']
MARKET_LIST = sorted(set(p['market'] for p in BASE_PRODUCTS))

# ── Build DataFrame ───────────────────────────────────────────
all_products = pd.DataFrame(BASE_PRODUCTS)
all_products['total_sales'] = all_products[['sales_jan','sales_feb','sales_mar','sales_apr']].sum(axis=1)

if st.session_state.extra_products:
    extra_df = pd.DataFrame(st.session_state.extra_products)
    for col in ['sales_jan','sales_feb','sales_mar','sales_apr']:
        if col not in extra_df.columns:
            extra_df[col] = 0
    extra_df['total_sales'] = extra_df[['sales_jan','sales_feb','sales_mar','sales_apr']].sum(axis=1)
    all_products = pd.concat([all_products, extra_df], ignore_index=True)

stop_df = pd.DataFrame(STOP_PRODUCTS)

# ── Header ───────────────────────────────────────────────────
st.markdown("""
<div class="dash-header">
  <div>
    <h1>📊 RTE 2026 — Product Development Dashboard</h1>
    <div class="sub">7-11 &amp; Non 7-11 · ข้อมูล ณ เดือน พฤษภาคม 2026</div>
  </div>
  <div class="dash-badge">Jan – Apr 2026</div>
</div>
""", unsafe_allow_html=True)

total_all = len(all_products)
total_new = len(all_products[all_products['type'] == 'New'])
total_lv  = len(all_products[all_products['type'] == 'Level Up'])

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 ภาพรวม",
    f"📦 สินค้าทั้งหมด ({total_all})",
    f"🛑 หยุดพัฒนา ({len(stop_df)})",
    "➕ เพิ่มสินค้าใหม่",
])

# ════════════════════════════════════════
# TAB 1 — OVERVIEW
# ════════════════════════════════════════
with tab1:
    delay_count = int(all_products['delay'].sum())
    total_sales_m = all_products['total_sales'].sum() / 1e6
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-bottom:20px;">
      <div class="kpi-card blue">
        <div class="kpi-label">สินค้าพัฒนาทั้งหมด</div>
        <div class="kpi-value">{total_all}</div>
        <div class="kpi-sub">Jan–Apr 2026</div>
      </div>
      <div class="kpi-card green">
        <div class="kpi-label">% Success New</div>
        <div class="kpi-value">100%</div>
        <div class="kpi-sub">ขายได้ครบทุกตัว</div>
      </div>
      <div class="kpi-card red">
        <div class="kpi-label">หยุดพัฒนานอกแผน</div>
        <div class="kpi-value">{len(stop_df)}</div>
        <div class="kpi-sub">ส่วนใหญ่ Apr (+8)</div>
      </div>
      <div class="kpi-card amber">
        <div class="kpi-label">Delay Plan</div>
        <div class="kpi-value">{delay_count}</div>
        <div class="kpi-sub">สินค้าที่เลื่อนแผน</div>
      </div>
      <div class="kpi-card purple">
        <div class="kpi-label">ยอดขายสะสม</div>
        <div class="kpi-value">{total_sales_m:.0f}M</div>
        <div class="kpi-sub">บาท ณ เมษายน</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="chart-card"><div class="chart-card-title">🔵 Plan vs Sold New — รายเดือน</div>', unsafe_allow_html=True)
        p_vals = plan_new[:]
        s_vals = sold_new[:]
        if st.session_state.extra_products:
            extra_df2 = pd.DataFrame(st.session_state.extra_products)
            for i, m in enumerate(MONTHS):
                cnt = len(extra_df2[extra_df2['month'] == m])
                p_vals[i] += cnt
                s_vals[i] += cnt
        fig = go.Figure()
        fig.add_bar(x=MONTHS, y=p_vals, name="Plan New", marker_color="#2563eb")
        fig.add_bar(x=MONTHS, y=s_vals, name="Sold New", marker_color="#93c5fd")
        fig.update_layout(barmode="group", height=250, margin=dict(l=0,r=0,t=4,b=0),
                          plot_bgcolor='white', paper_bgcolor='white',
                          legend=dict(orientation="h", y=1.12),
                          font=dict(family="Segoe UI, sans-serif"))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="chart-card"><div class="chart-card-title">🟢 % Success New — รายเดือน</div>', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_scatter(x=MONTHS, y=success_pct, mode="lines+markers",
                         fill="tozeroy", line_color="#16a34a",
                         fillcolor="rgba(22,163,74,0.12)", name="% Success",
                         marker=dict(size=8))
        fig2.update_layout(height=250, margin=dict(l=0,r=0,t=4,b=0),
                           plot_bgcolor='white', paper_bgcolor='white',
                           yaxis=dict(range=[0,120], ticksuffix="%"),
                           showlegend=False, font=dict(family="Segoe UI, sans-serif"))
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="chart-card"><div class="chart-card-title">🟣 ยอดขายสะสม (ล้านบาท) — รายเดือน</div>', unsafe_allow_html=True)
        fig3 = go.Figure()
        fig3.add_scatter(x=MONTHS[:4], y=sales_m[:4], mode="lines+markers",
                         fill="tozeroy", line_color="#7c3aed",
                         fillcolor="rgba(124,58,237,0.10)", name="ยอดขาย",
                         marker=dict(size=8))
        fig3.update_layout(height=250, margin=dict(l=0,r=0,t=4,b=0),
                           plot_bgcolor='white', paper_bgcolor='white',
                           yaxis=dict(ticksuffix="M"),
                           showlegend=False, font=dict(family="Segoe UI, sans-serif"))
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        st.markdown('<div class="chart-card"><div class="chart-card-title">🔴 สินค้าหยุดพัฒนานอกแผน — รายเดือน</div>', unsafe_allow_html=True)
        colors = ["#dc2626" if v>5 else "#d97706" if v>0 else "#e2e8f0" for v in stop_unplan]
        fig4 = go.Figure()
        fig4.add_bar(x=MONTHS, y=stop_unplan, marker_color=colors, name="หยุดพัฒนา")
        fig4.update_layout(height=250, margin=dict(l=0,r=0,t=4,b=0),
                           plot_bgcolor='white', paper_bgcolor='white',
                           showlegend=False, font=dict(family="Segoe UI, sans-serif"))
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    c5, c6, c7 = st.columns(3)
    with c5:
        st.markdown('<div class="chart-card"><div class="chart-card-title">🔵 Top กลุ่มสินค้า (Plan New)</div>', unsafe_allow_html=True)
        grp_df = all_products.groupby('group').size().reset_index(name='count').sort_values('count', ascending=False)
        max_cnt = grp_df['count'].max()
        bar_colors = ['#2563eb','#0d9488','#16a34a','#16a34a','#16a34a','#d97706','#d97706','#dc2626','#7c3aed','#64748b']
        bars_html = ''
        for i, row in grp_df.iterrows():
            pct = int(row['count'] / max_cnt * 100)
            color = bar_colors[min(i, len(bar_colors)-1)]
            bars_html += f'''<div class="prog-row">
              <div class="prog-label">{row["group"]}</div>
              <div class="prog-bar-wrap"><div class="prog-bar" style="width:{pct}%;background:{color};">{row["count"]}</div></div>
              <div class="prog-num">{int(row["count"])}</div>
            </div>'''
        st.markdown(bars_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c6:
        st.markdown('<div class="chart-card"><div class="chart-card-title">🟢 สัดส่วนตามตลาด (Plan New)</div>', unsafe_allow_html=True)
        mkt_df = all_products.groupby('market').size().reset_index(name='count')
        fig6 = go.Figure(go.Pie(
            labels=mkt_df['market'], values=mkt_df['count'],
            hole=0.55, marker_colors=px.colors.qualitative.Set2
        ))
        fig6.update_layout(
            height=340, margin=dict(l=0,r=0,t=4,b=0),
            paper_bgcolor='white', font=dict(family="Segoe UI, sans-serif"),
            annotations=[dict(text=f"<b>{total_all}</b><br>รายการ", x=0.5, y=0.5,
                              font_size=16, showarrow=False)]
        )
        st.plotly_chart(fig6, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c7:
        st.markdown('<div class="chart-card"><div class="chart-card-title">🟦 ผลิตภัณฑ์ตามตลาด — สัดส่วน New vs Level Up</div>', unsafe_allow_html=True)
        nv = all_products[all_products['type']=='New'].groupby('market').size().reset_index(name='new')
        lv = all_products[all_products['type']=='Level Up'].groupby('market').size().reset_index(name='lv')
        mv = pd.merge(nv, lv, on='market', how='outer').fillna(0).sort_values('new', ascending=False)
        fig7 = go.Figure()
        fig7.add_bar(x=mv['market'], y=mv['new'], name="New",      marker_color="#2563eb")
        fig7.add_bar(x=mv['market'], y=mv['lv'],  name="Level Up", marker_color="#0d9488")
        fig7.update_layout(barmode="stack", height=340, margin=dict(l=0,r=0,t=4,b=0),
                           plot_bgcolor='white', paper_bgcolor='white',
                           legend=dict(orientation="h", y=1.12),
                           font=dict(family="Segoe UI, sans-serif"))
        st.plotly_chart(fig7, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════
# TAB 2 — ALL PRODUCTS
# ════════════════════════════════════════
with tab2:
    st.markdown(f"### 📦 สินค้าทั้งหมด — New: {total_new} | Level Up: {total_lv}")
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
        months_opt = ["ทั้งหมด"] + ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        sel_month = st.selectbox("เดือน", months_opt)

    filtered = all_products.copy()
    if sel_group  != "ทั้งหมด": filtered = filtered[filtered['group']  == sel_group]
    if sel_market != "ทั้งหมด": filtered = filtered[filtered['market'] == sel_market]
    if sel_month  != "ทั้งหมด": filtered = filtered[filtered['month']  == sel_month]
    if search:
        q = search.lower()
        filtered = filtered[
            filtered['name'].str.lower().str.contains(q, na=False) |
            filtered['group'].str.lower().str.contains(q, na=False) |
            filtered['code'].str.lower().str.contains(q, na=False)
        ]

    st.caption(f"แสดง {len(filtered)} รายการ")
    display_df = filtered[['no','month','name','group','market','type','cm','total_sales']].copy()
    display_df['cm'] = display_df['cm'].apply(lambda x: f"{x:.2f}%" if x > 0 else "-")
    display_df['total_sales'] = display_df['total_sales'].apply(lambda x: f"{x/1e6:.2f}M" if x > 0 else "-")
    display_df.columns = ['#','เดือน','ชื่อสินค้า','กลุ่มสินค้า','ตลาด','ประเภท','%CM','ยอดขายรวม']
    st.dataframe(display_df, use_container_width=True, height=500, hide_index=True)

    if len(filtered) > 0:
        st.markdown("---")
        st.markdown("**🔎 ดูรายละเอียดสินค้า**")
        sel_product = st.selectbox("เลือกสินค้า", filtered['name'].tolist())
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
                    st.markdown("**Quality & Cost**")
                    st.write(f"%αβ: {row['alpha']}%")
                    st.write(f"%Defect: {row['defect']}%")
                    st.write(f"%CM ใบขอรหัส: {row['cm_request']:.2f}%")
                    st.write(f"%CM เกิดจริง: {row['cm']:.2f}%" if row['cm'] > 0 else "%CM เกิดจริง: -")
                    st.write(f"Delay: {'⚠️ มี' if row['delay'] else '✅ ไม่มี'}")
                    total = row['total_sales']
                    st.write(f"ยอดขายรวม: {total/1e6:.2f}M บาท" if total > 0 else "ยอดขายรวม: -")
                if row['total_sales'] > 0:
                    fig_s = go.Figure(go.Bar(
                        x=['Jan','Feb','Mar','Apr'],
                        y=[max(0, row['sales_jan']), max(0, row['sales_feb']),
                           max(0, row['sales_mar']), max(0, row['sales_apr'])],
                        marker_color='#2563eb'
                    ))
                    fig_s.update_layout(title="ยอดขายรายเดือน (บาท)", height=200,
                                        margin=dict(l=0,r=0,t=30,b=0))
                    st.plotly_chart(fig_s, use_container_width=True)

# ════════════════════════════════════════
# TAB 3 — STOPPED PRODUCTS
# ════════════════════════════════════════
with tab3:
    export_count = len(stop_df[stop_df['market'] == 'Export'])
    non7_count   = len(stop_df[stop_df['market'] == 'non-7'])
    pma20_count  = len(stop_df[stop_df['market'] == 'PMA20'])

    # Filters
    mkt_filter = st.radio("Filter ตลาด", ["ทั้งหมด","Export","non-7","PMA20"], horizontal=True)
    stop_filtered = stop_df if mkt_filter == "ทั้งหมด" else stop_df[stop_df['market'] == mkt_filter]

    left_col, right_col = st.columns([5, 3])

    with left_col:
        # Market tag color map
        tag_map = {'Export':'tag-blue','non-7':'tag-amber','PMA20':'tag-gray'}
        month_tag = {'Jan':'tag-blue','Apr':'tag-red','May':'tag-amber'}

        # Build table HTML
        rows_html = ''
        for i, row in enumerate(stop_filtered.to_dict('records'), 1):
            mkt_cls = tag_map.get(row['market'], 'tag-gray')
            mon_cls = month_tag.get(row['month'], 'tag-gray')
            rows_html += f"""<tr>
              <td style="color:#94a3b8;font-size:0.75rem;">{i}</td>
              <td style="font-size:0.78rem;">{row['group']}</td>
              <td><span class="tag {mkt_cls}">{row['market']}</span></td>
              <td style="font-size:0.75rem;color:#64748b;">{row['customer']}</td>
              <td style="font-size:0.78rem;font-weight:500;">{row['name']}</td>
              <td><span class="tag {mon_cls}">{row['month']}</span></td>
              <td><span class="tag tag-red" style="white-space:nowrap;">ราคา RM สูง</span></td>
            </tr>"""

        st.markdown(f"""
        <div class="chart-card">
          <div class="chart-card-title">🔴 รายการสินค้าหยุดพัฒนานอกแผน</div>
          <div style="overflow-x:auto;max-height:480px;overflow-y:auto;">
            <table style="width:100%;border-collapse:collapse;font-size:0.78rem;">
              <thead>
                <tr style="background:#f1f5f9;position:sticky;top:0;">
                  <th style="padding:8px 10px;text-align:left;font-size:0.7rem;color:#475569;text-transform:uppercase;">#</th>
                  <th style="padding:8px 10px;text-align:left;font-size:0.7rem;color:#475569;text-transform:uppercase;">กลุ่มสินค้า</th>
                  <th style="padding:8px 10px;text-align:left;font-size:0.7rem;color:#475569;text-transform:uppercase;">ตลาด</th>
                  <th style="padding:8px 10px;text-align:left;font-size:0.7rem;color:#475569;text-transform:uppercase;">ลูกค้า</th>
                  <th style="padding:8px 10px;text-align:left;font-size:0.7rem;color:#475569;text-transform:uppercase;">ชื่อสินค้า</th>
                  <th style="padding:8px 10px;text-align:left;font-size:0.7rem;color:#475569;text-transform:uppercase;">เดือน</th>
                  <th style="padding:8px 10px;text-align:left;font-size:0.7rem;color:#475569;text-transform:uppercase;">สาเหตุหลัก</th>
                </tr>
              </thead>
              <tbody>{rows_html}</tbody>
            </table>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with right_col:
        sm = stop_df.groupby('month').size().reset_index(name='count')
        fig_sm = go.Figure(go.Pie(
            labels=[f"{r['month']} ({r['count']})" for _, r in sm.iterrows()],
            values=sm['count'],
            hole=0.5,
            marker_colors=['#93c5fd','#dc2626','#d97706']
        ))
        fig_sm.update_layout(height=220, margin=dict(l=0,r=0,t=4,b=0),
                             paper_bgcolor='white', font=dict(family="Segoe UI, sans-serif"),
                             legend=dict(orientation="v"))

        st.markdown(f"""
        <div class="chart-card">
          <div class="chart-card-title">🟠 สาเหตุการหยุดพัฒนา &amp; รายละเอียด</div>
          <div class="cause-box">
            <div class="ct">Mer / ลูกค้าขอยกเลิก</div>
            <div class="cn">{len(stop_df)} <span style="font-size:0.78rem;font-weight:600;">รายการ (100%)</span></div>
          </div>
          <div class="info-box">
            <div class="it">💰 ราคา RM สูง → ราคาขายสูง</div>
            <div class="id">เป็นสาเหตุหลักของสินค้าทั้ง {len(stop_df)} รายการ ทำให้ลูกค้าและ Mer ขอยกเลิกการพัฒนา</div>
          </div>
          <div style="font-size:0.77rem;font-weight:700;color:#334155;margin-bottom:8px;">ช่วงเวลาที่หยุด</div>
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(fig_sm, use_container_width=True)

# ════════════════════════════════════════
# TAB 4 — ADD NEW PRODUCT
# ════════════════════════════════════════
with tab4:
    st.markdown("### ➕ เพิ่มสินค้าใหม่")
    st.info("กรอกข้อมูลแล้วกด **บันทึก** ข้อมูลจะขึ้น Dashboard อัตโนมัติ")

    with st.form("add_form", clear_on_submit=True):
        r1, r2, r3 = st.columns(3)
        p_code   = r1.text_input("รหัสสินค้า *", placeholder="เช่น 90113400")
        p_name   = r2.text_input("ชื่อสินค้า *", placeholder="ชื่อสินค้า")
        p_group  = r3.selectbox("กลุ่มสินค้า *", GROUP_LIST)

        r4, r5, r6, r7 = st.columns(4)
        p_market  = r4.selectbox("ตลาด *", MARKET_LIST)
        p_quarter = r5.selectbox("ไตรมาส", ['Q1','Q2','Q3','Q4'])
        p_month   = r6.selectbox("เดือน *", MONTHS)
        p_type    = r7.selectbox("ประเภท *", ['New','Level Up'])

        st.markdown("**🧪 Quality**")
        q1, q2, q3, q4 = st.columns(4)
        p_alpha  = q1.number_input("%αβ",    0.0, 100.0, 100.0, 0.1)
        p_defect = q2.number_input("%Defect", 0.0, 100.0, 0.0,   0.01)
        p_cm     = q3.number_input("%CM",     0.0, 100.0, 0.0,   0.01)
        p_delay  = q4.checkbox("Delay Plan")

        st.markdown("**💰 ยอดขาย (บาท)**")
        s1c, s2c, s3c, s4c = st.columns(4)
        p_sjan = s1c.number_input("Jan", 0, step=1000)
        p_sfeb = s2c.number_input("Feb", 0, step=1000)
        p_smar = s3c.number_input("Mar", 0, step=1000)
        p_sapr = s4c.number_input("Apr", 0, step=1000)

        if st.form_submit_button("✅ บันทึกสินค้า", type="primary", use_container_width=True):
            if not p_code or not p_name:
                st.error("กรุณากรอก รหัสสินค้า และ ชื่อสินค้า")
            else:
                existing = st.session_state.extra_products
                all_nos = [p.get('no', 0) for p in BASE_PRODUCTS] + [p.get('no', 0) for p in existing]
                new_no = max(all_nos) + 1 if all_nos else 77
                entry = dict(
                    no=new_no, group=p_group, market=p_market,
                    quarter=p_quarter, month=p_month, code=p_code,
                    name=p_name, type=p_type, cm=p_cm,
                    cm_request=p_cm, alpha=p_alpha,
                    defect=p_defect, delay=p_delay,
                    sales_jan=p_sjan, sales_feb=p_sfeb,
                    sales_mar=p_smar, sales_apr=p_sapr,
                )
                st.session_state.extra_products.append(entry)
                save_extra(st.session_state.extra_products)
                st.success(f"✅ เพิ่ม **{p_name}** เรียบร้อย!")
                st.balloons()
                st.rerun()

    if st.session_state.extra_products:
        st.divider()
        st.markdown(f"**สินค้าที่เพิ่มมาแล้ว ({len(st.session_state.extra_products)} รายการ)**")
        ed = pd.DataFrame(st.session_state.extra_products)
        st.dataframe(
            ed[['no','month','name','group','market','type']].rename(columns={
                'no':'#','month':'เดือน','name':'ชื่อสินค้า',
                'group':'กลุ่มสินค้า','market':'ตลาด','type':'ประเภท'
            }),
            use_container_width=True, hide_index=True
        )
        if st.button("🗑️ ลบสินค้าที่เพิ่มทั้งหมด", type="secondary"):
            st.session_state.extra_products = []
            save_extra([])
            st.rerun()
