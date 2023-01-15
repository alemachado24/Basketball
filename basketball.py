#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import pandas as pd
import base64
import numpy as np
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns
import io
import re
import plotly.express as px
from PIL import Image


st.set_page_config(page_title="NBA", page_icon="🏀",layout="wide",)

st.sidebar.markdown("NBA Forecast 🏀")

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
    table = soup.find("img",class_="teamlogo")
    logo = table['src']
    return logo

option1, option2 = st.columns(2)
with option1:
    st.title('Forecast & Stats')
with option2:
    st.image(nba_logo(),width=150)


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
    @st.cache
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


    #---------------------------------Week Forecast & Upcomming Games
    row1_1, row1_2 = st.columns((3, 3))#st.columns(2)

    with row1_2:

        st.write(f'Games Win Probabilities in {selected_year} from FiveThirtyEight ')
        #------------- webscrap for elo
#         @st.cache(hash_funcs={pd.DataFrame: lambda _: None})
        @st.cache
        def get_new_data538_games(year):
            '''
            Function to pull NFL stats from 538 Reference (https://projects.fivethirtyeight.com/2022-nfl-predictions/).
            - year : year (int)
            '''
            # pull data
            url = f'https://projects.fivethirtyeight.com/{selected_year}-nba-predictions/games/'
            html = requests.get(url).text

            soup = BeautifulSoup(html,'html.parser')

            table2 = soup.find_all(class_=["h3","h4","tr"])

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
            color = 'lightgreen' if str(val) > str(80) else 'white'
            return 'background-color: %s' % color
        s = testFrame.style.applymap(color_negative_red, subset=['Probability'])
        st.text('')
        st.text('')
        st.text('')
        st.text('')
        st.text('')
        st.dataframe(s)

    with row1_1:
        st.write(f'Games Scheduled in {selected_year-1}/{selected_year}')
        months = ['January','February','March','April','October','November','December']
        selected_month = st.selectbox('Month', months)
        
        @st.cache
        def get_schedules(year):
            '''
            Function to pull NFL stats from Pro Football Reference (https://www.pro-football-reference.com/).

            - team : team name (str)
            - year : year (int)
            https://www.pro-football-reference.com/years/2022/games.htm
            '''
            # pull data
            url = f'https://www.basketball-reference.com/leagues/NBA_{selected_year}_games-{selected_month.lower()}.html'
            html = requests.get(url).text
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
            
