from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
from cleantext import clean
import pandas as pd
import numpy as np
import emoji
extractor = URLExtract()

def fetch_count(user, df):
    if user != 'All':
        df = df[df['users'] == user]
        
    count = df.shape[0]
    
    media = df[df['messages'].str.contains('omitted')].shape[0]

    links = []
    for message in df['messages']:
        links.extend(extractor.find_urls(message))
    
    words = []
    for message in df['messages']:
        words.extend(message.split())
        
    return count, len(words), media, len(links)

def busy_users(df):
    df = df[df['users'] != 'Notifications']
    x = df['users'].value_counts().head()
    df = round(df['users'].value_counts()/df.shape[0]*100 ,2).reset_index().rename(columns={'index':'name', 'users':'percent'})
    return x, df

def create_wordcloud(user, df):
    if user != 'All':
        df = df[df['users'] == user]
    
    f = open('stop_words.txt', 'r')
    stop_words = f.read()
        
    temp = df[~df['messages'].str.contains('omitted')]
    temp = temp[~temp['messages'].str.contains('This message was deleted.')]
    temp = temp[~temp['messages'].str.contains('You deleted this message.')]
    temp = temp[temp['users'] != 'Notifications']
    
    links = []
    for message in temp['messages']:
        links.extend(extractor.find_urls(message)) 
        
    def remove_words(message):
        words = []
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)
        return ' '.join(words)
    
    def remove_links(message):
        if any(link in message for link in links):
            return np.nan
        return message
    
    cloud = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    temp['messages'] = temp['messages'].apply(remove_links)
    temp['messages'] = temp['messages'].dropna().apply(remove_words)
    cloud_df = cloud.generate(temp['messages'].str.cat(sep=' '))
    return cloud_df

def common_words(user, df):
    
    f = open('stop_words.txt', 'r')
    stop_words = f.read()
    
    if user != 'All':
        df = df[df['users'] == user]
        
    temp = df[~df['messages'].str.contains('omitted')]
    temp = temp[~temp['messages'].str.contains('This message was deleted.')]
    temp = temp[~temp['messages'].str.contains('You deleted this message.')]
    temp = temp[temp['users'] != 'Notifications']
    
    words = []
    
    for message in temp['messages']:
        for word in message.lower().split():
            if word not in stop_words:
                if clean(word, no_emoji=True) == '':
                    continue                
                words.append(word)
    
    word_count_df = pd.DataFrame(Counter(words).most_common(20))
    return word_count_df

def emoji_count(user, df):
    
    if user != 'All':
        df = df[df['users'] == user]
    
    emojis = []
    for message in df['messages']:
        emojis.extend([c for c in message if c in emoji.UNICODE_EMOJI['en']])
    
    emoji_count_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    emoji_count_df.rename(columns={0:'Emojis',1:'Count'}, inplace=True)
    return emoji_count_df

def monthly_engagement(user, df):
    
    if user != 'All':
        df = df[df['users'] == user]
    
    timeline = df.groupby(['year', 'month_num', 'month']).count()['messages'].reset_index()
    
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + '-' + str(timeline['year'][i]))
    
    timeline['time'] = time
    
    return timeline

def daily_engagement(user, df):
    
    if user != 'All':
        df = df[df['users'] == user]
    
    timeline = df.groupby('date').count()['messages'].reset_index()
    
    return timeline

def week_activity_map(user, df):
    
    if user != 'All':
        df = df[df['users'] == user]
    
    timeline = df['Day Name'].value_counts()
    
    return timeline

def month_activity_map(user, df):
    
    if user != 'All':
        df = df[df['users'] == user]
    
    timeline = df['month'].value_counts()
    
    return timeline

def activity_heatmap(user, df):
    
    if user != 'All':
        df = df[df['users'] == user]
    
    heatmap = df.pivot_table(index='Day Name',columns='Period', values='messages', aggfunc='count').fillna(0)
    
    return heatmap