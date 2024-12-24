import pandas as pd
import re

def preprocess(data):
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s*\u202f?[ap]m'
    message = re.split(pattern, data)[1:]
    if message == []:
        pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s*[AP]M'


    message = re.split(pattern, data)[1:]

    time = re.findall(pattern, data)

    df = pd.DataFrame({'date': time,
                       'message': message})

    #df['date'] = pd.to_datetime(df['date'], format='%d/%m/%y, %I:%M %p')
    def parse_date(date_str):
        for fmt in ('%d/%m/%y, %I:%M %p', '%m/%d/%y, %I:%M %p'):
            try:
                return pd.to_datetime(date_str, format=fmt)
            except ValueError:
                continue
        return pd.NaT  # Return NaT if no formats match

    df['num_words'] = df['message'].apply(lambda x:len(x.split()))
    df['date'] = df['date'].apply(parse_date)

    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['time'] = df['date'].dt.strftime('%H:%M')
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.day
    df['month_num'] = df['date'].dt.month
    df['only_date'] = df['date'].dt.date
    df['day_name'] = df['date'].dt.day_name()
    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str("00") + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))
    df['period'] = period

    user = []
    message = []
    for i in df['message']:
        data = re.split('([\w\W]+?):\s', i)
        if data[1:]:
            user.append(data[1])
            message.append(data[2])
        else:
            user.append('Group Notification')
            message.append(data[0])

    df.drop(columns=['message'], inplace=True)
    df['message'] = message
    df['user'] = user
    df['user'] = df['user'].str.replace('-', '')
    df['message'] = df['message'].str.replace('\n', '')
    df = df[df['message'] != 'null']
    df['time_diff'] = df['date'].diff()

    td = pd.to_timedelta(df['time_diff'])
    total_hours = [100.00]
    for i in df['time_diff'][1:]:
        td = pd.Timedelta(i)
        hours = td.total_seconds() / 3600
        total_hours.append(round(hours, 2))
    df['total_hours'] = total_hours


    return df


# FUTURE IMPLEMENTATION
# who started the conversation first ?
# Longest /smallest conversation duration
# Sentiment Analysis



