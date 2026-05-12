import re
import pandas as pd


def preprocess(data):
    """
    Handles both WhatsApp export formats:
      Bracket : [17/08/20, 3:56:04 PM] User: msg
      Dash    : 17/08/2020, 3:56 pm - User: msg
    """

    # ── 1. Detect format ────────────────────────────────────────────────────
    bracket_pattern = r'\[(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}(?::\d{2})?\s?(?:AM|PM|am|pm)?)\]'
    dash_pattern    = r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}(?::\d{2})?\s?(?:AM|PM|am|pm)?)\s\u2013\s|\s-\s'

    bracket_hits = len(re.findall(bracket_pattern, data))
    dash_hits    = len(re.findall(
        r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}(?::\d{2})?\s?(?:AM|PM|am|pm)?\s[-\u2013]\s',
        data))

    if bracket_hits >= dash_hits:
        # ── Bracket format ──────────────────────────────────────────────────
        parts    = re.split(bracket_pattern, data)
        # parts = [junk, date, msg, date, msg, ...]
        dates    = parts[1::2]
        messages = parts[2::2]
    else:
        # ── Dash format ─────────────────────────────────────────────────────
        # Normalise en-dash → hyphen, then split
        data_normalised = data.replace('\u2013', '-')
        split_pattern   = r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}(?::\d{2})?\s?(?:AM|PM|am|pm)?)\s-\s'
        parts    = re.split(split_pattern, data_normalised)
        dates    = parts[1::2]
        messages = parts[2::2]

    if not dates:
        # Return an empty but correctly-shaped DataFrame so the app can
        # show a friendly error rather than crash.
        return pd.DataFrame(columns=[
            'date','message','user',
            'year','month','month_num','day','day_name','hour','minute'
        ])

    df = pd.DataFrame({'date': dates, 'message': messages})

    # ── 2. Parse dates ───────────────────────────────────────────────────────
    # Try common format strings before falling back to the slow inference path
    fmt_attempts = [
        '%d/%m/%y, %I:%M:%S %p',   # [17/08/20, 3:56:04 PM]
        '%d/%m/%Y, %I:%M:%S %p',   # [17/08/2020, 3:56:04 PM]
        '%d/%m/%y, %I:%M %p',      # 17/08/20, 3:56 PM
        '%d/%m/%Y, %I:%M %p',      # 17/08/2020, 3:56 PM
        '%d/%m/%y, %H:%M:%S',      # 17/08/20, 15:56:04
        '%d/%m/%Y, %H:%M:%S',      # 17/08/2020, 15:56:04
        '%d/%m/%y, %H:%M',         # 17/08/20, 15:56
        '%d/%m/%Y, %H:%M',         # 17/08/2020, 15:56
        '%m/%d/%y, %I:%M:%S %p',   # US bracket variant
        '%m/%d/%Y, %I:%M:%S %p',
        '%m/%d/%y, %I:%M %p',
        '%m/%d/%Y, %I:%M %p',
    ]

    parsed = None
    for fmt in fmt_attempts:
        try:
            parsed = pd.to_datetime(df['date'].str.strip(), format=fmt)
            if parsed.notna().sum() > len(df) * 0.8:   # >80 % parsed → good
                break
        except Exception:
            continue

    if parsed is None or parsed.notna().sum() == 0:
        # Last resort: let pandas infer (slow but flexible)
        parsed = pd.to_datetime(df['date'], errors='coerce')

    df['date'] = parsed
    df = df.dropna(subset=['date']).reset_index(drop=True)

    if df.empty:
        return df

    # ── 3. Split user / message ──────────────────────────────────────────────
    users, message_text = [], []

    for message in df['message']:
        entry = re.split(r'([\w\W]+?):\s', str(message), maxsplit=1)
        if len(entry) > 2:
            users.append(entry[1].strip())
            message_text.append(entry[2].strip())
        else:
            users.append('group_notification')
            message_text.append(entry[0].strip())

    df['user']    = users
    df['message'] = message_text

    # ── 4. Time features ─────────────────────────────────────────────────────
    df['year']      = df['date'].dt.year
    df['month']     = df['date'].dt.month_name()
    df['month_num'] = df['date'].dt.month
    df['day']       = df['date'].dt.day
    df['day_name']  = df['date'].dt.day_name()
    df['hour']      = df['date'].dt.hour
    df['minute']    = df['date'].dt.minute

    return df