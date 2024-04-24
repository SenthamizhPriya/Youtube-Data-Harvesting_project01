import pandas as pd
import googleapiclient.discovery
import streamlit as st
import mysql.connector
from sqlalchemy import create_engine

# DATA EXTRACTION

#Connection with youtube API

api_service_name = "youtube"
api_version = "v3"
api_key = 'AIzaSyCrNZtBJYqT6n2XHVsfYhGSsEcZBuBTeko'
youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey = api_key)

# Channel data extraction

def channel_data(channel_id):
    
    channel_request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    )
    channel_response = channel_request.execute()

    data = {
        'channel_title' : channel_response['items'][0]['snippet']['title'],
        'channel_description' : channel_response['items'][0]['snippet']['description'],
        'published_date' : channel_response['items'][0]['snippet']['publishedAt'],
        'channel_playlist_ID' : channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads'],
        'channel_viewcount' : channel_response['items'][0]['statistics']['viewCount'],
        'channel_videocount' : channel_response['items'][0]['statistics']['videoCount'],
        'channel_subscount' : channel_response['items'][0]['statistics']['subscriberCount'],
    }

    return data

# Video data Extraction

import isodate

def video_data(channel_playlist_ID):
    playlist_data = []
    next_page_token = None
    video_data_final = []
    seen_video_ids = set()

    while True:
            playlist_request = youtube.playlistItems().list(
                part="snippet",
                playlistId=channel_playlist_ID,
                pageToken=next_page_token
            )
            playlist_response = playlist_request.execute()

            playlist_data += playlist_response['items']


            for item in playlist_data:
                
                video_id = item['snippet']['resourceId']['videoId']

                if video_id in seen_video_ids:
                    continue 

                seen_video_ids.add(video_id) 

                
            
                video_request = youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            )
                
                video_response = video_request.execute()
                video_items = video_response.get('items', [])

                
                for item in video_items:

                    video_duration = item['contentDetails']['duration']
                
                    video_duration_sec = isodate.parse_duration(video_duration).total_seconds()


                    channel_id = item['snippet']['channelId']
                    
                    channel_request = youtube.channels().list(
                        part="snippet",
                        id=channel_id
                    )
                    channel_response = channel_request.execute()

                    channel_title = channel_response['items'][0]['snippet']['title']

                    video_info = {
                        'channel_title': channel_title,
                        'video_id' : video_id,
                        'video_title' : video_response['items'][0]['snippet']['title'],
                        'video_description' : video_response['items'][0]['snippet']['description'],
                        'video_published_date' : video_response['items'][0]['snippet']['publishedAt'],
                        'video_thumbnail' : video_response['items'][0]['snippet']['thumbnails']['default']['url'],
                        'video_duration_sec' : video_duration_sec,
                        'video_caption' : video_response['items'][0]['contentDetails']['caption'],
                        'video_viewcount' : video_response['items'][0]['statistics']['viewCount'],
                        'video_likecount' : video_response['items'][0]['statistics'].get('likeCount',0),
                        'video_favoritecount' : video_response['items'][0]['statistics']['favoriteCount'],
                        'video_commentcount' : video_response['items'][0]['statistics'].get('commentCount',0)    
                    }
                    video_data_final.append(video_info)
            
            next_page_token = playlist_response.get('nextPageToken')

            if not next_page_token:
                break

    return video_data_final

# Video ID extraction

def video_id(channel_playlist_ID):
    video_id_full = []
    next_page_token = None

    while True:
        playlist_request = youtube.playlistItems().list(
            part="snippet",
            playlistId=channel_playlist_ID,
            pageToken=next_page_token
        )
        playlist_response = playlist_request.execute()

        playlist_items = playlist_response.get('items', [])

        for item in playlist_items:
            
            video_id_full.append(item['snippet']['resourceId']['videoId'])

        next_page_token = playlist_response.get('nextPageToken')

        if not next_page_token:

            break
        
    return video_id_full

# Comment Data Extraction