#             # subset
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

    #---------------------------------End of Week Forecast & Upcomming Games ADDED UP TO HERE

    #---------------------------------Select Team to Analyse
    team_names = ['Boston Celtics','Brooklyn Nets','Philadelphia 76ers','New York Knicks','Toronto Raptors','Milwaukee Bucks','Cleveland Cavaliers','Indiana Pacers','Chicago Bulls','Detroit Pistons','Atlanta Hawks','Miami Heat','Washington Wizards','Orlando Magic','Charlotte Hornets','Denver Nuggets','Portland Trail Blazers','Utah Jazz','Minnesota Timberwolves','Oklahoma City Thunder','Phoenix Suns','Los Angeles Clippers','Sacramento Kings','Golden State Warriors','Los Angeles Lakers','Memphis Grizzlies','New Orleans Pelicans','Dallas Mavericks','Houston Rockets','San Antonio Spurs']

    st.header('Compare teams:')
    
    team1, team2 = st.columns(2)#st.columns(2)

    with team1:
        selected_team_full = st.multiselect('',team_names,default = team_names[25])
        try:
            if selected_team_full[0] == 'Boston Celtics':
                short_name = 'BOS'
            elif selected_team_full[0] == 'Brooklyn Nets':
                short_name = 'BRK'
            elif selected_team_full[0] == 'Philadelphia 76ers':
                short_name = 'PHI'
            elif selected_team_full[0] == 'New York Knicks':
                short_name = 'NYK'
            elif selected_team_full[0] == 'Toronto Raptors':
                short_name = 'TOR'
            elif selected_team_full[0] == 'Milwaukee Bucks':
                short_name = 'MIL'
            elif selected_team_full[0] == 'Cleveland Cavaliers':
                short_name = 'CLE'
            elif selected_team_full[0] == 'Indiana Pacers':
                short_name = 'IND'
            elif selected_team_full[0] == 'Chicago Bulls':
                short_name = 'CHI'
            elif selected_team_full[0] == 'Detroit Pistons':
                short_name = 'DET'
            elif selected_team_full[0] == 'Atlanta Hawks':
                short_name = 'ATL'
            elif selected_team_full[0] == 'Miami Heat':
                short_name = 'MIA'
            elif selected_team_full[0] == 'Washington Wizards':
                short_name = 'WAS'
            elif selected_team_full[0] == 'Orlando Magic':
                short_name = 'ORL'
            elif selected_team_full[0] == 'Charlotte Hornets':
                short_name = 'CHO'
            elif selected_team_full[0] == 'Denver Nuggets':
                short_name = 'DEN'
            elif selected_team_full[0] == 'Portland Trail Blazers':
                short_name = 'POR'    
            elif selected_team_full[0] == 'Utah Jazz':
                short_name = 'UTA'
            elif selected_team_full[0] == 'Minnesota Timberwolves':
                short_name = 'MIN'
            elif selected_team_full[0] == 'Oklahoma City Thunder':
                short_name = 'OKC'  
            elif selected_team_full[0] == 'Phoenix Suns':
                short_name = 'PHO'
            elif selected_team_full[0] == 'Los Angeles Clippers':
                short_name = 'LAC'
            elif selected_team_full[0] == 'Sacramento Kings':
                short_name = 'SAC'
            elif selected_team_full[0] == 'Golden State Warriors':
                short_name = 'GSW'
            elif selected_team_full[0] == 'Los Angeles Lakers':
                short_name = 'LAL'
            elif selected_team_full[0] == 'Memphis Grizzlies':
                short_name = 'MEM'
            elif selected_team_full[0] == 'New Orleans Pelicans':
                short_name = 'NOP'
            elif selected_team_full[0] == 'Dallas Mavericks':
                short_name = 'DAL'
            elif selected_team_full[0] == 'Houston Rockets':
                short_name = 'HOU'
            elif selected_team_full[0] == 'San Antonio Spurs':
                short_name = 'SAS'

            @st.cache
            def get_record(team, year):
                '''
                Function to pull NFL stats from Pro Football Reference (https://www.pro-football-reference.com/).
                - team : team name (str)
                - year : year (int)
                '''
                # pull data
                url = f'https://www.basketball-reference.com/teams/{short_name}/{selected_year}.htm'
                html = requests.get(url).text
                #st.text(url)

                # parse the data
                soup = BeautifulSoup(html,'html.parser')
                table = soup.find("strong", text="Record:")
                record=table.next_sibling.strip()
                comma = record.find(',')
#                 st.text(record[:comma])
                
                # parse the data
                table2 = soup.find("strong", text="PTS/G:")
                ptsG=table2.next_sibling.strip()
#                 st.text(ptsG)
                
                # parse the data
                table3 = soup.find("strong", text="Opp PTS/G:")
                OptsG=table3.next_sibling.strip()
#                 st.text(OptsG)

                # parse the data
                table4 = soup.find("strong",text="SRS")
                srs=table4.next_sibling.strip()  
#                 st.text(srs[1:])
                
                # parse the data
                table5 = soup.find("strong",text="Pace")
                pace=table5.next_sibling.strip()  
#                 st.text(pace[1:])
                
                # parse the data
                table6 = soup.find("strong",text="Off Rtg")
                oRtg=table6.next_sibling.strip()  
#                 st.text(oRtg[1:])
                
                # parse the data
                table7 = soup.find("strong",text="Def Rtg")
                dRtg=table7.next_sibling.strip()  
#                 st.text(dRtg[1:])
                
                # parse the data
                table8 = soup.find("strong",text="Net Rtg")
                nRtg=table8.next_sibling.strip()  


                return record[:comma],ptsG,OptsG,srs[1:],pace[1:],oRtg[1:],dRtg[1:],nRtg[1:]

            @st.cache(allow_output_mutation=True) 
            def get_injuries():
                '''
                Function to pull NFL stats from Pro Football Reference (https://www.pro-football-reference.com/).
                - team : team name (str)
                - year : year (int)
                '''
                # pull data
                url = f'https://www.basketball-reference.com/friv/injuries.fcgi'
                html = requests.get(url).text
