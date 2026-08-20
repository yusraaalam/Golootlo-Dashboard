import streamlit as st
import pandas as pd
import gdown
import os
from collections import Counter

# ── PAGE CONFIG ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Golootlo Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── PASSWORD PROTECTION ───────────────────────────────────────────────
def check_password():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("## 📊 Golootlo Analytics")
        st.markdown("Enter the password to access the dashboard.")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if pwd == "YusraAlam1515":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password.")
        st.stop()

check_password()

# ── STYLING ───────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  
  .main { background: #f8f9fa; }
  
  .metric-card {
    background: #ffffff;
    border: 1px solid #e8e8e8;
    border-radius: 10px;
    padding: 16px 20px;
    text-align: center;
  }
  .metric-value {
    font-size: 26px;
    font-weight: 700;
    color: #111;
    line-height: 1.2;
  }
  .metric-label {
    font-size: 11px;
    color: #888;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .metric-sub {
    font-size: 11px;
    color: #aaa;
    margin-top: 2px;
  }
  
  .section-title {
    font-size: 15px;
    font-weight: 700;
    color: #111;
    margin: 24px 0 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #e8e8e8;
  }
  
  .seg-champion  { color: #1a7a4a; font-weight: 700; }
  .seg-loyal     { color: #0a4a8a; font-weight: 700; }
  .seg-atrisk    { color: #b35900; font-weight: 700; }
  .seg-new       { color: #3a2a9a; font-weight: 700; }
  .seg-lost      { color: #8a1a1a; font-weight: 700; }
  
  .stSelectbox label { font-size: 12px; color: #555; }
  .stTextInput label { font-size: 12px; color: #555; }
  
  div[data-testid="metric-container"] {
    background: #fff;
    border: 1px solid #e8e8e8;
    border-radius: 10px;
    padding: 12px 16px;
  }
  
  .table-container {
    background: #fff;
    border: 1px solid #e8e8e8;
    border-radius: 10px;
    overflow: hidden;
    margin-bottom: 16px;
  }
  .table-header {
    padding: 10px 16px;
    border-bottom: 1px solid #eee;
    font-size: 13px;
    font-weight: 700;
    color: #111;
  }
  
  .customer-card {
    background: #fff;
    border: 1px solid #e8e8e8;
    border-radius: 10px;
    overflow: hidden;
    margin-bottom: 16px;
  }
  .customer-header {
    padding: 14px 18px;
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
</style>
""", unsafe_allow_html=True)

# ── DATA LOADING ──────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data():
    import requests

    files = {
        'scored':  ('1xmZY11y_M24-1RlGE0M-CDl9kLUi76TE', 'scored.csv'),
        'rfm':     ('1JfUQzr4_McBAHyYUko3rMbKuun70sV5N', 'rfm.csv'),
        'journey': ('17csRmvdOt8rn89Zx9zCclpyVoYIjqjXu', 'journey.csv'),
    }

    def download_file(file_id, fname):
        if os.path.exists(fname):
            return
        # Try gdown first
        try:
            gdown.download(
                f'https://drive.google.com/uc?id={file_id}&export=download&confirm=t',
                fname, quiet=True, fuzzy=True
            )
            if os.path.exists(fname) and os.path.getsize(fname) > 1000:
                return
        except Exception:
            pass
        # Fallback: requests with session
        try:
            session = requests.Session()
            url = f'https://drive.google.com/uc?id={file_id}&export=download'
            response = session.get(url, stream=True)
            token = None
            for key, value in response.cookies.items():
                if key.startswith('download_warning'):
                    token = value
            if token:
                url = f'{url}&confirm={token}'
                response = session.get(url, stream=True)
            with open(fname, 'wb') as f:
                for chunk in response.iter_content(32768):
                    if chunk:
                        f.write(chunk)
        except Exception as e:
            st.error(f"Failed to download {fname}: {e}")
            raise

    for key, (file_id, fname) in files.items():
        download_file(file_id, fname)

    scored  = pd.read_csv('scored.csv',  low_memory=False)
    rfm     = pd.read_csv('rfm.csv',     low_memory=False)
    journey = pd.read_csv('journey.csv', low_memory=False)

    scored['DATE'] = pd.to_datetime(scored['DATE'], errors='coerce')
    return scored, rfm, journey

with st.spinner("Loading Golootlo data..."):
    df, rfm, journey = load_data()

rs199_phones = set(rfm[rfm['IS_RS199'] == True]['MASTER_ID'].astype(str).tolist()) if 'IS_RS199' in rfm.columns else set()

# ── SEGMENT STYLING ───────────────────────────────────────────────────
SEG_COLORS = {
    'Champion': '#1a7a4a',
    'Loyal':    '#0a4a8a',
    'At Risk':  '#b35900',
    'New':      '#3a2a9a',
    'Lost':     '#8a1a1a',
}
CH_COLORS = {
    'Instore':  '#2E86AB',
    'Delivery': '#A23B72',
    'Ecom':     '#F18F01',
}

def seg_badge(seg):
    color = SEG_COLORS.get(seg, '#555')
    return f'<span style="color:{color};font-weight:700;">{seg}</span>'

# ── SIDEBAR ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 Golootlo Analytics")
    st.markdown("**Jan – Jul 2026**")
    st.markdown("---")

    page = st.radio("Navigate", [
        "Overview",
        "Segments",
        "Channel Journey",
        "Category Analysis",
        "City Analysis",
        "Brand Affinity",
        "Customer Lookup",
    ])

    st.markdown("---")
    st.markdown(f"**{df['MASTER_ID'].nunique():,}** customers")
    st.markdown(f"**{len(df):,}** transactions")
    st.markdown(f"**{df['BRAND_CLEAN'].nunique():,}** brands")

# ══════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ══════════════════════════════════════════════════════════════════════
if page == "Overview":
    st.markdown("## Platform Overview")
    st.markdown("Jan 1 – Jul 31, 2026")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Total Customers", f"{df['MASTER_ID'].nunique():,}")
    with c2:
        st.metric("Total Transactions", f"{len(df):,}")
    with c3:
        st.metric("Unique Brands", f"{df['BRAND_CLEAN'].nunique():,}")
    with c4:
        delivery_spend = df[df['CHANNEL'] == 'Delivery']['AMOUNT'].sum()
        st.metric("Total Delivery Spend", f"PKR {delivery_spend:,.0f}")
    with c5:
        st.metric("Rs.199 Users", f"{len(rs199_phones):,}")

    st.markdown('<div class="section-title">Channel Breakdown</div>', unsafe_allow_html=True)
    ch_data = df.groupby('CHANNEL').agg(
        Transactions=('MASTER_ID','count'),
        Customers=('MASTER_ID','nunique')
    ).reset_index().sort_values('Transactions', ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(ch_data, use_container_width=True, hide_index=True)
    with col2:
        seg_data = rfm['Segment'].value_counts().reset_index()
        seg_data.columns = ['Segment', 'Customers']
        seg_data['%'] = (seg_data['Customers'] / seg_data['Customers'].sum() * 100).round(1)
        st.dataframe(seg_data, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-title">Monthly Transaction Trend</div>', unsafe_allow_html=True)
    monthly = df.groupby(['YEAR','MONTH_NUM','MONTH_NAME']).size().reset_index(name='Transactions')
    monthly = monthly.sort_values(['YEAR','MONTH_NUM'])
    monthly['Month'] = monthly['MONTH_NAME'] + ' ' + monthly['YEAR'].astype(str)
    st.bar_chart(monthly.set_index('Month')['Transactions'])

# ══════════════════════════════════════════════════════════════════════
# PAGE: SEGMENTS
# ══════════════════════════════════════════════════════════════════════
elif page == "Segments":
    st.markdown("## Customer Segments")

    seg_info = {
        'Champion': ('Recent, frequent, highest spenders.',     'VIP perks, early access, reward them.'),
        'Loyal':    ('Come back regularly, decent engagement.', 'Personalised offers, keep them warm.'),
        'At Risk':  ('Were active, now going quiet.',           'Win-back urgently. Time-sensitive offer.'),
        'New':      ('First or second transaction only.',       'Nurture fast. Push second visit within 7 days.'),
        'Lost':     ('Inactive for months, very low frequency.','One reactivation push only. Then write off.'),
    }

    seg_counts = rfm['Segment'].value_counts()
    total = seg_counts.sum()

    rows_html = ''
    for seg, (who, action) in seg_info.items():
        count = int(seg_counts.get(seg, 0))
        pct   = round(count/total*100, 1)
        color = SEG_COLORS.get(seg, '#555')
        bar_w = int(pct * 2)
        rows_html += f'''<tr style="border-bottom:1px solid #f0f0f0;">
            <td style="padding:10px 14px;width:12%;">
              <span style="font-size:13px;font-weight:700;color:{color};">{seg}</span>
            </td>
            <td style="padding:10px 14px;width:22%;">
              <div style="display:flex;align-items:center;gap:8px;">
                <div style="width:{bar_w}px;height:7px;background:{color};border-radius:3px;opacity:0.7;min-width:3px;"></div>
                <span style="font-size:13px;font-weight:600;color:#111;">{count:,}</span>
                <span style="font-size:11px;color:#aaa;">({pct}%)</span>
              </div>
            </td>
            <td style="padding:10px 14px;font-size:12px;color:#555;width:30%;">{who}</td>
            <td style="padding:10px 14px;font-size:12px;color:#111;width:36%;">{action}</td>
        </tr>'''

    st.markdown(f'''
    <div style="background:#fff;border:1px solid #e8e8e8;border-radius:10px;overflow:hidden;">
      <div style="padding:10px 16px;border-bottom:1px solid #eee;">
        <span style="font-size:13px;font-weight:700;color:#111;">Customer Segments — Jan to Jul 2026</span>
        <span style="font-size:11px;color:#aaa;margin-left:8px;">{total:,} total customers</span>
      </div>
      <table style="width:100%;border-collapse:collapse;font-family:Inter,sans-serif;">
        <thead>
          <tr style="background:#fafafa;border-bottom:1px solid #eee;">
            <th style="padding:8px 14px;text-align:left;font-size:11px;color:#888;font-weight:600;">SEGMENT</th>
            <th style="padding:8px 14px;text-align:left;font-size:11px;color:#888;font-weight:600;">COUNT</th>
            <th style="padding:8px 14px;text-align:left;font-size:11px;color:#888;font-weight:600;">WHO THEY ARE</th>
            <th style="padding:8px 14px;text-align:left;font-size:11px;color:#888;font-weight:600;">WHAT TO DO</th>
          </tr>
        </thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>''', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Channel Breakdown by Segment</div>', unsafe_allow_html=True)

    df_seg = df.merge(rfm[['MASTER_ID','Segment']], on='MASTER_ID', how='left')
    ch_seg = df_seg.groupby(['Segment','CHANNEL']).size().unstack(fill_value=0)
    ch_seg['Total'] = ch_seg.sum(axis=1)
    ch_pct = ch_seg.div(ch_seg['Total'], axis=0).drop(columns='Total') * 100
    ch_pct = ch_pct.round(1)

    channels = [c for c in ch_seg.columns if c != 'Total']
    rows2 = ''
    for seg in ch_seg.index:
        color = SEG_COLORS.get(seg, '#555')
        cells = ''
        total_seg = int(ch_seg.loc[seg,'Total'])
        for ch in channels:
            count = int(ch_seg.loc[seg, ch]) if ch in ch_seg.columns else 0
            pct   = float(ch_pct.loc[seg, ch]) if ch in ch_pct.columns else 0
            cells += f'<td style="padding:7px 12px;text-align:center;font-size:12px;color:#111;"><b>{count:,}</b> <span style="color:#aaa;font-size:11px;">({pct}%)</span></td>'
        rows2 += f'''<tr style="border-bottom:1px solid #f0f0f0;">
            <td style="padding:7px 12px;font-weight:700;color:{color};font-size:13px;">{seg}</td>
            {cells}
            <td style="padding:7px 12px;text-align:center;font-weight:700;font-size:12px;">{total_seg:,}</td>
        </tr>'''

    header_cols = ''.join([f'<th style="padding:7px 12px;text-align:center;font-size:11px;color:#888;font-weight:600;">{c.upper()}</th>' for c in channels])
    st.markdown(f'''
    <div style="background:#fff;border:1px solid #e8e8e8;border-radius:10px;overflow:hidden;">
      <table style="width:100%;border-collapse:collapse;font-family:Inter,sans-serif;">
        <thead>
          <tr style="background:#fafafa;border-bottom:1px solid #eee;">
            <th style="padding:7px 12px;text-align:left;font-size:11px;color:#888;font-weight:600;">SEGMENT</th>
            {header_cols}
            <th style="padding:7px 12px;text-align:center;font-size:11px;color:#888;font-weight:600;">TOTAL</th>
          </tr>
        </thead>
        <tbody>{rows2}</tbody>
      </table>
    </div>''', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# PAGE: CHANNEL JOURNEY
# ══════════════════════════════════════════════════════════════════════
elif page == "Channel Journey":
    st.markdown("## Channel Journey")

    j_counts = journey['Channel_Journey'].value_counts().reset_index()
    j_counts.columns = ['Journey Path','Customers']
    j_counts['%'] = (j_counts['Customers'] / j_counts['Customers'].sum() * 100).round(1)

    def classify(p):
        if '→' not in str(p): return 'Single Channel', '#888'
        elif str(p).count('→') == 1: return 'Two Channel', '#0a4a8a'
        else: return 'Full Multichannel', '#1a7a4a'

    j_counts['Type']  = j_counts['Journey Path'].apply(lambda x: classify(x)[0])
    j_counts['Color'] = j_counts['Journey Path'].apply(lambda x: classify(x)[1])

    total = j_counts['Customers'].sum()
    single = j_counts[j_counts['Type']=='Single Channel']['Customers'].sum()
    two    = j_counts[j_counts['Type']=='Two Channel']['Customers'].sum()
    multi  = j_counts[j_counts['Type']=='Full Multichannel']['Customers'].sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Customers", f"{total:,}")
    c2.metric("Single Channel", f"{single:,}")
    c3.metric("Two Channel", f"{two:,}")
    c4.metric("Full Multichannel", f"{multi:,}")

    max_c = j_counts['Customers'].max()
    rows = ''
    for _, row in j_counts.iterrows():
        bar_w = int((row['Customers']/max_c)*80)
        rows += f'''<tr style="border-bottom:1px solid #f0f0f0;">
            <td style="padding:7px 14px;font-size:13px;color:#111;font-weight:500;">{row["Journey Path"]}</td>
            <td style="padding:7px 14px;">
              <div style="display:flex;align-items:center;gap:8px;">
                <div style="width:{bar_w}px;min-width:2px;height:7px;background:#2E86AB;border-radius:3px;opacity:0.6;"></div>
                <span style="font-size:13px;font-weight:600;color:#111;">{int(row["Customers"]):,}</span>
                <span style="font-size:11px;color:#aaa;">({row["%"]}%)</span>
              </div>
            </td>
            <td style="padding:7px 14px;font-size:12px;font-weight:600;color:{row["Color"]};">{row["Type"]}</td>
        </tr>'''

    st.markdown(f'''
    <div style="background:#fff;border:1px solid #e8e8e8;border-radius:10px;overflow:hidden;max-width:700px;">
      <div style="padding:10px 16px;border-bottom:1px solid #eee;">
        <span style="font-size:13px;font-weight:700;color:#111;">Channel Journey Paths</span>
      </div>
      <table style="width:100%;border-collapse:collapse;font-family:Inter,sans-serif;">
        <thead><tr style="background:#fafafa;border-bottom:1px solid #eee;">
          <th style="padding:7px 14px;text-align:left;font-size:11px;color:#888;font-weight:600;">PATH</th>
          <th style="padding:7px 14px;text-align:left;font-size:11px;color:#888;font-weight:600;">CUSTOMERS</th>
          <th style="padding:7px 14px;text-align:left;font-size:11px;color:#888;font-weight:600;">TYPE</th>
        </tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>''', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# PAGE: CATEGORY ANALYSIS
# ══════════════════════════════════════════════════════════════════════
elif page == "Category Analysis":
    st.markdown("## Category Analysis")

    df_cat = df.merge(rfm[['MASTER_ID','Segment']], on='MASTER_ID', how='left')

    def clean_cat(cat):
        cat = str(cat).strip()
        if 'GOLOOTLO EXCLUSIVE' in cat.upper(): return 'Golootlo Exclusive'
        if any(x in cat.upper() for x in ['CLASSIC PIZZA','DELUXE PIZZA','PREMIUM PIZZA']): return 'Food'
        if 'RAMADAN' in cat.upper(): return 'Golootlo Exclusive'
        return cat

    if 'CATEGORY_CLEAN' not in df_cat.columns:
        df_cat['CATEGORY_CLEAN'] = df_cat['CATEGORY'].apply(clean_cat)

    cat_total = df_cat.groupby('CATEGORY_CLEAN').agg(
        Transactions=('MASTER_ID','count'),
        Customers=('MASTER_ID','nunique'),
        Top_Segment=('Segment', lambda x: x.value_counts().index[0] if x.notna().any() else '—')
    ).reset_index()

    cat_ch = df_cat.groupby(['CATEGORY_CLEAN','CHANNEL']).agg(
        C=('MASTER_ID','nunique')
    ).reset_index().pivot_table(
        index='CATEGORY_CLEAN', columns='CHANNEL', values='C', fill_value=0
    ).reset_index()

    cat_total = cat_total.merge(cat_ch, on='CATEGORY_CLEAN', how='left')
    for ch in ['Instore','Delivery','Ecom']:
        if ch not in cat_total.columns: cat_total[ch] = 0

    cat_total = cat_total[
        cat_total['CATEGORY_CLEAN'].notna() &
        (cat_total['CATEGORY_CLEAN'].astype(str).str.strip() != '')
    ].sort_values('Transactions', ascending=False).head(12).reset_index(drop=True)
    cat_total['% Share'] = (cat_total['Transactions']/cat_total['Transactions'].sum()*100).round(1)

    rows = ''
    for _, row in cat_total.iterrows():
        seg_color = SEG_COLORS.get(row['Top_Segment'], '#555')
        ins  = int(row.get('Instore', 0))
        dlv  = int(row.get('Delivery', 0))
        eco  = int(row.get('Ecom', 0))
        tot  = ins + dlv + eco or 1

        def bar(val, color):
            w = int(val/tot*50)
            p = round(val/tot*100)
            return f'<div style="display:flex;align-items:center;gap:3px;margin-bottom:2px;"><div style="width:{w}px;min-width:2px;height:5px;background:{color};border-radius:2px;"></div><span style="font-size:10px;color:#888;">{val:,} ({p}%)</span></div>'

        brands = df_cat[(df_cat['CATEGORY_CLEAN']==row['CATEGORY_CLEAN']) & df_cat['BRAND_CLEAN'].notna()]['BRAND_CLEAN'].value_counts().head(4)
        brand_str = ' · '.join(brands.index.tolist()) if len(brands) > 0 else '—'

        rows += f'''<tr style="border-bottom:1px solid #f0f0f0;vertical-align:top;">
            <td style="padding:8px 12px;">
              <div style="font-size:13px;font-weight:700;color:#111;">{row["CATEGORY_CLEAN"]}</div>
              <div style="font-size:10px;color:#aaa;">{row["% Share"]}% share</div>
            </td>
            <td style="padding:8px 12px;text-align:center;">
              <div style="font-size:14px;font-weight:700;color:#111;">{int(row["Customers"]):,}</div>
              <div style="font-size:10px;color:#aaa;">{int(row["Transactions"]):,} tx</div>
            </td>
            <td style="padding:8px 12px;font-size:12px;font-weight:600;color:{seg_color};text-align:center;">{row["Top_Segment"]}</td>
            <td style="padding:8px 12px;">{bar(ins,"#2E86AB")}{bar(dlv,"#A23B72")}{bar(eco,"#F18F01")}</td>
            <td style="padding:8px 12px;font-size:11px;color:#555;">{brand_str}</td>
        </tr>'''

    st.markdown(f'''
    <div style="background:#fff;border:1px solid #e8e8e8;border-radius:10px;overflow:hidden;">
      <div style="padding:10px 16px;border-bottom:1px solid #eee;display:flex;justify-content:space-between;">
        <span style="font-size:13px;font-weight:700;color:#111;">Top 12 Categories</span>
        <span style="font-size:11px;color:#aaa;">
          <span style="color:#2E86AB;">■</span> Instore &nbsp;
          <span style="color:#A23B72;">■</span> Delivery &nbsp;
          <span style="color:#F18F01;">■</span> Ecom
        </span>
      </div>
      <table style="width:100%;border-collapse:collapse;font-family:Inter,sans-serif;">
        <thead><tr style="background:#fafafa;border-bottom:1px solid #eee;">
          <th style="padding:7px 12px;text-align:left;font-size:11px;color:#888;font-weight:600;">CATEGORY</th>
          <th style="padding:7px 12px;text-align:center;font-size:11px;color:#888;font-weight:600;">CUSTOMERS</th>
          <th style="padding:7px 12px;text-align:center;font-size:11px;color:#888;font-weight:600;">TOP SEGMENT</th>
          <th style="padding:7px 12px;text-align:left;font-size:11px;color:#888;font-weight:600;">CHANNEL SPLIT</th>
          <th style="padding:7px 12px;text-align:left;font-size:11px;color:#888;font-weight:600;">TOP BRANDS</th>
        </tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>''', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# PAGE: CITY ANALYSIS
# ══════════════════════════════════════════════════════════════════════
elif page == "City Analysis":
    st.markdown("## City Analysis")

    df_city = df.merge(rfm[['MASTER_ID','Segment']], on='MASTER_ID', how='left')

    city_total = df_city.groupby('CITY').agg(
        Transactions=('MASTER_ID','count'),
        Customers=('MASTER_ID','nunique'),
        Top_Channel=('CHANNEL', lambda x: x.value_counts().index[0]),
        Top_Segment=('Segment', lambda x: x.value_counts().index[0] if x.notna().any() else '—')
    ).reset_index()

    city_ch = df_city.groupby(['CITY','CHANNEL']).agg(
        C=('MASTER_ID','nunique')
    ).reset_index().pivot_table(
        index='CITY', columns='CHANNEL', values='C', fill_value=0
    ).reset_index()

    city_total = city_total.merge(city_ch, on='CITY', how='left')
    for ch in ['Instore','Delivery','Ecom']:
        if ch not in city_total.columns: city_total[ch] = 0

    city_total = city_total[
        city_total['CITY'].notna() &
        (city_total['CITY'].astype(str).str.strip() != '') &
        (city_total['CITY'].astype(str).str.strip() != '--')
    ].sort_values('Customers', ascending=False).head(15).reset_index(drop=True)
    city_total['% Share'] = (city_total['Transactions']/city_total['Transactions'].sum()*100).round(1)

    rows = ''
    for _, row in city_total.iterrows():
        seg_color = SEG_COLORS.get(row['Top_Segment'], '#555')
        ch_color  = CH_COLORS.get(row['Top_Channel'], '#555')
        ins  = int(row.get('Instore', 0))
        dlv  = int(row.get('Delivery', 0))
        eco  = int(row.get('Ecom', 0))
        tot  = ins + dlv + eco or 1

        def bar(val, color):
            w = int(val/tot*50)
            p = round(val/tot*100)
            return f'<div style="display:flex;align-items:center;gap:3px;margin-bottom:2px;"><div style="width:{w}px;min-width:2px;height:5px;background:{color};border-radius:2px;"></div><span style="font-size:10px;color:#888;">{val:,} ({p}%)</span></div>'

        rows += f'''<tr style="border-bottom:1px solid #f0f0f0;">
            <td style="padding:8px 12px;">
              <div style="font-size:13px;font-weight:700;color:#111;">{row["CITY"]}</div>
              <div style="font-size:10px;color:#aaa;">{row["% Share"]}% of transactions</div>
            </td>
            <td style="padding:8px 12px;text-align:center;">
              <div style="font-size:14px;font-weight:700;color:#111;">{int(row["Customers"]):,}</div>
              <div style="font-size:10px;color:#aaa;">{int(row["Transactions"]):,} tx</div>
            </td>
            <td style="padding:8px 12px;font-size:12px;font-weight:600;color:{ch_color};text-align:center;">{row["Top_Channel"]}</td>
            <td style="padding:8px 12px;font-size:12px;font-weight:600;color:{seg_color};text-align:center;">{row["Top_Segment"]}</td>
            <td style="padding:8px 12px;">{bar(ins,"#2E86AB")}{bar(dlv,"#A23B72")}{bar(eco,"#F18F01")}</td>
        </tr>'''

    st.markdown(f'''
    <div style="background:#fff;border:1px solid #e8e8e8;border-radius:10px;overflow:hidden;">
      <div style="padding:10px 16px;border-bottom:1px solid #eee;display:flex;justify-content:space-between;">
        <span style="font-size:13px;font-weight:700;color:#111;">Top 15 Cities</span>
        <span style="font-size:11px;color:#aaa;">
          <span style="color:#2E86AB;">■</span> Instore &nbsp;
          <span style="color:#A23B72;">■</span> Delivery &nbsp;
          <span style="color:#F18F01;">■</span> Ecom
        </span>
      </div>
      <table style="width:100%;border-collapse:collapse;font-family:Inter,sans-serif;">
        <thead><tr style="background:#fafafa;border-bottom:1px solid #eee;">
          <th style="padding:7px 12px;text-align:left;font-size:11px;color:#888;font-weight:600;">CITY</th>
          <th style="padding:7px 12px;text-align:center;font-size:11px;color:#888;font-weight:600;">CUSTOMERS</th>
          <th style="padding:7px 12px;text-align:center;font-size:11px;color:#888;font-weight:600;">TOP CHANNEL</th>
          <th style="padding:7px 12px;text-align:center;font-size:11px;color:#888;font-weight:600;">TOP SEGMENT</th>
          <th style="padding:7px 12px;text-align:left;font-size:11px;color:#888;font-weight:600;">CHANNEL SPLIT</th>
        </tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>''', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# PAGE: BRAND AFFINITY
# ══════════════════════════════════════════════════════════════════════
elif page == "Brand Affinity":
    st.markdown("## Brand Affinity")

    top_brands = df['BRAND_CLEAN'].value_counts().dropna().head(25).index.tolist()
    selected_brand = st.selectbox("Select Brand", top_brands)

    brand_users = set(df[df['BRAND_CLEAN'] == selected_brand]['MASTER_ID'].unique())

    also_use = df[
        (df['MASTER_ID'].isin(brand_users)) &
        (df['BRAND_CLEAN'] != selected_brand) &
        (df['BRAND_CLEAN'].notna())
    ]['BRAND_CLEAN'].value_counts().head(5).reset_index()
    also_use.columns = ['Brand','Users']

    user_tx_map = (
        df[df['BRAND_CLEAN'].notna()]
        .sort_values('DATE')
        .groupby('MASTER_ID')['BRAND_CLEAN']
        .apply(list)
        .to_dict()
    )

    next_brands = []
    for user in brand_users:
        tx = user_tx_map.get(user, [])
        if selected_brand in tx:
            idx = tx.index(selected_brand)
            for b in tx[idx+1:]:
                if b != selected_brand:
                    next_brands.append(b)
                    break

    next_df = pd.DataFrame(Counter(next_brands).most_common(5), columns=['Brand','Users'])
    next_df['%'] = (next_df['Users']/len(brand_users)*100).round(1)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Customers", f"{len(brand_users):,}")
    c2.metric("Also Use Another Brand", f"{also_use['Users'].iloc[0]:,}" if len(also_use) > 0 else "—")
    c3.metric("Move to Another Brand Next", f"{next_df['Users'].iloc[0]:,}" if len(next_df) > 0 else "—")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Customers Also Use**")
        st.dataframe(also_use, use_container_width=True, hide_index=True)
    with col2:
        st.markdown("**Next Brand After First Visit**")
        st.dataframe(next_df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════
# PAGE: CUSTOMER LOOKUP
# ══════════════════════════════════════════════════════════════════════
elif page == "Customer Lookup":
    st.markdown("## Customer Lookup")

    phone = st.text_input("Enter phone number or user ID", placeholder="e.g. 3001234567")

    if phone:
        phone = str(phone).strip()
        customer_df = df[
            (df['PHONE'].astype(str).str.strip() == phone) |
            (df['MASTER_ID'].astype(str).str.strip() == phone)
        ].copy().sort_values('DATE')

        if len(customer_df) == 0:
            st.warning(f"No customer found for: {phone}")
        else:
            master_id   = str(customer_df['MASTER_ID'].iloc[0]).strip()
            rfm_row     = rfm[rfm['MASTER_ID'] == master_id]
            journey_row = journey[journey['MASTER_ID'] == master_id]
            is_rs199    = master_id in rs199_phones

            segment   = rfm_row['Segment'].values[0] if not rfm_row.empty else '—'
            recency   = int(rfm_row['Recency'].values[0]) if not rfm_row.empty else '—'
            frequency = int(rfm_row['Frequency'].values[0]) if not rfm_row.empty else '—'
            monetary  = float(rfm_row['Monetary'].values[0]) if not rfm_row.empty else 0
            r_score   = int(rfm_row['R_Score'].values[0]) if not rfm_row.empty else '—'
            f_score   = int(rfm_row['F_Score'].values[0]) if not rfm_row.empty else '—'
            m_score   = int(rfm_row['M_Score'].values[0]) if not rfm_row.empty else '—'
            ch_journey  = journey_row['Channel_Journey'].values[0] if not journey_row.empty else '—'
            cat_journey = journey_row['Category_Journey'].values[0] if not journey_row.empty else '—'
            top_brand   = journey_row['Top_Brand'].values[0] if not journey_row.empty else '—'
            top_cat     = journey_row['Top_Category'].values[0] if not journey_row.empty else '—'
            name        = str(customer_df['CUSTOMER_NAME'].dropna().iloc[0]) if not customer_df['CUSTOMER_NAME'].dropna().empty else '—'
            city        = str(customer_df['CITY'].dropna().iloc[0]) if not customer_df['CITY'].dropna().empty else '—'
            first_date  = customer_df['DATE'].min().strftime('%d %b %Y')
            last_date   = customer_df['DATE'].max().strftime('%d %b %Y')
            seg_color   = SEG_COLORS.get(segment, '#555')
            rs199_badge = '🟡 Rs.199 User' if is_rs199 else ''

            st.markdown(f'''
            <div style="background:#fff;border:1px solid #e8e8e8;border-radius:10px;overflow:hidden;margin-bottom:16px;">
              <div style="padding:14px 18px;border-bottom:1px solid #eee;display:flex;justify-content:space-between;align-items:center;">
                <div>
                  <span style="font-size:16px;font-weight:700;color:#111;">{name}</span>
                  <span style="font-size:12px;color:#888;margin-left:8px;">{phone} · {city}</span>
                  <span style="font-size:12px;color:#856404;margin-left:8px;">{rs199_badge}</span>
                </div>
                <span style="font-size:15px;font-weight:700;color:{seg_color};">{segment}</span>
              </div>
              <div style="display:flex;border-bottom:1px solid #eee;">
                <div style="flex:1;padding:12px 16px;border-right:1px solid #eee;text-align:center;">
                  <div style="font-size:20px;font-weight:700;color:#111;">{recency}d</div>
                  <div style="font-size:10px;color:#888;">Days Since Last Visit</div>
                  <div style="font-size:10px;color:#aaa;">R Score: {r_score}/5</div>
                </div>
                <div style="flex:1;padding:12px 16px;border-right:1px solid #eee;text-align:center;">
                  <div style="font-size:20px;font-weight:700;color:#111;">{frequency}</div>
                  <div style="font-size:10px;color:#888;">Total Transactions</div>
                  <div style="font-size:10px;color:#aaa;">F Score: {f_score}/5</div>
                </div>
                <div style="flex:1;padding:12px 16px;border-right:1px solid #eee;text-align:center;">
                  <div style="font-size:20px;font-weight:700;color:#111;">PKR {int(monetary):,}</div>
                  <div style="font-size:10px;color:#888;">Total Delivery Spend</div>
                  <div style="font-size:10px;color:#aaa;">M Score: {m_score}/5</div>
                </div>
                <div style="flex:1;padding:12px 16px;border-right:1px solid #eee;text-align:center;">
                  <div style="font-size:14px;font-weight:600;color:#111;">{top_brand}</div>
                  <div style="font-size:10px;color:#888;">Favourite Brand</div>
                  <div style="font-size:10px;color:#aaa;">{top_cat}</div>
                </div>
                <div style="flex:1;padding:12px 16px;text-align:center;">
                  <div style="font-size:12px;font-weight:600;color:#111;">{first_date}</div>
                  <div style="font-size:10px;color:#888;">First Seen</div>
                  <div style="font-size:12px;font-weight:600;color:#111;margin-top:6px;">{last_date}</div>
                  <div style="font-size:10px;color:#888;">Last Seen</div>
                </div>
              </div>
              <div style="display:flex;border-bottom:1px solid #eee;">
                <div style="flex:1;padding:8px 16px;border-right:1px solid #eee;">
                  <span style="font-size:10px;color:#888;">CHANNEL JOURNEY: </span>
                  <span style="font-size:12px;color:#111;font-weight:500;">{ch_journey}</span>
                </div>
                <div style="flex:1;padding:8px 16px;">
                  <span style="font-size:10px;color:#888;">CATEGORY JOURNEY: </span>
                  <span style="font-size:12px;color:#111;font-weight:500;">{str(cat_journey)[:70]}</span>
                </div>
              </div>
            </div>''', unsafe_allow_html=True)

            st.markdown("**Last 10 Transactions**")
            tx_display = customer_df[['DATE','CHANNEL','BRAND_CLEAN','CATEGORY_CLEAN','AMOUNT']].tail(10).iloc[::-1].copy()
            tx_display['DATE'] = tx_display['DATE'].dt.strftime('%d %b %Y')
            tx_display['AMOUNT'] = tx_display['AMOUNT'].apply(lambda x: f"PKR {int(x):,}" if pd.notna(x) and x > 0 else '—')
            tx_display.columns = ['Date','Channel','Brand','Category','Amount']
            st.dataframe(tx_display, use_container_width=True, hide_index=True)