def comment_data(video_id_full):
    all_comments = []

    for video_id in video_id_full:
        next_page_token = None
        comment_count = 0

        video_request = youtube.videos().list(
            part="snippet",
            id=video_id
        )
        video_response = video_request.execute()

        channel_title = video_response['items'][0]['snippet']['channelTitle']


        while comment_count < 5:
            try:
                comment_request = youtube.commentThreads().list(
                part="snippet",
                videoId = video_id,
                maxResults=25 - comment_count,
                pageToken = next_page_token

            )
                comment_response = comment_request.execute()

                comment_items = comment_response.get('items',[])

                for item in comment_items:
                    
                    comment = item['snippet']['topLevelComment']['snippet']

                    all_comments.append({
                        'channel_title' : channel_title,
                        'video_id': video_id,
                        'comment_id': item['id'],
                        'author': comment['authorDisplayName'],
                        'text': comment['textDisplay'],
                        'published_at': comment['publishedAt']
                    })

                    comment_count += 1

                    if comment_count >= 5:
                        break

                next_page_token = comment_response.get('nextpagetoken')

                if not next_page_token:
                    break

            except Exception as e:
                if 'commentsDisabled' in str(e):
                    print(f"Comments are blocked by the user for video ID: {video_id}")
                    break  
                else:
                    raise

    return all_comments


# Connecting with SQL local host

mydb = mysql.connector.connect(host="localhost",user="root",password="")

print(mydb)
mycursor = mydb.cursor(buffered=True)

# Streamlit 

import streamlit as st

# Page Functions

