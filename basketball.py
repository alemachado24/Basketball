
#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import pandas as pd
import base64
import numpy as np
import requests
from bs4 import BeautifulSoup
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
import io
from datetime import date
import re
import datetime
import plotly.express as px
from PIL import Image



st.set_page_config(page_title="NBA", page_icon="📈",layout="wide",)


st.sidebar.markdown("NBA Forecast")

############################## PENDING TO ADD NBA GAMES ###############################

@st.cache
def nba_logo():
    '''
    Function to pull NFL stats from Pro Football Reference (https://www.pro-football-reference.com/).
    - team : team name (str)
    - year : year (int)
    '''
    # pull data
    url = f'https://www.basketball-reference.com/leagues/NBA_2023.html'
    html = requests.get(url).text
    soup = BeautifulSoup(html,'html.parser')

    # parse the data
    table = soup.find("img",class_="teamlogo")
#     st.text(table)
    logo = table['src']
#     st.text(logo)
    return logo

option1, option2 = st.columns(2)
with option1:
    st.title('Forecast & Stats')
with option2:
    st.image(nba_logo(),width=150)

# https://github.com/alemachado24/NFL/blob/b37dbae27924a9580b1e5a79fdf113262b58354b/nfl-league-logo.png

# nfl-league-logo.png

# st.markdown("""
# This app performs simple webscraping of NFL Football player stats data
# * **Data source:** [https://projects.fivethirtyeight.com/](https://projects.fivethirtyeight.com/).
# """)

st.caption("This app performs simple webscraping of NBA player stats data")
st.caption("Data Sources: fivethirtyeight and pro-basketball-reference Websites")

#sidebar
selected_year = st.sidebar.selectbox('Year', list(reversed(range(1990,2024))))

general_stats, upcoming_games = st.tabs(["Standing Forecast", "Upcoming Games & Stats"])

##############################################################################################################################
############################################         Standing Forecast            ############################################
##############################################################################################################################

with general_stats:

    st.header(f'Standing {selected_year} NBA Forecast from FiveThirtyEight ')
    #---------------------------------538 Prediction Table
#     @st.cache
    def get_new_data538(year):
        '''
        Function to pull NFL stats from 538 Reference (https://projects.fivethirtyeight.com/2023-nba-predictions/?ex_cid=irpromo).
        - year : year (int)
        '''
        # pull data
        url = f'https://projects.fivethirtyeight.com/{selected_year}-nba-predictions/'
        html = requests.get(url).text
        #to make sure the url is corrext check the .text
    #     st.text(url)

        # parse the data
        soup = BeautifulSoup(html,'html.parser')
    #     st.header('soup')

        #find the id in the table by inspecting the website
        table = soup.find("table", id="standings-table")
#         st.dataframe(table)

        #find the right body
        gdp_table_body = table.tbody.find("tbody")#[2:] 

        #to find all row values in the table
        gdp_table_data = table.tbody.find_all("tr")#[2:] 
#         st.dataframe(gdp_table_data)

        #it's not for headings, it's for the row data
        headings = []
        for tablerow in gdp_table_data:
            # remove any newlines and extra spaces from left and right
            headings.append([tabledata.get_text(strip=True) for tabledata in tablerow.find_all("td")])
    #     st.dataframe(headings)
    #tabledata.get_text(strip=True)

        df = pd.DataFrame(headings)
#         st.dataframe(df)

        #Instead of dropping the columns and selecting the columns I'm going to use
        index = [0] + list(range(3,12))
        new_data_standings = df.iloc[:,index].copy()
        

#         #Rename columns
        col_names = ['Current Rating', 'Team', 'Conference', 'Full Rating', 'Proj Record', 'PROJ Point Diff', 'Playoffs %','Full Rating Playoffs', 'To Finals', 'Win Finals']
        new_data_standings.columns = col_names
#         st.dataframe(new_data_standings)
        return new_data_standings

    #Dataframe with Standing Predictions from 538
    
    st.dataframe(get_new_data538(selected_year))
    
    
    
    #---------------------------------End Of 538 Prediction Table


##############################################################################################################################
############################################           Upcoming Games             ############################################
##############################################################################################################################

with upcoming_games:
    
    
    
#     st.header("Upcoming Games")

    #---------------------------------Week Forecast & Upcomming Games
    row1_1, row1_2 = st.columns((3, 3))#st.columns(2)

    with row1_2:

        st.write(f'Games Win Probabilities in {selected_year} from FiveThirtyEight ')
        #------------- webscrap for elo
