import streamlit as st
import Preprocessor as p
import Helper as h
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

st.set_page_config(page_title='Whatsapp Chat Analyser',page_icon = 'icon.png',layout="wide")
st.sidebar.title("Whatsapp Analyser")

uploaded_file = st.sidebar.file_uploader("Choose a file")

if uploaded_file is not None:
     bytes_data = uploaded_file.getvalue()
     data = bytes_data.decode("utf-8")
     
     df = p.preprocessor(data)
     
     users = df['users'].unique().tolist()
     users.remove('Notifications')
     users.append('All')
     users.sort()
     user = st.sidebar.selectbox('Show analysis of',users)
     
     if st.sidebar.button('Show Analysis'):
          
          st.title('Top Stats')
          col1, col2, col3, col4 = st.columns(4)
          count, words, media, links = h.fetch_count(user, df)
          
          with col1:
               st.header('Total Messages')
               st.title(count)
          with col2:
               st.header('Total Words')
               st.title(words)          
          with col3:
               st.header('Media Shared')
               st.title(media)
          with col4:
               st.header('Links Shared')
               st.title(links)
          
          st.title('Monthly Engagement')
          monthly_timeline = h.monthly_engagement(user, df)
          fig, ax = plt.subplots()
          ax.plot(monthly_timeline['time'], monthly_timeline['messages'], color='black')
          plt.xticks(rotation='vertical')
          st.pyplot(fig)
          
          st.title('Daily Engagement')
          daily_timeline = h.daily_engagement(user, df)
          fig, ax = plt.subplots()
          ax.plot(daily_timeline['date'], daily_timeline['messages'], color='green')
          plt.xticks(rotation = 'vertical')
          st.pyplot(fig)    
          
          st.title('Daily Activity Map')
          col1, col2 = st.columns(2)
          with col1:
               st.header('Most busy day')
               day = h.week_activity_map(user, df)
               fig, ax = plt.subplots()
               ax.plot(day.index, day.values, color='blue')
               plt.xticks(rotation = 'vertical')
               st.pyplot(fig)
          with col2:
               st.header('Most busy month')
               month = h.month_activity_map(user, df)
               fig, ax = plt.subplots()
               ax.plot(month.index, month.values, color='orange')
               plt.xticks(rotation = 'vertical')
               st.pyplot(fig)               
          
          st.title('Activity Heatmap')
          heatmap = h.activity_heatmap(user, df)
          fig, ax = plt.subplots()
          ax = sns.heatmap(heatmap)
          st.pyplot(fig)    
          
          if user == 'All':
               st.title('Busy Users')
               x, new_df = h.busy_users(df)
               fig, ax = plt.subplots()
               
               col1, col2 = st.columns(2)
          
               with col1:
                    ax.bar(x.index, x.values)
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)             
               with col2:
                    st.dataframe(new_df.set_index('name'))
          
          st.title('WordCloud')
          wc = h.create_wordcloud(user, df)
          fig, ax = plt.subplots()
          ax.imshow(wc)
          ax.set_axis_off()
          st.pyplot(fig)
          
          st.title('Most Common Words')
          word_count_df = h.common_words(user,df)
          
          fig, ax = plt.subplots()
          ax.barh(word_count_df[0], word_count_df[1])
          plt.xticks(rotation='vertical')
          ax.invert_yaxis()
          st.pyplot(fig)
          
          st.title('Emojis')
          emoji_count_df = h.emoji_count(user,df)
          col1, col2 = st.columns(2)
          
          with col1:
               st.dataframe(emoji_count_df.set_index('Emojis'))
          with col2:
               fig = px.pie(emoji_count_df.head(), values='Count', names='Emojis')
               st.plotly_chart(fig, use_container_width=True)