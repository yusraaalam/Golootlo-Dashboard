import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Golootlo Analytics", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

def check_password():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("### 📊 Golootlo Analytics")
            st.markdown("<p style='color:#888;font-size:13px;'>Enter your password to continue</p>", unsafe_allow_html=True)
            pwd = st.text_input("", type="password", placeholder="Password")
            if st.button("Continue", use_container_width=True):
                if pwd == "YusraAlam1515":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Incorrect password.")
        st.stop()

check_password()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.main { background: #ffffff !important; }
section[data-testid="stSidebar"] { background: #f7f7f5 !important; border-right: 1px solid #e8e8e4; }
section[data-testid="stSidebar"] * { color: #37352f !important; }
.block-container { padding: 2rem 2.5rem !important; background: #ffffff; }
h1,h2,h3 { color: #37352f !important; font-weight: 600 !important; letter-spacing: -0.02em !important; }
.stRadio label { font-size: 13px !important; color: #6b6b6b !important; }
.stSelectbox label, .stMultiSelect label { font-size: 12px !important; color: #9b9b9b !important; text-transform: uppercase; letter-spacing: .05em; }
div[data-testid="metric-container"] { background: #f7f7f5 !important; border: 1px solid #e8e8e4 !important; border-radius: 8px !important; padding: 16px 20px !important; }
div[data-testid="metric-container"] label { font-size: 12px !important; color: #9b9b9b !important; text-transform: uppercase; letter-spacing: .05em; }
div[data-testid="metric-container"] div[data-testid="stMetricValue"] { font-size: 22px !important; font-weight: 600 !important; color: #37352f !important; }
.stDataFrame { border: 1px solid #e8e8e4 !important; border-radius: 8px !important; }
div[data-testid="stDataFrame"] th { background: #f7f7f5 !important; color: #9b9b9b !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: .05em; font-weight: 500 !important; }
.notion-divider { height: 1px; background: #e8e8e4; margin: 1.5rem 0; }
.notion-caption { font-size: 12px; color: #9b9b9b; margin-bottom: 1rem; }
.notion-section { font-size: 11px; color: #9b9b9b; text-transform: uppercase; letter-spacing: .08em; font-weight: 500; margin: 1.5rem 0 .75rem; }
.notion-card { background: #f7f7f5; border: 1px solid #e8e8e4; border-radius: 8px; padding: 16px 20px; }
.winner-card { background: #f0faf5; border: 1.5px solid #1a7a4a; border-radius: 10px; padding: 20px 24px; margin-bottom: 1.5rem; }
.winner-brand { font-size: 26px; font-weight: 600; color: #37352f; margin: 6px 0 12px; }
.winner-label { font-size: 11px; color: #1a7a4a; text-transform: uppercase; letter-spacing: .08em; font-weight: 500; }
.winner-stat { text-align: center; }
.winner-stat-val { font-size: 22px; font-weight: 600; }
.winner-stat-lab { font-size: 11px; color: #9b9b9b; margin-top: 2px; }
.seg-pill { display: inline-block; padding: 2px 10px; border-radius: 4px; font-size: 12px; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

DB_URL = "postgresql+psycopg2://postgres.sbhvdjuxasqkjrxdvmcy:YusraAlam1515@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"

@st.cache_resource
def get_engine():
    return create_engine(DB_URL, connect_args={"sslmode": "require"})

@st.cache_data(show_spinner="Loading data...")
def load_data():
    engine = get_engine()
    df       = pd.read_sql("SELECT * FROM scored",       engine)
    rfm      = pd.read_sql("SELECT * FROM rfm",          engine)
    journey  = pd.read_sql("SELECT * FROM journey",      engine)
    bc       = pd.read_sql("SELECT * FROM brand_city",   engine)
    rs199p   = pd.read_sql("SELECT * FROM rs199_products", engine)
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
    return df, rfm, journey, bc, rs199p

df, rfm, journey, brand_city, rs199_prod = load_data()

rs199_phones = set(rfm[rfm['IS_RS199']==True]['MASTER_ID'].astype(str)) if 'IS_RS199' in rfm.columns else set()

SEG_COLORS = {'Champion':'#1a7a4a','Loyal':'#0a4a8a','At Risk':'#b35900','New':'#3a2a9a','Lost':'#8a1a1a'}
SEG_BG     = {'Champion':'#f0faf5','Loyal':'#f0f5ff','At Risk':'#fff8f0','New':'#f5f0ff','Lost':'#fff0f0'}
CH_COLORS  = {'Instore':'#2E86AB','Delivery':'#A23B72','Ecom':'#F18F01'}
SUB_COLORS = {'Pizza':'#2E86AB','Burger':'#A23B72','Juices & Beverages':'#F18F01','Coffee':'#1a7a4a','Bakery & Desserts':'#b35900','Ice Cream':'#3a2a9a'}

PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter', color='#37352f', size=12),
    margin=dict(t=20, b=20, l=10, r=10),
    showlegend=True,
    legend=dict(font=dict(size=11), bgcolor='rgba(0,0,0,0)'),
    xaxis=dict(showgrid=True, gridcolor='#f0f0ee', zeroline=False, tickfont=dict(size=11)),
    yaxis=dict(showgrid=True, gridcolor='#f0f0ee', zeroline=False, tickfont=dict(size=11)),
)

def notion_chart(fig, height=300):
    fig.update_layout(**PLOTLY_LAYOUT, height=height)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with st.sidebar:
    st.markdown("### 📊 Golootlo")
    st.markdown("<p class='notion-caption'>Jan – Jul 2026</p>", unsafe_allow_html=True)
    st.markdown("<div class='notion-divider'></div>", unsafe_allow_html=True)
    page = st.radio("", [
        "Overview", "Segments", "Channel Journey",
        "Category Analysis", "City Analysis",
        "Brand Affinity", "Product Affinity",
        "Next Campaign Recommender", "Customer Lookup"
    ], label_visibility="collapsed")
    st.markdown("<div class='notion-divider'></div>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:12px;color:#9b9b9b;'>{df['MASTER_ID'].nunique():,} customers<br>{len(df):,} transactions<br>{df['BRAND_CLEAN'].nunique():,} brands</p>", unsafe_allow_html=True)

# ── OVERVIEW ──────────────────────────────────────────────────────────
if page == "Overview":
    st.markdown("## Platform overview")
    st.markdown("<p class='notion-caption'>Jan 1 – Jul 31, 2026</p>", unsafe_allow_html=True)

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Customers",    f"{df['MASTER_ID'].nunique():,}")
    c2.metric("Transactions", f"{len(df):,}")
    c3.metric("Brands",       f"{df['BRAND_CLEAN'].nunique():,}")
    c4.metric("Delivery spend", f"PKR {df[df['CHANNEL']=='Delivery']['AMOUNT'].sum():,.0f}")
    c5.metric("Rs.199 users", f"{len(rs199_phones):,}")

    st.markdown("<div class='notion-section'>Channel & segments</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        ch = df.groupby('CHANNEL').agg(Customers=('MASTER_ID','nunique')).reset_index()
        fig = px.pie(ch, names='CHANNEL', values='Customers', color='CHANNEL',
                     color_discrete_map=CH_COLORS, hole=0.55)
        fig.update_traces(textposition='outside', textfont_size=11)
        notion_chart(fig, 260)

    with col2:
        seg = rfm['Segment'].value_counts().reset_index()
        seg.columns = ['Segment','Customers']
        fig2 = px.bar(seg.sort_values('Customers'), x='Customers', y='Segment',
                      orientation='h', color='Segment', color_discrete_map=SEG_COLORS)
        fig2.update_traces(marker_line_width=0)
        notion_chart(fig2, 260)

    st.markdown("<div class='notion-section'>Monthly trend</div>", unsafe_allow_html=True)
    col3, col4 = st.columns([2,1])

    with col3:
        monthly = df.groupby(['YEAR','MONTH_NUM','MONTH_NAME']).size().reset_index(name='Transactions')
        monthly = monthly.sort_values(['YEAR','MONTH_NUM'])
        monthly['Month'] = monthly['MONTH_NAME'].str[:3]
        ch_monthly = df.groupby(['YEAR','MONTH_NUM','CHANNEL']).size().reset_index(name='Count')
        ch_monthly['Month'] = ch_monthly['MONTH_NAME'] if 'MONTH_NAME' in ch_monthly.columns else ch_monthly['MONTH_NUM'].astype(str)
        fig3 = px.line(monthly, x='Month', y='Transactions', markers=True,
                       color_discrete_sequence=['#2E86AB'], line_shape='spline')
        fig3.update_traces(line_width=2, marker_size=6)
        notion_chart(fig3, 240)

    with col4:
        top5 = df['BRAND_CLEAN'].value_counts().dropna().head(5).reset_index()
        top5.columns = ['Brand','Transactions']
        fig4 = px.bar(top5.sort_values('Transactions'), x='Transactions', y='Brand',
                      orientation='h', color_discrete_sequence=['#2E86AB'])
        fig4.update_traces(marker_line_width=0)
        notion_chart(fig4, 240)

# ── SEGMENTS ──────────────────────────────────────────────────────────
elif page == "Segments":
    st.markdown("## Customer segments")

    seg_options = ["All"] + list(SEG_COLORS.keys())
    seg_filter = st.selectbox("Segment", seg_options)

    seg_info = {
        'Champion': ('Recent, frequent, highest spenders.', 'VIP perks, early access, reward them.'),
        'Loyal':    ('Come back regularly, decent engagement.', 'Personalised offers, keep them warm.'),
        'At Risk':  ('Were active, now going quiet.', 'Win-back urgently. Time-sensitive offer.'),
        'New':      ('First or second transaction only.', 'Nurture fast. Push second visit within 7 days.'),
        'Lost':     ('Inactive for months, very low frequency.', 'One reactivation push only. Then write off.'),
    }

    seg_counts = rfm['Segment'].value_counts()
    total = seg_counts.sum()

    rows = ''
    for seg, (who, action) in seg_info.items():
        if seg_filter != "All" and seg != seg_filter: continue
        count = int(seg_counts.get(seg, 0))
        pct   = round(count/total*100, 1)
        color = SEG_COLORS.get(seg,'#555')
        bg    = SEG_BG.get(seg,'#f7f7f5')
        bar_w = int(pct*2.2)
        rows += f'''<tr style="border-bottom:1px solid #f0f0ee;">
          <td style="padding:12px 16px;width:13%;">
            <span style="background:{bg};color:{color};padding:3px 10px;border-radius:4px;font-size:12px;font-weight:500;">{seg}</span>
          </td>
          <td style="padding:12px 16px;width:22%;">
            <div style="display:flex;align-items:center;gap:8px;">
              <div style="width:{bar_w}px;height:6px;background:{color};border-radius:3px;opacity:.6;min-width:2px;"></div>
              <span style="font-size:13px;font-weight:500;color:#37352f;">{count:,}</span>
              <span style="font-size:11px;color:#9b9b9b;">({pct}%)</span>
            </div>
          </td>
          <td style="padding:12px 16px;font-size:12px;color:#6b6b6b;width:30%;">{who}</td>
          <td style="padding:12px 16px;font-size:12px;color:#37352f;width:35%;">{action}</td>
        </tr>'''

    st.markdown(f'''
    <div style="background:#fff;border:1px solid #e8e8e4;border-radius:10px;overflow:hidden;">
      <div style="padding:12px 16px;border-bottom:1px solid #e8e8e4;background:#f7f7f5;">
        <span style="font-size:13px;font-weight:500;color:#37352f;">Customer segments — Jan to Jul 2026</span>
        <span style="font-size:11px;color:#9b9b9b;margin-left:8px;">{total:,} total</span>
      </div>
      <table style="width:100%;border-collapse:collapse;font-family:Inter,sans-serif;">
        <thead><tr style="background:#fafafa;border-bottom:1px solid #e8e8e4;">
          <th style="padding:8px 16px;text-align:left;font-size:11px;color:#9b9b9b;font-weight:500;text-transform:uppercase;letter-spacing:.05em;">Segment</th>
          <th style="padding:8px 16px;text-align:left;font-size:11px;color:#9b9b9b;font-weight:500;text-transform:uppercase;letter-spacing:.05em;">Count</th>
          <th style="padding:8px 16px;text-align:left;font-size:11px;color:#9b9b9b;font-weight:500;text-transform:uppercase;letter-spacing:.05em;">Who they are</th>
          <th style="padding:8px 16px;text-align:left;font-size:11px;color:#9b9b9b;font-weight:500;text-transform:uppercase;letter-spacing:.05em;">What to do</th>
        </tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>''', unsafe_allow_html=True)

    st.markdown("<div class='notion-section'>Breakdown</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        seg_df = seg_counts.reset_index()
        seg_df.columns = ['Segment','Customers']
        fig = px.bar(seg_df.sort_values('Customers'), x='Customers', y='Segment',
                     orientation='h', color='Segment', color_discrete_map=SEG_COLORS)
        fig.update_traces(marker_line_width=0)
        notion_chart(fig, 280)

    with col2:
        ch_seg = df.groupby(['Segment','CHANNEL']).size().unstack(fill_value=0).reset_index()
        ch_cols = [c for c in ['Instore','Delivery','Ecom'] if c in ch_seg.columns]
        fig2 = px.bar(ch_seg, x='Segment', y=ch_cols, color_discrete_map=CH_COLORS, barmode='stack')
        fig2.update_traces(marker_line_width=0)
        notion_chart(fig2, 280)

    if seg_filter != "All":
        st.markdown(f"<div class='notion-section'>Top brands for {seg_filter}</div>", unsafe_allow_html=True)
        seg_users = rfm[rfm['Segment']==seg_filter]['MASTER_ID'].tolist()
        seg_brands = df[df['MASTER_ID'].isin(seg_users)]['BRAND_CLEAN'].value_counts().head(10).reset_index()
        seg_brands.columns = ['Brand','Transactions']
        fig3 = px.bar(seg_brands.sort_values('Transactions'), x='Transactions', y='Brand',
                      orientation='h', color_discrete_sequence=[SEG_COLORS.get(seg_filter,'#2E86AB')])
        fig3.update_traces(marker_line_width=0)
        notion_chart(fig3, 320)

# ── CHANNEL JOURNEY ───────────────────────────────────────────────────
elif page == "Channel Journey":
    st.markdown("## Channel journey")

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        seg_filter = st.selectbox("Segment", ["All"] + list(SEG_COLORS.keys()))
    with col_f2:
        ch_filter = st.multiselect("Channel", ["Instore","Delivery","Ecom"], default=["Instore","Delivery","Ecom"])

    j = journey.copy()
    if seg_filter != "All":
        seg_users = rfm[rfm['Segment']==seg_filter]['MASTER_ID'].tolist()
        j = j[j['MASTER_ID'].isin(seg_users)]

    j_counts = j['Channel_Journey'].value_counts().reset_index()
    j_counts.columns = ['Journey Path','Customers']
    j_counts['%'] = (j_counts['Customers']/j_counts['Customers'].sum()*100).round(1)

    def classify(p):
        if '→' not in str(p): return 'Single Channel'
        elif str(p).count('→') == 1: return 'Two Channel'
        else: return 'Full Multichannel'

    j_counts['Type'] = j_counts['Journey Path'].apply(classify)
    total  = j_counts['Customers'].sum()
    single = j_counts[j_counts['Type']=='Single Channel']['Customers'].sum()
    two    = j_counts[j_counts['Type']=='Two Channel']['Customers'].sum()
    multi  = j_counts[j_counts['Type']=='Full Multichannel']['Customers'].sum()

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total customers",   f"{total:,}")
    c2.metric("Single channel",    f"{single:,}")
    c3.metric("Two channel",       f"{two:,}")
    c4.metric("Full multichannel", f"{multi:,}")

    col1, col2 = st.columns(2)
    with col1:
        type_df = pd.DataFrame({'Type':['Single Channel','Two Channel','Full Multichannel'],'Customers':[single,two,multi]})
        fig = px.pie(type_df, names='Type', values='Customers', hole=0.55,
                     color_discrete_sequence=['#e8e8e4','#0a4a8a','#1a7a4a'])
        fig.update_traces(textposition='outside', textfont_size=11)
        notion_chart(fig, 280)

    with col2:
        fig2 = px.bar(j_counts.head(10).sort_values('Customers'), x='Customers', y='Journey Path',
                      orientation='h', color='Type',
                      color_discrete_map={'Single Channel':'#e8e8e4','Two Channel':'#0a4a8a','Full Multichannel':'#1a7a4a'})
        fig2.update_traces(marker_line_width=0)
        notion_chart(fig2, 280)

    type_color_map = {'Single Channel':'#9b9b9b','Two Channel':'#0a4a8a','Full Multichannel':'#1a7a4a'}
    max_c = j_counts['Customers'].max()
    rows = ''
    for _, row in j_counts.iterrows():
        bar_w = int((row['Customers']/max_c)*80)
        color = type_color_map.get(row['Type'],'#555')
        rows += f'''<tr style="border-bottom:1px solid #f0f0ee;">
          <td style="padding:8px 16px;font-size:13px;color:#37352f;">{row["Journey Path"]}</td>
          <td style="padding:8px 16px;">
            <div style="display:flex;align-items:center;gap:8px;">
              <div style="width:{bar_w}px;min-width:2px;height:6px;background:#2E86AB;border-radius:3px;opacity:.5;"></div>
              <span style="font-size:13px;font-weight:500;color:#37352f;">{int(row["Customers"]):,}</span>
              <span style="font-size:11px;color:#9b9b9b;">({row["%"]}%)</span>
            </div>
          </td>
          <td style="padding:8px 16px;font-size:12px;font-weight:500;color:{color};">{row["Type"]}</td>
        </tr>'''

    st.markdown(f'''
    <div style="background:#fff;border:1px solid #e8e8e4;border-radius:10px;overflow:hidden;max-width:750px;">
      <table style="width:100%;border-collapse:collapse;font-family:Inter,sans-serif;">
        <thead><tr style="background:#f7f7f5;border-bottom:1px solid #e8e8e4;">
          <th style="padding:8px 16px;text-align:left;font-size:11px;color:#9b9b9b;font-weight:500;text-transform:uppercase;letter-spacing:.05em;">Path</th>
          <th style="padding:8px 16px;text-align:left;font-size:11px;color:#9b9b9b;font-weight:500;text-transform:uppercase;letter-spacing:.05em;">Customers</th>
          <th style="padding:8px 16px;text-align:left;font-size:11px;color:#9b9b9b;font-weight:500;text-transform:uppercase;letter-spacing:.05em;">Type</th>
        </tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>''', unsafe_allow_html=True)

# ── CATEGORY ANALYSIS ─────────────────────────────────────────────────
elif page == "Category Analysis":
    st.markdown("## Category analysis")

    all_cats = sorted(df['CATEGORY_CLEAN'].dropna().unique().tolist())
    cat_filter = st.multiselect("Categories", all_cats, default=[])

    df_cat = df[df['CATEGORY_CLEAN'].isin(cat_filter)] if cat_filter else df

    cat_agg = df_cat.groupby('CATEGORY_CLEAN').agg(
        Transactions=('MASTER_ID','count'),
        Customers=('MASTER_ID','nunique'),
        Top_Segment=('Segment', lambda x: x.value_counts().index[0] if x.notna().any() else '—')
    ).reset_index().sort_values('Transactions', ascending=False).head(12)

    cat_ch = df_cat.groupby(['CATEGORY_CLEAN','CHANNEL']).agg(C=('MASTER_ID','nunique')).reset_index()
    cat_ch_piv = cat_ch.pivot_table(index='CATEGORY_CLEAN', columns='CHANNEL', values='C', fill_value=0).reset_index()
    cat_agg = cat_agg.merge(cat_ch_piv, on='CATEGORY_CLEAN', how='left')
    for ch in ['Instore','Delivery','Ecom']:
        if ch not in cat_agg.columns: cat_agg[ch] = 0

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(cat_agg.sort_values('Customers'), x='Customers', y='CATEGORY_CLEAN',
                     orientation='h', color_discrete_sequence=['#2E86AB'])
        fig.update_traces(marker_line_width=0)
        fig.update_yaxes(title='')
        notion_chart(fig, 320)

    with col2:
        ch_cols = [c for c in ['Instore','Delivery','Ecom'] if c in cat_agg.columns]
        fig2 = px.bar(cat_agg, x='CATEGORY_CLEAN', y=ch_cols, color_discrete_map=CH_COLORS, barmode='stack')
        fig2.update_traces(marker_line_width=0)
        fig2.update_xaxes(title='', tickangle=30)
        notion_chart(fig2, 320)

    rows = ''
    for _, row in cat_agg.iterrows():
        cat = row['CATEGORY_CLEAN']
        seg_color = SEG_COLORS.get(row['Top_Segment'],'#555')
        seg_bg    = SEG_BG.get(row['Top_Segment'],'#f7f7f5')
        ins = int(row.get('Instore',0)); dlv = int(row.get('Delivery',0)); eco = int(row.get('Ecom',0))
        tot = ins+dlv+eco or 1
        brands = df[(df['CATEGORY_CLEAN']==cat) & df['BRAND_CLEAN'].notna()]['BRAND_CLEAN'].value_counts().head(4)
        brand_str = ' · '.join(brands.index.tolist()) if len(brands)>0 else '—'
        def bar(v,c):
            w=int(v/tot*50); p=round(v/tot*100)
            return f'<div style="display:flex;align-items:center;gap:3px;margin-bottom:2px;"><div style="width:{w}px;min-width:2px;height:5px;background:{c};border-radius:2px;opacity:.7;"></div><span style="font-size:10px;color:#9b9b9b;">{v:,} ({p}%)</span></div>'
        rows += f'''<tr style="border-bottom:1px solid #f0f0ee;vertical-align:top;">
          <td style="padding:10px 14px;"><div style="font-size:13px;font-weight:500;color:#37352f;">{cat}</div></td>
          <td style="padding:10px 14px;text-align:center;"><span style="font-size:14px;font-weight:500;color:#37352f;">{int(row["Customers"]):,}</span></td>
          <td style="padding:10px 14px;text-align:center;"><span style="background:{seg_bg};color:{seg_color};padding:2px 8px;border-radius:4px;font-size:11px;font-weight:500;">{row["Top_Segment"]}</span></td>
          <td style="padding:10px 14px;">{bar(ins,"#2E86AB")}{bar(dlv,"#A23B72")}{bar(eco,"#F18F01")}</td>
          <td style="padding:10px 14px;font-size:11px;color:#6b6b6b;">{brand_str}</td>
        </tr>'''

    st.markdown(f'''
    <div style="background:#fff;border:1px solid #e8e8e4;border-radius:10px;overflow:hidden;">
      <table style="width:100%;border-collapse:collapse;font-family:Inter,sans-serif;">
        <thead><tr style="background:#f7f7f5;border-bottom:1px solid #e8e8e4;">
          <th style="padding:8px 14px;text-align:left;font-size:11px;color:#9b9b9b;font-weight:500;text-transform:uppercase;letter-spacing:.05em;">Category</th>
          <th style="padding:8px 14px;text-align:center;font-size:11px;color:#9b9b9b;font-weight:500;text-transform:uppercase;letter-spacing:.05em;">Customers</th>
          <th style="padding:8px 14px;text-align:center;font-size:11px;color:#9b9b9b;font-weight:500;text-transform:uppercase;letter-spacing:.05em;">Top segment</th>
          <th style="padding:8px 14px;text-align:left;font-size:11px;color:#9b9b9b;font-weight:500;text-transform:uppercase;letter-spacing:.05em;">Channel split</th>
          <th style="padding:8px 14px;text-align:left;font-size:11px;color:#9b9b9b;font-weight:500;text-transform:uppercase;letter-spacing:.05em;">Top brands</th>
        </tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>''', unsafe_allow_html=True)

# ── CITY ANALYSIS ─────────────────────────────────────────────────────
elif page == "City Analysis":
    st.markdown("## City analysis")

    all_cities = sorted(df[df['CITY'].notna() & (df['CITY'].astype(str).str.strip()!='') & (df['CITY'].astype(str).str.strip()!='--')]['CITY'].unique().tolist())
    city_filter = st.multiselect("Cities", all_cities, default=[])

    city_agg = df.groupby('CITY').agg(
        Transactions=('MASTER_ID','count'),
        Customers=('MASTER_ID','nunique'),
        Top_Channel=('CHANNEL', lambda x: x.value_counts().index[0]),
        Top_Segment=('Segment', lambda x: x.value_counts().index[0] if x.notna().any() else '—')
    ).reset_index()

    city_ch = df.groupby(['CITY','CHANNEL']).agg(C=('MASTER_ID','nunique')).reset_index()
    city_ch_piv = city_ch.pivot_table(index='CITY', columns='CHANNEL', values='C', fill_value=0).reset_index()
    city_agg = city_agg.merge(city_ch_piv, on='CITY', how='left')
    for ch in ['Instore','Delivery','Ecom']:
        if ch not in city_agg.columns: city_agg[ch] = 0

    city_agg = city_agg[
        city_agg['CITY'].notna() &
        (city_agg['CITY'].astype(str).str.strip()!='') &
        (city_agg['CITY'].astype(str).str.strip()!='--')
    ].sort_values('Customers', ascending=False)

    display = city_agg[city_agg['CITY'].isin(city_filter)] if city_filter else city_agg.head(15)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(display.sort_values('Customers'), x='Customers', y='CITY',
                     orientation='h', color_discrete_sequence=['#2E86AB'])
        fig.update_traces(marker_line_width=0)
        fig.update_yaxes(title='')
        notion_chart(fig, 380)
    with col2:
        ch_cols = [c for c in ['Instore','Delivery','Ecom'] if c in display.columns]
        fig2 = px.bar(display.head(10), x='CITY', y=ch_cols, color_discrete_map=CH_COLORS, barmode='stack')
        fig2.update_traces(marker_line_width=0)
        fig2.update_xaxes(title='', tickangle=35)
        notion_chart(fig2, 380)

    rows = ''
    for _, row in display.iterrows():
        seg_color = SEG_COLORS.get(row['Top_Segment'],'#555')
        seg_bg    = SEG_BG.get(row['Top_Segment'],'#f7f7f5')
        ch_color  = CH_COLORS.get(row['Top_Channel'],'#555')
        ins=int(row.get('Instore',0)); dlv=int(row.get('Delivery',0)); eco=int(row.get('Ecom',0)); tot=ins+dlv+eco or 1
        def bar(v,c):
            w=int(v/tot*50); p=round(v/tot*100)
            return f'<div style="display:flex;align-items:center;gap:3px;margin-bottom:2px;"><div style="width:{w}px;min-width:2px;height:5px;background:{c};border-radius:2px;opacity:.7;"></div><span style="font-size:10px;color:#9b9b9b;">{v:,} ({p}%)</span></div>'
        rows += f'''<tr style="border-bottom:1px solid #f0f0ee;">
          <td style="padding:10px 14px;font-size:13px;font-weight:500;color:#37352f;">{row["CITY"]}</td>
          <td style="padding:10px 14px;text-align:center;font-size:13px;font-weight:500;color:#37352f;">{int(row["Customers"]):,}</td>
          <td style="padding:10px 14px;text-align:center;font-size:12px;font-weight:500;color:{ch_color};">{row["Top_Channel"]}</td>
          <td style="padding:10px 14px;text-align:center;"><span style="background:{seg_bg};color:{seg_color};padding:2px 8px;border-radius:4px;font-size:11px;font-weight:500;">{row["Top_Segment"]}</span></td>
          <td style="padding:10px 14px;">{bar(ins,"#2E86AB")}{bar(dlv,"#A23B72")}{bar(eco,"#F18F01")}</td>
        </tr>'''

    st.markdown(f'''
    <div style="background:#fff;border:1px solid #e8e8e4;border-radius:10px;overflow:hidden;">
      <table style="width:100%;border-collapse:collapse;font-family:Inter,sans-serif;">
        <thead><tr style="background:#f7f7f5;border-bottom:1px solid #e8e8e4;">
          <th style="padding:8px 14px;text-align:left;font-size:11px;color:#9b9b9b;font-weight:500;text-transform:uppercase;letter-spacing:.05em;">City</th>
          <th style="padding:8px 14px;text-align:center;font-size:11px;color:#9b9b9b;font-weight:500;text-transform:uppercase;letter-spacing:.05em;">Customers</th>
          <th style="padding:8px 14px;text-align:center;font-size:11px;color:#9b9b9b;font-weight:500;text-transform:uppercase;letter-spacing:.05em;">Top channel</th>
          <th style="padding:8px 14px;text-align:center;font-size:11px;color:#9b9b9b;font-weight:500;text-transform:uppercase;letter-spacing:.05em;">Top segment</th>
          <th style="padding:8px 14px;text-align:left;font-size:11px;color:#9b9b9b;font-weight:500;text-transform:uppercase;letter-spacing:.05em;">Channel split</th>
        </tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>''', unsafe_allow_html=True)

# ── BRAND AFFINITY ────────────────────────────────────────────────────
elif page == "Brand Affinity":
    st.markdown("## Brand affinity")

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        vertical = st.selectbox("Channel vertical", ["All","Instore","Delivery","Ecom"])
    with col_f2:
        df_v = df[df['CHANNEL']==vertical] if vertical != "All" else df
        top_brands = df_v['BRAND_CLEAN'].value_counts().dropna().head(25).index.tolist()
        selected_brands = st.multiselect("Brands", top_brands, default=[top_brands[0]] if top_brands else [])

    if not selected_brands:
        st.info("Select at least one brand above.")
    else:
        for selected_brand in selected_brands:
            brand_users = set(df_v[df_v['BRAND_CLEAN']==selected_brand]['MASTER_ID'].unique())

            also_use = df_v[
                (df_v['MASTER_ID'].isin(brand_users)) &
                (df_v['BRAND_CLEAN']!=selected_brand) &
                (df_v['BRAND_CLEAN'].notna())
            ]['BRAND_CLEAN'].value_counts().head(8).reset_index()
            also_use.columns = ['Brand','Users']

            user_tx = (df_v[df_v['BRAND_CLEAN'].notna()].sort_values('DATE')
                       .groupby('MASTER_ID')['BRAND_CLEAN'].apply(list).to_dict())
            next_b = []
            for u in brand_users:
                tx = user_tx.get(u,[])
                if selected_brand in tx:
                    idx = tx.index(selected_brand)
                    for b in tx[idx+1:]:
                        if b != selected_brand: next_b.append(b); break
            next_df = pd.DataFrame(Counter(next_b).most_common(8), columns=['Brand','Users'])
            if len(next_df)>0: next_df['%'] = (next_df['Users']/len(brand_users)*100).round(1)

            bc_row = brand_city[brand_city['BRAND_CLEAN']==selected_brand]
            cities_n = int(bc_row['Cities'].values[0]) if len(bc_row)>0 else '—'

            st.markdown(f"<div class='notion-section'>{selected_brand} · {vertical} vertical</div>", unsafe_allow_html=True)
            c1,c2,c3 = st.columns(3)
            c1.metric("Unique customers", f"{len(brand_users):,}")
            c2.metric("Cities present",   f"{cities_n}")
            c3.metric("Move to next brand", f"{int(next_df['Users'].iloc[0]):,}" if len(next_df)>0 else "—")

            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(also_use.sort_values('Users'), x='Users', y='Brand', orientation='h',
                             title="Customers also use", color_discrete_sequence=['#2E86AB'])
                fig.update_traces(marker_line_width=0)
                notion_chart(fig, 300)
            with col2:
                if len(next_df)>0:
                    fig2 = px.bar(next_df.sort_values('Users'), x='Users', y='Brand', orientation='h',
                                  title="Next brand after first visit", color_discrete_sequence=['#A23B72'])
                    fig2.update_traces(marker_line_width=0)
                    notion_chart(fig2, 300)

            st.markdown("<div class='notion-divider'></div>", unsafe_allow_html=True)

# ── PRODUCT AFFINITY ──────────────────────────────────────────────────
elif page == "Product Affinity":
    st.markdown("## Product affinity")
    st.markdown("<p class='notion-caption'>Based on Rs.199 campaign food subcategories — Pizza, Burger, Coffee, etc.</p>", unsafe_allow_html=True)

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        vertical_p = st.selectbox("Channel vertical", ["All (Rs.199 Instore)","By City"])
    with col_f2:
        all_subs = sorted(rs199_prod['FOOD_SUBCATEGORY'].dropna().unique().tolist())
        sub_filter = st.multiselect("Product subcategory", all_subs, default=[])

    df_p = rs199_prod.copy()
    if sub_filter:
        df_p = df_p[df_p['FOOD_SUBCATEGORY'].isin(sub_filter)]

    st.markdown("<div class='notion-section'>Subcategory volume</div>", unsafe_allow_html=True)
    sub_counts = df_p['FOOD_SUBCATEGORY'].value_counts().reset_index()
    sub_counts.columns = ['Subcategory','Transactions']

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(sub_counts.sort_values('Transactions'), x='Transactions', y='Subcategory',
                     orientation='h', color='Subcategory', color_discrete_map=SUB_COLORS)
        fig.update_traces(marker_line_width=0)
        notion_chart(fig, 280)

    with col2:
        fig2 = px.pie(sub_counts, names='Subcategory', values='Transactions',
                      color='Subcategory', color_discrete_map=SUB_COLORS, hole=0.5)
        fig2.update_traces(textposition='outside', textfont_size=11)
        notion_chart(fig2, 280)

    st.markdown("<div class='notion-section'>Product affinity — what users order together</div>", unsafe_allow_html=True)

    user_sub_map = rs199_prod.groupby('USER_PHONE')['FOOD_SUBCATEGORY'].apply(list).to_dict()
    all_subs_list = rs199_prod['FOOD_SUBCATEGORY'].dropna().unique().tolist()

    affinity_matrix = []
    for sub_a in all_subs_list:
        users_a = set(rs199_prod[rs199_prod['FOOD_SUBCATEGORY']==sub_a]['USER_PHONE'].unique())
        for sub_b in all_subs_list:
            if sub_a == sub_b: continue
            users_b = set(rs199_prod[rs199_prod['FOOD_SUBCATEGORY']==sub_b]['USER_PHONE'].unique())
            overlap = len(users_a & users_b)
            if overlap > 0:
                affinity_matrix.append({'From':sub_a,'To':sub_b,'Users':overlap,'%':round(overlap/len(users_a)*100,1)})

    aff_df = pd.DataFrame(affinity_matrix).sort_values('Users', ascending=False)

    fig3 = px.density_heatmap(aff_df, x='To', y='From', z='Users',
                               color_continuous_scale='Blues', text_auto=True)
    fig3.update_traces(textfont_size=11)
    notion_chart(fig3, 320)

    st.markdown("<div class='notion-section'>Top cross-subcategory pairs</div>", unsafe_allow_html=True)
    st.dataframe(aff_df.head(15), use_container_width=True, hide_index=True)

    st.markdown("<div class='notion-section'>By city</div>", unsafe_allow_html=True)
    city_sub = rs199_prod.groupby(['CITY','FOOD_SUBCATEGORY']).size().reset_index(name='Transactions')
    city_sub_top = city_sub.groupby('CITY')['Transactions'].sum().sort_values(ascending=False).head(10).index.tolist()
    city_sub_f = city_sub[city_sub['CITY'].isin(city_sub_top)]
    fig4 = px.bar(city_sub_f, x='CITY', y='Transactions', color='FOOD_SUBCATEGORY',
                  color_discrete_map=SUB_COLORS, barmode='stack')
    fig4.update_traces(marker_line_width=0)
    fig4.update_xaxes(tickangle=30)
    notion_chart(fig4, 320)

# ── NEXT CAMPAIGN RECOMMENDER ─────────────────────────────────────────
elif page == "Next Campaign Recommender":
    st.markdown("## Next Rs.199 campaign recommender")
    st.markdown("<p class='notion-caption'>Instore only. Scored on brand affinity + category fit + city coverage.</p>", unsafe_allow_html=True)

    instore_brands = df[df['CHANNEL']=='Instore']['BRAND_CLEAN'].value_counts().dropna().head(25).index.tolist()
    current_brand = st.selectbox("Current Rs.199 brand (this month)", instore_brands)

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        preferred_cat = st.multiselect("Preferred category for next brand", ['Food','Fashion','Entertainment','Health','Travel'], default=['Food'])
    with col_f2:
        min_cities = st.slider("Minimum city coverage", 1, 36, 8)

    with st.spinner("Analysing affinity..."):
        brand_users = set(df[df['CHANNEL']=='Instore'][df['BRAND_CLEAN']==current_brand]['MASTER_ID'].unique())
        user_tx = (df[df['CHANNEL']=='Instore'][df['BRAND_CLEAN'].notna()]
                   .sort_values('DATE').groupby('MASTER_ID')['BRAND_CLEAN'].apply(list).to_dict())
        next_b = []
        for u in brand_users:
            tx = user_tx.get(u,[])
            if current_brand in tx:
                idx = tx.index(current_brand)
                for b in tx[idx+1:]:
                    if b != current_brand: next_b.append(b); break
        next_counts = Counter(next_b)

        candidates = []
        for brand, aff_count in next_counts.most_common(30):
            if brand == current_brand: continue
            bc_row = brand_city[brand_city['BRAND_CLEAN']==brand]
            cities  = int(bc_row['Cities'].values[0]) if len(bc_row)>0 else 1
            total_c = int(bc_row['Total_Customers'].values[0]) if len(bc_row)>0 else 0
            if cities < min_cities: continue
            cat = df[df['BRAND_CLEAN']==brand]['CATEGORY_CLEAN'].value_counts().index[0] if len(df[df['BRAND_CLEAN']==brand])>0 else '—'
            cat_fit = 1.2 if (not preferred_cat or cat in preferred_cat) else 0.7
            aff_pct = round(aff_count/len(brand_users)*100, 1)
            city_score  = min(cities/36*100, 100)
            scale_score = min(total_c/61840*100, 100)
            final_score = round((aff_pct*0.4 + city_score*0.3 + scale_score*0.3) * cat_fit, 1)
            candidates.append({'Brand':brand,'Affinity %':aff_pct,'Users after':aff_count,
                                'Cities':cities,'Platform users':total_c,'Category':cat,'Score':final_score})

        rec_df = pd.DataFrame(candidates).sort_values('Score', ascending=False).head(5).reset_index(drop=True) if candidates else pd.DataFrame()

    if len(rec_df) > 0:
        winner = rec_df.iloc[0]
        st.markdown(f'''
        <div class="winner-card">
          <div class="winner-label">Recommended next brand</div>
          <div class="winner-brand">{winner["Brand"]}</div>
          <div style="display:flex;gap:32px;">
            <div class="winner-stat"><div class="winner-stat-val" style="color:#1a7a4a;">{winner["Affinity %"]}%</div><div class="winner-stat-lab">of {current_brand} users go here next</div></div>
            <div class="winner-stat"><div class="winner-stat-val" style="color:#0a4a8a;">{winner["Cities"]}</div><div class="winner-stat-lab">cities covered</div></div>
            <div class="winner-stat"><div class="winner-stat-val" style="color:#b35900;">{int(winner["Platform users"]):,}</div><div class="winner-stat-lab">platform customers</div></div>
            <div class="winner-stat"><div class="winner-stat-val" style="color:#37352f;">{winner["Score"]}</div><div class="winner-stat-lab">recommendation score</div></div>
          </div>
          <p style="margin-top:12px;font-size:12px;color:#6b6b6b;">Category: <strong>{winner["Category"]}</strong> · {int(winner["Users after"]):,} {current_brand} customers naturally visit {winner["Brand"]} after their first instore visit. High city coverage + strong affinity = ideal Rs.199 candidate.</p>
        </div>''', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(rec_df.sort_values('Score'), x='Score', y='Brand', orientation='h',
                         color='Score', color_continuous_scale=[[0,'#e8f5f0'],[1,'#1a7a4a']], text='Score')
            fig.update_traces(textposition='outside', marker_line_width=0)
            fig.update_layout(coloraxis_showscale=False)
            notion_chart(fig, 280)
        with col2:
            fig2 = px.scatter(rec_df, x='Affinity %', y='Cities', size='Platform users',
                              color='Brand', hover_name='Brand', size_max=40)
            fig2.update_traces(marker_line_width=0)
            notion_chart(fig2, 280)

        st.markdown("<div class='notion-section'>All recommendations</div>", unsafe_allow_html=True)
        st.dataframe(rec_df, use_container_width=True, hide_index=True)

        st.markdown("""
        <div class='notion-card' style='margin-top:1rem;'>
          <p style='font-size:12px;color:#6b6b6b;margin:0;'><strong>Score formula:</strong> Affinity % (40%) + City coverage (30%) + Platform scale (30%), adjusted by category fit multiplier. Instore-only brands. Minimum city coverage filter applied.</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.warning("No candidates found with current filters. Try reducing minimum city coverage.")

# ── CUSTOMER LOOKUP ───────────────────────────────────────────────────
elif page == "Customer Lookup":
    st.markdown("## Customer lookup")

    phone = st.text_input("", placeholder="Enter phone number — e.g. 3001234567", label_visibility="collapsed")

    if phone:
        phone = str(phone).strip()
        cdf = df[df['MASTER_ID'].astype(str).str.strip()==phone].copy().sort_values('DATE')

        if len(cdf)==0:
            st.warning(f"No customer found for: {phone}")
        else:
            mid       = str(cdf['MASTER_ID'].iloc[0]).strip()
            rfm_row   = rfm[rfm['MASTER_ID']==mid]
            j_row     = journey[journey['MASTER_ID']==mid]
            is_rs199  = mid in rs199_phones and (bool(rfm_row['IS_RS199'].values[0]) if not rfm_row.empty and 'IS_RS199' in rfm_row.columns else False)

            seg     = rfm_row['Segment'].values[0] if not rfm_row.empty else '—'
            rec     = int(rfm_row['Recency'].values[0]) if not rfm_row.empty else '—'
            freq    = int(rfm_row['Frequency'].values[0]) if not rfm_row.empty else '—'
            mon     = float(rfm_row['Monetary'].values[0]) if not rfm_row.empty else 0
            r_s     = int(rfm_row['R_Score'].values[0]) if not rfm_row.empty else '—'
            f_s     = int(rfm_row['F_Score'].values[0]) if not rfm_row.empty else '—'
            m_s     = int(rfm_row['M_Score'].values[0]) if not rfm_row.empty else '—'
            ch_j    = j_row['Channel_Journey'].values[0] if not j_row.empty else '—'
            cat_j   = j_row['Category_Journey'].values[0] if not j_row.empty else '—'
            top_b   = j_row['Top_Brand'].values[0] if not j_row.empty else '—'
            top_c   = j_row['Top_Category'].values[0] if not j_row.empty else '—'
            city    = str(cdf['CITY'].dropna().iloc[0]) if not cdf['CITY'].dropna().empty else '—'
            name    = str(cdf['CUSTOMER_NAME'].dropna().iloc[0]) if 'CUSTOMER_NAME' in cdf.columns and not cdf['CUSTOMER_NAME'].dropna().empty else '—'
            fd      = cdf['DATE'].min().strftime('%d %b %Y')
            ld      = cdf['DATE'].max().strftime('%d %b %Y')
            seg_c   = SEG_COLORS.get(seg,'#555')
            seg_bg  = SEG_BG.get(seg,'#f7f7f5')
            rs_badge = '🟡 Rs.199 user' if is_rs199 else ''

            st.markdown(f'''
            <div style="background:#fff;border:1px solid #e8e8e4;border-radius:10px;overflow:hidden;margin-bottom:16px;">
              <div style="padding:16px 20px;border-bottom:1px solid #e8e8e4;display:flex;justify-content:space-between;align-items:center;">
                <div>
                  <span style="font-size:17px;font-weight:600;color:#37352f;">{name}</span>
                  <span style="font-size:13px;color:#9b9b9b;margin-left:8px;">{phone} · {city}</span>
                  <span style="font-size:12px;color:#b35900;margin-left:8px;">{rs_badge}</span>
                </div>
                <span style="background:{seg_bg};color:{seg_c};padding:4px 12px;border-radius:6px;font-size:13px;font-weight:500;">{seg}</span>
              </div>
              <div style="display:grid;grid-template-columns:repeat(5,1fr);border-bottom:1px solid #e8e8e4;">
                <div style="padding:14px 18px;border-right:1px solid #e8e8e4;text-align:center;"><div style="font-size:22px;font-weight:600;color:#37352f;">{rec}d</div><div style="font-size:11px;color:#9b9b9b;text-transform:uppercase;letter-spacing:.05em;margin-top:2px;">Last visit · R {r_s}/5</div></div>
                <div style="padding:14px 18px;border-right:1px solid #e8e8e4;text-align:center;"><div style="font-size:22px;font-weight:600;color:#37352f;">{freq}</div><div style="font-size:11px;color:#9b9b9b;text-transform:uppercase;letter-spacing:.05em;margin-top:2px;">Transactions · F {f_s}/5</div></div>
                <div style="padding:14px 18px;border-right:1px solid #e8e8e4;text-align:center;"><div style="font-size:20px;font-weight:600;color:#37352f;">PKR {int(mon):,}</div><div style="font-size:11px;color:#9b9b9b;text-transform:uppercase;letter-spacing:.05em;margin-top:2px;">Delivery spend · M {m_s}/5</div></div>
                <div style="padding:14px 18px;border-right:1px solid #e8e8e4;text-align:center;"><div style="font-size:14px;font-weight:500;color:#37352f;">{top_b}</div><div style="font-size:11px;color:#9b9b9b;margin-top:2px;">Favourite brand · {top_c}</div></div>
                <div style="padding:14px 18px;text-align:center;"><div style="font-size:12px;font-weight:500;color:#37352f;">{fd}</div><div style="font-size:11px;color:#9b9b9b;">First seen</div><div style="font-size:12px;font-weight:500;color:#37352f;margin-top:4px;">{ld}</div><div style="font-size:11px;color:#9b9b9b;">Last seen</div></div>
              </div>
              <div style="display:flex;border-bottom:1px solid #e8e8e4;">
                <div style="flex:1;padding:10px 20px;border-right:1px solid #e8e8e4;"><span style="font-size:11px;color:#9b9b9b;text-transform:uppercase;letter-spacing:.05em;">Channel journey </span><span style="font-size:13px;color:#37352f;font-weight:500;">{ch_j}</span></div>
                <div style="flex:1;padding:10px 20px;"><span style="font-size:11px;color:#9b9b9b;text-transform:uppercase;letter-spacing:.05em;">Category journey </span><span style="font-size:13px;color:#37352f;font-weight:500;">{str(cat_j)[:80]}</span></div>
              </div>
            </div>''', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                ch_d = cdf['CHANNEL'].value_counts().reset_index()
                ch_d.columns = ['Channel','Visits']
                fig = px.pie(ch_d, names='Channel', values='Visits', color='Channel',
                             color_discrete_map=CH_COLORS, hole=0.5)
                fig.update_traces(textposition='outside', textfont_size=11)
                notion_chart(fig, 220)
            with col2:
                bd = cdf['BRAND_CLEAN'].value_counts().head(6).reset_index()
                bd.columns = ['Brand','Visits']
                fig2 = px.bar(bd.sort_values('Visits'), x='Visits', y='Brand', orientation='h',
                              color_discrete_sequence=['#2E86AB'])
                fig2.update_traces(marker_line_width=0)
                notion_chart(fig2, 220)

            st.markdown(f"<div class='notion-section'>All transactions ({len(cdf):,})</div>", unsafe_allow_html=True)
            tx_cols = ['DATE','CHANNEL','BRAND_CLEAN','CATEGORY_CLEAN','OFFER_TITLE','OFFER_DESC','AMOUNT']
            tx = cdf[[c for c in tx_cols if c in cdf.columns]].copy().iloc[::-1]
            tx['DATE'] = tx['DATE'].dt.strftime('%d %b %Y')
            if 'AMOUNT' in tx.columns:
                tx['AMOUNT'] = tx['AMOUNT'].apply(lambda x: f"PKR {int(x):,}" if pd.notna(x) and x>0 else '—')
            tx = tx.rename(columns={'DATE':'Date','CHANNEL':'Channel','BRAND_CLEAN':'Brand',
                                    'CATEGORY_CLEAN':'Category','OFFER_TITLE':'Offer','OFFER_DESC':'Deal','AMOUNT':'Amount'})
            st.dataframe(tx, use_container_width=True, hide_index=True)