#                 st.text(url)

                # parse the data
                soup = BeautifulSoup(html,'html.parser')
                table = soup.find('table', id='injuries')
#                 st.dataframe(table)
                tablerows = table.find_all('tr')[1:]
                data = []
                data_names = []

                for tablerow in tablerows:
                    data.append([tabledata.get_text(strip=True) for tabledata in tablerow.find_all('td')])

                for tablerow in tablerows:
                    data_names.append([tabledata.get_text(strip=True) for tabledata in tablerow.find_all('th')])

                df = pd.DataFrame(data)
#                 st.dataframe(pd.DataFrame(data_names))
                
                col_names = ['Team', 'Update', 'Description']
                df.columns = col_names
                df2 = pd.DataFrame(data_names)
                col_names2 = ['Player']
                df2.columns = col_names2

                # to combined 2 dataframes by adding new columns
                combined_list = pd.concat([df2, df], axis=1)
                new_data = combined_list.loc[combined_list['Team']==selected_team_full[0]]

                return new_data
    
            injuries = get_injuries()
            injury_count = len(injuries.index)



            #---------------------------------End of Select Team to Analyse        



            st.header("Team Summary")
            st.markdown(f'Team record: {get_record(team=short_name, year=selected_year)[0]}')
            st.markdown(f'Points For: {get_record(team=short_name, year=selected_year)[1]}')
            st.markdown(f'Points Against: {get_record(team=short_name, year=selected_year)[2]}')
            st.markdown(f'Simple Rating System: {get_record(team=short_name, year=selected_year)[3]}')
            st.markdown(f'Possession Estimate (Pace): {get_record(team=short_name, year=selected_year)[4]}')
            st.markdown(f'Offense Rating: {get_record(team=short_name, year=selected_year)[5]}')
            st.markdown(f'Defense Rating: {get_record(team=short_name, year=selected_year)[6]}')
            st.markdown(f'Net Rating: {get_record(team=short_name, year=selected_year)[7]}')
            st.markdown(f'Team Injury Count for Current Week: {injury_count}')

#COUNT GAMES STATS ADD IT
            @st.cache(allow_output_mutation=True) 
            def get_stats(team, year):
                '''
                Function to pull NFL stats from Pro Football Reference (https://www.pro-football-reference.com/).
                - team : team name (str)
                - year : year (int)
                '''
                # pull data
                url = f'https://www.basketball-reference.com/teams/{short_name}/{selected_year}/gamelog/'
                html = requests.get(url).text

                # parse the data
                soup = BeautifulSoup(html,'html.parser')
                table = soup.find("table", id="tgl_basic")
                tablerows = table.find_all('tr')[2:]
                data = []

                for tablerow in tablerows:
                    data.append([tabledata.get_text(strip=True) for tabledata in tablerow.find_all('td')])

                df = pd.DataFrame(data)

                #Grabbing columns needed
                index = [0,1,2,3,4,5,6,16,17,19,20,21,33,34,36,37,38]
                new_data = df.iloc[:,index].copy()

                #rename columns
                col_names = [ 'Game', 'Date','At', 'Opp','W/L', 'PTS', 'Opp PTS', 'Team ORB', 'Team TRB', 'Team Steals', 'Team Blocks', 'Team TO', 'Opp ORB', 'Opp TRB', 'Opp Steals', 'Opp Blocks', 'Opp TO']
                new_data.columns = col_names
                new_data['Date'] = new_data['Date'].fillna('')
                new_data2=new_data.loc[new_data['Date']!='']

                return new_data2

            new_data = get_stats(team=short_name, year=selected_year)
            
            new_data['PTS'] = new_data['PTS'].astype(int)
            new_data['Opp PTS'] = new_data['Opp PTS'].astype(int)
            new_data['Won/Lost By'] = new_data.apply(lambda x: x['PTS'] - x['Opp PTS'], axis=1)
            new_data['TOT PTS'] = new_data.apply(lambda x: x['PTS'] + x['Opp PTS'], axis=1)
            
            new_data = new_data.reindex([ 'Game', 'Date','At', 'Opp','W/L', 'PTS', 'Opp PTS','Won/Lost By','TOT PTS', 'Team ORB', 'Team TRB', 'Team Steals', 'Team Blocks', 'Team TO', 'Opp ORB', 'Opp TRB', 'Opp Steals', 'Opp Blocks', 'Opp TO'], axis=1)
            
            all_together = new_data['Opp']
            all_together2=all_together.drop_duplicates()

            loss_count=new_data.loc[new_data['W/L']=='L']
            win_count=new_data.loc[new_data['W/L']=='W']

            result_encoder_loss = {'W/L': {'L': 1,'W': 0,'' : pd.NA}}
            loss_encoded = loss_count
            loss_encoded.replace(result_encoder_loss, inplace=True)
            losses = loss_encoded.groupby('Opp').agg({'W/L': sum,'Won/Lost By':'mean','TOT PTS':'mean'}).reset_index()

            result_encoder_wins = {'W/L': {'L': 0,'W': 1,'' : pd.NA}}
            wins_encoded = win_count
            wins_encoded.replace(result_encoder_wins, inplace=True)
            wins=wins_encoded.groupby('Opp').agg({'W/L': sum,'Won/Lost By':'mean','TOT PTS':'mean'}).reset_index()

            result=pd.merge(all_together2,wins,how="left", on=["Opp"])
            result2 = pd.merge(result,losses,how="left", on=["Opp"])
            col_names_results = ['Opp','Win Count', 'Win Avg Pts','Win TOT Pts', 'Loss Count','Lost Avg Pts','Lost TOT Pts']
            result2.columns = col_names_results
