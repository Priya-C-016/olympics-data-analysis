import streamlit as st
import pandas as pd
import preprocessor, helper
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import requests

# Set page configuration
st.set_page_config(page_title="Olympics Analysis", page_icon="🏅", layout="wide")

# Fetch and read CSV files
url = "https://drive.google.com/uc?export=download&id=1S9scFRbnlAi_PxYKfnyrrM33O69prXfa"
response = requests.get(url)
response.raise_for_status()

with open("data.csv", "wb") as file:
    file.write(response.content)

df = pd.read_csv("data.csv")

url1 = "https://drive.google.com/uc?export=download&id=1uF_fbc-OYLUqh_Nap39O3gzUFCjWoTP_"
response = requests.get(url1)
response.raise_for_status()

with open("noc_regions.csv", "wb") as file:
    file.write(response.content)

region_df = pd.read_csv("noc_regions.csv")

df = preprocessor.preprocess(df, region_df)

# Sidebar configuration
st.sidebar.title("Olympics Analysis")
st.sidebar.image('https://e7.pngegg.com/pngimages/1020/402/png-clipart-2024-summer-olympics-brand-circle-area-olympic-rings-olympics-logo-text-sport.png')
user_menu = st.sidebar.radio(
    'Select an Option',
    ('Medal Tally', 'Overall Analysis', 'Country-wise Analysis', 'Athlete wise Analysis')
)

# Medal Tally Section
if user_menu == 'Medal Tally':
    st.sidebar.header("Medal Tally")
    years, country = helper.country_year_list(df)
    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country = st.sidebar.selectbox("Select Country", country)

    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)
    
    if selected_year == 'Overall' and selected_country == 'Overall':
        st.title("Overall Tally")
    elif selected_year != 'Overall' and selected_country == 'Overall':
        st.title(f"Medal Tally in {selected_year} Olympics")
    elif selected_year == 'Overall' and selected_country != 'Overall':
        st.title(f"{selected_country} overall performance")
    elif selected_year != 'Overall' and selected_country != 'Overall':
        st.title(f"{selected_country} performance in {selected_year} Olympics")
    
    st.table(medal_tally)

# Overall Analysis Section
if user_menu == 'Overall Analysis':
    editions = df['Year'].unique().shape[0] - 1
    cities = df['City'].unique().shape[0]
    sports = df['Sport'].unique().shape[0]
    events = df['Event'].unique().shape[0]
    athletes = df['Name'].unique().shape[0]
    nations = df['region'].unique().shape[0]

    st.title("Top Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Editions")
        st.title(editions)
    with col2:
        st.header("Hosts")
        st.title(cities)
    with col3:
        st.header("Sports")
        st.title(sports)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Events")
        st.title(events)
    with col2:
        st.header("Nations")
        st.title(nations)
    with col3:
        st.header("Athletes")
        st.title(athletes)
    
    medal_tally = helper.fetch_medal_tally(df, 'Overall', 'Overall')

# Create a bar chart to show the number of medals each country has won
    fig = px.bar(medal_tally, 
             x='region', 
             y=['Gold', 'Silver', 'Bronze'], 
             title="Medal Tally by Country", 
             labels={'region': 'Country', 'value': 'Number of Medals'}, 
             color_discrete_sequence=['gold', 'silver', 'brown'])

# Customize the layout for better visual appeal
    fig.update_layout(
    barmode='stack',  # Stack the bars for each country
    xaxis_tickangle=-45,  # Rotate the x-axis labels for better readability
    title_font=dict(size=24, family='Arial', color='black'),
    xaxis_title="Countries",
    yaxis_title="Number of Medals",
    showlegend=True
)

