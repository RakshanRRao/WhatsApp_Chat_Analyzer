import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import preprocessor
import helper

st.set_page_config(layout="wide")

st.markdown("""
    <style>
        .stApp {
            background-color: #0e1117;
            color: #fafafa;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📊 WhatsApp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Upload WhatsApp Chat (.txt)")

if uploaded_file is not None:

    data = uploaded_file.read().decode("utf-8", errors="ignore")
    df = preprocessor.preprocess(data)

    if df.empty:
        st.error("Could not parse this file. Please upload a valid WhatsApp exported .txt file.")
        st.stop()

    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')

    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis of", user_list)

    if st.sidebar.button("Show Analysis"):

        num_messages, words, num_media, links = helper.fetch_stats(selected_user, df)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Messages", num_messages)
        col2.metric("Total Words", words)
        col3.metric("Media Shared", num_media)
        col4.metric("Links Shared", links)

        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        if not timeline.empty:
            fig, ax = plt.subplots()
            ax.plot(timeline['time'], timeline['message'], color='green')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
            plt.close(fig)

        st.title("Daily Timeline")
        daily = helper.daily_timeline(selected_user, df)
        if not daily.empty:
            fig, ax = plt.subplots()
            ax.plot(daily['only_date'], daily['message'], color='black')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
            plt.close(fig)

        st.title("Activity Map")
        col1, col2 = st.columns(2)
        with col1:
            st.header("Most Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values)
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
            plt.close(fig)
        with col2:
            st.header("Most Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
            plt.close(fig)

        st.title("Weekly Activity Heatmap")
        heatmap_df = helper.activity_heatmap(selected_user, df)
        if not heatmap_df.empty:
            fig, ax = plt.subplots(figsize=(20, 6))
            sns.heatmap(heatmap_df, ax=ax)
            st.pyplot(fig)
            plt.close(fig)

        if selected_user == "Overall":
            st.title("Most Busy Users")
            x, new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()
            ax.bar(x.index, x.values)
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
            plt.close(fig)
            st.dataframe(new_df)

        st.title("Word Cloud")
        try:
            df_wc = helper.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            ax.axis("off")
            st.pyplot(fig)
            plt.close(fig)
        except Exception as e:
            st.warning(f"Could not generate word cloud: {e}")

        st.title("Most Common Words")
        common_df = helper.most_common_words(selected_user, df)
        if not common_df.empty:
            fig, ax = plt.subplots()
            ax.barh(common_df['word'], common_df['count'])
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
            plt.close(fig)

        st.title("Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)
        if not emoji_df.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(emoji_df.head())
            with col2:
                fig, ax = plt.subplots()
                ax.pie(emoji_df['count'].head(),
                       labels=emoji_df['emoji'].head(),
                       autopct="%0.2f")
                st.pyplot(fig)
                plt.close(fig)

st.sidebar.markdown("---")
st.sidebar.markdown("### 👨‍💻 Developed by")
st.sidebar.markdown("**Rakshan R Rao**")
st.sidebar.markdown("[GitHub Profile](https://github.com/RakshanRRao)")
st.markdown("---")
st.markdown("### 👨‍💻 Developed by Rakshan R Rao")
st.markdown(
    """
    🔗 [GitHub](https://github.com/RakshanRRao)  
    📊 WhatsApp Chat Analyzer built using Python, Pandas & Streamlit
    """
)