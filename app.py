import streamlit as st
import pandas as pd
import preprocessor, helper
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import requests
from sklearn.linear_model import LinearRegression
import numpy as np

# Set page configuration
st.set_page_config(page_title="Olympics Insights & Predictions", page_icon="🏅", layout="wide")

# Custom CSS for better visuals
st.markdown("""
    <style>
    .stApp {
        background-color: #f9f9f9;
    }
    .metric-container {
        display: flex;
        justify-content: space-evenly;
        gap: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Fetch and read CSV files
@st.cache_data
def load_data():
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

    return preprocessor.preprocess(df, region_df)

df = load_data()

# Sidebar with branding
# st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/e/e5/Olympic_rings_without_white_rims.svg", use_column_width=True)
st.sidebar.title("🏅 Olympics Dashboard")
st.sidebar.write("**Explore data, trends, and insights from the history of the Olympics!**")

# Sidebar Menu
user_menu = st.sidebar.radio(
    'Navigate',
    ('Medal Tally', 'Overall Analysis', 'Country-wise Analysis', 'Athlete-wise Analysis', 'Medal Predictions')
)

# Medal Tally Section
if user_menu == 'Medal Tally':
    st.sidebar.header("Filter Options")
    years, country = helper.country_year_list(df)
    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country = st.sidebar.selectbox("Select Country", country)

    st.title(f"🎖️ Medal Tally for {selected_year} | {selected_country}")
    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)
    st.table(medal_tally.style.set_table_styles(
        [{'selector': 'th', 'props': [('background-color', '#FFD700'), ('color', 'white'), ('font-weight', 'bold')]},
        {'selector': 'td', 'props': [('color', 'white'), ('background-color', '#2E2E2E')]} ]
    ))

# Overall Analysis Section
elif user_menu == 'Overall Analysis':
    st.title("🌍 Olympics History Overview")
    st.markdown("### Explore key statistics, trends, and milestones in the history of the Olympics!")

    # Key Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Editions", df['Year'].nunique() - 1)
    col2.metric("Host Cities", df['City'].nunique())
    col3.metric("Sports", df['Sport'].nunique())

    col4, col5, col6 = st.columns(3)
    col4.metric("Events", df['Event'].nunique())
    col5.metric("Nations", df['region'].nunique())
    col6.metric("Athletes", df['Name'].nunique())

    st.markdown("---")
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
    st.subheader("📈 Trends Over Time")
    metrics = {'region': "Participating Nations", 'Event': "Events", 'Name': "Athletes"}
    for key, value in metrics.items():
        data = helper.participating_nations_over_time(df, key)
        fig = px.line(data, x="Edition", y="No of Countries", title=f"{value} Over Time", markers=True, color_discrete_sequence=['#EF553B'])
        st.plotly_chart(fig)

    # Heatmap of Events
    st.subheader("🔥 Number of Events Over Time")
    fig, ax = plt.subplots(figsize=(15, 10))
    heat_data = df.drop_duplicates(['Year', 'Sport', 'Event']).pivot_table(
        index='Sport', columns='Year', values='Event', aggfunc='count').fillna(0).astype('int')
    sns.heatmap(heat_data, annot=True, cmap="coolwarm", cbar_kws={'label': 'Number of Events'})
    st.pyplot(fig)

# Country-wise Analysis Section
elif user_menu == 'Country-wise Analysis':
    country_list = df['region'].dropna().unique().tolist()
    selected_country = st.sidebar.selectbox("Select a Country", sorted(country_list))
    country_df = helper.year_wise_medal_tally(df, selected_country)

    st.title(f"🏅 Medal Tally Over Time - {selected_country}")
    fig = px.line(country_df, x="Year", y="Medal", title=f"{selected_country} Medal Tally", markers=True, color_discrete_sequence=['#636EFA'])
    st.plotly_chart(fig)

# Athlete-wise Analysis Section
elif user_menu == 'Athlete-wise Analysis':
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    st.title("👟 Athlete Statistics")
    st.subheader("Age Distribution of Medalists")
    x1 = athlete_df['Age'].dropna()
    x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
    x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
    x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()
    fig = ff.create_distplot([x1, x2, x3, x4], ['Overall', 'Gold', 'Silver', 'Bronze'], show_hist=False, show_rug=False)
    st.plotly_chart(fig)
     # Age Distribution wrt Sports (Gold Medalists)
    st.subheader("Distribution of Age wrt Sports (Gold Medalist)")
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
    fig.update_layout(autosize=False, width=1000, height=600)
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
    st.subheader("Men vs Women Participation Over the Years")
    final = helper.men_vs_women(df)
    fig = px.line(final, x="Year", y=["Male", "Female"], markers=True)
    fig.update_layout(autosize=False, width=1000, height=600)
    st.plotly_chart(fig)

# Medal Predictions Section
elif user_menu == 'Medal Predictions':
    st.title("🔮 Medal Predictions")
    st.markdown("### Use this feature to predict future medal counts using different features.")
    feature = st.selectbox("Select Feature for Prediction", ['GDP', 'Population', 'Athlete Count'])
    st.info("This is a mock prediction demo using random data for illustrative purposes.")

    # Mock Data Example
    X = np.random.rand(100, 1) * 100
    y = X * 2 + np.random.rand(100, 1) * 10
    model = LinearRegression()
    model.fit(X, y)
    predicted = model.predict(X)
    st.line_chart(pd.DataFrame({"Actual": y.flatten(), "Predicted": predicted.flatten()}))
