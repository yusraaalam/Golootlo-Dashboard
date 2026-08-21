import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go

# ── PAGE CONFIG ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Golootlo Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── PASSWORD ──────────────────────────────────────────────────────────
def check_password():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.markdown("## 📊 Golootlo Analytics")
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
div[data-testid="metric-container"] {
    background:#fff; border:1px solid #e8e8e8;
    border-radius:10px; padding:12px 16px;
}
.section-title {
    font-size:15px; font-weight:700; color:#111;
    margin:24px 0 12px; padding-bottom:8px;
    border-bottom:1px solid #e8e8e8;
}
</style>
""", unsafe_allow_html=True)

# ── DB ────────────────────────────────────────────────────────────────
DB_URL = "postgresql+psycopg2://postgres.sbhvdjuxasqkjrxdvmcy:YusraAlam1515@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"

@st.cache_resource
def get_engine():
    return create_engine(DB_URL, connect_args={"sslmode": "require"})

@st.cache_data(show_spinner="Loading data...")
def load_data():
    engine = get_engine()
    df      = pd.read_sql("SELECT * FROM scored",     engine)
    rfm     = pd.read_sql("SELECT * FROM rfm",        engine)
    journey = pd.read_sql("SELECT * FROM journey",    engine)
    bc      = pd.read_sql("SELECT * FROM brand_city", engine)
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
    return df, rfm, journey, bc

df, rfm, journey, brand_city = load_data()

rs199_phones = set(rfm[rfm['IS_RS199']==True]['MASTER_ID'].astype(str)) if 'IS_RS199' in rfm.columns else set()

SEG_COLORS = {
    'Champion':'#1a7a4a','Loyal':'#0a4a8a',
    'At Risk':'#b35900','New':'#3a2a9a','Lost':'#8a1a1a'
}
CH_COLORS = {'Instore':'#2E86AB','Delivery':'#A23B72','Ecom':'#F18F01'}
PLOTLY_COLORS = ['#2E86AB','#A23B72','#F18F01','#1a7a4a','#3a2a9a','#8a1a1a','#b35900']

# ── SIDEBAR ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 Golootlo Analytics")
    st.markdown("**Jan – Jul 2026**")
    st.markdown("---")
    page = st.radio("Navigate", [
        "Overview","Segments","Channel Journey",
        "Category Analysis","City Analysis",
        "Brand Affinity","Next Campaign Recommender",
        "Customer Lookup"
    ])
    st.markdown("---")
    st.markdown(f"**{df['MASTER_ID'].nunique():,}** customers")
    st.markdown(f"**{len(df):,}** transactions")
    st.markdown(f"**{df['BRAND_CLEAN'].nunique():,}** brands")

# ══════════════════════════════════════════════════════════════════════
# OVERVIEW
# ══════════════════════════════════════════════════════════════════════
if page == "Overview":
    st.markdown("## Platform Overview")
    st.caption("Jan 1 – Jul 31, 2026")

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Total Customers",    f"{df['MASTER_ID'].nunique():,}")
    c2.metric("Total Transactions", f"{len(df):,}")
    c3.metric("Unique Brands",      f"{df['BRAND_CLEAN'].nunique():,}")
    c4.metric("Delivery Spend",     f"PKR {df[df['CHANNEL']=='Delivery']['AMOUNT'].sum():,.0f}")
    c5.metric("Rs.199 Users",       f"{len(rs199_phones):,}")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">Channel Split</div>', unsafe_allow_html=True)
        ch = df.groupby('CHANNEL').agg(
            Transactions=('MASTER_ID','count'),
            Customers=('MASTER_ID','nunique')
        ).reset_index()
        fig = px.pie(ch, names='CHANNEL', values='Customers',
                     color='CHANNEL',
                     color_discrete_map=CH_COLORS,
                     hole=0.4)
        fig.update_layout(margin=dict(t=20,b=20,l=20,r=20), height=280,
                         paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Segment Distribution</div>', unsafe_allow_html=True)
        seg = rfm['Segment'].value_counts().reset_index()
        seg.columns = ['Segment','Customers']
        fig2 = px.bar(seg, x='Segment', y='Customers',
                      color='Segment',
                      color_discrete_map=SEG_COLORS)
        fig2.update_layout(showlegend=False, margin=dict(t=20,b=20,l=20,r=20),
                           height=280, paper_bgcolor='rgba(0,0,0,0)',
                           plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">Monthly Transaction Trend</div>', unsafe_allow_html=True)
    monthly = df.groupby(['YEAR','MONTH_NUM','MONTH_NAME']).size().reset_index(name='Transactions')
    monthly = monthly.sort_values(['YEAR','MONTH_NUM'])
    monthly['Month'] = monthly['MONTH_NAME'].str[:3] + ' ' + monthly['YEAR'].astype(str)
    fig3 = px.line(monthly, x='Month', y='Transactions', markers=True,
                   color_discrete_sequence=['#2E86AB'])
    fig3.update_layout(margin=dict(t=20,b=20,l=20,r=20), height=300,
                       paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig3.update_xaxes(showgrid=False)
    st.plotly_chart(fig3, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="section-title">Top 10 Brands</div>', unsafe_allow_html=True)
        top_brands = df['BRAND_CLEAN'].value_counts().dropna().head(10).reset_index()
        top_brands.columns = ['Brand','Transactions']
        fig4 = px.bar(top_brands, x='Transactions', y='Brand', orientation='h',
                      color_discrete_sequence=['#2E86AB'])
        fig4.update_layout(yaxis={'categoryorder':'total ascending'},
                           margin=dict(t=10,b=10,l=10,r=10), height=320,
                           paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig4, use_container_width=True)

    with col4:
        st.markdown('<div class="section-title">Top 10 Cities</div>', unsafe_allow_html=True)
        top_cities = df.groupby('CITY')['MASTER_ID'].nunique().sort_values(ascending=False).head(10).reset_index()
        top_cities.columns = ['City','Customers']
        fig5 = px.bar(top_cities, x='Customers', y='City', orientation='h',
                      color_discrete_sequence=['#A23B72'])
        fig5.update_layout(yaxis={'categoryorder':'total ascending'},
                           margin=dict(t=10,b=10,l=10,r=10), height=320,
                           paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig5, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════
# SEGMENTS
# ══════════════════════════════════════════════════════════════════════
elif page == "Segments":
    st.markdown("## Customer Segments")

    seg_filter = st.selectbox("Filter by Segment", ["All"] + list(SEG_COLORS.keys()))

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
        if seg_filter != "All" and seg != seg_filter:
            continue
        count = int(seg_counts.get(seg, 0))
        pct   = round(count/total*100, 1)
        color = SEG_COLORS.get(seg, '#555')
        bar_w = int(pct * 2)
        rows_html += f'''<tr style="border-bottom:1px solid #f0f0f0;">
            <td style="padding:10px 14px;">
              <span style="font-size:13px;font-weight:700;color:{color};">{seg}</span>
            </td>
            <td style="padding:10px 14px;">
              <div style="display:flex;align-items:center;gap:8px;">
                <div style="width:{bar_w}px;height:7px;background:{color};border-radius:3px;opacity:0.7;min-width:3px;"></div>
                <span style="font-size:13px;font-weight:600;color:#111;">{count:,}</span>
                <span style="font-size:11px;color:#aaa;">({pct}%)</span>
              </div>
            </td>
            <td style="padding:10px 14px;font-size:12px;color:#555;">{who}</td>
            <td style="padding:10px 14px;font-size:12px;color:#111;">{action}</td>
        </tr>'''

    st.markdown(f'''
    <div style="background:#fff;border:1px solid #e8e8e8;border-radius:10px;overflow:hidden;">
      <div style="padding:10px 16px;border-bottom:1px solid #eee;">
        <span style="font-size:13px;font-weight:700;color:#111;">Customer Segments — Jan to Jul 2026</span>
      </div>
      <table style="width:100%;border-collapse:collapse;font-family:Inter,sans-serif;">
        <thead><tr style="background:#fafafa;border-bottom:1px solid #eee;">
          <th style="padding:8px 14px;text-align:left;font-size:11px;color:#888;font-weight:600;">SEGMENT</th>
          <th style="padding:8px 14px;text-align:left;font-size:11px;color:#888;font-weight:600;">COUNT</th>
          <th style="padding:8px 14px;text-align:left;font-size:11px;color:#888;font-weight:600;">WHO THEY ARE</th>
          <th style="padding:8px 14px;text-align:left;font-size:11px;color:#888;font-weight:600;">WHAT TO DO</th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>''', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Segment Size</div>', unsafe_allow_html=True)
        seg_df = pd.DataFrame({'Segment': list(seg_counts.index), 'Customers': list(seg_counts.values)})
        fig = px.bar(seg_df, x='Segment', y='Customers', color='Segment',
                     color_discrete_map=SEG_COLORS)
        fig.update_layout(showlegend=False, margin=dict(t=10,b=10,l=10,r=10),
                          height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Channel Breakdown by Segment</div>', unsafe_allow_html=True)
        ch_seg = df.groupby(['Segment','CHANNEL']).size().unstack(fill_value=0).reset_index()
        fig2 = px.bar(ch_seg, x='Segment', y=[c for c in ['Instore','Delivery','Ecom'] if c in ch_seg.columns],
                      color_discrete_map=CH_COLORS, barmode='stack')
        fig2.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=300,
                           paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)

    if seg_filter != "All":
        st.markdown(f'<div class="section-title">Top Brands for {seg_filter} Customers</div>', unsafe_allow_html=True)
        seg_users = rfm[rfm['Segment']==seg_filter]['MASTER_ID'].tolist()
        seg_brands = df[df['MASTER_ID'].isin(seg_users)]['BRAND_CLEAN'].value_counts().head(10).reset_index()
        seg_brands.columns = ['Brand','Transactions']
        fig3 = px.bar(seg_brands, x='Transactions', y='Brand', orientation='h',
                      color_discrete_sequence=[SEG_COLORS.get(seg_filter,'#2E86AB')])
        fig3.update_layout(yaxis={'categoryorder':'total ascending'},
                           margin=dict(t=10,b=10,l=10,r=10), height=320,
                           paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════
# CHANNEL JOURNEY
# ══════════════════════════════════════════════════════════════════════
elif page == "Channel Journey":
    st.markdown("## Channel Journey")

    seg_filter = st.selectbox("Filter by Segment", ["All"] + list(SEG_COLORS.keys()))

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
    c1.metric("Total Customers",  f"{total:,}")
    c2.metric("Single Channel",   f"{single:,}")
    c3.metric("Two Channel",      f"{two:,}")
    c4.metric("Full Multichannel",f"{multi:,}")

    col1, col2 = st.columns([1,1])
    with col1:
        fig = px.pie(
            pd.DataFrame({'Type':['Single Channel','Two Channel','Full Multichannel'],
                          'Customers':[single,two,multi]}),
            names='Type', values='Customers', hole=0.4,
            color_discrete_sequence=['#888','#0a4a8a','#1a7a4a']
        )
        fig.update_layout(margin=dict(t=20,b=20,l=20,r=20), height=280,
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        top_paths = j_counts.head(8)
        fig2 = px.bar(top_paths, x='Customers', y='Journey Path', orientation='h',
                      color='Type',
                      color_discrete_map={'Single Channel':'#888','Two Channel':'#0a4a8a','Full Multichannel':'#1a7a4a'})
        fig2.update_layout(yaxis={'categoryorder':'total ascending'},
                           margin=dict(t=10,b=10,l=10,r=10), height=300,
                           paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                           showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    type_colors_map = {'Single Channel':'#888','Two Channel':'#0a4a8a','Full Multichannel':'#1a7a4a'}
    max_c = j_counts['Customers'].max()
    rows = ''
    for _, row in j_counts.iterrows():
        bar_w = int((row['Customers']/max_c)*80)
        color = type_colors_map.get(row['Type'],'#555')
        rows += f'''<tr style="border-bottom:1px solid #f0f0f0;">
            <td style="padding:7px 14px;font-size:13px;color:#111;font-weight:500;">{row["Journey Path"]}</td>
            <td style="padding:7px 14px;">
              <div style="display:flex;align-items:center;gap:8px;">
                <div style="width:{bar_w}px;min-width:2px;height:7px;background:#2E86AB;border-radius:3px;opacity:0.6;"></div>
                <span style="font-size:13px;font-weight:600;color:#111;">{int(row["Customers"]):,}</span>
                <span style="font-size:11px;color:#aaa;">({row["%"]}%)</span>
              </div>
            </td>
            <td style="padding:7px 14px;font-size:12px;font-weight:600;color:{color};">{row["Type"]}</td>
        </tr>'''

    st.markdown(f'''
    <div style="background:#fff;border:1px solid #e8e8e8;border-radius:10px;overflow:hidden;max-width:750px;">
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
# CATEGORY ANALYSIS
# ══════════════════════════════════════════════════════════════════════
elif page == "Category Analysis":
    st.markdown("## Category Analysis")

    all_cats = sorted(df['CATEGORY_CLEAN'].dropna().unique().tolist())
    cat_filter = st.selectbox("Filter by Category", ["All"] + all_cats)

    df_cat = df.copy()
    if cat_filter != "All":
        df_cat = df_cat[df_cat['CATEGORY_CLEAN'] == cat_filter]

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

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(cat_total, x='Customers', y='CATEGORY_CLEAN', orientation='h',
                     color_discrete_sequence=['#2E86AB'])
        fig.update_layout(yaxis={'categoryorder':'total ascending'},
                          margin=dict(t=10,b=10,l=10,r=10), height=350,
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        fig.update_yaxes(title='')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        ch_cols = [c for c in ['Instore','Delivery','Ecom'] if c in cat_total.columns]
        fig2 = px.bar(cat_total, x='CATEGORY_CLEAN', y=ch_cols,
                      color_discrete_map=CH_COLORS, barmode='stack')
        fig2.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=350,
                           paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        fig2.update_xaxes(title='')
        st.plotly_chart(fig2, use_container_width=True)

    rows = ''
    for _, row in cat_total.iterrows():
        cat = row['CATEGORY_CLEAN']
        seg_color = SEG_COLORS.get(row['Top_Segment'], '#555')
        ins = int(row.get('Instore', 0))
        dlv = int(row.get('Delivery', 0))
        eco = int(row.get('Ecom', 0))
        tot = ins + dlv + eco or 1

        def bar(val, color):
            w = int(val/tot*50)
            p = round(val/tot*100)
            return f'<div style="display:flex;align-items:center;gap:3px;margin-bottom:2px;"><div style="width:{w}px;min-width:2px;height:5px;background:{color};border-radius:2px;"></div><span style="font-size:10px;color:#888;">{val:,} ({p}%)</span></div>'

        brands = df[(df['CATEGORY_CLEAN']==cat) & df['BRAND_CLEAN'].notna()]['BRAND_CLEAN'].value_counts().head(4)
        brand_str = ' · '.join(brands.index.tolist()) if len(brands) > 0 else '—'

        rows += f'''<tr style="border-bottom:1px solid #f0f0f0;vertical-align:top;">
            <td style="padding:8px 12px;">
              <div style="font-size:13px;font-weight:700;color:#111;">{cat}</div>
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
        <span style="font-size:13px;font-weight:700;color:#111;">Category Breakdown</span>
        <span style="font-size:11px;color:#aaa;"><span style="color:#2E86AB;">■</span> Instore &nbsp;<span style="color:#A23B72;">■</span> Delivery &nbsp;<span style="color:#F18F01;">■</span> Ecom</span>
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
# CITY ANALYSIS
# ══════════════════════════════════════════════════════════════════════
elif page == "City Analysis":
    st.markdown("## City Analysis")

    all_cities = sorted(df['CITY'].dropna().unique().tolist())
    city_filter = st.selectbox("Filter by City", ["All Top 15"] + all_cities)

    city_total = df.groupby('CITY').agg(
        Transactions=('MASTER_ID','count'),
        Customers=('MASTER_ID','nunique'),
        Top_Channel=('CHANNEL', lambda x: x.value_counts().index[0]),
        Top_Segment=('Segment', lambda x: x.value_counts().index[0] if x.notna().any() else '—')
    ).reset_index()

    city_ch = df.groupby(['CITY','CHANNEL']).agg(
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
    ].sort_values('Customers', ascending=False).reset_index(drop=True)

    if city_filter == "All Top 15":
        display_cities = city_total.head(15)
    else:
        display_cities = city_total[city_total['CITY'] == city_filter]

    display_cities['% Share'] = (display_cities['Transactions']/city_total['Transactions'].sum()*100).round(1)

    col1, col2 = st.columns(2)
    with col1:
        top15 = city_total.head(15)
        fig = px.bar(top15, x='Customers', y='CITY', orientation='h',
                     color_discrete_sequence=['#2E86AB'])
        fig.update_layout(yaxis={'categoryorder':'total ascending'},
                          margin=dict(t=10,b=10,l=10,r=10), height=400,
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        fig.update_yaxes(title='')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        ch_cols = [c for c in ['Instore','Delivery','Ecom'] if c in top15.columns]
        fig2 = px.bar(top15.head(10), x='CITY', y=ch_cols,
                      color_discrete_map=CH_COLORS, barmode='stack')
        fig2.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=400,
                           paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        fig2.update_xaxes(title='', tickangle=45)
        st.plotly_chart(fig2, use_container_width=True)

    rows = ''
    for _, row in display_cities.iterrows():
        seg_color = SEG_COLORS.get(row['Top_Segment'], '#555')
        ch_color  = CH_COLORS.get(row['Top_Channel'], '#555')
        ins = int(row.get('Instore', 0))
        dlv = int(row.get('Delivery', 0))
        eco = int(row.get('Ecom', 0))
        tot = ins + dlv + eco or 1

        def bar(val, color):
            w = int(val/tot*50)
            p = round(val/tot*100)
            return f'<div style="display:flex;align-items:center;gap:3px;margin-bottom:2px;"><div style="width:{w}px;min-width:2px;height:5px;background:{color};border-radius:2px;"></div><span style="font-size:10px;color:#888;">{val:,} ({p}%)</span></div>'

        rows += f'''<tr style="border-bottom:1px solid #f0f0f0;">
            <td style="padding:8px 12px;"><div style="font-size:13px;font-weight:700;color:#111;">{row["CITY"]}</div><div style="font-size:10px;color:#aaa;">{row["% Share"]}% of tx</div></td>
            <td style="padding:8px 12px;text-align:center;"><div style="font-size:14px;font-weight:700;color:#111;">{int(row["Customers"]):,}</div><div style="font-size:10px;color:#aaa;">{int(row["Transactions"]):,} tx</div></td>
            <td style="padding:8px 12px;font-size:12px;font-weight:600;color:{ch_color};text-align:center;">{row["Top_Channel"]}</td>
            <td style="padding:8px 12px;font-size:12px;font-weight:600;color:{seg_color};text-align:center;">{row["Top_Segment"]}</td>
            <td style="padding:8px 12px;">{bar(ins,"#2E86AB")}{bar(dlv,"#A23B72")}{bar(eco,"#F18F01")}</td>
        </tr>'''

    st.markdown(f'''
    <div style="background:#fff;border:1px solid #e8e8e8;border-radius:10px;overflow:hidden;">
      <div style="padding:10px 16px;border-bottom:1px solid #eee;display:flex;justify-content:space-between;">
        <span style="font-size:13px;font-weight:700;color:#111;">City Breakdown</span>
        <span style="font-size:11px;color:#aaa;"><span style="color:#2E86AB;">■</span> Instore &nbsp;<span style="color:#A23B72;">■</span> Delivery &nbsp;<span style="color:#F18F01;">■</span> Ecom</span>
      </div>
      <table style="width:100%;border-collapse:collapse;font-family:Inter,sans-serif;">
        <thead><tr style="background:#fafafa;border-bottom:1px solid #eee;">
          <th style="padding:7px 12px;font-size:11px;color:#888;font-weight:600;text-align:left;">CITY</th>
          <th style="padding:7px 12px;font-size:11px;color:#888;font-weight:600;text-align:center;">CUSTOMERS</th>
          <th style="padding:7px 12px;font-size:11px;color:#888;font-weight:600;text-align:center;">TOP CHANNEL</th>
          <th style="padding:7px 12px;font-size:11px;color:#888;font-weight:600;text-align:center;">TOP SEGMENT</th>
          <th style="padding:7px 12px;font-size:11px;color:#888;font-weight:600;text-align:left;">CHANNEL SPLIT</th>
        </tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>''', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# BRAND AFFINITY
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
    ]['BRAND_CLEAN'].value_counts().head(8).reset_index()
    also_use.columns = ['Brand','Users']

    user_tx_map = (
        df[df['BRAND_CLEAN'].notna()]
        .sort_values('DATE')
        .groupby('MASTER_ID')['BRAND_CLEAN']
        .apply(list).to_dict()
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

    next_df = pd.DataFrame(Counter(next_brands).most_common(8), columns=['Brand','Users'])
    if len(next_df) > 0:
        next_df['%'] = (next_df['Users']/len(brand_users)*100).round(1)

    bc_row = brand_city[brand_city['BRAND_CLEAN']==selected_brand]
    cities_count = int(bc_row['Cities'].values[0]) if len(bc_row) > 0 else '—'
    total_cust   = int(bc_row['Total_Customers'].values[0]) if len(bc_row) > 0 else len(brand_users)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Customers",         f"{len(brand_users):,}")
    c2.metric("Cities Present",          f"{cities_count}")
    c3.metric("Also Use Another Brand",  f"{also_use['Users'].iloc[0]:,}" if len(also_use)>0 else "—")
    c4.metric("Move to Next Brand",      f"{next_df['Users'].iloc[0]:,}" if len(next_df)>0 else "—")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Customers Also Use**")
        fig = px.bar(also_use, x='Users', y='Brand', orientation='h',
                     color_discrete_sequence=['#2E86AB'])
        fig.update_layout(yaxis={'categoryorder':'total ascending'},
                          margin=dict(t=10,b=10,l=10,r=10), height=320,
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Next Brand After First Visit**")
        if len(next_df) > 0:
            fig2 = px.bar(next_df, x='Users', y='Brand', orientation='h',
                          color_discrete_sequence=['#A23B72'])
            fig2.update_layout(yaxis={'categoryorder':'total ascending'},
                               margin=dict(t=10,b=10,l=10,r=10), height=320,
                               paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════
# NEXT CAMPAIGN RECOMMENDER
# ══════════════════════════════════════════════════════════════════════
elif page == "Next Campaign Recommender":
    st.markdown("## Next Rs.199 Campaign Recommender")
    st.caption("Based on platform-wide brand affinity — not random selection.")

    top_brands = df['BRAND_CLEAN'].value_counts().dropna().head(25).index.tolist()
    current_brand = st.selectbox("Current Rs.199 Brand (this month)", top_brands)

    st.markdown("---")

    # Build user tx map
    with st.spinner("Analysing brand affinity..."):
        brand_users = set(df[df['BRAND_CLEAN'] == current_brand]['MASTER_ID'].unique())

        user_tx_map = (
            df[df['BRAND_CLEAN'].notna()]
            .sort_values('DATE')
            .groupby('MASTER_ID')['BRAND_CLEAN']
            .apply(list).to_dict()
        )

        next_brands = []
        for user in brand_users:
            tx = user_tx_map.get(user, [])
            if current_brand in tx:
                idx = tx.index(current_brand)
                for b in tx[idx+1:]:
                    if b != current_brand:
                        next_brands.append(b)
                        break

        next_counts = Counter(next_brands)

        # Score each candidate
        candidates = []
        for brand, affinity_count in next_counts.most_common(20):
            if brand == current_brand:
                continue
            bc_row = brand_city[brand_city['BRAND_CLEAN']==brand]
            cities = int(bc_row['Cities'].values[0]) if len(bc_row)>0 else 1
            total_c = int(bc_row['Total_Customers'].values[0]) if len(bc_row)>0 else 0
            affinity_pct = round(affinity_count/len(brand_users)*100, 1)

            # Score = affinity % (40%) + city coverage (30%) + scale (30%)
            city_score  = min(cities/36*100, 100)
            scale_score = min(total_c/61840*100, 100)
            final_score = (affinity_pct*0.4) + (city_score*0.3) + (scale_score*0.3)

            # Category
            cat = df[df['BRAND_CLEAN']==brand]['CATEGORY_CLEAN'].value_counts().index[0] if len(df[df['BRAND_CLEAN']==brand]) > 0 else '—'

            candidates.append({
                'Brand':         brand,
                'Affinity %':    affinity_pct,
                'Users After':   affinity_count,
                'Cities':        cities,
                'Platform Users':total_c,
                'Category':      cat,
                'Score':         round(final_score, 1)
            })

        rec_df = pd.DataFrame(candidates).sort_values('Score', ascending=False).head(5).reset_index(drop=True)

    # Winner card
    if len(rec_df) > 0:
        winner = rec_df.iloc[0]
        st.markdown(f'''
        <div style="background:#f0faf5;border:2px solid #1a7a4a;border-radius:12px;padding:20px 24px;margin-bottom:20px;">
          <div style="font-size:11px;color:#1a7a4a;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Recommended Next Brand</div>
          <div style="font-size:28px;font-weight:700;color:#111;margin-bottom:8px;">{winner["Brand"]}</div>
          <div style="display:flex;gap:24px;">
            <div><span style="font-size:20px;font-weight:700;color:#1a7a4a;">{winner["Affinity %"]}%</span><div style="font-size:11px;color:#888;">of {current_brand} users go here next</div></div>
            <div><span style="font-size:20px;font-weight:700;color:#0a4a8a;">{winner["Cities"]}</span><div style="font-size:11px;color:#888;">cities covered</div></div>
            <div><span style="font-size:20px;font-weight:700;color:#b35900;">{int(winner["Platform Users"]):,}</span><div style="font-size:11px;color:#888;">platform customers</div></div>
            <div><span style="font-size:20px;font-weight:700;color:#111;">{winner["Score"]}</span><div style="font-size:11px;color:#888;">recommendation score</div></div>
          </div>
          <div style="margin-top:12px;font-size:12px;color:#555;">
            Category: <b>{winner["Category"]}</b> &nbsp;·&nbsp;
            {int(winner["Users After"]):,} {current_brand} customers naturally visit {winner["Brand"]} after their first visit.
            High city coverage + strong affinity = ideal Rs.199 candidate.
          </div>
        </div>''', unsafe_allow_html=True)

    st.markdown("**Top 5 Recommendations**")
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(rec_df, x='Score', y='Brand', orientation='h',
                     color='Score', color_continuous_scale='Greens',
                     text='Score')
        fig.update_layout(yaxis={'categoryorder':'total ascending'},
                          margin=dict(t=10,b=10,l=10,r=10), height=300,
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          coloraxis_showscale=False)
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.scatter(rec_df, x='Affinity %', y='Cities',
                          size='Platform Users', color='Brand',
                          hover_name='Brand', size_max=40,
                          color_discrete_sequence=PLOTLY_COLORS)
        fig2.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=300,
                           paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(rec_df, use_container_width=True, hide_index=True)

    st.markdown("""
    **How the score is calculated:**
    - **Affinity % (40%)** — how many current brand users naturally go to this brand next
    - **City Coverage (30%)** — how many cities this brand is present in (nationwide = higher score)
    - **Platform Scale (30%)** — how large this brand's existing customer base is
    """)

# ══════════════════════════════════════════════════════════════════════
# CUSTOMER LOOKUP
# ══════════════════════════════════════════════════════════════════════
elif page == "Customer Lookup":
    st.markdown("## Customer Lookup")

    phone = st.text_input("Enter phone number", placeholder="e.g. 3001234567")

    if phone:
        phone = str(phone).strip()
        customer_df = df[df['MASTER_ID'].astype(str).str.strip() == phone].copy().sort_values('DATE')

        if len(customer_df) == 0:
            st.warning(f"No customer found for: {phone}")
        else:
            master_id   = str(customer_df['MASTER_ID'].iloc[0]).strip()
            rfm_row     = rfm[rfm['MASTER_ID'] == master_id]
            journey_row = journey[journey['MASTER_ID'] == master_id]

            # Only tag Rs.199 if confirmed in rs199 dataset
            is_rs199 = master_id in rs199_phones and rfm_row['IS_RS199'].values[0] if not rfm_row.empty and 'IS_RS199' in rfm_row.columns else False

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
            city        = str(customer_df['CITY'].dropna().iloc[0]) if not customer_df['CITY'].dropna().empty else '—'
            name        = str(customer_df['CUSTOMER_NAME'].dropna().iloc[0]) if 'CUSTOMER_NAME' in customer_df.columns and not customer_df['CUSTOMER_NAME'].dropna().empty else '—'
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
                  <span style="font-size:12px;color:#111;font-weight:500;">{str(cat_journey)[:80]}</span>
                </div>
              </div>
            </div>''', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                ch_data = customer_df['CHANNEL'].value_counts().reset_index()
                ch_data.columns = ['Channel','Visits']
                fig = px.pie(ch_data, names='Channel', values='Visits',
                             color='Channel', color_discrete_map=CH_COLORS, hole=0.4)
                fig.update_layout(margin=dict(t=20,b=20,l=20,r=20), height=220,
                                  paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                brand_data = customer_df['BRAND_CLEAN'].value_counts().head(6).reset_index()
                brand_data.columns = ['Brand','Visits']
                fig2 = px.bar(brand_data, x='Visits', y='Brand', orientation='h',
                              color_discrete_sequence=['#2E86AB'])
                fig2.update_layout(yaxis={'categoryorder':'total ascending'},
                                   margin=dict(t=10,b=10,l=10,r=10), height=220,
                                   paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig2, use_container_width=True)

            st.markdown(f"**All Transactions ({len(customer_df):,})**")
            tx_cols = ['DATE','CHANNEL','BRAND_CLEAN','CATEGORY_CLEAN','OFFER_TITLE','AMOUNT']
            tx = customer_df[[c for c in tx_cols if c in customer_df.columns]].copy().iloc[::-1]
            tx['DATE'] = tx['DATE'].dt.strftime('%d %b %Y')
            if 'AMOUNT' in tx.columns:
                tx['AMOUNT'] = tx['AMOUNT'].apply(lambda x: f"PKR {int(x):,}" if pd.notna(x) and x > 0 else '—')
            col_rename = {'DATE':'Date','CHANNEL':'Channel','BRAND_CLEAN':'Brand',
                          'CATEGORY_CLEAN':'Category','OFFER_TITLE':'Offer','AMOUNT':'Amount'}
            tx = tx.rename(columns={k:v for k,v in col_rename.items() if k in tx.columns})
            st.dataframe(tx, use_container_width=True, hide_index=True)
