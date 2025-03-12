import streamlit as st
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import preprocessor, helper

# Set page config at the very top
st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide", page_icon="💬")

# Sidebar Header with Styling
st.sidebar.markdown(
    "<h1 style='text-align: center; color: #32cd32; font-size: 28px;'>📊 WhatsApp Chat Analyzer</h1>",
    unsafe_allow_html=True
)
# File uploader for chat file
uploaded_file = st.sidebar.file_uploader("Upload your WhatsApp chat file (.txt)", type="txt",
                                         help="Make sure it's exported in .txt format")

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode('utf-8')
    df = preprocessor.preprocess(data)

    # Check if df is empty before proceeding
    if df.empty:
        st.sidebar.warning("⚠️ The uploaded file is empty or not in the correct format!")
    else:
        # User selection for analysis
        user_list = df['user'].unique().tolist()
        user_list = [user for user in user_list if user != 'Group Notification']
        user_list.sort()
        user_list.insert(0, 'Overall')
        selected_user = st.sidebar.selectbox('Choose User for Analysis', user_list)

        # Display Analysis button
        if st.sidebar.button('Show Analysis'):
            st.markdown("""
                        <style>
                        .title-container {
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            margin-top: 20px;
                            margin-bottom: 20px;
                        }
                        .title {
                            font-size: 3em;
                            font-weight: 700;
                            color: #ffffff;
                            background: linear-gradient(90deg, #ff4500, #ff6347);
                            padding: 15px 30px;
                            border-radius: 12px;
                            box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.3);
                            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
                        }
                        </style>
                        <div class="title-container">
                            <h2 class="title">🔍 Chat Analysis Dashboard</h2>
                        </div>
                        """, unsafe_allow_html=True)

            # Display top statistics
            num_msg, words, num_media, num_link, total_days_of_convo = helper.fetch_stats(selected_user, df)
            st.markdown("<h3 style='color: #fdee00 ;'>📈 Top Statistics</h3>", unsafe_allow_html=True)
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric(label="💬 :blue[Total Messages]", value=num_msg)
            col2.metric("✍️ :blue[Total Words]", words)
            col3.metric("📷 :blue[Media Shared]", num_media)
            col4.metric("🔗 :blue[Links Shared]", num_link)
            col5.metric("📅 :blue[Active Days]", f"{total_days_of_convo} days")

            # Monthly and Daily Timeline Analysis

            # Monthly timeline plot
            st.markdown("<h3 style='color: #fdee00 ;'>📆 Message Timeline</h3>", unsafe_allow_html=True)
            monthly_timeline = helper.monthly_analysis(selected_user, df)
            fig = px.line(monthly_timeline, x='time', y='message', title="Monthly Timeline", markers=True,
                          line_shape='spline')
            st.plotly_chart(fig, use_container_width=True)

            # Daily timeline plot
            daily_timeline = helper.daily_analysis(selected_user, df)
            fig = px.line(daily_timeline, x='only_date', y='message', title="Daily Timeline", markers=True,
                          line_shape='spline')
            st.plotly_chart(fig, use_container_width=True)

            # Busiest User Analysis
            if selected_user == 'Overall':
                st.markdown("<h3 style='color: #fdee00 ;'>🧑🏼‍💻 Most Active Users</h3>", unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    x, percent_df = helper.most_busy_user(df)
                    fig = px.bar(x, x='user', y='percent', title="Most Active Users", color='percent', text='percent',
                                 color_continuous_scale='Blues', labels={'percent': 'Activity Percentage'})
                    fig.update_layout(xaxis_title='Users', yaxis_title='Percentage', xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    fig = px.pie(percent_df, names='user', values='percent', title='User Activity Percentage',
                                 color_discrete_sequence=px.colors.sequential.Magenta,hole=0.5)
                    st.plotly_chart(fig)

            # Who Messages First Analysis
            first_msg_user = helper.first_message_user(df)
            if selected_user == 'Overall':
                st.markdown("<h3 style='color: #fdee00;'>💬 Who Messages First</h3>", unsafe_allow_html=True)
                fig = px.bar(first_msg_user, x=first_msg_user.index, y=first_msg_user.values,
                             title="Who Messages First", color=first_msg_user.values, color_continuous_scale="Reds")
                fig.update_layout(xaxis_title='User', yaxis_title='Initialize Conversation (Total Count)',
                                  xaxis_tickangle=-45)
                st.plotly_chart(fig)

            # Weekly & Monthly Activity
            st.markdown("<h3 style='color: #fdee00 ;'>User Activity</h3>", unsafe_allow_html=True)
            col3, col4 = st.columns(2)

            with col3:
                week_activity = helper.week_activity_chart(selected_user, df)
                fig = px.bar(x=week_activity.index, y=week_activity.values, title='Weekly Activity',
                             labels={'x': 'Days', 'y': 'Chats'}, color=week_activity.values)
                st.plotly_chart(fig)

            with col4:
                month_activity = helper.month_activity_chart(selected_user, df)
                fig = px.bar(x=month_activity.index, y=month_activity.values, title='Monthly Activity',
                             labels={'x': 'Months', 'y': 'Chats'}, color=month_activity.values,color_continuous_scale="Greens")
                st.plotly_chart(fig)

            # Heatmap
            st.markdown("<h3 style='color: #fdee00;'>🗺️ Weekly Activity Heatmap</h3>", unsafe_allow_html=True)
            pivot_activity_heatmap = helper.activity_heatmap(selected_user, df)
            plt.figure(figsize=(20, 6))  # Move this before plotting
            fig, ax = plt.subplots()
            sns.heatmap(pivot_activity_heatmap, ax=ax, cmap="YlGnBu")
            st.pyplot(fig)

            # Word Cloud
            st.markdown("<h3 style='color: #fdee00 ;'>☁️ Word Cloud</h3>", unsafe_allow_html=True)
            df_wc = helper.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots()
            ax.imshow(df_wc, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)

            # Most Common Words & Emoji Analysis
            col5, col6 = st.columns([2, 1])
            with col5:
                st.markdown("<h3 style='color: #fdee00 ;'>🔠 Most Common Words</h3>", unsafe_allow_html=True)
                most_common_words = helper.most_common_word(selected_user, df)
                fig = px.bar(y=most_common_words[0], x=most_common_words[1], orientation='h',
                             title="Most Common Words",
                             color=most_common_words[1])
                st.plotly_chart(fig)

            with col6:
                st.markdown("<h3 style='color: #fdee00;'>😊 Emoji Analysis</h3>", unsafe_allow_html=True)
                emojis_count = helper.count_emojis(selected_user, df)
                fig = px.pie(names=emojis_count[0], values=emojis_count[1], title="Emoji Distribution",color_discrete_sequence=px.colors.cyclical.Phase)
                st.plotly_chart(fig)
# Sidebar Footer Styling
st.sidebar.markdown("<small style='text-align: center; color: grey;'>© 2025 Powered by WhatsApp Chat Analyzer</small>",
                    unsafe_allow_html=True)