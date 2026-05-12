import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import preprocessor
import helper

st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")

st.title("📊 WhatsApp Chat Analyzer")

# ── Sidebar upload ────────────────────────────────────────────────────────────
st.sidebar.title("📁 Upload & Settings")
uploaded_file = st.sidebar.file_uploader("Upload WhatsApp Chat (.txt)")

if uploaded_file is None:
    st.info("👈 Upload a WhatsApp exported `.txt` file from the sidebar to get started.")
    st.markdown(
        """
        **How to export your WhatsApp chat:**
        1. Open a WhatsApp chat
        2. Tap ⋮ → More → Export Chat
        3. Choose **Without Media**
        4. Upload the `.txt` file here
        """
    )
    st.stop()

# ── Pre-process ───────────────────────────────────────────────────────────────
data = uploaded_file.read().decode("utf-8", errors="ignore")
df   = preprocessor.preprocess(data)

if df.empty:
    st.error(
        "⚠️ Could not parse this file. "
        "Make sure you uploaded a WhatsApp exported `.txt` file and try again."
    )
    st.stop()

# ── User selector ─────────────────────────────────────────────────────────────
user_list = df['user'].unique().tolist()
if 'group_notification' in user_list:
    user_list.remove('group_notification')
user_list = sorted(user_list)
user_list.insert(0, "Overall")

selected_user = st.sidebar.selectbox("Show analysis for", user_list)

if not st.sidebar.button("Show Analysis"):
    st.info("Select a user and click **Show Analysis** to begin.")
    st.stop()

# ═════════════════════════════════════════════════════════════════════════════
# 1. Top-level stats
# ═════════════════════════════════════════════════════════════════════════════
st.header("📈 Overview")
num_messages, words, num_media, links = helper.fetch_stats(selected_user, df)

col1, col2, col3, col4 = st.columns(4)
col1.metric("💬 Total Messages", num_messages)
col2.metric("🔤 Total Words",    words)
col3.metric("🖼️ Media Shared",   num_media)
col4.metric("🔗 Links Shared",   links)

# ═════════════════════════════════════════════════════════════════════════════
# 2. Monthly timeline
# ═════════════════════════════════════════════════════════════════════════════
st.header("📅 Monthly Timeline")
timeline = helper.monthly_timeline(selected_user, df)
if not timeline.empty:
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(timeline['time'], timeline['message'], color='teal', marker='o', markersize=4)
    ax.set_xlabel("Month")
    ax.set_ylabel("Messages")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
else:
    st.info("Not enough data for a monthly timeline.")

# ═════════════════════════════════════════════════════════════════════════════
# 3. Daily timeline
# ═════════════════════════════════════════════════════════════════════════════
st.header("📆 Daily Timeline")
daily = helper.daily_timeline(selected_user, df)
if not daily.empty:
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(daily['only_date'], daily['message'], color='steelblue', linewidth=0.8)
    ax.set_xlabel("Date")
    ax.set_ylabel("Messages")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
else:
    st.info("Not enough data for a daily timeline.")

# ═════════════════════════════════════════════════════════════════════════════
# 4. Activity maps
# ═════════════════════════════════════════════════════════════════════════════
st.header("🗓️ Activity Map")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Most Busy Day")
    busy_day = helper.week_activity_map(selected_user, df)
    fig, ax = plt.subplots()
    ax.bar(busy_day.index, busy_day.values, color='coral')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with col2:
    st.subheader("Most Busy Month")
    busy_month = helper.month_activity_map(selected_user, df)
    fig, ax = plt.subplots()
    ax.bar(busy_month.index, busy_month.values, color='mediumseagreen')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# ── Heatmap ───────────────────────────────────────────────────────────────────
st.subheader("⏰ Weekly Activity Heatmap")
heatmap_df = helper.activity_heatmap(selected_user, df)
if not heatmap_df.empty and heatmap_df.shape[1] > 0:
    fig, ax = plt.subplots(figsize=(20, 6))
    sns.heatmap(heatmap_df, ax=ax, cmap='YlOrRd')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
else:
    st.info("Not enough data for a heatmap.")

# ═════════════════════════════════════════════════════════════════════════════
# 5. Most busy users (group-level only)
# ═════════════════════════════════════════════════════════════════════════════
if selected_user == "Overall":
    st.header("👥 Most Busy Users")
    x, pct_df = helper.most_busy_users(df)

    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots()
        ax.bar(x.index, x.values, color='mediumpurple')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    with col2:
        st.dataframe(pct_df, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# 6. Word Cloud
# ═════════════════════════════════════════════════════════════════════════════
st.header("☁️ Word Cloud")
try:
    wc_image = helper.create_wordcloud(selected_user, df)
    fig, ax = plt.subplots()
    ax.imshow(wc_image, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)
    plt.close(fig)
except Exception as e:
    st.warning(f"Could not generate word cloud: {e}")

# ═════════════════════════════════════════════════════════════════════════════
# 7. Most common words
# ═════════════════════════════════════════════════════════════════════════════
st.header("🔤 Most Common Words")
common_df = helper.most_common_words(selected_user, df)
if not common_df.empty:
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(common_df['word'], common_df['count'], color='darkorange')
    ax.invert_yaxis()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
else:
    st.info("No common words found.")

# ═════════════════════════════════════════════════════════════════════════════
# 8. Emoji Analysis
# ═════════════════════════════════════════════════════════════════════════════
st.header("😀 Emoji Analysis")
emoji_df = helper.emoji_helper(selected_user, df)

if not emoji_df.empty:
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(emoji_df.head(10), use_container_width=True)
    with col2:
        fig, ax = plt.subplots()
        ax.pie(
            emoji_df['count'].head(8),
            labels=emoji_df['emoji'].head(8),
            autopct="%0.1f%%",
            startangle=140,
        )
        ax.axis("equal")
        st.pyplot(fig)
        plt.close(fig)
else:
    st.info("No emojis found in this chat.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 👨‍💻 Developed by Rakshan R Rao")
st.markdown(
    "🔗 [GitHub](https://github.com/RakshanRRao) &nbsp;|&nbsp; "
    "📊 WhatsApp Chat Analyzer built using Python, Pandas & Streamlit"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 👨‍💻 Developed by")
st.sidebar.markdown("**Rakshan R Rao**")
st.sidebar.markdown("[GitHub Profile](https://github.com/RakshanRRao)")