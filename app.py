import streamlit as st
import pandas as pd
from lead_scoring import score_leads

# 🌟 Clean UI styling
st.set_page_config(page_title="SmartLeadRanker", page_icon="📊", layout="wide")
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 SmartLeadRanker")
st.caption("Enriched leads. Ready to engage. Start outreach with one click.")

uploaded_file = st.file_uploader("📤 Upload your leads CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip().str.lower()

    # 🔍 Smart column matching
    column_aliases = {
        'company': ['company', 'organization', 'business name'],
        'website': ['website', 'url'],
        'email': ['email 1', 'email', 'contact email'],
        'linkedin': ['linkedin', 'linkedin url'],
        'city': ['city', 'location'],
        'deal stage': ['deal stage', 'funding stage'],
        'industry': ['industry', 'sector'],
        'funding amount': ['funding amount', 'funding'],
        'employees': ['employees', 'team size']
    }

    mapped_columns = {}
    for standard, aliases in column_aliases.items():
        for alias in aliases:
            if alias in df.columns:
                mapped_columns[standard] = alias
                break
        else:
            df[standard] = None  # Create column if not found

    df.rename(columns=mapped_columns, inplace=True)
    df.columns = df.columns.str.lower()

    # 🧼 Fill fallback values
    df['industry'] = df.get('industry', 'SaaS').fillna('SaaS')
    df['city'] = df.get('city', 'Bangalore').fillna('Bangalore')
    df['funding amount'] = pd.to_numeric(df.get('funding amount', 1000000), errors='coerce').fillna(1000000)
    df['employees'] = pd.to_numeric(df.get('employees', 50), errors='coerce').fillna(50)

    # 🧮 Apply scoring
    df = score_leads(df)

    # 🎯 Filters using safe access
    with st.sidebar:
        st.header("🔍 Filter Leads")

        industry_values = df.get('industry')
        if industry_values is not None:
            industry_options = ['All'] + sorted(industry_values.dropna().unique().tolist())
            industry = st.selectbox("Industry", industry_options)
        else:
            industry = 'All'

        city_values = df.get('city')
        if city_values is not None:
            city_options = ['All'] + sorted(city_values.dropna().unique().tolist())
            city = st.selectbox("City", city_options)
        else:
            city = 'All'

    # Apply filters
    filtered_df = df.copy()
    if industry != 'All' and 'industry' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['industry'] == industry]
    if city != 'All' and 'city' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['city'] == city]

    # Display lead cards
    st.markdown("---")
    st.subheader("📋 Scored & Interactive Leads")

    for _, row in filtered_df.iterrows():
        with st.expander(f"🏢 {row.get('company', 'Unknown Company')}"):
            col1, col2, col3 = st.columns(3)

            # 🔗 Buttons
            with col1:
                if pd.notnull(row.get('website')):
                    st.markdown(f"[🌐 Website]({row['website']})", unsafe_allow_html=True)
                if pd.notnull(row.get('linkedin')):
                    st.markdown(f"[🔗 LinkedIn]({row['linkedin']})", unsafe_allow_html=True)

            with col2:
                if pd.notnull(row.get('city')):
                    maps_url = f"https://www.google.com/maps/search/{row['city'].replace(' ', '+')}"
                    st.markdown(f"[🗺️ View on Map]({maps_url})", unsafe_allow_html=True)

            with col3:
                if pd.notnull(row.get('email')):
                    st.markdown(f"**📧 Email:** `{row['email']}`")
                    if st.button(f"✉️ Draft Email to {row['company']}", key=f"email_{row['company']}"):
                        default_msg = f"""
Hi {row['company']} team,

I came across your company while researching innovative businesses and was impressed by your journey and stage ({row.get('deal stage', 'N/A')}).

We help teams like yours streamline lead gen and outreach using custom tools — and I'd love to share more if you're open to a quick chat.

Best,  
[Your Name]
"""
                        st.text_area("Generated Email", value=default_msg.strip(), height=180)

    # 📥 Export
    st.markdown("---")
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Filtered Leads", csv, "filtered_leads.csv", "text/csv")

else:
    st.info("Upload a CSV file with your leads to begin scoring and outreach.")