# Display the figure
    st.plotly_chart(fig)
    # Plot interactive charts
    nations_over_time = helper.participating_nations_over_time(df, 'region')
    fig = px.line(nations_over_time, x="Edition", y="No of Countries", title="Participating Nations over the years", 
                  line_shape="linear", markers=True)
    st.plotly_chart(fig)

    nations_over_time = helper.participating_nations_over_time(df, 'Event')
    fig = px.line(nations_over_time, x="Edition", y="No of Countries", title="Events over the years", 
                  line_shape="linear", markers=True)
    st.plotly_chart(fig)

    nations_over_time = helper.participating_nations_over_time(df, 'Name')
    fig = px.line(nations_over_time, x="Edition", y="No of Countries", title="Athletes over the years", 
                  line_shape="linear", markers=True)
    st.plotly_chart(fig)

    st.title("No. of Events over time (Every Sport)")
    fig, ax = plt.subplots(figsize=(20, 20))
    x = df.drop_duplicates(['Year', 'Sport', 'Event'])
    ax = sns.heatmap(
        x.pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count').fillna(0).astype('int'),
        annot=True, cmap="coolwarm", cbar_kws={'label': 'Number of Events'})
    st.pyplot(fig)

    st.title("Most Successful Athletes")
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')
    selected_sport = st.selectbox("Select Sport", sport_list)
    x = helper.most_successful(df, selected_sport)
    st.table(x)

# Country-wise Analysis Section
if user_menu == 'Country-wise Analysis':
    st.sidebar.title('Country-wise Analysis')
    country_list = df['region'].dropna().unique().tolist()
    country_list.sort()
    selected_country = st.sidebar.selectbox('Select a Country', country_list)

    country_df = helper.year_wise_medal_tally(df, selected_country)
    fig = px.line(country_df, x="Year", y="Medal", title=f"{selected_country} Medal Tally over the years", markers=True)
    st.plotly_chart(fig)

    st.title(f"{selected_country} Excels in the Following Sports")
    pt = helper.country_event_heatmap(df, selected_country)
    fig, ax = plt.subplots(figsize=(20, 20))
    ax = sns.heatmap(pt, annot=True, cmap="coolwarm", cbar_kws={'label': 'Medals'})
    st.pyplot(fig)

    st.title(f"Top 10 Athletes of {selected_country}")
    top10_df = helper.most_successful_country_wise(df, selected_country)
    st.table(top10_df)

# Athlete-wise Analysis Section
if user_menu == 'Athlete wise Analysis':
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    # Age Distribution
    x1 = athlete_df['Age'].dropna()
    x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
    x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
    x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()

    fig = ff.create_distplot([x1, x2, x3, x4], ['Overall Age', 'Gold Medalist', 'Silver Medalist', 'Bronze Medalist'], 
                             show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, width=1000, height=600, title="Distribution of Age")
    st.plotly_chart(fig)

    # Age Distribution wrt Sports (Gold Medalists)
    x = []
    name = []
    famous_sports = ['Basketball', 'Judo', 'Football', 'Tug-Of-War', 'Athletics', 'Swimming', 'Badminton', 
                     'Sailing', 'Gymnastics', 'Art Competitions', 'Handball', 'Weightlifting', 'Wrestling',
                     'Water Polo', 'Hockey', 'Rowing', 'Fencing', 'Shooting', 'Boxing', 'Taekwondo', 'Cycling',
                     'Diving', 'Canoeing', 'Tennis', 'Golf', 'Softball', 'Archery', 'Volleyball', 
                     'Synchronized Swimming', 'Table Tennis', 'Baseball', 'Rhythmic Gymnastics', 'Rugby Sevens', 
                     'Beach Volleyball', 'Triathlon', 'Rugby', 'Polo', 'Ice Hockey']
    for sport in famous_sports:
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        x.append(temp_df[temp_df['Medal'] == 'Gold']['Age'].dropna())
        name.append(sport)

    fig = ff.create_distplot(x, name, show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, width=1000, height=600, title="Distribution of Age wrt Sports (Gold Medalist)")
    st.plotly_chart(fig)

    # Height vs Weight scatter plot
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')
    selected_sport = st.selectbox('Select a Sport', sport_list)

    temp_df = helper.weight_v_height(df, selected_sport)
    fig, ax = plt.subplots()
    sns.scatterplot(x=temp_df['Weight'], y=temp_df['Height'], hue=temp_df['Medal'], style=temp_df['Sex'], s=60, ax=ax)
    st.pyplot(fig)

    # Men vs Women Participation Over the Years
    final = helper.men_vs_women(df)
    fig = px.line(final, x="Year", y=["Male", "Female"], title="Men vs Women Participation Over the Years", markers=True)
    fig.update_layout(autosize=False, width=1000, height=600)
    st.plotly_chart(fig)
