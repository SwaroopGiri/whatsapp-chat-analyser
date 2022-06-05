import pandas as pd
import re

def preprocessor(data):
    dformat = 12
    pattern = re.compile('\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[aApP][Mm]\s-\s')
    pattern24 = re.compile('\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s')
    if bool(pattern24.match(data)):
        pattern = pattern24.pattern
        dformat = 24
        del(pattern24)
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
    df.head()
    formatstring = validate_formatstring(df, '%d/%m/%Y, %H:%M - ')   
    if dformat == 12:
        formatstring = validate_formatstring(df, '%d/%m/%y, %I:%M %p - ')
        df['dates'] = df['dates'].str.replace('am', 'AM').str.replace('pm', 'PM')
        
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