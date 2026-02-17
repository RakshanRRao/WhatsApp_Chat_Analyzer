from collections import Counter
import pandas as pd
from wordcloud import WordCloud
import emoji
from urlextract import URLExtract

extract = URLExtract()


def fetch_stats(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    df['message'] = df['message'].astype(str)

    num_messages = df.shape[0]

    words = []
    for message in df['message']:
        words.extend(message.split())

    num_media = df[df['message'].str.contains('<Media omitted>', na=False)].shape[0]

    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media, len(links)


def most_busy_users(df):
    x = df['user'].value_counts().head()
    df_percent = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index()
    df_percent.columns = ['user', 'percent']
    return x, df_percent


def create_wordcloud(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    df['message'] = df['message'].astype(str)

    try:
        with open('stop_hinglish.txt', 'r', encoding='utf-8') as f:
            stop_words = f.read().split()
    except:
        stop_words = []

    temp = df[df['user'] != 'group_notification']

    def remove_stopwords(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')

    temp['message'] = temp['message'].apply(remove_stopwords)

    df_wc = wc.generate(temp['message'].str.cat(sep=" "))

    return df_wc


def most_common_words(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    df['message'] = df['message'].astype(str)

    words = []

    try:
        with open('stop_hinglish.txt', 'r', encoding='utf-8') as f:
            stop_words = f.read().split()
    except:
        stop_words = []

    temp = df[df['user'] != 'group_notification']

    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common = Counter(words).most_common(20)

    most_common_df = pd.DataFrame(most_common, columns=['word', 'count'])

    return most_common_df


def emoji_helper(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    df['message'] = df['message'].astype(str)

    emojis = []

    for message in df['message']:
        for char in message:
            if char in emoji.EMOJI_DATA:
                emojis.append(char)

    emoji_df = pd.DataFrame(Counter(emojis).most_common(), columns=['emoji', 'count'])

    return emoji_df
