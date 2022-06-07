import pandas as pd
import re

def preprocessor(data):
    pattern, formatstring, timeformat, platform = validate_OS(data)
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)
    df = pd.DataFrame({'user_messages':messages, 'dates':dates})
    
    users = []
    messages = []
    for message in df['user_messages']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('Notifications')
            messages.append(entry[0])
            
    df['users'] = users
    df['messages'] = messages
    df.drop(columns='user_messages', inplace=True)
    if platform == 'iOS': 
        df['dates'] = df['dates'].str.replace('[', '')
        df['dates'] = df['dates'].str.replace(']', '')    
    if timeformat == 12:
        df['dates'] = df['dates'].str.replace('am', 'AM').str.replace('pm', 'PM')
    formatstring = validate_formatstring(df, formatstring)
    df['dates'] = pd.to_datetime(df['dates'], format=formatstring)
    df['year'] = df['dates'].dt.year
    df['month_num'] = df['dates'].dt.month
    df['month'] = df['dates'].dt.month_name()
    df['day'] = df['dates'].dt.day
    df['Hour'] = df['dates'].dt.hour
    df['minutes'] = df['dates'].dt.minute
    df['date'] = df['dates'].dt.date
    df['Day Name'] = df['dates'].dt.day_name()
    
    period = []
    for hour in df[['Day Name', 'Hour']]['Hour']:
        if hour == 23:
            period.append(str(hour) + '-' + str('00'))
        elif hour == 0:
            period.append(str('00') + '-' + str(hour+1))
        else:
            period.append(str(hour) + '-' + str(hour+1))
    
    df['Period'] = period
    
    df.drop(columns='dates', inplace=True)
    
    df['messages'] = df['messages'].str.replace('\n', '')
    
    return df

def validate_formatstring(df, formatstring):
    try:
        pd.to_datetime(df['dates'], format=formatstring)
    except ValueError:
        formatstring = formatstring.replace('%d/%m', '%m/%d')
    return formatstring

def validate_OS(data):   
    pattern = re.compile('\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[aApP][Mm]\s-\s')
    pattern_ios = re.compile('\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s[aApP][Mm]\]\s')
    pattern_ios_24h = re.compile('\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\]\s')
    pattern24h = re.compile('\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s')
    formatstring = '%d/%m/%y, %I:%M %p - '
    formatstring_ios = '%d/%m/%y, %I:%M:%S %p '
    formatstring24h = '%d/%m/%Y, %H:%M - '
    formatstring_ios_24h = '%d/%m/%Y, %H:%M:%S '
    timeformat = 12
    platform = 'Android'
    if bool(pattern_ios.match(data)):
        pattern = pattern_ios.pattern
        formatstring = formatstring_ios
        platform = 'iOS'
    elif bool(pattern24h.match(data)):
        pattern = pattern24h.pattern
        formatstring = formatstring24h
        timeformat = 24
    elif bool(pattern_ios_24h.match(data)):
        pattern = pattern_ios_24h.pattern
        formatstring = formatstring_ios_24h
        timeformat = 24
        platform = 'iOS'
    return pattern, formatstring, timeformat, platform