def intro_page():

    st.markdown("<h1 style='text-align: center; color: #003366;'>Youtube Data Harvesting and Warehousing</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])  
    with col2:
        st.image('youtube.jpg', width=350, output_format="auto")

    st.markdown(f"""
    <h3 style='color: #003366;'>Tools Used</h3>
    <ul style=font-size: 16px;>
        <li><b>YouTube Data API</b>: For Accessing YouTube Channel Data.</li>
        <li><b>Python</b>: For Data Extraction from API(Backend Development) .</li>
        <li><b>Pandas</b>: For Converting Data to Data Frame.</li>
        <li><b>SQL</b>: For Database Management.</li>
        <li><b>Streamlit</b>: For Creating the Web Application.</li>
        
    </ul>
    """, unsafe_allow_html=True)


    st.markdown("<p style='text-align: right; font-size: 16px;margin-bottom: 0px; '>Submitted by</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: right; font-size: 18px;'><b>N. Senthamizh Priya</b></p>", unsafe_allow_html=True)
    

def data_scraping_page():
    st.title("Data Scraping")
    channel_id = st.text_input("Enter YouTube Channel ID:", "")
    if st.button("Fetch Channel Data"):
        if channel_id:
            channel_info = channel_data(channel_id)
            
            if 'Error' in channel_info:
                st.error(channel_info['Error'])

            else:

                # Display channel data

                st.write(f"**Channel Title:** {channel_info['channel_title']}")
                st.write(f"**Description:** {channel_info['channel_description']}")
                st.write(f"**Published Date:** {channel_info['published_date']}")
                st.write(f"**Playlist ID:** {channel_info['channel_playlist_ID']}")
                st.write(f"**View Count:** {channel_info['channel_viewcount']}")
                st.write(f"**Video Count:** {channel_info['channel_videocount']}")
                st.write(f"**Subscriber Count:** {channel_info['channel_subscount']}")
        else:
            st.error("Please enter a valid YouTube Channel ID")     

def extract_store_exhibit_page():

    engine = create_engine('mysql+pymysql://root:@localhost/youtube_project')

    def insert_data(df, table_name):
        df.to_sql(table_name, con=engine, if_exists='append', index=False)

    def main():
        st.title('YouTube Channel Data Extraction and storage')

        channel_id = st.text_input("Enter the YouTube Channel ID:")

        if st.button("Fetch and Store Channel Data"):
            with st.spinner("Fetching and storing data..."):
                if channel_id:
                    # Fetch channel data
                    channel_info = channel_data(channel_id)
                    if channel_info:
                        # Store channel data
                        df_channel = pd.DataFrame([channel_info])
                        insert_data(df_channel, 'channels_data')
                        st.success("Channel data stored successfully!")

                        # Fetch video data
                        playlist_id = channel_info.get('channel_playlist_ID')
                        if playlist_id:
                            videos = video_data(playlist_id)
                            if videos:
                                # Store video data
                                df_videos = pd.DataFrame(videos)
                                insert_data(df_videos, 'video_data')
                                st.success("Video data stored successfully!")

                                # Fetch and store comments for each video
                                video_ids = [video['video_id'] for video in videos]
                                comments = comment_data(video_ids)
                                if comments:
                                    # Store comment data
                                    df_comments = pd.DataFrame(comments)
                                    insert_data(df_comments, 'comment_data')
                                    st.success("Comment data stored successfully!")
                                else:
                                    st.error("Failed to fetch comments.")
                            else:
                                st.error("Failed to fetch video data.")
                        else:
                            st.error("Playlist ID not found in channel data.")
                    else:
                        st.error("Failed to fetch channel data.")
                else:
                    st.error("Please enter a valid channel ID.")

    if __name__ == "__main__":
        main()

def questions_answers_page():

    Question_1 = '1. What are the names of all the videos and their corresponding channels?'

    mycursor.execute('select channel_title, video_title from youtube_project.video_data')
    out=mycursor.fetchall()
    df1 = pd.DataFrame(out, columns=[i[0] for i in mycursor.description])

    Question_2 = '2. Which channels have the most number of videos, and how many videos do they have?'

    mycursor.execute('select channel_title, channel_videocount from youtube_project.channels_data order by channel_videocount DESC')
    out=mycursor.fetchall()
    df2 = pd.DataFrame(out, columns=[i[0] for i in mycursor.description])

    Question_3 = '3. What are the top 10 most viewed videos and their respective channels?'

    mycursor.execute('select channel_title,video_title, video_viewcount from youtube_project.video_data order by video_viewcount DESC limit 10')
    out=mycursor.fetchall()
    df3 = pd.DataFrame(out, columns=[i[0] for i in mycursor.description])

    Question_4 = '4. How many comments were made on each video, and what are their corresponding video names?'

    mycursor.execute('select video_title, video_commentcount from youtube_project.video_data')
    out=mycursor.fetchall()
    df4 = pd.DataFrame(out, columns=[i[0] for i in mycursor.description])

    Question_5 = '5. Which videos have the highest number of likes, and what are their corresponding channel names?'

    mycursor.execute('select video_title, video_likecount, channel_title from youtube_project.video_data order by video_likecount DESC limit 25')
    out=mycursor.fetchall()
    df5 = pd.DataFrame(out, columns=[i[0] for i in mycursor.description])

    Question_6 = '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?'

    mycursor.execute('select video_title, video_likecount from youtube_project.video_data order by video_likecount DESC limit 25')
    out=mycursor.fetchall()
    df6 = pd.DataFrame(out, columns=[i[0] for i in mycursor.description])

    Question_7 = '7. What is the total number of views for each channel, and what are their corresponding channel names?'

    mycursor.execute('select channel_viewcount , channel_title from youtube_project.channels_data order by channel_viewcount DESC')
    out=mycursor.fetchall()
    df7 = pd.DataFrame(out, columns=[i[0] for i in mycursor.description])

    Question_8 = '8. What are the names of all the channels that have published videos in the year 2022?'

    mycursor.execute('select channel_title from youtube_project.channels_data where year(published_date) = 2022')
    out=mycursor.fetchall()
    df8 = pd.DataFrame(out, columns=[i[0] for i in mycursor.description])

    Question_9 = '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?'

    mycursor.execute('select channel_title, avg(video_duration_sec) as average_duration from youtube_project.video_data group by channel_title')
    out=mycursor.fetchall()
    df9 = pd.DataFrame(out, columns=[i[0] for i in mycursor.description])

    Question_10 = '10. Which videos have the highest number of comments, and what are their corresponding channel names?'

    mycursor.execute('select video_title, video_commentcount,channel_title from youtube_project.video_data order by video_commentcount DESC limit 15')
    out=mycursor.fetchall()
    df10 = pd.DataFrame(out, columns=[i[0] for i in mycursor.description])

    questions = {Question_1 : df1,
                Question_2 : df2,
                Question_3 : df3,
                Question_4 : df4,
                Question_5 : df5,
                Question_6 : df6,
                Question_7 : df7,
                Question_8 : df8,
                Question_9 : df9,
                Question_10 : df10             
    }

    st.title("Questions and Answers")
    selected_question = st.selectbox("Select a question", list(questions.keys()))

    st.write(f"## {selected_question}")
    st.write(questions[selected_question])

# Main function

def main():
    st.sidebar.title("Navigation")
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Introduction'

    # Button navigation
    if st.sidebar.button("Introduction"):
        st.session_state.current_page = 'Introduction'
    if st.sidebar.button("Data Scraping"):
        st.session_state.current_page = 'Data Scraping'
    if st.sidebar.button("Extract Store Exhibit"):
        st.session_state.current_page = 'Extract Store Exhibit'
    if st.sidebar.button("Questions and Answers"):
        st.session_state.current_page = 'Questions and Answers'

    # Display the selected page
    if st.session_state.current_page == "Introduction":
        intro_page()
    elif st.session_state.current_page == "Data Scraping":
        data_scraping_page()
    elif st.session_state.current_page == "Extract Store Exhibit":
        extract_store_exhibit_page()
    elif st.session_state.current_page == "Questions and Answers":
        questions_answers_page()

if __name__ == "__main__":
    main()