#         @st.cache(hash_funcs={pd.DataFrame: lambda _: None})
        def get_new_data538_games(year):
            '''
            Function to pull NFL stats from 538 Reference (https://projects.fivethirtyeight.com/2022-nfl-predictions/).
            - year : year (int)
            '''
            # pull data
            url = f'https://projects.fivethirtyeight.com/{selected_year}-nba-predictions/games/'
            html = requests.get(url).text

            soup = BeautifulSoup(html,'html.parser')
#             st.text(url)
            #------------------------

            table2 = soup.find_all(class_=["h3","h4","tr"])
#             st.dataframe(table2)


            data_tocheck = []

            for tablerow in table2:
                data_tocheck.append([tabledata.get_text(strip=True) for tabledata in tablerow.find_all('th')])
                data_tocheck.append([tabledata.get_text(strip=True) for tabledata in tablerow.find_all('td')])


            df_tocheck = pd.DataFrame(data_tocheck)
#             st.dataframe(df_tocheck)
            
            index = list(range(1,5))
            df_tocheck2 = df_tocheck.iloc[:,index].copy()

            col_names = ['Time', 'Team', 'Spread', 'Probability']
            df_tocheck2.columns = col_names

            df_tocheck2 = df_tocheck2[df_tocheck2.Team.notnull()]

            df_tocheck2['Team'] = df_tocheck2['Team'].str.replace('RAPTOR spread','')
            df_tocheck2['Spread'] = df_tocheck2['Spread'].str.replace('Win prob.','')
            df_tocheck2['Probability'] = df_tocheck2['Probability'].str.replace('Score','')


            return df_tocheck2
    
        
        testFrame=pd.DataFrame(get_new_data538_games(selected_year))

        def color_negative_red(val):
            '''
            highlight the maximum in a Series yellow.
            '''
            color = 'lightgreen' if str(val) > str(70) else 'white'
            return 'background-color: %s' % color
        s = testFrame.style.applymap(color_negative_red, subset=['Probability'])
        st.text('')
        st.text('')
        st.text('')
        st.text('')
        st.text('')
#         st.text('')
        st.dataframe(s)

    with row1_1:
#         @st.cache
        st.write(f'Games Scheduled in {selected_year-1}/{selected_year}')
#         st.write('')
        months = ['January','February','March','April','October','November','December']
        selected_month = st.selectbox('Month', months)
        
        def get_schedules(year):
            '''
            Function to pull NFL stats from Pro Football Reference (https://www.pro-football-reference.com/).

            - team : team name (str)
            - year : year (int)
            https://www.pro-football-reference.com/years/2022/games.htm
            '''
            # pull data
#             url = f'https://www.pro-football-reference.com/years/{selected_year}/games.htm'
            url = f'https://www.basketball-reference.com/leagues/NBA_{selected_year}_games-{selected_month.lower()}.html'
            html = requests.get(url).text
        #     st.text(url)

            # parse the data
            soup = BeautifulSoup(html,'html.parser')
            table = soup.find('table', id='schedule')
            tablerows = table.find_all('tr')[1:]
            data = []
            data2 = []

            for tablerow in tablerows:
                data.append([tabledata.get_text(strip=True) for tabledata in tablerow.find_all('td')])
    
            for tablerow in tablerows:
                    data2.append([tabledata.get_text(strip=True) for tabledata in tablerow.find_all('th')])

            df = pd.DataFrame(data)
            
#              # subset
            index = [0,1,2,3]
            new_data = df.iloc[:,index].copy()

#         #     rename columns
            col_names = [ 'Time (ET)', 'Visitor','VisitorPoints', 'Home']
            new_data.columns = col_names
#             st.dataframe(new_data)

            df2 = pd.DataFrame(data2)
            col_names2 = ['Date']
            df2.columns = col_names2
#             st.dataframe(df2)
            
            combined_list2 = pd.concat([df2, new_data], axis=1)
            combined_list=combined_list2.loc[combined_list2['VisitorPoints']=='']
            combined_list=combined_list.drop(['VisitorPoints'], axis=1)
#             st.dataframe(combined_list)
            return combined_list
        
        new_data_future = get_schedules(year=selected_year)

        # Filtering data
        st.dataframe(new_data_future)