#             result2.sort_values(by='Opp')

            result2['Win Count'] = result2['Win Count'].fillna(-1)
            result2['Win Count'] = result2['Win Count'].astype(int)
            result2['Win Count'] = result2['Win Count'].astype(str)
            result2['Win Count'] = result2['Win Count'].replace('-1', '')

            result2['Loss Count'] = result2['Loss Count'].fillna(-1)
            result2['Loss Count'] = result2['Loss Count'].astype(int)
            result2['Loss Count'] = result2['Loss Count'].astype(str)
            result2['Loss Count'] = result2['Loss Count'].replace('-1', '')
            
            result2['Win Avg Pts'] = result2['Win Avg Pts'].fillna(-1000)
            result2['Win Avg Pts'] = result2['Win Avg Pts'].astype(float).round(2)
            result2['Win Avg Pts'] = result2['Win Avg Pts'].astype(str)
            result2['Win Avg Pts'] = result2['Win Avg Pts'].replace('-1000.0', '')

            result2['Lost Avg Pts'] = result2['Lost Avg Pts'].fillna(-1000)
            result2['Lost Avg Pts'] = result2['Lost Avg Pts'].astype(float).round(2)
            result2['Lost Avg Pts'] = result2['Lost Avg Pts'].astype(str)
            result2['Lost Avg Pts'] = result2['Lost Avg Pts'].replace('-1000.0', '')
            
            result2['Win TOT Pts'] = result2['Win TOT Pts'].fillna(-1000)
            result2['Win TOT Pts'] = result2['Win TOT Pts'].astype(float).round(2)
            result2['Win TOT Pts'] = result2['Win TOT Pts'].astype(str)
            result2['Win TOT Pts'] = result2['Win TOT Pts'].replace('-1000.0', '')

            result2['Lost TOT Pts'] = result2['Lost TOT Pts'].fillna(-1000)
            result2['Lost TOT Pts'] = result2['Lost TOT Pts'].astype(float).round(2)
            result2['Lost TOT Pts'] = result2['Lost TOT Pts'].astype(str)
            result2['Lost TOT Pts'] = result2['Lost TOT Pts'].replace('-1000.0', '')
            
            
            st.header('Played Against Summary')
            st.dataframe(result2.sort_values(by='Opp'))

            result_encoder = {'W/L': {'L': 0,'W': 1,'' : pd.NA}}
            new_data_encoded = new_data
            new_data_encoded.replace(result_encoder, inplace=True)

            inform = f"All Past Games this season: Win = 1, Loss=0"
            fig_all = px.line(new_data_encoded, x="Date",hover_data=['Opp','PTS','Opp PTS'], y=new_data_encoded['W/L'], title=inform)
            fig_all.update_traces(line=dict(color="#013369"))
            fig_all.update_layout({ 'plot_bgcolor': 'rgba(128,128,128, 0.1)', 'paper_bgcolor': 'rgba(128,128,128, 0)', })
            st.plotly_chart(fig_all, use_container_width=True)
            
            my_expander_alldata = st.expander(label=f'Click Here to access Previous Plays Details')
            with my_expander_alldata:
                st.dataframe(new_data)
                
            my_expander_injuries = st.expander(label=f'Click Here to access Injuries Details')
            with my_expander_injuries:
                st.dataframe(injuries)


        except:
            st.warning('Please select a team') 
            
