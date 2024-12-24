from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
import pandas as pd
import emoji


def fetch_stats(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # no. of msg
    num_msg = df.shape[0]

    # no. of words
    num_words = []
    for msg in df['message']:
        num_words.extend(msg.split())

    # no. of media shared
    num_media = df[df['message'] == '<Media omitted>'].shape[0]

    # no. of URL/ links
    extractor = URLExtract()
    num_link = []
    for msg in df['message']:
        num_link.extend(extractor.find_urls(msg))



    return num_msg, len(num_words),num_media, len(num_link),df['only_date'].nunique()

def most_busy_user(df):
    num_words = []
    for msg in df['message']:
        num_words.extend(msg.split())
    temp_df = df[df['user'] != 'Group Notification']
    temp_df = temp_df[['user', 'num_words']]
    total_words = temp_df['num_words'].sum()

    x = (temp_df.groupby('user').sum()).rename(columns = {'num_words':'percent'}).reset_index().head(5)
    x = x.sort_values('percent', ascending=False)
    percent_df = round((temp_df.groupby('user').sum()/total_words)*100,2).rename(columns = {'num_words':'percent'}).reset_index()
    return x,percent_df

def create_wordcloud(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp_df = df[df['user'] != 'Group Notification']
    temp_df = temp_df[temp_df['message'] != '<Media omitted>']

    file = open("stop_hinglish.txt", 'r')
    stop_word = file.read()

    def remove_stop_words(msg):
        y = []
        for word in msg.lower().split():
            if word not in stop_word:
                y.append(word)
        return " ".join(y)


    wc = WordCloud(height=500,width=500,min_font_size=10,background_color='white')
    temp_df['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp_df['message'].str.cat(sep = " "))
    return df_wc

def most_common_word(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp_df = df[df['user'] != 'Group Notification']
    temp_df = temp_df[temp_df['message'] != '<Media omitted>']

    file = open("stop_hinglish.txt", 'r')
    stop_word = file.read()

    word = []
    for msg in temp_df['message']:
        for i in msg.lower().split():
            if i not in stop_word:
                word.append(i)


    most_common_word = pd.DataFrame(Counter(word).most_common(20))
    return most_common_word

def count_emojis(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for msg in df['message']:
        emojis.extend([c for c in msg if c in emoji.EMOJI_DATA])

    emojis_count = pd.DataFrame(Counter(emojis).most_common(20))
    return emojis_count

def monthly_analysis(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    monthly_timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    time = []
    for i in range(monthly_timeline.shape[0]):
        time.append(monthly_timeline['month'][i] + "-" + str(monthly_timeline['year'][i]))

    monthly_timeline['time'] = time
    return monthly_timeline

def daily_analysis(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline

def week_activity_chart(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_chart(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    pivot_activity_heatmap = df.pivot_table(index='day_name',columns='period',values='message',aggfunc='count').fillna(0)
    return pivot_activity_heatmap

def first_message_user(df):
    hour_gap = 5.00
    temp_df = df[df['user'] != 'Group Notification']
    temp_df['total_hours'][1] = 10
    if temp_df['user'].nunique()==2:
        return temp_df[temp_df['total_hours']>=hour_gap]['user'].value_counts()
    else:
        try:
            return temp_df[temp_df['total_hours'] >= hour_gap]['user'].value_counts()[:5]
        except:
            return temp_df[temp_df['total_hours'] >= hour_gap]['user'].value_counts()[:3]
