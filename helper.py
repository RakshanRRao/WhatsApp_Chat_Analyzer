from collections import Counter
import pandas as pd
from wordcloud import WordCloud
import emoji
from urlextract import URLExtract

extract = URLExtract()

# ── Stop-words ───────────────────────────────────────────────────────────────
def _load_stopwords():
    try:
        with open('stop_hinglish.txt', 'r', encoding='utf-8') as f:
            return set(f.read().split())
    except FileNotFoundError:
        return set()

STOP_WORDS = _load_stopwords()

# ── Basic stats ──────────────────────────────────────────────────────────────
def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    df = df.copy()
    df['message'] = df['message'].astype(str)

    num_messages = df.shape[0]

    words = [w for msg in df['message'] for w in msg.split()]

    num_media = df[df['message'].str.contains(
        '<Media omitted>|<media omitted>', na=False, regex=True)].shape[0]

    links = [url for msg in df['message'] for url in extract.find_urls(msg)]

    return num_messages, len(words), num_media, len(links)


# ── Most busy users ──────────────────────────────────────────────────────────
def most_busy_users(df):
    x = df['user'].value_counts().head()
    df_percent = (
        round((df['user'].value_counts() / df.shape[0]) * 100, 2)
        .reset_index()
    )
    df_percent.columns = ['user', 'percent']
    return x, df_percent


# ── Word Cloud ───────────────────────────────────────────────────────────────
def create_wordcloud(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    df = df.copy()
    df['message'] = df['message'].astype(str)

    temp = df[df['user'] != 'group_notification'].copy()
    temp = temp[~temp['message'].str.contains(
        '<Media omitted>|<media omitted>', na=False, regex=True)]

    def remove_stopwords(message):
        return " ".join(
            w for w in message.lower().split() if w not in STOP_WORDS
        )

    temp['message'] = temp['message'].apply(remove_stopwords)
    combined = temp['message'].str.cat(sep=" ").strip()

    if not combined:
        combined = "no words available"   # prevent WordCloud crash

    wc = WordCloud(
        width=500, height=500, min_font_size=10, background_color='white'
    )
    return wc.generate(combined)


# ── Most common words ────────────────────────────────────────────────────────
def most_common_words(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    df = df.copy()
    df['message'] = df['message'].astype(str)

    temp = df[df['user'] != 'group_notification']
    temp = temp[~temp['message'].str.contains(
        '<Media omitted>|<media omitted>', na=False, regex=True)]

    words = [
        w for msg in temp['message']
        for w in msg.lower().split()
        if w not in STOP_WORDS
    ]

    most_common = Counter(words).most_common(20)
    return pd.DataFrame(most_common, columns=['word', 'count'])


# ── Emoji analysis ───────────────────────────────────────────────────────────
def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    df = df.copy()
    df['message'] = df['message'].astype(str)

    emojis = [
        char
        for msg in df['message']
        for char in msg
        if char in emoji.EMOJI_DATA
    ]

    return pd.DataFrame(Counter(emojis).most_common(), columns=['emoji', 'count'])


# ── Monthly timeline ─────────────────────────────────────────────────────────
def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = (
        df.groupby(['year', 'month_num', 'month'])
        .count()['message']
        .reset_index()
    )
    timeline['time'] = timeline['month'] + '-' + timeline['year'].astype(str)
    return timeline


# ── Daily timeline ────────────────────────────────────────────────────────────
def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    df = df.copy()
    df['only_date'] = df['date'].dt.date
    return df.groupby('only_date').count()['message'].reset_index()


# ── Activity map ─────────────────────────────────────────────────────────────
def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['day_name'].value_counts()


def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['month'].value_counts()


def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Build period label: "00-01", "01-02", …
    df = df.copy()
    df['period'] = df['hour'].apply(
        lambda h: f"{h:02d}-{(h+1)%24:02d}"
    )
    return df.pivot_table(
        index='day_name',
        columns='period',
        values='message',
        aggfunc='count'
    ).fillna(0)