######################################### TEAM2 ######################################################

    team_names2 = ['Boston Celtics','Brooklyn Nets','Philadelphia 76ers','New York Knicks','Toronto Raptors','Milwaukee Bucks','Cleveland Cavaliers','Indiana Pacers','Chicago Bulls','Detroit Pistons','Atlanta Hawks','Miami Heat','Washington Wizards','Orlando Magic','Charlotte Hornets','Denver Nuggets','Portland Trail Blazers','Utah Jazz','Minnesota Timberwolves','Oklahoma City Thunder','Phoenix Suns','Los Angeles Clippers','Sacramento Kings','Golden State Warriors','Los Angeles Lakers','Memphis Grizzlies','New Orleans Pelicans','Dallas Mavericks','Houston Rockets','San Antonio Spurs']


    with team2:
        selected_team_full2 = st.multiselect('',team_names2,default = team_names[15])
        try:

            if selected_team_full2[0] == 'Boston Celtics':
                short_name2 = 'BOS'
            elif selected_team_full2[0] == 'Brooklyn Nets':
                short_name2 = 'BRK'
            elif selected_team_full2[0] == 'Philadelphia 76ers':
                short_name2 = 'PHI'
            elif selected_team_full2[0] == 'New York Knicks':
                short_name2 = 'NYK'
            elif selected_team_full2[0] == 'Toronto Raptors':
                short_name2 = 'TOR'
            elif selected_team_full2[0] == 'Milwaukee Bucks':
                short_name2 = 'MIL'
            elif selected_team_full2[0] == 'Cleveland Cavaliers':
                short_name2 = 'CLE'
            elif selected_team_full2[0] == 'Indiana Pacers':
                short_name2 = 'IND'
            elif selected_team_full2[0] == 'Chicago Bulls':
                short_name2 = 'CHI'
            elif selected_team_full2[0] == 'Detroit Pistons':
                short_name2 = 'DET'
            elif selected_team_full2[0] == 'Atlanta Hawks':
                short_name2 = 'ATL'
            elif selected_team_full2[0] == 'Miami Heat':
                short_name2 = 'MIA'
            elif selected_team_full2[0] == 'Washington Wizards':
                short_name2 = 'WAS'
            elif selected_team_full2[0] == 'Orlando Magic':
                short_name2 = 'ORL'
            elif selected_team_full2[0] == 'Charlotte Hornets':
                short_name2 = 'CHO'
            elif selected_team_full2[0] == 'Denver Nuggets':
                short_name2 = 'DEN'
            elif selected_team_full2[0] == 'Portland Trail Blazers':
                short_name2 = 'POR'    
            elif selected_team_full2[0] == 'Utah Jazz':
                short_name2 = 'UTA'
            elif selected_team_full2[0] == 'Minnesota Timberwolves':
                short_name2 = 'MIN'
            elif selected_team_full2[0] == 'Oklahoma City Thunder':
                short_name2 = 'OKC'  
            elif selected_team_full2[0] == 'Phoenix Suns':
                short_name2 = 'PHO'
            elif selected_team_full2[0] == 'Los Angeles Clippers':
                short_name2 = 'LAC'
            elif selected_team_full2[0] == 'Sacramento Kings':
                short_name2 = 'SAC'
            elif selected_team_full2[0] == 'Golden State Warriors':
                short_name2 = 'GSW'
            elif selected_team_full2[0] == 'Los Angeles Lakers':
                short_name2 = 'LAL'
            elif selected_team_full2[0] == 'Memphis Grizzlies':
                short_name2 = 'MEM'
            elif selected_team_full2[0] == 'New Orleans Pelicans':
                short_name2 = 'NOP'
            elif selected_team_full2[0] == 'Dallas Mavericks':
                short_name2 = 'DAL'
            elif selected_team_full2[0] == 'Houston Rockets':
                short_name2 = 'HOU'
            elif selected_team_full2[0] == 'San Antonio Spurs':
                short_name2 = 'SAS'


    #         st.text(short_name)

            @st.cache
            def get_record2(team2, year2):
                '''
                Function to pull NFL stats from Pro Football Reference (https://www.pro-football-reference.com/).
                - team : team name (str)
                - year : year (int)
                '''
                # pull data
                url = f'https://www.basketball-reference.com/teams/{short_name2}/{selected_year}.htm'
                html = requests.get(url).text
                #st.text(url)

                # parse the data
                soup = BeautifulSoup(html,'html.parser')
                table = soup.find("strong", text="Record:")
                record=table.next_sibling.strip()
                comma = record.find(',')
    #                 st.text(record[:comma])

                # parse the data
                table2 = soup.find("strong", text="PTS/G:")
                ptsG=table2.next_sibling.strip()
    #                 st.text(ptsG)

                # parse the data
                table3 = soup.find("strong", text="Opp PTS/G:")
                OptsG=table3.next_sibling.strip()
    #                 st.text(OptsG)

                # parse the data
                table4 = soup.find("strong",text="SRS")
                srs=table4.next_sibling.strip()  
    #                 st.text(srs[1:])

                # parse the data
                table5 = soup.find("strong",text="Pace")
                pace=table5.next_sibling.strip()  
    #                 st.text(pace[1:])

                # parse the data
                table6 = soup.find("strong",text="Off Rtg")
                oRtg=table6.next_sibling.strip()  
    #                 st.text(oRtg[1:])

                # parse the data
                table7 = soup.find("strong",text="Def Rtg")
                dRtg=table7.next_sibling.strip()  
    #                 st.text(dRtg[1:])

                # parse the data
                table8 = soup.find("strong",text="Net Rtg")
                nRtg=table8.next_sibling.strip()  


                return record[:comma],ptsG,OptsG,srs[1:],pace[1:],oRtg[1:],dRtg[1:],nRtg[1:]

            @st.cache(allow_output_mutation=True) 
            def get_injuries2():
                '''
                Function to pull NFL stats from Pro Football Reference (https://www.pro-football-reference.com/).
                - team : team name (str)
                - year : year (int)
                '''
                # pull data
                url = f'https://www.basketball-reference.com/friv/injuries.fcgi'
                html = requests.get(url).text
    #                 st.text(url)

                # parse the data
                soup = BeautifulSoup(html,'html.parser')
                table = soup.find('table', id='injuries')
    #                 st.dataframe(table)
                tablerows = table.find_all('tr')[1:]
                data = []
                data_names = []

                for tablerow in tablerows:
                    data.append([tabledata.get_text(strip=True) for tabledata in tablerow.find_all('td')])

                for tablerow in tablerows:
                    data_names.append([tabledata.get_text(strip=True) for tabledata in tablerow.find_all('th')])

                df = pd.DataFrame(data)
    #                 st.dataframe(pd.DataFrame(data_names))

                col_names = ['Team', 'Update', 'Description']
                df.columns = col_names
                df2 = pd.DataFrame(data_names)
                col_names2 = ['Player']
                df2.columns = col_names2

                # to combined 2 dataframes by adding new columns
                combined_list = pd.concat([df2, df], axis=1)
    #                 st.dataframe(combined_list)


                new_data = combined_list.loc[combined_list['Team']==selected_team_full2[0]]
    #                 st.text(short_name)
    #             st.text(injury_name)
    #                 st.dataframe(new_data)
                return new_data

            injuries2 = get_injuries2()
            injury_count2 = len(injuries2.index)



            #---------------------------------End of Select Team to Analyse        



            st.header("Team Summary")
            st.markdown(f'Team record: {get_record2(team2=short_name2, year2=selected_year)[0]}')
            st.markdown(f'Points For: {get_record2(team2=short_name2, year2=selected_year)[1]}')
            st.markdown(f'Points Against: {get_record2(team2=short_name2, year2=selected_year)[2]}')
            st.markdown(f'Simple Rating System: {get_record2(team2=short_name2, year2=selected_year)[3]}')
            st.markdown(f'Possession Estimate (Pace): {get_record2(team2=short_name2, year2=selected_year)[4]}')
            st.markdown(f'Offense Rating: {get_record2(team2=short_name2, year2=selected_year)[5]}')
            st.markdown(f'Defense Rating: {get_record2(team2=short_name2, year2=selected_year)[6]}')
            st.markdown(f'Net Rating: {get_record2(team2=short_name2, year2=selected_year)[7]}')
            st.markdown(f'Team Injury Count for Current Week: {injury_count2}')

    #COUNT GAMES STATS ADD IT
            @st.cache(allow_output_mutation=True) 
            def get_stats2(team2, year2):
                '''
                Function to pull NFL stats from Pro Football Reference (https://www.pro-football-reference.com/).
                - team : team name (str)
                - year : year (int)
                '''
                # pull data
                url = f'https://www.basketball-reference.com/teams/{short_name2}/{selected_year}/gamelog/'
                html = requests.get(url).text

                # parse the data
                soup = BeautifulSoup(html,'html.parser')
                table = soup.find("table", id="tgl_basic")
                tablerows = table.find_all('tr')[2:]
                data = []

                for tablerow in tablerows:
                    data.append([tabledata.get_text(strip=True) for tabledata in tablerow.find_all('td')])

                df = pd.DataFrame(data)

                #Grabbing columns needed
                index = [0,1,2,3,4,5,6,16,17,19,20,21,33,34,36,37,38]
                new_data = df.iloc[:,index].copy()

                #rename columns
                col_names = [ 'Game', 'Date','At', 'Opp','W/L', 'PTS', 'Opp PTS', 'Team ORB', 'Team TRB', 'Team Steals', 'Team Blocks', 'Team TO', 'Opp ORB', 'Opp TRB', 'Opp Steals', 'Opp Blocks', 'Opp TO']
                new_data.columns = col_names
                new_data['Date'] = new_data['Date'].fillna('')
                new_data2=new_data.loc[new_data['Date']!='']

                return new_data2

            new_data_team2 = get_stats2(team2=short_name2, year2=selected_year)

            new_data_team2['PTS'] = new_data_team2['PTS'].astype(int)
            new_data_team2['Opp PTS'] = new_data_team2['Opp PTS'].astype(int)
            new_data_team2['Won/Lost By'] = new_data_team2.apply(lambda x: x['PTS'] - x['Opp PTS'], axis=1)
            new_data_team2['TOT PTS'] = new_data_team2.apply(lambda x: x['PTS'] + x['Opp PTS'], axis=1)

            new_data_team2 = new_data_team2.reindex([ 'Game', 'Date','At', 'Opp','W/L', 'PTS', 'Opp PTS','Won/Lost By','TOT PTS', 'Team ORB', 'Team TRB', 'Team Steals', 'Team Blocks', 'Team TO', 'Opp ORB', 'Opp TRB', 'Opp Steals', 'Opp Blocks', 'Opp TO'], axis=1)

            all_together_team2 = new_data_team2['Opp']
            all_together2_team2=all_together_team2.drop_duplicates()

            loss_count_team2=new_data_team2.loc[new_data_team2['W/L']=='L']
            win_count_team2=new_data_team2.loc[new_data_team2['W/L']=='W']

            result_encoder_loss_team2 = {'W/L': {'L': 1,'W': 0,'' : pd.NA}}
            loss_encoded_team2 = loss_count_team2
            loss_encoded_team2.replace(result_encoder_loss_team2, inplace=True)
            losses_team2 = loss_encoded_team2.groupby('Opp').agg({'W/L': sum,'Won/Lost By':'mean','TOT PTS':'mean'}).reset_index()

            result_encoder_wins_team2 = {'W/L': {'L': 0,'W': 1,'' : pd.NA}}
            wins_encoded_team2 = win_count_team2
            wins_encoded_team2.replace(result_encoder_wins_team2, inplace=True)
            wins_team2=wins_encoded_team2.groupby('Opp').agg({'W/L': sum,'Won/Lost By':'mean','TOT PTS':'mean'}).reset_index()

            result_team2=pd.merge(all_together2_team2,wins_team2,how="left", on=["Opp"])
            result2_team2 = pd.merge(result_team2,losses_team2,how="left", on=["Opp"])
            col_names_results_team2 = ['Opp','Win Count', 'Win Avg Pts','Win TOT Pts', 'Loss Count','Lost Avg Pts','Lost TOT Pts']
            result2_team2.columns = col_names_results_team2

            result2_team2['Win Count'] = result2_team2['Win Count'].fillna(-1)
            result2_team2['Win Count'] = result2_team2['Win Count'].astype(int)
            result2_team2['Win Count'] = result2_team2['Win Count'].astype(str)
            result2_team2['Win Count'] = result2_team2['Win Count'].replace('-1', '')

            result2_team2['Loss Count'] = result2_team2['Loss Count'].fillna(-1)
            result2_team2['Loss Count'] = result2_team2['Loss Count'].astype(int)
            result2_team2['Loss Count'] = result2_team2['Loss Count'].astype(str)
            result2_team2['Loss Count'] = result2_team2['Loss Count'].replace('-1', '')

            result2_team2['Win Avg Pts'] = result2_team2['Win Avg Pts'].fillna(-1000)
            result2_team2['Win Avg Pts'] = result2_team2['Win Avg Pts'].astype(float).round(2)
            result2_team2['Win Avg Pts'] = result2_team2['Win Avg Pts'].astype(str)
            result2_team2['Win Avg Pts'] = result2_team2['Win Avg Pts'].replace('-1000.0', '')

            result2_team2['Lost Avg Pts'] = result2_team2['Lost Avg Pts'].fillna(-1000)
            result2_team2['Lost Avg Pts'] = result2_team2['Lost Avg Pts'].astype(float).round(2)
            result2_team2['Lost Avg Pts'] = result2_team2['Lost Avg Pts'].astype(str)
            result2_team2['Lost Avg Pts'] = result2_team2['Lost Avg Pts'].replace('-1000.0', '')
            
            result2_team2['Win TOT Pts'] = result2_team2['Win TOT Pts'].fillna(-1000)
            result2_team2['Win TOT Pts'] = result2_team2['Win TOT Pts'].astype(float).round(2)
            result2_team2['Win TOT Pts'] = result2_team2['Win TOT Pts'].astype(str)
            result2_team2['Win TOT Pts'] = result2_team2['Win TOT Pts'].replace('-1000.0', '')

            result2_team2['Lost TOT Pts'] = result2_team2['Lost TOT Pts'].fillna(-1000)
            result2_team2['Lost TOT Pts'] = result2_team2['Lost TOT Pts'].astype(float).round(2)
            result2_team2['Lost TOT Pts'] = result2_team2['Lost TOT Pts'].astype(str)
            result2_team2['Lost TOT Pts'] = result2_team2['Lost TOT Pts'].replace('-1000.0', '')
            result2_team2.sort_values(by='Opp', ascending=True)

            st.header('Played Against Summary')
            st.dataframe(result2_team2.sort_values(by='Opp'))

            result_encoder_team2 = {'W/L': {'L': 0,'W': 1,'' : pd.NA}}
            new_data_encoded_team2 = new_data_team2
            new_data_encoded_team2.replace(result_encoder_team2, inplace=True)

            inform_team2 = f"All Past Games this season: Win = 1, Loss=0"
            fig_all_team2 = px.line(new_data_encoded_team2, x="Date",hover_data=['Opp','PTS','Opp PTS'], y=new_data_encoded_team2['W/L'], title=inform_team2)
            fig_all_team2.update_traces(line=dict(color="#013369"))
            fig_all_team2.update_layout({ 'plot_bgcolor': 'rgba(128,128,128, 0.1)', 'paper_bgcolor': 'rgba(128,128,128, 0)', })
            st.plotly_chart(fig_all_team2, use_container_width=True)

            my_expander_alldata_team2 = st.expander(label=f'Click Here to access Previous Plays Details')
            with my_expander_alldata_team2:
                st.dataframe(new_data_team2)

            my_expander_injuries_team2 = st.expander(label=f'Click Here to access Injuries Details')
            with my_expander_injuries_team2:
                st.dataframe(injuries2)


        except:
            st.warning('Please select a team') 

 
            
