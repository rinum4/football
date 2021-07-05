# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 10:41:05 2021

@author: Ринат
"""

from bs4 import BeautifulSoup
import requests as req
import pandas as pd
from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError

def get_table(table_data, club, league): 
    #table_data = soup.find('table', class_ = 'table table-striped table-bordered table-hover table-condensed table-list')
    
    headers = []
    for i in table_data.find_all('th'):
        title = i.text
        headers.append(title)
    
    headers.append('Club')
    headers.append('League')
    df = pd.DataFrame(columns = headers)
    cnt = 0
    
    for j in table_data.find_all('tr')[1:]:
            row_data = j.find_all('td')
            row = [tr.text for tr in row_data]
            if len(row)>1:
                row.append(club)
                row.append(league)
                df.loc[cnt] = row
                cnt = cnt + 1
     
    return df       

    
resp = req.get("https://salarysport.com/football/")
 
soup = BeautifulSoup(resp.text, 'lxml')

headers = ['Player Name', 'Weekly Wage', 'Yearly Salary', 'Age', 'Position',
           'Nationality', 'Club', 'League']

all_df = pd.DataFrame(columns = headers)

for league in soup.find_all("h2", class_="Typography__H2-sc-1byk2c7-1 SportIndex__Header-sc-1q24g6y-0 hkViCb jAVToZ"): 
    #if league.text!='La Liga':
        #continue
    
    #print("{0}".format(league.text))
    league_list = league.next_element.next_element
    #for club in league_list.find_all("p", class_="Typography__Text-sc-1byk2c7-6 dgbBAr"):
    for club_href in league_list.find_all("a"):
        #print("{0}".format(club.text))
        #print("{0}".format(club_href['href']))
        club_link = club_href['href'].encode('latin5', errors='replace').decode()
        club_url = "https://salarysport.com"+ club_link
        #club_resp = req.get("https://salarysport.com"+club_link)
        try:
            club_resp = req.get(club_url, timeout=6.0)
        except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError):
            print("{0}: не найден".format(club_url))
            continue
        
        club_soup = BeautifulSoup(club_resp.text, 'lxml')
        club_table_data = club_soup.find('table', class_ = 'Table__TableStyle-sc-373fc0-0 nxsDh')
        if len(club_table_data)>1:
            club_name = club_href.text.encode('latin5', errors='replace').decode()
            club_df = get_table(club_table_data, club_name, league.text)
            all_df = pd.concat([all_df, club_df], ignore_index=True, sort=False)
    
    #break

all_df.to_excel("football_wages.xlsx")  