import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Golootlo Analytics", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

# ── PASSWORD ──────────────────────────────────────────────────────────
def check_password():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        col1,col2,col3 = st.columns([1,1,1])
        with col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("<h2 style='color:#f0f4f8;text-align:center;'>📊 Golootlo Analytics</h2>", unsafe_allow_html=True)
            st.markdown("<p style='color:#718096;font-size:13px;text-align:center;'>Enter your password to continue</p>", unsafe_allow_html=True)
            pwd = st.text_input("", type="password", placeholder="Password", label_visibility="collapsed")
            if st.button("Continue →", use_container_width=True):
                if pwd == "YusraAlam1515":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Incorrect password.")
        st.stop()

check_password()

# ── STYLING ───────────────────────────────────────────────────────────
BLUE = "#0064DC"
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* {{ font-family: 'Inter', sans-serif !important; }}
.main, .block-container {{ background: #13151e !important; }}
section[data-testid="stSidebar"] {{ background: #0d0f17 !important; border-right: 1px solid #1e2235; }}
section[data-testid="stSidebar"] * {{ color: #a0aec0 !important; }}
.block-container {{ padding: 1.5rem 2rem !important; }}
h1,h2,h3 {{ color: #f0f4f8 !important; font-weight: 600 !important; letter-spacing:-0.02em !important; }}
div[data-testid="metric-container"] {{ background:#1a1d2e !important; border:1px solid #1e2235 !important; border-radius:10px !important; padding:16px 20px !important; }}
div[data-testid="metric-container"] label {{ font-size:11px !important; color:#718096 !important; text-transform:uppercase; letter-spacing:.06em; }}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{ font-size:24px !important; font-weight:600 !important; color:#f0f4f8 !important; }}
.stRadio label {{ font-size:13px !important; color:#a0aec0 !important; }}
.stSelectbox label, .stMultiSelect label {{ font-size:11px !important; color:#718096 !important; text-transform:uppercase; letter-spacing:.06em; }}
.stDataFrame {{ border:1px solid #1e2235 !important; border-radius:8px !important; }}
.g-card {{ background:#1a1d2e; border:1px solid #1e2235; border-radius:10px; padding:20px; margin-bottom:12px; }}
.g-section {{ font-size:11px; color:#718096; text-transform:uppercase; letter-spacing:.08em; font-weight:500; margin:1.5rem 0 .75rem; }}
.g-divider {{ height:1px; background:#1e2235; margin:1.5rem 0; }}
.g-caption {{ font-size:13px; color:#718096; margin-bottom:1rem; }}
.g-badge {{ display:inline-block; padding:3px 10px; border-radius:5px; font-size:12px; font-weight:500; }}
.winner-card {{ background:#0a1929; border:1.5px solid {BLUE}; border-radius:12px; padding:24px; margin-bottom:1.5rem; }}
.insight-box {{ background:#131c2e; border-left:3px solid {BLUE}; border-radius:0 8px 8px 0; padding:14px 18px; margin:1rem 0; }}
.insight-text {{ font-size:13px; color:#a0aec0; line-height:1.8; margin:0; }}
.nav-item {{ padding:8px 12px; border-radius:8px; margin:2px 0; font-size:13px; cursor:pointer; }}
</style>
""", unsafe_allow_html=True)

# ── DB ────────────────────────────────────────────────────────────────
DB_URL = "postgresql+psycopg2://postgres.sbhvdjuxasqkjrxdvmcy:YusraAlam1515@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"

@st.cache_resource
def get_engine():
    return create_engine(DB_URL, connect_args={"sslmode":"require"})

@st.cache_data(show_spinner="Loading data...")
def load_data():
    engine = get_engine()
    df      = pd.read_sql("SELECT * FROM scored",        engine)
    rfm     = pd.read_sql("SELECT * FROM rfm",           engine)
    journey = pd.read_sql("SELECT * FROM journey",       engine)
    bc      = pd.read_sql("SELECT * FROM brand_city",    engine)
    rs199p  = pd.read_sql("SELECT * FROM rs199_products",engine)
    subs    = pd.read_sql("SELECT * FROM subscriptions", engine)
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
    return df, rfm, journey, bc, rs199p, subs

df, rfm, journey, brand_city, rs199_prod, subs = load_data()

rs199_phones = set(rfm[rfm['IS_RS199']==True]['MASTER_ID'].astype(str)) if 'IS_RS199' in rfm.columns else set()

# ── COLORS ────────────────────────────────────────────────────────────
SEG_COLORS = {
    'Super Fan': '#0064DC',
    'Fan':       '#2dd4a0',
    'Loyal':     '#60a5fa',
    'At Risk':   '#fb923c',
    'New':       '#a78bfa',
    'Lost':      '#f87171'
}
SEG_BG = {
    'Super Fan': '#0a1929',
    'Fan':       '#0a2420',
    'Loyal':     '#0f1e35',
    'At Risk':   '#2e1a0e',
    'New':       '#1e1535',
    'Lost':      '#2e1515'
}
CH_COLORS = {'Instore':'#0064DC','Delivery':'#f472b6','Ecom':'#fb923c'}
SUB_COLORS = {'Pizza':'#0064DC','Burger':'#f472b6','Juices & Beverages':'#fb923c','Coffee':'#2dd4a0','Bakery & Desserts':'#a78bfa','Ice Cream':'#f87171'}

PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter', color='#a0aec0', size=13),
    margin=dict(t=30,b=20,l=10,r=10),
    legend=dict(font=dict(size=12,color='#a0aec0'), bgcolor='rgba(0,0,0,0)'),
    xaxis=dict(showgrid=True, gridcolor='#1e2235', zeroline=False, tickfont=dict(size=12,color='#718096')),
    yaxis=dict(showgrid=True, gridcolor='#1e2235', zeroline=False, tickfont=dict(size=12,color='#718096')),
)

def gc(fig, height=300):
    fig.update_layout(**PLOTLY_LAYOUT, height=height)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False})

# ── SIDEBAR ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<div style='padding:8px 0 16px;'><span style='font-size:20px;font-weight:700;color:#f0f4f8;'>📊 Golootlo</span><br><span style='font-size:12px;color:#718096;'>Jan – Aug 2026</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='g-divider'></div>", unsafe_allow_html=True)
    page = st.radio("", [
        "🏠  Dashboard",
        "👥  RFM Segments",
        "🔗  Brand Affinity",
        "🍕  Product Affinity",
        "⭐  Rs.199 Recommender",
        "📋  Subscriptions",
        "🔍  Customer Lookup"
    ], label_visibility="collapsed")
    st.markdown("<div class='g-divider'></div>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:12px;color:#718096;line-height:1.8;'>{df['MASTER_ID'].nunique():,} customers<br>{len(df):,} transactions<br>{df['BRAND_CLEAN'].nunique():,} brands</p>", unsafe_allow_html=True)

page = page.split("  ")[1].strip()

# ══════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════
if page == "Dashboard":
    st.markdown("## Dashboard")
    st.markdown("<p class='g-caption'>Jan 1 – Aug 31, 2026 · All channels</p>", unsafe_allow_html=True)

    # KPI row
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Total Customers",    f"{df['MASTER_ID'].nunique():,}")
    c2.metric("Total Transactions", f"{len(df):,}")
    c3.metric("Unique Brands",      f"{df['BRAND_CLEAN'].nunique():,}")
    c4.metric("Delivery Spend",     f"PKR {df[df['CHANNEL']=='Delivery']['AMOUNT'].sum():,.0f}")
    c5.metric("Rs.199 Users",       f"{len(rs199_phones):,}")

    st.markdown("<div class='g-section'>Transaction trend</div>", unsafe_allow_html=True)

    # Toggle monthly/weekly
    trend_toggle = st.radio("View", ["Monthly","By Channel"], horizontal=True)

    monthly = df.groupby(['YEAR','MONTH_NUM','MONTH_NAME']).size().reset_index(name='Transactions')
    monthly = monthly.sort_values(['YEAR','MONTH_NUM'])
    monthly['Month'] = monthly['MONTH_NAME'].str[:3] + ' ' + monthly['YEAR'].astype(str)

    if trend_toggle == "Monthly":
        fig = px.line(monthly, x='Month', y='Transactions', markers=True,
                      color_discrete_sequence=[BLUE], line_shape='spline')
        fig.update_traces(line_width=2.5, marker_size=7, marker_color=BLUE,
                          fill='tozeroy', fillcolor='rgba(0,100,220,0.08)')
        gc(fig, 300)
    else:
        ch_monthly = df.groupby(['MONTH_NUM','MONTH_NAME','CHANNEL']).size().reset_index(name='Transactions')
        ch_monthly = ch_monthly.sort_values('MONTH_NUM')
        ch_monthly['Month'] = ch_monthly['MONTH_NAME'].str[:3]
        fig = px.line(ch_monthly, x='Month', y='Transactions', color='CHANNEL',
                      color_discrete_map=CH_COLORS, markers=True, line_shape='spline')
        fig.update_traces(line_width=2.5, marker_size=6)
        gc(fig, 300)

    col1,col2 = st.columns(2)

    with col1:
        st.markdown("<div class='g-section'>Top 10 cities by volume</div>", unsafe_allow_html=True)
        city_vol = df[df['CITY'].notna()&(df['CITY'].astype(str).str.strip()!='')&(df['CITY'].astype(str).str.strip()!='--')].groupby('CITY').size().sort_values(ascending=False).head(10).reset_index()
        city_vol.columns = ['City','Transactions']
        fig2 = px.bar(city_vol.sort_values('Transactions'), x='Transactions', y='City',
                      orientation='h', color_discrete_sequence=[BLUE])
        fig2.update_traces(marker_line_width=0, marker_color=BLUE)
        gc(fig2, 340)

    with col2:
        st.markdown("<div class='g-section'>Top 5 categories by vertical</div>", unsafe_allow_html=True)
        ch_sel = st.selectbox("Channel", ["Instore","Delivery","Ecom"], key="dash_ch")
        cat_vol = df[df['CHANNEL']==ch_sel].groupby('CATEGORY_CLEAN').size().sort_values(ascending=False).head(5).reset_index()
        cat_vol.columns = ['Category','Transactions']
        fig3 = px.bar(cat_vol.sort_values('Transactions'), x='Transactions', y='Category',
                      orientation='h', color_discrete_sequence=[CH_COLORS.get(ch_sel,BLUE)])
        fig3.update_traces(marker_line_width=0)
        gc(fig3, 340)

    st.markdown("<div class='g-section'>Vertical trendlines</div>", unsafe_allow_html=True)
    col3,col4,col5 = st.columns(3)
    for col, ch, color in [(col3,'Instore',BLUE),(col4,'Delivery','#f472b6'),(col5,'Ecom','#fb923c')]:
        with col:
            st.markdown(f"<p style='font-size:12px;font-weight:500;color:{color};margin-bottom:6px;'>{ch}</p>", unsafe_allow_html=True)
            ch_t = df[df['CHANNEL']==ch].groupby(['MONTH_NUM','MONTH_NAME']).size().reset_index(name='Tx')
            ch_t = ch_t.sort_values('MONTH_NUM')
            ch_t['Month'] = ch_t['MONTH_NAME'].str[:3]
            fig_ch = px.area(ch_t, x='Month', y='Tx', color_discrete_sequence=[color])
            fig_ch.update_traces(line_width=2, fillcolor=f'rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.1)')
            gc(fig_ch, 200)

# ══════════════════════════════════════════════════════════════════════
# RFM SEGMENTS
# ══════════════════════════════════════════════════════════════════════
elif page == "RFM Segments":
    st.markdown("## RFM Segments")

    col_f1,col_f2,col_f3 = st.columns(3)
    with col_f1:
        month_filter = st.multiselect("Month", sorted(df['MONTH_NAME'].dropna().unique().tolist()), default=[])
    with col_f2:
        seg_filter = st.selectbox("Segment", ["All"]+list(SEG_COLORS.keys()))
    with col_f3:
        ch_filter = st.multiselect("Channel", ["Instore","Delivery","Ecom"], default=[])

    rfm_display = rfm.copy()
    if seg_filter != "All":
        rfm_display = rfm_display[rfm_display['Segment']==seg_filter]

    seg_info = {
        'Super Fan': ('10+ transactions per month. Your most engaged users.', 'VIP treatment. Exclusive access. Make them brand advocates.'),
        'Fan':       ('5-10 transactions per month. Highly active.',           'Reward consistency. Push them toward Super Fan.'),
        'Loyal':     ('3-5 transactions per month. Solid core base.',          'Personalised offers based on favourite brand/category.'),
        'At Risk':   ('Going quiet. Was active, now slowing down.',            'Win-back campaign urgently. Time-sensitive offer.'),
        'New':       ('Just joined. 1-2 transactions total, seen recently.',   'Nurture fast. Second visit within 7 days is critical.'),
        'Lost':      ('Inactive. Less than 2 tx/month, not seen recently.',    'One reactivation push only. Then write off.'),
    }

    seg_counts = rfm['Segment'].value_counts()
    total = seg_counts.sum()

    rows = ''
    for seg,(who,action) in seg_info.items():
        if seg_filter != "All" and seg != seg_filter: continue
        count = int(seg_counts.get(seg,0))
        pct   = round(count/total*100,1)
        color = SEG_COLORS.get(seg,'#a0aec0')
        bg    = SEG_BG.get(seg,'#1a1d2e')
        bar_w = int(pct*2)
        rows += f'''<tr style="border-bottom:1px solid #1e2235;">
          <td style="padding:14px 16px;width:13%;">
            <span style="background:{bg};color:{color};padding:4px 12px;border-radius:6px;font-size:13px;font-weight:500;">{seg}</span>
          </td>
          <td style="padding:14px 16px;width:20%;">
            <div style="display:flex;align-items:center;gap:8px;">
              <div style="width:{bar_w}px;height:6px;background:{color};border-radius:3px;opacity:.7;min-width:2px;"></div>
              <span style="font-size:14px;font-weight:600;color:#f0f4f8;">{count:,}</span>
              <span style="font-size:12px;color:#718096;">({pct}%)</span>
            </div>
          </td>
          <td style="padding:14px 16px;font-size:13px;color:#a0aec0;width:32%;">{who}</td>
          <td style="padding:14px 16px;font-size:13px;color:#e2e8f0;width:35%;">{action}</td>
        </tr>'''

    st.markdown(f'''
    <div style="background:#1a1d2e;border:1px solid #1e2235;border-radius:12px;overflow:hidden;margin-bottom:20px;">
      <div style="padding:14px 18px;border-bottom:1px solid #1e2235;background:#13162a;">
        <span style="font-size:14px;font-weight:600;color:#f0f4f8;">Customer Segments — Jan to Aug 2026</span>
        <span style="font-size:12px;color:#718096;margin-left:8px;">{total:,} total customers</span>
      </div>
      <table style="width:100%;border-collapse:collapse;font-family:Inter,sans-serif;">
        <thead><tr style="background:#13162a;border-bottom:1px solid #1e2235;">
          <th style="padding:10px 16px;text-align:left;font-size:11px;color:#718096;font-weight:500;text-transform:uppercase;letter-spacing:.07em;">Segment</th>
          <th style="padding:10px 16px;text-align:left;font-size:11px;color:#718096;font-weight:500;text-transform:uppercase;letter-spacing:.07em;">Count</th>
          <th style="padding:10px 16px;text-align:left;font-size:11px;color:#718096;font-weight:500;text-transform:uppercase;letter-spacing:.07em;">Who they are</th>
          <th style="padding:10px 16px;text-align:left;font-size:11px;color:#718096;font-weight:500;text-transform:uppercase;letter-spacing:.07em;">What to do</th>
        </tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>''', unsafe_allow_html=True)

    col1,col2 = st.columns(2)
    with col1:
        seg_df = seg_counts.reset_index(); seg_df.columns=['Segment','Customers']
        fig = px.bar(seg_df.sort_values('Customers'), x='Customers', y='Segment',
                     orientation='h', color='Segment', color_discrete_map=SEG_COLORS)
        fig.update_traces(marker_line_width=0)
        gc(fig,300)
    with col2:
        ch_seg = df.groupby(['Segment','CHANNEL']).size().unstack(fill_value=0).reset_index()
        ch_cols = [c for c in ['Instore','Delivery','Ecom'] if c in ch_seg.columns]
        fig2 = px.bar(ch_seg, x='Segment', y=ch_cols, color_discrete_map=CH_COLORS, barmode='stack')
        fig2.update_traces(marker_line_width=0)
        gc(fig2,300)

    if seg_filter != "All":
        st.markdown(f"<div class='g-section'>Top brands for {seg_filter}</div>", unsafe_allow_html=True)
        seg_users = rfm[rfm['Segment']==seg_filter]['MASTER_ID'].tolist()
        seg_brands = df[df['MASTER_ID'].isin(seg_users)]['BRAND_CLEAN'].value_counts().head(10).reset_index()
        seg_brands.columns=['Brand','Transactions']
        fig3 = px.bar(seg_brands.sort_values('Transactions'), x='Transactions', y='Brand',
                      orientation='h', color_discrete_sequence=[SEG_COLORS.get(seg_filter,BLUE)])
        fig3.update_traces(marker_line_width=0)
        gc(fig3,320)

# ══════════════════════════════════════════════════════════════════════
# BRAND AFFINITY
# ══════════════════════════════════════════════════════════════════════
elif page == "Brand Affinity":
    st.markdown("## Brand Affinity")

    col_f1,col_f2 = st.columns(2)
    with col_f1:
        vertical = st.selectbox("Channel Vertical", ["All","Instore","Delivery","Ecom"])
    with col_f2:
        df_v = df[df['CHANNEL']==vertical] if vertical != "All" else df
        top_brands = df_v['BRAND_CLEAN'].value_counts().dropna().head(25).index.tolist()
        selected_brands = st.multiselect("Select Brands", top_brands, default=[top_brands[0]] if top_brands else [])

    if not selected_brands:
        st.info("Select at least one brand to see affinity data.")
    else:
        for brand in selected_brands:
            brand_users = set(df_v[df_v['BRAND_CLEAN']==brand]['MASTER_ID'].unique())

            also_use = df_v[
                (df_v['MASTER_ID'].isin(brand_users)) &
                (df_v['BRAND_CLEAN']!=brand) &
                (df_v['BRAND_CLEAN'].notna())
            ]['BRAND_CLEAN'].value_counts().head(8).reset_index()
            also_use.columns = ['Brand','Users']

            user_tx = (df_v[df_v['BRAND_CLEAN'].notna()].sort_values('DATE')
                       .groupby('MASTER_ID')['BRAND_CLEAN'].apply(list).to_dict())
            next_b = []
            for u in brand_users:
                tx = user_tx.get(u,[])
                if brand in tx:
                    idx = tx.index(brand)
                    for b in tx[idx+1:]:
                        if b != brand: next_b.append(b); break
            next_df = pd.DataFrame(Counter(next_b).most_common(8), columns=['Brand','Users'])
            if len(next_df)>0: next_df['%']=(next_df['Users']/len(brand_users)*100).round(1)

            bc_row = brand_city[brand_city['BRAND_CLEAN']==brand]
            cities_n = int(bc_row['Cities'].values[0]) if len(bc_row)>0 else '—'

            st.markdown(f"<div class='g-section'>{brand} · {vertical}</div>", unsafe_allow_html=True)
            c1,c2,c3 = st.columns(3)
            c1.metric("Unique Customers",   f"{len(brand_users):,}")
            c2.metric("Cities Present",     f"{cities_n}")
            c3.metric("Move to Next Brand", f"{int(next_df['Users'].iloc[0]):,}" if len(next_df)>0 else "—")

            col1,col2 = st.columns(2)
            with col1:
                if len(also_use)>0:
                    fig = px.bar(also_use.sort_values('Users'), x='Users', y='Brand',
                                 orientation='h', title="Customers also use",
                                 color_discrete_sequence=[BLUE])
                    fig.update_traces(marker_line_width=0)
                    gc(fig,300)
            with col2:
                if len(next_df)>0:
                    fig2 = px.bar(next_df.sort_values('Users'), x='Users', y='Brand',
                                  orientation='h', title="Next brand after first visit",
                                  color_discrete_sequence=['#2dd4a0'])
                    fig2.update_traces(marker_line_width=0)
                    gc(fig2,300)

            st.markdown("<div class='g-divider'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# PRODUCT AFFINITY
# ══════════════════════════════════════════════════════════════════════
elif page == "Product Affinity":
    st.markdown("## Product Affinity")
    st.markdown("<p class='g-caption'>Based on Rs.199 campaign food subcategories — Pizza, Burger, Coffee, Juices, Bakery, Ice Cream.</p>", unsafe_allow_html=True)

    col_f1,col_f2 = st.columns(2)
    with col_f1:
        city_filter_p = st.multiselect("Filter by City", sorted(rs199_prod['CITY'].dropna().unique().tolist()), default=[])
    with col_f2:
        sub_filter = st.multiselect("Filter by Subcategory", sorted(rs199_prod['FOOD_SUBCATEGORY'].dropna().unique().tolist()) if 'FOOD_SUBCATEGORY' in rs199_prod.columns and rs199_prod['FOOD_SUBCATEGORY'].notna().any() else [], default=[])

    df_p = rs199_prod.copy()
    if city_filter_p: df_p = df_p[df_p['CITY'].isin(city_filter_p)]

    has_subcategory = 'FOOD_SUBCATEGORY' in df_p.columns and df_p['FOOD_SUBCATEGORY'].notna().any()

    if has_subcategory:
        if sub_filter: df_p = df_p[df_p['FOOD_SUBCATEGORY'].isin(sub_filter)]
        sub_counts = df_p['FOOD_SUBCATEGORY'].value_counts().reset_index()
        sub_counts.columns = ['Subcategory','Transactions']

        col1,col2 = st.columns(2)
        with col1:
            fig = px.bar(sub_counts.sort_values('Transactions'), x='Transactions', y='Subcategory',
                         orientation='h', color='Subcategory', color_discrete_map=SUB_COLORS)
            fig.update_traces(marker_line_width=0)
            gc(fig,280)
        with col2:
            fig2 = px.pie(sub_counts, names='Subcategory', values='Transactions',
                          color='Subcategory', color_discrete_map=SUB_COLORS, hole=0.55)
            fig2.update_traces(textposition='outside', textfont_size=12, textfont_color='#a0aec0')
            gc(fig2,280)

        # Affinity matrix
        all_subs = df_p['FOOD_SUBCATEGORY'].dropna().unique().tolist()
        aff = []
        for sa in all_subs:
            ua = set(df_p[df_p['FOOD_SUBCATEGORY']==sa]['USER_PHONE'].unique())
            for sb in all_subs:
                if sa==sb: continue
                ub = set(df_p[df_p['FOOD_SUBCATEGORY']==sb]['USER_PHONE'].unique())
                ov = len(ua&ub)
                if ov>0: aff.append({'From':sa,'To':sb,'Users':ov,'Overlap %':round(ov/len(ua)*100,1)})
        aff_df = pd.DataFrame(aff).sort_values('Users',ascending=False) if aff else pd.DataFrame()

        if len(aff_df)>0:
            top_pair = aff_df.iloc[0]
            niche = sub_counts.iloc[-1]['Subcategory'] if len(sub_counts)>0 else '—'
            insight = f"<strong style='color:#f0f4f8;'>{top_pair['From']} and {top_pair['To']}</strong> have the strongest overlap — <strong style='color:{BLUE};'>{int(top_pair['Users']):,} users</strong> bought both ({top_pair['Overlap %']}% of {top_pair['From']} buyers also bought {top_pair['To']}). <strong style='color:#f0f4f8;'>{niche}</strong> has the lowest cross-buying. <br><br><strong style='color:#f0f4f8;'>What this means:</strong> If you ran a {top_pair['From']} campaign this month, {top_pair['To']} buyers are your most natural next audience — they already overlap heavily."
            st.markdown(f"<div class='insight-box'><p class='insight-text'>{insight}</p></div>", unsafe_allow_html=True)

            col1,col2 = st.columns(2)
            with col1:
                fig3 = px.density_heatmap(aff_df, x='To', y='From', z='Users',
                                          color_continuous_scale=[[0,'#1a1d2e'],[0.5,'#003d85'],[1,BLUE]],
                                          text_auto=True)
                fig3.update_traces(textfont_size=12, textfont_color='#ffffff')
                gc(fig3,300)
            with col2:
                top_pairs = aff_df.head(8).copy()
                top_pairs['Pair'] = top_pairs['From']+' → '+top_pairs['To']
                fig4 = px.bar(top_pairs.sort_values('Users'), x='Users', y='Pair',
                              orientation='h', color='Users',
                              color_continuous_scale=[[0,'#1e2235'],[1,BLUE]])
                fig4.update_traces(marker_line_width=0)
                fig4.update_layout(coloraxis_showscale=False)
                gc(fig4,300)

            st.markdown("<div class='g-section'>Top pairs — plain view</div>", unsafe_allow_html=True)
            aff_df['Insight'] = aff_df.apply(lambda r: f"{int(r['Users']):,} users who used {r['From']} also used {r['To']} ({r['Overlap %']}% overlap)",axis=1)
            st.dataframe(aff_df.head(10)[['From','To','Users','Overlap %','Insight']], use_container_width=True, hide_index=True)
    else:
        # No subcategory — show brand level affinity
        st.markdown("<div class='g-section'>Brand volume in Rs.199 campaign</div>", unsafe_allow_html=True)
        brand_counts = df_p['BRAND_NAME'].value_counts().head(10).reset_index()
        brand_counts.columns = ['Brand','Scans']
        fig = px.bar(brand_counts.sort_values('Scans'), x='Scans', y='Brand',
                     orientation='h', color_discrete_sequence=[BLUE])
        fig.update_traces(marker_line_width=0)
        gc(fig,320)

    st.markdown("<div class='g-section'>Product mix by city (top 10)</div>", unsafe_allow_html=True)
    city_brand = df_p.groupby(['CITY','BRAND_NAME']).size().reset_index(name='Scans')
    city_top = city_brand.groupby('CITY')['Scans'].sum().sort_values(ascending=False).head(10).index.tolist()
    city_brand_f = city_brand[city_brand['CITY'].isin(city_top)]
    fig5 = px.bar(city_brand_f, x='CITY', y='Scans', color='BRAND_NAME', barmode='stack')
    fig5.update_traces(marker_line_width=0)
    fig5.update_xaxes(tickangle=30)
    gc(fig5,320)

# ══════════════════════════════════════════════════════════════════════
# RS.199 RECOMMENDER
# ══════════════════════════════════════════════════════════════════════
elif page == "Rs.199 Recommender":
    st.markdown("## Next Rs.199 Campaign Recommender")
    st.markdown("<p class='g-caption'>Instore only. Scored on brand affinity + category fit + city coverage.</p>", unsafe_allow_html=True)

    instore_brands = df[df['CHANNEL']=='Instore']['BRAND_CLEAN'].value_counts().dropna().head(25).index.tolist()
    col_f1,col_f2 = st.columns(2)
    with col_f1:
        current_brand = st.selectbox("Current Rs.199 Brand (this month)", instore_brands)
    with col_f2:
        preferred_cat = st.multiselect("Preferred Category", ['Food','Fashion','Entertainment','Health','Travel'], default=['Food'])

    with st.spinner("Analysing brand affinity..."):
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
        for brand,aff_count in next_counts.most_common(30):
            if brand==current_brand: continue
            bc_row = brand_city[brand_city['BRAND_CLEAN']==brand]
            cities  = int(bc_row['Cities'].values[0]) if len(bc_row)>0 else 1
            total_c = int(bc_row['Total_Customers'].values[0]) if len(bc_row)>0 else 0
            cat = df[df['BRAND_CLEAN']==brand]['CATEGORY_CLEAN'].value_counts().index[0] if len(df[df['BRAND_CLEAN']==brand])>0 else '—'
            cat_fit = 1.2 if (not preferred_cat or cat in preferred_cat) else 0.7
            aff_pct = round(aff_count/len(brand_users)*100,1)
            city_score  = min(cities/36*100,100)
            scale_score = min(total_c/61840*100,100)
            final_score = round((aff_pct*0.4+city_score*0.3+scale_score*0.3)*cat_fit,1)
            candidates.append({'Brand':brand,'Affinity %':aff_pct,'Users after':aff_count,'Cities':cities,'Platform users':total_c,'Category':cat,'Score':final_score})
        rec_df = pd.DataFrame(candidates).sort_values('Score',ascending=False).head(5).reset_index(drop=True) if candidates else pd.DataFrame()

    if len(rec_df)>0:
        winner = rec_df.iloc[0]
        st.markdown(f'''
        <div class="winner-card">
          <div style="font-size:11px;color:{BLUE};text-transform:uppercase;letter-spacing:.08em;font-weight:600;margin-bottom:6px;">Recommended Next Brand</div>
          <div style="font-size:28px;font-weight:700;color:#f0f4f8;margin-bottom:16px;">{winner["Brand"]}</div>
          <div style="display:flex;gap:32px;">
            <div style="text-align:center;"><div style="font-size:24px;font-weight:600;color:{BLUE};">{winner["Affinity %"]}%</div><div style="font-size:12px;color:#718096;margin-top:4px;">of {current_brand} users go here next</div></div>
            <div style="text-align:center;"><div style="font-size:24px;font-weight:600;color:#2dd4a0;">{winner["Cities"]}</div><div style="font-size:12px;color:#718096;margin-top:4px;">cities covered</div></div>
            <div style="text-align:center;"><div style="font-size:24px;font-weight:600;color:#fb923c;">{int(winner["Platform users"]):,}</div><div style="font-size:12px;color:#718096;margin-top:4px;">platform customers</div></div>
            <div style="text-align:center;"><div style="font-size:24px;font-weight:600;color:#f0f4f8;">{winner["Score"]}</div><div style="font-size:12px;color:#718096;margin-top:4px;">recommendation score</div></div>
          </div>
          <p style="margin-top:16px;font-size:13px;color:#a0aec0;">Category: <strong style="color:#f0f4f8;">{winner["Category"]}</strong> · {int(winner["Users after"]):,} {current_brand} customers naturally visit {winner["Brand"]} after their first instore visit.</p>
        </div>''', unsafe_allow_html=True)

        col1,col2 = st.columns(2)
        with col1:
            fig = px.bar(rec_df.sort_values('Score'), x='Score', y='Brand', orientation='h',
                         color='Score', color_continuous_scale=[[0,'#0a1929'],[1,BLUE]], text='Score')
            fig.update_traces(textposition='outside', textfont_color='#f0f4f8', marker_line_width=0)
            fig.update_layout(coloraxis_showscale=False)
            gc(fig,280)
        with col2:
            fig2 = px.scatter(rec_df, x='Affinity %', y='Cities', size='Platform users',
                              color='Brand', hover_name='Brand', size_max=40)
            fig2.update_traces(marker_line_width=0)
            gc(fig2,280)

        st.markdown("<div class='g-section'>All recommendations</div>", unsafe_allow_html=True)
        st.dataframe(rec_df, use_container_width=True, hide_index=True)

        st.markdown(f"<div class='g-card'><p style='font-size:13px;color:#718096;margin:0;'><strong style='color:#a0aec0;'>Score formula:</strong> Affinity % (40%) + City coverage (30%) + Platform scale (30%), adjusted by category fit (1.2x match, 0.7x mismatch). Instore brands only.</p></div>", unsafe_allow_html=True)
    else:
        st.warning("No candidates found. Try changing the category filter.")

# ══════════════════════════════════════════════════════════════════════
# SUBSCRIPTIONS
# ══════════════════════════════════════════════════════════════════════
elif page == "Subscriptions":
    st.markdown("## Subscriptions")
    st.markdown("<p class='g-caption'>Jan – Aug 2026 · All subscription packages</p>", unsafe_allow_html=True)

    col_f1,col_f2 = st.columns(2)
    with col_f1:
        city_filter_s = st.multiselect("Filter by City", sorted(subs['City'].dropna().unique().tolist()), default=[])
    with col_f2:
        pkg_filter = st.multiselect("Filter by Package", sorted(subs['Subscription_Package'].dropna().unique().tolist()), default=[])

    subs_f = subs.copy()
    if city_filter_s: subs_f = subs_f[subs_f['City'].isin(city_filter_s)]
    if pkg_filter:    subs_f = subs_f[subs_f['Subscription_Package'].isin(pkg_filter)]

    # KPIs
    total_subs   = len(subs_f)
    active_subs  = len(subs_f[subs_f['Subscription_Status']=='active'])
    lapsed_subs  = total_subs - active_subs
    auto_payment = len(subs_f[subs_f['Transaction_Type'].str.lower().isin(['easypaisa','jazzcash','jazzcash checkout','ufone','jazz'])])

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Subscriptions", f"{total_subs:,}")
    c2.metric("Active",              f"{active_subs:,}")
    c3.metric("Lapsed",              f"{lapsed_subs:,}")
    c4.metric("Auto Payment",        f"{auto_payment:,}")

    col1,col2 = st.columns(2)

    with col1:
        st.markdown("<div class='g-section'>Package breakdown</div>", unsafe_allow_html=True)
        pkg = subs_f['Subscription_Package'].value_counts().reset_index()
        pkg.columns = ['Package','Count']
        fig = px.bar(pkg.sort_values('Count'), x='Count', y='Package',
                     orientation='h', color_discrete_sequence=[BLUE])
        fig.update_traces(marker_line_width=0)
        gc(fig,300)

    with col2:
        st.markdown("<div class='g-section'>Active vs Lapsed</div>", unsafe_allow_html=True)
        status = subs_f['Subscription_Status'].value_counts().reset_index()
        status.columns = ['Status','Count']
        fig2 = px.pie(status, names='Status', values='Count', hole=0.55,
                      color_discrete_sequence=[BLUE,'#f87171'])
        fig2.update_traces(textposition='outside', textfont_size=12, textfont_color='#a0aec0')
        gc(fig2,300)

    col3,col4 = st.columns(2)

    with col3:
        st.markdown("<div class='g-section'>Auto vs Manual payment</div>", unsafe_allow_html=True)
        auto_methods = ['easypaisa','jazzcash','jazzcash checkout','ufone','jazz']
        subs_f['Payment_Type'] = subs_f['Transaction_Type'].str.lower().apply(
            lambda x: 'Auto' if x in auto_methods else 'Manual'
        )
        pay = subs_f['Payment_Type'].value_counts().reset_index()
        pay.columns = ['Type','Count']
        fig3 = px.pie(pay, names='Type', values='Count', hole=0.55,
                      color_discrete_sequence=[BLUE,'#2dd4a0'])
        fig3.update_traces(textposition='outside', textfont_size=12, textfont_color='#a0aec0')
        gc(fig3,300)

    with col4:
        st.markdown("<div class='g-section'>Payment method breakdown</div>", unsafe_allow_html=True)
        pay_method = subs_f['Transaction_Type'].value_counts().head(8).reset_index()
        pay_method.columns = ['Method','Count']
        fig4 = px.bar(pay_method.sort_values('Count'), x='Count', y='Method',
                      orientation='h', color_discrete_sequence=['#2dd4a0'])
        fig4.update_traces(marker_line_width=0)
        gc(fig4,300)

    st.markdown("<div class='g-section'>Top 15 cities by subscriptions</div>", unsafe_allow_html=True)
    city_subs = subs_f.groupby('City').size().sort_values(ascending=False).head(15).reset_index()
    city_subs.columns = ['City','Subscriptions']
    col5,col6 = st.columns(2)
    with col5:
        fig5 = px.bar(city_subs.sort_values('Subscriptions'), x='Subscriptions', y='City',
                      orientation='h', color_discrete_sequence=[BLUE])
        fig5.update_traces(marker_line_width=0)
        gc(fig5,380)
    with col6:
        city_pkg = subs_f.groupby(['City','Subscription_Package']).size().reset_index(name='Count')
        city_top_s = city_subs.head(8)['City'].tolist()
        city_pkg_f = city_pkg[city_pkg['City'].isin(city_top_s)]
        fig6 = px.bar(city_pkg_f, x='City', y='Count', color='Subscription_Package', barmode='stack')
        fig6.update_traces(marker_line_width=0)
        fig6.update_xaxes(tickangle=30)
        gc(fig6,380)

# ══════════════════════════════════════════════════════════════════════
# CUSTOMER LOOKUP
# ══════════════════════════════════════════════════════════════════════
elif page == "Customer Lookup":
    st.markdown("## Customer Lookup")
    st.markdown("<p class='g-caption'>Search any customer by phone number to see their full profile.</p>", unsafe_allow_html=True)

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
            avg_m   = round(float(rfm_row['Avg_Monthly_Tx'].values[0]),1) if not rfm_row.empty and 'Avg_Monthly_Tx' in rfm_row.columns else '—'
            ch_j    = j_row['Channel_Journey'].values[0] if not j_row.empty else '—'
            cat_j   = j_row['Category_Journey'].values[0] if not j_row.empty else '—'
            top_b   = j_row['Top_Brand'].values[0] if not j_row.empty else '—'
            top_c   = j_row['Top_Category'].values[0] if not j_row.empty else '—'
            city    = str(cdf['CITY'].dropna().iloc[0]) if not cdf['CITY'].dropna().empty else '—'
            name    = str(cdf['CUSTOMER_NAME'].dropna().iloc[0]) if 'CUSTOMER_NAME' in cdf.columns and not cdf['CUSTOMER_NAME'].dropna().empty else '—'
            fd      = cdf['DATE'].min().strftime('%d %b %Y')
            ld      = cdf['DATE'].max().strftime('%d %b %Y')
            seg_c   = SEG_COLORS.get(seg,'#a0aec0')
            seg_bg  = SEG_BG.get(seg,'#1a1d2e')
            rs_badge = f'<span style="background:#2e1f0e;color:#fb923c;padding:3px 10px;border-radius:5px;font-size:12px;font-weight:500;">🟡 Rs.199 User</span>' if is_rs199 else ''

            # Check subscription
            sub_row = subs[subs['User_Number'].astype(str).str.replace('.0','').str.strip()==phone] if len(subs)>0 else pd.DataFrame()
            sub_badge = f'<span style="background:#0a1929;color:{BLUE};padding:3px 10px;border-radius:5px;font-size:12px;font-weight:500;">📋 Subscriber</span>' if len(sub_row)>0 else ''
            sub_pkg   = sub_row['Subscription_Package'].iloc[0] if len(sub_row)>0 else None

            st.markdown(f'''
            <div style="background:#1a1d2e;border:1px solid #1e2235;border-radius:12px;overflow:hidden;margin-bottom:16px;">
              <div style="padding:18px 22px;border-bottom:1px solid #1e2235;display:flex;justify-content:space-between;align-items:center;">
                <div>
                  <span style="font-size:18px;font-weight:600;color:#f0f4f8;">{name}</span>
                  <span style="font-size:13px;color:#718096;margin-left:10px;">{phone} · {city}</span>
                  <span style="margin-left:8px;">{rs_badge}</span>
                  <span style="margin-left:8px;">{sub_badge}</span>
                  {'<span style="font-size:12px;color:#718096;margin-left:6px;">· '+sub_pkg+'</span>' if sub_pkg else ''}
                </div>
                <span style="background:{seg_bg};color:{seg_c};padding:5px 14px;border-radius:8px;font-size:14px;font-weight:600;">{seg}</span>
              </div>
              <div style="display:grid;grid-template-columns:repeat(6,1fr);border-bottom:1px solid #1e2235;">
                <div style="padding:14px 16px;border-right:1px solid #1e2235;text-align:center;"><div style="font-size:22px;font-weight:600;color:#f0f4f8;">{rec}d</div><div style="font-size:11px;color:#718096;text-transform:uppercase;letter-spacing:.05em;margin-top:3px;">Last Visit · R {r_s}/5</div></div>
                <div style="padding:14px 16px;border-right:1px solid #1e2235;text-align:center;"><div style="font-size:22px;font-weight:600;color:#f0f4f8;">{freq}</div><div style="font-size:11px;color:#718096;text-transform:uppercase;letter-spacing:.05em;margin-top:3px;">Transactions · F {f_s}/5</div></div>
                <div style="padding:14px 16px;border-right:1px solid #1e2235;text-align:center;"><div style="font-size:20px;font-weight:600;color:#f0f4f8;">{avg_m}/mo</div><div style="font-size:11px;color:#718096;text-transform:uppercase;letter-spacing:.05em;margin-top:3px;">Avg Monthly Tx</div></div>
                <div style="padding:14px 16px;border-right:1px solid #1e2235;text-align:center;"><div style="font-size:20px;font-weight:600;color:#f0f4f8;">PKR {int(mon):,}</div><div style="font-size:11px;color:#718096;text-transform:uppercase;letter-spacing:.05em;margin-top:3px;">Delivery Spend · M {m_s}/5</div></div>
                <div style="padding:14px 16px;border-right:1px solid #1e2235;text-align:center;"><div style="font-size:14px;font-weight:500;color:#f0f4f8;">{top_b}</div><div style="font-size:11px;color:#718096;margin-top:3px;">Fav Brand · {top_c}</div></div>
                <div style="padding:14px 16px;text-align:center;"><div style="font-size:12px;font-weight:500;color:#f0f4f8;">{fd}</div><div style="font-size:11px;color:#718096;">First Seen</div><div style="font-size:12px;font-weight:500;color:#f0f4f8;margin-top:6px;">{ld}</div><div style="font-size:11px;color:#718096;">Last Seen</div></div>
              </div>
              <div style="display:flex;border-bottom:1px solid #1e2235;">
                <div style="flex:1;padding:10px 22px;border-right:1px solid #1e2235;"><span style="font-size:11px;color:#718096;text-transform:uppercase;letter-spacing:.05em;">Channel Journey </span><span style="font-size:13px;color:#e2e8f0;font-weight:500;margin-left:6px;">{ch_j}</span></div>
                <div style="flex:1;padding:10px 22px;"><span style="font-size:11px;color:#718096;text-transform:uppercase;letter-spacing:.05em;">Category Journey </span><span style="font-size:13px;color:#e2e8f0;font-weight:500;margin-left:6px;">{str(cat_j)[:80]}</span></div>
              </div>
            </div>''', unsafe_allow_html=True)

            col1,col2 = st.columns(2)
            with col1:
                ch_d = cdf['CHANNEL'].value_counts().reset_index(); ch_d.columns=['Channel','Visits']
                fig = px.pie(ch_d, names='Channel', values='Visits', color='Channel',
                             color_discrete_map=CH_COLORS, hole=0.55)
                fig.update_traces(textposition='outside', textfont_size=12, textfont_color='#a0aec0')
                gc(fig,220)
            with col2:
                bd = cdf['BRAND_CLEAN'].value_counts().head(6).reset_index(); bd.columns=['Brand','Visits']
                fig2 = px.bar(bd.sort_values('Visits'), x='Visits', y='Brand', orientation='h',
                              color_discrete_sequence=[BLUE])
                fig2.update_traces(marker_line_width=0)
                gc(fig2,220)

            st.markdown(f"<div class='g-section'>All Transactions ({len(cdf):,})</div>", unsafe_allow_html=True)
            tx_cols = ['DATE','CHANNEL','BRAND_CLEAN','CATEGORY_CLEAN','OFFER_TITLE','OFFER_DESC','AMOUNT']
            tx = cdf[[c for c in tx_cols if c in cdf.columns]].copy().iloc[::-1]
            tx['DATE'] = tx['DATE'].dt.strftime('%d %b %Y')
            if 'AMOUNT' in tx.columns:
                tx['AMOUNT'] = tx['AMOUNT'].apply(lambda x: f"PKR {int(x):,}" if pd.notna(x) and x>0 else '—')
            tx = tx.rename(columns={'DATE':'Date','CHANNEL':'Channel','BRAND_CLEAN':'Brand',
                                    'CATEGORY_CLEAN':'Category','OFFER_TITLE':'Offer',
                                    'OFFER_DESC':'Deal','AMOUNT':'Amount'})
            st.dataframe(tx, use_container_width=True, hide_index=True)
