import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import preprocessor, helper


# Set page config for wider layout
st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide", page_icon="💬")

# Sidebar Header with Styling                                                                                           
st.sidebar.markdown(
    "<h1 style='text-align: center; color: #32cd32; font-size: 28px;'>📊 WhatsApp Chat Analyzer</h1>",
    unsafe_allow_html=True
)

# File uploader for chat file with custom instructions
uploaded_file = st.sidebar.file_uploader("Upload your WhatsApp chat file (.txt)", type="txt",
                                         help="Make sure it's exported in .txt format")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode('utf-8')
    df = preprocessor.preprocess(data)

    # User selection for analysis
    user_list = df['user'].unique().tolist()
    user_list = [user for user in user_list if user != 'Group Notification']
    user_list.sort()
    user_list.insert(0, 'Overall')
    selected_user = st.sidebar.selectbox('Choose User for Analysis', user_list)

    # Display Analysis button
    if st.sidebar.button('Show Analysis'):


        # with st.spinner('Wait for it...'):  (Process Spinner)

        # Main title
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

        # Display top statistics in columns
        num_msg, words, num_media, num_link,total_days_of_convo = helper.fetch_stats(selected_user, df)
        st.markdown("<h3 style='color: #fdee00 ;'>📈 Top Statistics</h3>", unsafe_allow_html=True)
        st.write("<hr>", unsafe_allow_html=True)

        with st.container():
            col1, col2, col3, col4,col5 = st.columns(5)
            col1.metric("💬 :blue[Total Messages]", num_msg)
            col2.metric("✍️ :blue[Total Words]", words)
            col3.metric("📷 :blue[Media Shared]", num_media)
            col4.metric("🔗 :blue[Links Shared]", num_link)
            col5.metric("🔗 :blue[Active Days of Chatting]", str(total_days_of_convo)+" days")
        # Monthly and Daily Timeline Analysis
        st.markdown("<h3 style='color: #fdee00 ;'>📆 Message Timeline</h3>", unsafe_allow_html=True)



        # Monthly timeline plot (fixed size)
        monthly_timeline = helper.monthly_analysis(selected_user, df)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=monthly_timeline['time'], y=monthly_timeline['message'],
                                 mode='lines+markers', line=dict(color='green'),
                                 hoverinfo='x+y+text', text=monthly_timeline['message']))  # Added hover info
        fig.update_layout(
            title="Monthly Timeline",
            xaxis_title="Month",
            yaxis_title="Messages",
            title_font_size=14,
            xaxis_tickangle=45,
            plot_bgcolor='white',  # Set background color to white
            paper_bgcolor='black',  # Set paper background color to white
            autosize=True,  # Allow the plot to resize
            width=1800,  # Fixed width
            height=500,  # Fixed height
            margin=dict(t=50, b=50, l=50, r=50),  # Add margins to prevent clipping
        )

        # Use Streamlit to display the plot
        st.plotly_chart(fig, use_container_width=True)

        # Daily timeline plot (fixed size)
        daily_timeline = helper.daily_analysis(selected_user, df)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily_timeline['only_date'], y=daily_timeline['message'],
                                 mode='lines+markers', line=dict(color='blue'),
                                 hoverinfo='x+y+text', text=daily_timeline['message']))  # Added hover info
        fig.update_layout(
            title="Daily Timeline",
            xaxis_title="Date",
            yaxis_title="Messages",
            title_font_size=14,
            xaxis_tickangle=45,
            plot_bgcolor='white',  # Set background color to white
            paper_bgcolor='black',  # Set paper background color to white
            autosize=True,  # Allow the plot to resize
            width=1800,  # Fixed width
            height=500,  # Fixed height
            margin=dict(t=50, b=50, l=50, r=50),  # Add margins to prevent clipping
        )

        # Use Streamlit to display the plot
        st.plotly_chart(fig, use_container_width=True)

        # Busiest User Analysis
        if selected_user == 'Overall':
            st.markdown("<h3 style='color: #fdee00 ;'>🧑🏼‍💻 Most Active Users</h3>", unsafe_allow_html=True)
            st.write("<hr>", unsafe_allow_html=True)
            x, percent_df = helper.most_busy_user(df)
            col1, col2 = st.columns([1.2, 1])

            with col1:
                fig, ax = plt.subplots()
                ax.bar(x['user'], x['percent'], color='red', edgecolor='black')
                ax.set_title("Most Active Users", fontsize=14)
                plt.xticks(rotation=45)
                plt.figure(figsize=(6,6))
                st.pyplot(fig)

            with col2:
                fig,ax = plt.subplots()
                ax.pie(percent_df['percent'],labels = percent_df['user'],autopct='%1.1f%%',shadow=True  )
                plt.title('User Activity Percentage')
                plt.figure(figsize=(6, 6))
                st.pyplot(fig)




        # Conversation
        first_msg_user = helper.first_message_user(df)
        col1,col2 = st.columns(2)
        if selected_user == 'Overall':
            with col1:

                fig,ax = plt.subplots()
                ax.bar(first_msg_user.index,first_msg_user.values,color = '#0bda51')
                plt.xticks(rotation = 45)
                plt.ylabel('Initialize Conversation(Total Count)')
                plt.title('Who message first')
                st.pyplot(fig)




        # User Activity

        st.markdown("<h3 style='color: #fdee00 ;'>User Activity</h3>", unsafe_allow_html=True)
        col1,col2 = st.columns(2)
        with col1:
            week_activity = helper.week_activity_chart(selected_user,df)
            fig,ax = plt.subplots()
            ax.bar(week_activity.index,week_activity.values,color = '#00ccff')
            plt.xticks(rotation=45)
            plt.xlabel('Days')
            plt.ylabel('Chats')
            plt.title('Weekly Activity')
            st.pyplot(fig)

        with col2:
            month_activity = helper.month_activity_chart(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(month_activity.index, month_activity.values,color = '#ff69b4')
            plt.title('Monthly Activity')
            plt.xticks(rotation=45)
            plt.xlabel('Months')
            plt.ylabel('Chats')
            st.pyplot(fig)

        st.markdown("<h3 style='color: #fdee00 ;'>Weekly Activity</h3>", unsafe_allow_html=True)
        pivot_activity_heatmap = helper.activity_heatmap(selected_user,df)
        fig,ax = plt.subplots()
        ax = sns.heatmap(pivot_activity_heatmap)
        plt.figure(figsize=(20,6))
        st.pyplot(fig)


        # Word Cloud
        st.markdown("<h3 style='color: #fdee00 ;'>☁️ Word Cloud</h3>", unsafe_allow_html=True)
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)

        # Most Common Words
        st.markdown("<h3 style='color: #fdee00 ;'>🔠 Most Common Words</h3>", unsafe_allow_html=True)
        most_common_words = helper.most_common_word(selected_user, df)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=most_common_words[0],
            x=most_common_words[1],
            orientation='h',
            marker=dict(color='#20B2AA', line=dict(color='black', width=1))
        ))
        fig.update_layout(
            title="Most Common Words",
            xaxis_title="Frequency",
            yaxis_title="Words",
            title_font_size=14,
            width = 950,  # Increase the width
            height = 500
        )
        st.plotly_chart(fig)

        # Emoji Analysis
        st.markdown("<h3 style='color: #fdee00;'>😊 Emoji Analysis</h3>", unsafe_allow_html=True)

        # Count emojis
        emojis_count = helper.count_emojis(selected_user, df)

        # Ensure emojis_count[0] (emoji names) and emojis_count[1] (emoji counts) are lists of strings/numbers
        emoji_names = list(emojis_count[0])  # Convert to list of strings if not already
        emoji_counts = list(emojis_count[1])  # Convert to list of integers if not already

        # Columns for layout (adjusted for closeness)
        col1, col2 = st.columns([1, 1])

        # Display the emoji count data frame in col1
        with col1:
            st.write("**Emoji Count**")
            st.dataframe(emojis_count)

        # Plotly pie chart in col2
        with col2:
            fig = px.pie(
                names=emoji_names,  # Pass list of emoji names
                values=emoji_counts,  # Pass list of emoji counts
                title="Emoji Distribution",
                color_discrete_sequence=px.colors.diverging.RdYlBu
            )

            # Update the chart for better readability
            fig.update_traces(
                textinfo="percent+label",  # Show percentage and emoji label
                textfont_size=16,  # Increase text size for better readability
                pull=[0.1] * len(emoji_names)  # Slightly pull out each slice to give more space to labels
            )

            # Increase the pie chart size
            fig.update_layout(
                autosize=False,
                width=500,  # Width of the chart
                height=500,  # Height of the chart
                title_font_size=20,  # Larger title font size
                margin=dict(t=50, b=50, l=50, r=50)  # Add margins to avoid text cutoff
            )

            # Display the Plotly chart
            st.plotly_chart(fig)

# Sidebar Footer Styling
st.sidebar.markdown("<small style='text-align: center; color: grey;'>© 2025 Powered by WhatsApp Chat Analyzer</small>",
                    unsafe_allow_html=True)



# heyo this is sourav sharma
