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
        col1,col2,col3 = st.columns([1,1,1])
        with col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("<h2 style='color:#f0f4f8;text-align:center;'>Golootlo Analytics</h2>", unsafe_allow_html=True)
            st.markdown("<p style='color:#718096;font-size:13px;text-align:center;'>Enter your password to continue</p>", unsafe_allow_html=True)
            pwd = st.text_input("", type="password", placeholder="Password", label_visibility="collapsed")
            if st.button("Continue", use_container_width=True):
                if pwd == "Golootlo2026":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Incorrect password.")
        st.stop()

check_password()

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
.g-card {{ background:#1a1d2e; border:1px solid #1e2235; border-radius:10px; padding:20px; margin-bottom:12px; }}
.g-section {{ font-size:11px; color:#718096; text-transform:uppercase; letter-spacing:.08em; font-weight:500; margin:1.5rem 0 .75rem; }}
.g-divider {{ height:1px; background:#1e2235; margin:1.5rem 0; }}
.g-caption {{ font-size:13px; color:#718096; margin-bottom:1rem; }}
.winner-card {{ background:#0a1929; border:1.5px solid {BLUE}; border-radius:12px; padding:24px; margin-bottom:1.5rem; }}
.disclaimer {{ background:#1a1520; border:1px solid #3d1f3d; border-radius:8px; padding:12px 16px; margin-bottom:16px; font-size:12px; color:#a78bfa; }}
</style>
""", unsafe_allow_html=True)

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
    aff     = pd.read_sql("SELECT * FROM brand_affinity",engine)
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
    return df, rfm, journey, bc, rs199p, subs, aff

df, rfm, journey, brand_city, rs199_prod, subs, affinity_db = load_data()

# Merge segment into df
df = df.merge(rfm[['MASTER_ID','Segment']], on='MASTER_ID', how='left')

rs199_phones = set(rfm[rfm['IS_RS199']==True]['MASTER_ID'].astype(str)) if 'IS_RS199' in rfm.columns else set()

MONTH_ORDER = ['January','February','March','April','May','June','July','August','September','October','November','December']

SEG_COLORS = {
    'Super Fan': BLUE,
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
CH_COLORS = {'Instore':BLUE,'Delivery':'#f472b6','Ecom':'#fb923c'}

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

with st.sidebar:
    st.markdown(f"<div style='padding:8px 0 16px;'><span style='font-size:18px;font-weight:700;color:#f0f4f8;'>Golootlo Analytics</span><br><span style='font-size:12px;color:#718096;'>Jan – Aug 2026</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='g-divider'></div>", unsafe_allow_html=True)
    page = st.radio("", [
        "Dashboard",
        "RFM Segments",
        "Brand Affinity",
        "Rs.199 Recommender",
        "Subscriptions",
        "Customer Lookup"
    ], label_visibility="collapsed")
    st.markdown("<div class='g-divider'></div>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:12px;color:#718096;line-height:1.8;'>{df['MASTER_ID'].nunique():,} customers<br>{len(df):,} transactions<br>{df['BRAND_CLEAN'].nunique():,} brands with transactions</p>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════
if page == "Dashboard":
    st.markdown("## Dashboard")
    st.markdown("<p class='g-caption'>Jan 1 – Aug 31, 2026 · All channels</p>", unsafe_allow_html=True)

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Total Customers",    f"{df['MASTER_ID'].nunique():,}")
    c2.metric("Total Transactions", f"{len(df):,}")
    c3.metric("Unique Brands",      f"{df['BRAND_CLEAN'].nunique():,}")
    c4.metric("Delivery Spend",     f"PKR {df[df['CHANNEL']=='Delivery']['AMOUNT'].sum():,.0f}")
    c5.metric("Rs.199 Users",       f"{len(rs199_phones):,}")

    st.markdown("<div class='g-section'>Transaction trend</div>", unsafe_allow_html=True)
    trend_toggle = st.radio("View", ["Monthly","By Channel"], horizontal=True)

    monthly = df.groupby(['YEAR','MONTH_NUM','MONTH_NAME']).size().reset_index(name='Transactions')
    monthly = monthly.sort_values(['YEAR','MONTH_NUM'])
    monthly['Month'] = monthly['MONTH_NAME'].str[:3] + ' ' + monthly['YEAR'].astype(str)

    if trend_toggle == "Monthly":
        fig = px.line(monthly, x='Month', y='Transactions', markers=True,
                      color_discrete_sequence=[BLUE], line_shape='spline')
        fig.update_traces(line_width=2.5, marker_size=7, fill='tozeroy',
                          fillcolor='rgba(0,100,220,0.08)')
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
        city_vol = df[
            df['CITY'].notna() &
            (df['CITY'].astype(str).str.strip()!='') &
            (df['CITY'].astype(str).str.strip()!='--')
        ].groupby('CITY').size().sort_values(ascending=False).head(10).reset_index()
        city_vol.columns=['City','Transactions']
        fig2 = px.bar(city_vol.sort_values('Transactions'), x='Transactions', y='City',
                      orientation='h', color_discrete_sequence=[BLUE])
        fig2.update_traces(marker_line_width=0)
        gc(fig2, 340)

    with col2:
        st.markdown("<div class='g-section'>Top 5 categories by vertical</div>", unsafe_allow_html=True)
        ch_sel = st.selectbox("Channel", ["Instore","Delivery","Ecom"], key="dash_ch_cat")
        cat_vol = df[df['CHANNEL']==ch_sel].groupby('CATEGORY_CLEAN').size().sort_values(ascending=False).head(5).reset_index()
        cat_vol.columns=['Category','Transactions']
        fig3 = px.bar(cat_vol.sort_values('Transactions'), x='Transactions', y='Category',
                      orientation='h', color_discrete_sequence=[CH_COLORS.get(ch_sel,BLUE)])
        fig3.update_traces(marker_line_width=0)
        gc(fig3, 340)

    col3,col4 = st.columns(2)
    with col3:
        st.markdown("<div class='g-section'>Top 5 brands by vertical</div>", unsafe_allow_html=True)
        ch_sel2 = st.selectbox("Channel", ["Instore","Delivery","Ecom"], key="dash_ch_brand")
        brand_vol = df[(df['CHANNEL']==ch_sel2) & df['BRAND_CLEAN'].notna()].groupby('BRAND_CLEAN').size().sort_values(ascending=False).head(5).reset_index()
        brand_vol.columns=['Brand','Transactions']
        fig4 = px.bar(brand_vol.sort_values('Transactions'), x='Transactions', y='Brand',
                      orientation='h', color_discrete_sequence=[CH_COLORS.get(ch_sel2,BLUE)])
        fig4.update_traces(marker_line_width=0)
        gc(fig4, 300)

    with col4:
        st.markdown("<div class='g-section'>Vertical trendlines</div>", unsafe_allow_html=True)
        ch_trend = df.groupby(['MONTH_NUM','CHANNEL']).size().reset_index(name='Tx')
        ch_trend = ch_trend.sort_values('MONTH_NUM')
        month_map = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug'}
        ch_trend['Month'] = ch_trend['MONTH_NUM'].map(month_map)
        fig5 = px.line(ch_trend, x='Month', y='Tx', color='CHANNEL',
                       color_discrete_map=CH_COLORS, markers=True, line_shape='spline')
        fig5.update_traces(line_width=2, marker_size=5)
        gc(fig5, 300)

# ══════════════════════════════════════════════════════════════════════
# RFM SEGMENTS
# ══════════════════════════════════════════════════════════════════════
elif page == "RFM Segments":
    st.markdown("## RFM Segments")

    col_f1,col_f2 = st.columns(2)
    with col_f1:
        available_months = [m for m in MONTH_ORDER if m in df['MONTH_NAME'].dropna().unique()]
        month_filter = st.multiselect("Month", available_months, default=[])
    with col_f2:
        seg_filter = st.selectbox("Segment", ["All"]+list(SEG_COLORS.keys()))

    seg_info = {
        'Super Fan': ('10+ transactions/month. Most engaged users.', 'VIP treatment. Exclusive access. Make them brand advocates.'),
        'Fan':       ('5-10 transactions/month. Highly active.',      'Reward consistency. Push toward Super Fan.'),
        'Loyal':     ('3-5 transactions/month. Solid core base.',     'Personalised offers based on favourite brand or category.'),
        'At Risk':   ('Going quiet. Was active, now slowing down.',   'Win-back campaign urgently. Time-sensitive offer.'),
        'New':       ('Just joined. Seen recently, low transactions.','Nurture fast. Second visit within 7 days is critical.'),
        'Lost':      ('Less than 2 tx/month. Not seen recently.',     'One reactivation push only. Then write off.'),
    }

    seg_counts = rfm['Segment'].value_counts()
    total = seg_counts.sum()

    rows = ''
    for seg,(who,action) in seg_info.items():
        if seg_filter != "All" and seg != seg_filter: continue
        count = int(seg_counts.get(seg,0))
        pct   = round(count/total*100,1)
        color = SEG_COLORS.get(seg,'#a0aec0')
        bar_w = int(pct*2)
        rows += f'''<tr style="border-bottom:1px solid #1e2235;">
          <td style="padding:14px 16px;width:13%;font-size:14px;font-weight:600;color:{color};">{seg}</td>
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
      <div style="padding:14px 18px;border-bottom:1px solid #1e2235;">
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

    st.markdown("<div class='g-section'>Rs.199 usage & subscriptions by segment</div>", unsafe_allow_html=True)
    col3,col4 = st.columns(2)
    with col3:
        rs199_seg = rfm.groupby('Segment')['IS_RS199'].sum().reset_index()
        rs199_seg.columns=['Segment','Rs199_Users']
        fig3 = px.bar(rs199_seg.sort_values('Rs199_Users'), x='Rs199_Users', y='Segment',
                      orientation='h', color='Segment', color_discrete_map=SEG_COLORS,
                      title="Rs.199 users per segment")
        fig3.update_traces(marker_line_width=0)
        gc(fig3,280)
    with col4:
        if len(subs)>0:
            sub_phones = set(subs['User_Number'].dropna().astype(str).str.replace('.0','').str.strip().unique())
            rfm['Is_Subscriber'] = rfm['MASTER_ID'].astype(str).isin(sub_phones)
            sub_seg = rfm.groupby('Segment')['Is_Subscriber'].sum().reset_index()
            sub_seg.columns=['Segment','Subscribers']
            fig4 = px.bar(sub_seg.sort_values('Subscribers'), x='Subscribers', y='Segment',
                          orientation='h', color='Segment', color_discrete_map=SEG_COLORS,
                          title="Subscribers per segment")
            fig4.update_traces(marker_line_width=0)
            gc(fig4,280)

    if seg_filter != "All":
        st.markdown(f"<div class='g-section'>Top brands for {seg_filter}</div>", unsafe_allow_html=True)
        seg_users = rfm[rfm['Segment']==seg_filter]['MASTER_ID'].tolist()
        seg_brands = df[df['MASTER_ID'].isin(seg_users)]['BRAND_CLEAN'].value_counts().head(10).reset_index()
        seg_brands.columns=['Brand','Transactions']
        fig5 = px.bar(seg_brands.sort_values('Transactions'), x='Transactions', y='Brand',
                      orientation='h', color_discrete_sequence=[SEG_COLORS.get(seg_filter,BLUE)])
        fig5.update_traces(marker_line_width=0)
        gc(fig5,320)

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
        all_brands = sorted(df_v['BRAND_CLEAN'].value_counts().dropna().index.tolist())
        selected_brands = st.multiselect("Select Brands (up to 3)", all_brands,
                                          default=[all_brands[0]] if all_brands else [],
                                          max_selections=3)

    st.markdown("<div class='g-section'>Top 5 brands by volume</div>", unsafe_allow_html=True)
    top5 = df_v['BRAND_CLEAN'].value_counts().dropna().head(5).reset_index()
    top5.columns=['Brand','Transactions']
    fig_ov = px.bar(top5.sort_values('Transactions'), x='Transactions', y='Brand',
                    orientation='h', color_discrete_sequence=[BLUE])
    fig_ov.update_traces(marker_line_width=0)
    gc(fig_ov, 240)

    if not selected_brands:
        st.info("Select up to 3 brands above to see detailed affinity.")
    else:
        for brand in selected_brands:
            brand_aff = affinity_db[(affinity_db['Brand']==brand) & (affinity_db['Channel']==vertical)]
            also_use  = brand_aff[brand_aff['Type']=='also_use'].sort_values('Rank')[['Related_Brand','Users']]
            next_brand = brand_aff[brand_aff['Type']=='next_brand'].sort_values('Rank')[['Related_Brand','Users']]
            if len(next_brand)>0:
                next_brand = next_brand.copy()
                next_brand['%'] = (next_brand['Users']/next_brand['Users'].sum()*100).round(1)

            bc_row   = brand_city[brand_city['BRAND_CLEAN']==brand]
            cities_n = int(bc_row['Cities'].values[0]) if len(bc_row)>0 else '—'
            brand_channels = df[df['BRAND_CLEAN']==brand]['CHANNEL'].unique().tolist()
            channel_note = f" · Present on: {', '.join(brand_channels)}"

            st.markdown(f"<div class='g-section'>{brand}{channel_note}</div>", unsafe_allow_html=True)
            c1,c2,c3 = st.columns(3)
            c1.metric("Unique Customers",   f"{df_v[df_v['BRAND_CLEAN']==brand]['MASTER_ID'].nunique():,}")
            c2.metric("Cities Present",     f"{cities_n}")
            c3.metric("Move to Next Brand", f"{int(next_brand['Users'].iloc[0]):,}" if len(next_brand)>0 else "—")

            col1,col2 = st.columns(2)
            with col1:
                st.markdown("<p style='font-size:12px;color:#718096;margin-bottom:4px;'>Which other brands do this brand's customers use — at any point in time.</p>", unsafe_allow_html=True)
                if len(also_use)>0:
                    fig = px.bar(also_use.sort_values('Users'), x='Users', y='Related_Brand',
                                 orientation='h', title="Customers also use",
                                 color_discrete_sequence=[BLUE])
                    fig.update_traces(marker_line_width=0)
                    gc(fig,280)
            with col2:
                st.markdown("<p style='font-size:12px;color:#718096;margin-bottom:4px;'>After visiting this brand for the first time, which brand did customers go to next.</p>", unsafe_allow_html=True)
                if len(next_brand)>0:
                    fig2 = px.bar(next_brand.sort_values('Users'), x='Users', y='Related_Brand',
                                  orientation='h', title="Next brand after first visit",
                                  color_discrete_sequence=['#2dd4a0'])
                    fig2.update_traces(marker_line_width=0)
                    gc(fig2,280)

            if len(brand_channels)>1 and vertical=="All":
                st.markdown(f"<div class='g-section'>{brand} — affinity by channel</div>", unsafe_allow_html=True)
                ch_cols_display = st.columns(len(brand_channels))
                for ci,ch in enumerate(brand_channels):
                    ch_aff = affinity_db[
                        (affinity_db['Brand']==brand) &
                        (affinity_db['Channel']==ch) &
                        (affinity_db['Type']=='next_brand')
                    ].sort_values('Rank')
                    ch_users = df[(df['CHANNEL']==ch) & (df['BRAND_CLEAN']==brand)]['MASTER_ID'].nunique()
                    with ch_cols_display[ci]:
                        st.markdown(f"<p style='font-size:12px;color:{CH_COLORS.get(ch,BLUE)};font-weight:500;'>{ch} ({ch_users:,} users)</p>", unsafe_allow_html=True)
                        if len(ch_aff)>0:
                            fig_ch = px.bar(ch_aff.sort_values('Users'), x='Users', y='Related_Brand',
                                            orientation='h', color_discrete_sequence=[CH_COLORS.get(ch,BLUE)])
                            fig_ch.update_traces(marker_line_width=0)
                            gc(fig_ch,220)

            st.markdown("<div class='g-divider'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# RS.199 RECOMMENDER
# ══════════════════════════════════════════════════════════════════════
elif page == "Rs.199 Recommender":
    st.markdown("## Next Rs.199 Campaign Recommender")
    st.markdown("<p class='g-caption'>Instore only · Scored on brand affinity + city coverage + platform scale</p>", unsafe_allow_html=True)

    st.markdown("<div class='disclaimer'>KFC and Domino's are excluded — both are dominant platform brands that would always rank first. Recommendations surface brands with strong natural affinity and real growth potential, including emerging brands.</div>", unsafe_allow_html=True)

    EXCLUDED_BRANDS = ['KFC', "Domino's"]

    # All instore brands — not just food, not just rs199 brands
    all_instore_brands = sorted(
        df[(df['CHANNEL']=='Instore') &
           (df['BRAND_CLEAN'].notna()) &
           (~df['BRAND_CLEAN'].isin(EXCLUDED_BRANDS))]
        ['BRAND_CLEAN'].value_counts().index.tolist()
    )

    col_f1,col_f2 = st.columns(2)
    with col_f1:
        # Multi-select for last 1-3 campaigns
        past_brands = st.multiselect(
            "Select past Rs.199 brand(s) — up to 3",
            all_instore_brands,
            default=[all_instore_brands[0]] if all_instore_brands else [],
            max_selections=3
        )
    with col_f2:
        all_cities_r = sorted(df[df['CHANNEL']=='Instore']['CITY'].dropna().unique().tolist())
        city_scope = st.multiselect("City Scope", ["Nationwide"] + all_cities_r, default=["Nationwide"])

    if not past_brands:
        st.info("Select at least one past Rs.199 brand above.")
        st.stop()

    with st.spinner("Analysing affinity across selected brands..."):
        if "Nationwide" in city_scope or not city_scope:
            df_instore = df[(df['CHANNEL']=='Instore') & (df['BRAND_CLEAN'].notna())]
        else:
            df_instore = df[(df['CHANNEL']=='Instore') & (df['BRAND_CLEAN'].notna()) & (df['CITY'].isin(city_scope))]

        # Combine affinity from all selected past brands
        combined_scores = {}

        for current_brand in past_brands:
            brand_next_aff = affinity_db[
                (affinity_db['Brand']==current_brand) &
                (affinity_db['Channel']=='Instore') &
                (affinity_db['Type']=='next_brand')
            ].sort_values('Users', ascending=False)

            brand_users = set(df_instore[df_instore['BRAND_CLEAN']==current_brand]['MASTER_ID'].unique())
            if len(brand_users)==0: continue

            for _,row in brand_next_aff.iterrows():
                brand = row['Related_Brand']
                if brand in past_brands + EXCLUDED_BRANDS: continue

                bc_row  = brand_city[brand_city['BRAND_CLEAN']==brand]
                cities  = int(bc_row['Cities'].values[0]) if len(bc_row)>0 else 1
                total_c = int(bc_row['Total_Customers'].values[0]) if len(bc_row)>0 else 0
                aff_pct = round(row['Users']/len(brand_users)*100,1)
                city_score  = min(cities/36*100,100)
                scale_score = min(total_c/61840*100,100)
                score = round(aff_pct*0.4 + city_score*0.3 + scale_score*0.3, 1)

                if brand not in combined_scores:
                    combined_scores[brand] = {
                        'Brand':brand,'Cities':cities,'Platform users':total_c,
                        'Total Affinity':aff_pct,'Total Users':int(row['Users']),
                        'Score':score,'Appears in':1
                    }
                else:
                    combined_scores[brand]['Total Affinity'] += aff_pct
                    combined_scores[brand]['Total Users'] += int(row['Users'])
                    combined_scores[brand]['Score'] += score
                    combined_scores[brand]['Appears in'] += 1

        if combined_scores:
            rec_df = pd.DataFrame(combined_scores.values())
            # Boost brands that appear across multiple past campaigns
            rec_df['Score'] = rec_df['Score'] * (1 + rec_df['Appears in']*0.1)
            rec_df['Affinity %'] = (rec_df['Total Affinity']/rec_df['Appears in']).round(1)
            rec_df = rec_df.sort_values('Score', ascending=False)
        else:
            rec_df = pd.DataFrame()

        # Split established vs emerging
        top_rec  = rec_df[rec_df['Platform users']>=3000].head(5) if len(rec_df)>0 else pd.DataFrame()
        emerging = rec_df[rec_df['Platform users']<3000].head(5) if len(rec_df)>0 else pd.DataFrame()

    if len(top_rec)>0:
        winner = top_rec.iloc[0]
        past_brands_str = ' + '.join(past_brands)
        appears_in = int(winner["Appears in"])
        appears_note = f'<div style="margin-top:8px;font-size:12px;color:#2dd4a0;">Appears in affinity data for {appears_in} of your selected brand(s)</div>' if appears_in > 1 else ''

        st.markdown(f"""
<div style="background:#0a1929;border:1.5px solid {BLUE};border-radius:12px;padding:24px;margin-bottom:1.5rem;">
  <div style="display:flex;align-items:center;gap:32px;">
    <div style="flex:1;">
      <div style="font-size:11px;color:{BLUE};text-transform:uppercase;letter-spacing:.08em;font-weight:600;margin-bottom:8px;">Recommended Next Brand</div>
      <div style="font-size:32px;font-weight:700;color:#f0f4f8;line-height:1.1;">{winner["Brand"]}</div>
      <div style="font-size:13px;color:#718096;margin-top:8px;">Based on affinity from: <strong style="color:#a0aec0;">{past_brands_str}</strong>. Customers from these campaigns naturally visit {winner["Brand"]} next.</div>
      {appears_note}
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;min-width:320px;">
      <div style="text-align:center;background:#0d1929;border-radius:8px;padding:14px;">
        <div style="font-size:28px;font-weight:700;color:{BLUE};">{winner["Affinity %"]}%</div>
        <div style="font-size:11px;color:#718096;margin-top:4px;">Avg Affinity Score</div>
      </div>
      <div style="text-align:center;background:#0d1929;border-radius:8px;padding:14px;">
        <div style="font-size:28px;font-weight:700;color:#2dd4a0;">{winner["Cities"]}</div>
        <div style="font-size:11px;color:#718096;margin-top:4px;">Cities Covered</div>
      </div>
      <div style="text-align:center;background:#0d1929;border-radius:8px;padding:14px;">
        <div style="font-size:28px;font-weight:700;color:#fb923c;">{int(winner["Platform users"]):,}</div>
        <div style="font-size:11px;color:#718096;margin-top:4px;">Platform Customers</div>
      </div>
      <div style="text-align:center;background:#0d1929;border-radius:8px;padding:14px;">
        <div style="font-size:28px;font-weight:700;color:#f0f4f8;">{round(winner["Score"],1)}</div>
        <div style="font-size:11px;color:#718096;margin-top:4px;">Combined Score</div>
      </div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

        # Combine top + emerging for chart — minimum 3 brands shown
        chart_df = top_rec.copy()
        if len(chart_df) < 3 and len(emerging) > 0:
            needed = 3 - len(chart_df)
            chart_df = pd.concat([chart_df, emerging.head(needed)], ignore_index=True)
        chart_df = chart_df.drop_duplicates(subset=['Brand']).sort_values('Score', ascending=False).head(6)

        col1,col2 = st.columns(2)
        with col1:
            fig = px.bar(chart_df.sort_values('Score'), x='Score', y='Brand',
                         orientation='h', color='Score',
                         color_continuous_scale=[[0,'#0a1929'],[1,BLUE]], text='Score')
            fig.update_traces(textposition='outside', textfont_color='#f0f4f8', marker_line_width=0)
            fig.update_layout(coloraxis_showscale=False)
            gc(fig,300)
        with col2:
            fig2 = px.scatter(chart_df, x='Affinity %', y='Cities', size='Platform users',
                              color='Brand', hover_name='Brand', size_max=40)
            fig2.update_traces(marker_line_width=0)
            gc(fig2,300)

        if len(emerging)>0:
            st.markdown("<div class='g-section'>Emerging brands — low volume, strong affinity signal</div>", unsafe_allow_html=True)
            st.markdown("<p class='g-caption'>These brands have fewer platform users but customers from your past campaigns naturally go there. High-risk, high-reward picks. Test in 2-3 cities first before going nationwide.</p>", unsafe_allow_html=True)
            em_rows = ''
            for _,r in emerging.iterrows():
                em_rows += f'''<tr style="border-bottom:1px solid #1e2235;">
                  <td style="padding:12px 16px;font-size:14px;font-weight:500;color:#f0f4f8;">{r["Brand"]}</td>
                  <td style="padding:12px 16px;font-size:13px;color:{BLUE};">{r["Affinity %"]}% affinity</td>
                  <td style="padding:12px 16px;font-size:13px;color:#2dd4a0;">{r["Cities"]} cities</td>
                  <td style="padding:12px 16px;font-size:13px;color:#718096;">{int(r["Platform users"]):,} users</td>
                  <td style="padding:12px 16px;font-size:12px;color:#a0aec0;">Strong affinity signal. Lower scale but worth testing in select cities first.</td>
                </tr>'''
            st.markdown(f'''
            <div style="background:#1a1d2e;border:1px solid #1e2235;border-radius:10px;overflow:hidden;">
              <table style="width:100%;border-collapse:collapse;font-family:Inter,sans-serif;">
                <thead><tr style="background:#13162a;border-bottom:1px solid #1e2235;">
                  <th style="padding:10px 16px;font-size:11px;color:#718096;font-weight:500;text-transform:uppercase;text-align:left;">Brand</th>
                  <th style="padding:10px 16px;font-size:11px;color:#718096;font-weight:500;text-transform:uppercase;text-align:left;">Affinity</th>
                  <th style="padding:10px 16px;font-size:11px;color:#718096;font-weight:500;text-transform:uppercase;text-align:left;">Coverage</th>
                  <th style="padding:10px 16px;font-size:11px;color:#718096;font-weight:500;text-transform:uppercase;text-align:left;">Scale</th>
                  <th style="padding:10px 16px;font-size:11px;color:#718096;font-weight:500;text-transform:uppercase;text-align:left;">Why</th>
                </tr></thead>
                <tbody>{em_rows}</tbody>
              </table>
            </div>''', unsafe_allow_html=True)

        st.markdown("<div class='g-section'>Full recommendations</div>", unsafe_allow_html=True)
        st.dataframe(top_rec, use_container_width=True, hide_index=True)
        st.markdown(f"<div class='g-card'><p style='font-size:13px;color:#718096;margin:0;'><strong style='color:#a0aec0;'>Score formula:</strong> Affinity % (40%) + City coverage (30%) + Platform scale (30%). Food brands only. KFC excluded. Instore only.</p></div>", unsafe_allow_html=True)
    else:
        st.warning("No food brand candidates found. Try changing the city scope.")

# ══════════════════════════════════════════════════════════════════════
# SUBSCRIPTIONS
# ══════════════════════════════════════════════════════════════════════
elif page == "Subscriptions":
    st.markdown("## Subscriptions")
    st.markdown("<p class='g-caption'>Jan – Aug 2026 · All subscription packages</p>", unsafe_allow_html=True)

    col_f1,col_f2 = st.columns(2)
    with col_f1:
        city_filter_s = st.multiselect("City", sorted(subs['City'].dropna().unique().tolist()), default=[])
    with col_f2:
        pkg_filter = st.multiselect("Package", sorted(subs['Subscription_Package'].dropna().unique().tolist()), default=[])

    subs_f = subs.copy()
    if city_filter_s: subs_f = subs_f[subs_f['City'].isin(city_filter_s)]
    if pkg_filter:    subs_f = subs_f[subs_f['Subscription_Package'].isin(pkg_filter)]

    total_subs  = len(subs_f)
    active_subs = len(subs_f[subs_f['Subscription_Status']=='active'])
    lapsed_subs = total_subs - active_subs
    auto_methods = ['easypaisa','jazzcash','jazzcash checkout','ufone','jazz']
    auto_pay = len(subs_f[subs_f['Transaction_Type'].str.lower().isin(auto_methods)])

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Subscriptions", f"{total_subs:,}")
    c2.metric("Active",              f"{active_subs:,}")
    c3.metric("Lapsed",              f"{lapsed_subs:,}")
    c4.metric("Auto Payment",        f"{auto_pay:,}")

    col1,col2 = st.columns(2)
    with col1:
        st.markdown("<div class='g-section'>Package breakdown</div>", unsafe_allow_html=True)
        pkg = subs_f['Subscription_Package'].value_counts().reset_index()
        pkg.columns=['Package','Count']
        fig = px.bar(pkg.sort_values('Count'), x='Count', y='Package',
                     orientation='h', color_discrete_sequence=[BLUE])
        fig.update_traces(marker_line_width=0)
        gc(fig,300)
    with col2:
        st.markdown("<div class='g-section'>Active vs Lapsed</div>", unsafe_allow_html=True)
        status = subs_f['Subscription_Status'].value_counts().reset_index()
        status.columns=['Status','Count']
        fig2 = px.pie(status, names='Status', values='Count', hole=0.55,
                      color_discrete_sequence=[BLUE,'#f87171'])
        fig2.update_traces(textposition='outside', textfont_size=12, textfont_color='#a0aec0')
        gc(fig2,300)

    col3,col4 = st.columns(2)
    with col3:
        st.markdown("<div class='g-section'>Auto vs Manual payment</div>", unsafe_allow_html=True)
        subs_f2 = subs_f.copy()
        subs_f2['Payment_Type'] = subs_f2['Transaction_Type'].str.lower().apply(
            lambda x: 'Auto' if x in auto_methods else 'Manual'
        )
        pay = subs_f2['Payment_Type'].value_counts().reset_index()
        pay.columns=['Type','Count']
        fig3 = px.pie(pay, names='Type', values='Count', hole=0.55,
                      color_discrete_sequence=[BLUE,'#2dd4a0'])
        fig3.update_traces(textposition='outside', textfont_size=12, textfont_color='#a0aec0')
        gc(fig3,300)
    with col4:
        st.markdown("<div class='g-section'>Payment method breakdown</div>", unsafe_allow_html=True)
        pay_method = subs_f['Transaction_Type'].value_counts().head(8).reset_index()
        pay_method.columns=['Method','Count']
        fig4 = px.bar(pay_method.sort_values('Count'), x='Count', y='Method',
                      orientation='h', color_discrete_sequence=['#2dd4a0'])
        fig4.update_traces(marker_line_width=0)
        gc(fig4,300)

    st.markdown("<div class='g-section'>Top cities by subscriptions</div>", unsafe_allow_html=True)
    col5,col6 = st.columns(2)
    with col5:
        city_subs = subs_f.groupby('City').size().sort_values(ascending=False).head(15).reset_index()
        city_subs.columns=['City','Subscriptions']
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
    st.markdown("<p class='g-caption'>Search any customer by phone number.</p>", unsafe_allow_html=True)

    phone = st.text_input("", placeholder="Enter phone number — e.g. 3001234567", label_visibility="collapsed")

    if phone:
        phone = str(phone).strip()
        cdf = df[df['MASTER_ID'].astype(str).str.strip()==phone].copy().sort_values('DATE')

        if len(cdf)==0:
            st.warning(f"No customer found for: {phone}")
        else:
            mid     = str(cdf['MASTER_ID'].iloc[0]).strip()
            rfm_row = rfm[rfm['MASTER_ID']==mid]
            j_row   = journey[journey['MASTER_ID']==mid]
            is_rs199 = mid in rs199_phones and (bool(rfm_row['IS_RS199'].values[0]) if not rfm_row.empty and 'IS_RS199' in rfm_row.columns else False)

            seg   = rfm_row['Segment'].values[0] if not rfm_row.empty else '—'
            rec   = int(rfm_row['Recency'].values[0]) if not rfm_row.empty else '—'
            freq  = int(rfm_row['Frequency'].values[0]) if not rfm_row.empty else '—'
            mon   = float(rfm_row['Monetary'].values[0]) if not rfm_row.empty else 0
            r_s   = int(rfm_row['R_Score'].values[0]) if not rfm_row.empty else '—'
            f_s   = int(rfm_row['F_Score'].values[0]) if not rfm_row.empty else '—'
            m_s   = int(rfm_row['M_Score'].values[0]) if not rfm_row.empty else '—'
            avg_m = round(float(rfm_row['Avg_Monthly_Tx'].values[0]),1) if not rfm_row.empty and 'Avg_Monthly_Tx' in rfm_row.columns else '—'
            ch_j  = j_row['Channel_Journey'].values[0] if not j_row.empty else '—'
            cat_j = j_row['Category_Journey'].values[0] if not j_row.empty else '—'
            top_b = j_row['Top_Brand'].values[0] if not j_row.empty else '—'
            top_c = j_row['Top_Category'].values[0] if not j_row.empty else '—'
            city  = str(cdf['CITY'].dropna().iloc[0]) if not cdf['CITY'].dropna().empty else '—'
            name  = str(cdf['CUSTOMER_NAME'].dropna().iloc[0]) if 'CUSTOMER_NAME' in cdf.columns and not cdf['CUSTOMER_NAME'].dropna().empty else '—'
            fd    = cdf['DATE'].min().strftime('%d %b %Y')
            ld    = cdf['DATE'].max().strftime('%d %b %Y')
            seg_c  = SEG_COLORS.get(seg,'#a0aec0')
            seg_bg = SEG_BG.get(seg,'#1a1d2e')

            sub_row = subs[subs['User_Number'].astype(str).str.replace('.0','').str.strip()==phone] if len(subs)>0 else pd.DataFrame()
            sub_pkg = sub_row['Subscription_Package'].iloc[0] if len(sub_row)>0 else None

            badges = ''
            if is_rs199: badges += f'<span style="background:#2e1f0e;color:#fb923c;padding:3px 10px;border-radius:5px;font-size:12px;font-weight:500;margin-right:6px;">Rs.199 User</span>'
            if sub_pkg:  badges += f'<span style="background:#0a1929;color:{BLUE};padding:3px 10px;border-radius:5px;font-size:12px;font-weight:500;">{sub_pkg}</span>'

            st.markdown(f'''
            <div style="background:#1a1d2e;border:1px solid #1e2235;border-radius:12px;overflow:hidden;margin-bottom:16px;">
              <div style="padding:16px 22px;border-bottom:1px solid #1e2235;display:flex;justify-content:space-between;align-items:center;">
                <div>
                  <span style="font-size:20px;font-weight:600;color:#f0f4f8;">{name}</span>
                  <span style="font-size:13px;color:#718096;margin-left:10px;">{phone} · {city}</span>
                  <div style="margin-top:6px;">{badges}</div>
                </div>
                <span style="background:{seg_bg};color:{seg_c};padding:6px 16px;border-radius:8px;font-size:15px;font-weight:600;">{seg}</span>
              </div>
              <div style="display:grid;grid-template-columns:repeat(4,1fr);border-bottom:1px solid #1e2235;">
                <div style="padding:16px 20px;border-right:1px solid #1e2235;">
                  <div style="font-size:11px;color:#718096;text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px;">Last Visit</div>
                  <div style="font-size:26px;font-weight:600;color:#f0f4f8;">{rec}d ago</div>
                  <div style="font-size:12px;color:#718096;margin-top:4px;">Recency score {r_s}/5</div>
                </div>
                <div style="padding:16px 20px;border-right:1px solid #1e2235;">
                  <div style="font-size:11px;color:#718096;text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px;">Transactions</div>
                  <div style="font-size:26px;font-weight:600;color:#f0f4f8;">{freq}</div>
                  <div style="font-size:12px;color:#718096;margin-top:4px;">{avg_m}/month avg · F {f_s}/5</div>
                </div>
                <div style="padding:16px 20px;border-right:1px solid #1e2235;">
                  <div style="font-size:11px;color:#718096;text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px;">Delivery Spend</div>
                  <div style="font-size:26px;font-weight:600;color:#f0f4f8;">PKR {int(mon):,}</div>
                  <div style="font-size:12px;color:#718096;margin-top:4px;">Monetary score {m_s}/5</div>
                </div>
                <div style="padding:16px 20px;">
                  <div style="font-size:11px;color:#718096;text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px;">Favourite</div>
                  <div style="font-size:20px;font-weight:600;color:#f0f4f8;">{top_b}</div>
                  <div style="font-size:12px;color:#718096;margin-top:4px;">{top_c}</div>
                </div>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;border-bottom:1px solid #1e2235;">
                <div style="padding:12px 22px;border-right:1px solid #1e2235;">
                  <span style="font-size:11px;color:#718096;text-transform:uppercase;letter-spacing:.06em;">Channel Journey  </span>
                  <span style="font-size:13px;color:#e2e8f0;font-weight:500;">{ch_j}</span>
                </div>
                <div style="padding:12px 22px;">
                  <span style="font-size:11px;color:#718096;text-transform:uppercase;letter-spacing:.06em;">Active  </span>
                  <span style="font-size:13px;color:#e2e8f0;font-weight:500;">{fd} → {ld}</span>
                </div>
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
