import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import preprocessor
import helper

st.set_page_config(layout="wide")

st.title("📊 WhatsApp Chat Analyzer")

uploaded_file = st.file_uploader("Upload WhatsApp Chat (.txt)")

if uploaded_file is not None:

    data = uploaded_file.read().decode("utf-8", errors="ignore")

    df = preprocessor.preprocess(data)

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

        # Most Busy Users
        if selected_user == "Overall":
            st.title("Most Busy Users")
            x, new_df = helper.most_busy_users(df)

            fig, ax = plt.subplots()
            ax.bar(x.index, x.values)
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

            st.dataframe(new_df)

        # Wordcloud
        st.title("Word Cloud")
        df_wc = helper.create_wordcloud(selected_user, df)

        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        ax.axis("off")
        st.pyplot(fig)

        # Most Common Words
        st.title("Most Common Words")
        common_df = helper.most_common_words(selected_user, df)

        fig, ax = plt.subplots()
        ax.barh(common_df['word'], common_df['count'])
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Emoji Analysis
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
