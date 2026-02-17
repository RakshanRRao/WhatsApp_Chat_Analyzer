import re
import pandas as pd


def preprocess(data):

    # Pattern for your format: [17/08/20, 3:56:04 PM]
    pattern = r'\[(.*?)\]'

    messages = re.split(pattern, data)[1:]
    
    dates = messages[0::2]
    messages = messages[1::2]

    df = pd.DataFrame({'date': dates, 'message': messages})

    # Convert to datetime safely
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    df = df.dropna(subset=['date'])

    users = []
    message_text = []

    for message in df['message']:
        entry = re.split(r'([\w\W]+?):\s', message, maxsplit=1)

        if len(entry) > 2:
            users.append(entry[1])
            message_text.append(entry[2])
        else:
            users.append('group_notification')
            message_text.append(entry[0])

    df['user'] = users
    df['message'] = message_text

    df['message'] = df['message'].astype(str)

    # Time features
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['month_num'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    return df
