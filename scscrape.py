from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
from time import sleep
import bs4 as bs
import datetime
import MySQLdb
from MySQLdb import escape_string
from datetime import timedelta

todaysDate = datetime.datetime.now().date()

db = MySQLdb.connect("127.0.0.1", DB_NAME, USER_NAME, PSSWRD)
# prepare a cursor object using cursor() method
cursor = db.cursor()

# to run in server monitor mode is required
# see newcron.sh use xvfb or any other for the virtual display
driver = webdriver.Firefox()

with open('sclinks.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        url = row['url']
        data_source = row['chart_type']
        chart_name = row['chart_name']
        Market = row['chart_name_2']

        data = driver.get(url)
        print(url)
        # two times full scroll gives all 50 songs
        driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
        sleep(2)
        driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
        sleep(2)
        driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
        sleep(2)

        soup = bs.BeautifulSoup(driver.page_source, 'lxml')
        refinedData = soup.find_all('div', class_='chartTrack')
        for data in refinedData:
            artist = data.find('div', class_='chartTrack__username')
            if(artist is not None):
                artist = artist.text.strip('\n')
            else:
                artist = ''

            songname = data.find('div', class_='chartTrack__title')
            if(songname is not None):
                songname = songname.text.strip('\n')
            else:
                songname = ''
            row_in_list = data.find('div', class_='chartTrack__position')
            if(row_in_list is not None):
                row_in_list = int(row_in_list.text.strip('\n'))

            Date = todaysDate
            Streams_tw = data.find('span', class_='chartTrack__scoreWeekPlays')
            if(Streams_tw is not None):
                Streams_tw = int(filter(str.isdigit, str(Streams_tw.find('span').text.strip('\n'))))

            Streams_td = data.find('span', class_='chartTrack__scoreAllPlays')
            if(Streams_td is not None):
                Streams_td = int(filter(str.isdigit, str(Streams_td.find('span').text.strip('\n'))))

            releaseDate = data.find('span', class_='chartTrack__timePosted')
            if(releaseDate is not None):
                releaseDate = releaseDate.find('time')['datetime']
                releaseDate = str(datetime.datetime.strptime(releaseDate, "%Y-%m-%dT%H:%M:%S.%fZ").date())

                # releaseDate = int(filter(str.isdigit, str(releaseDate.text[:6])))
                # releaseDate = (datetime.datetime.now() - datetime.timedelta(days=releaseDate)).date()
                # releaseDate = str(releaseDate)

            print 'artist:', artist
            print 'songname:', songname
            print 'row:', row_in_list
            print 'datasource:', data_source
            print 'Date:', Date
            print 'week:', Streams_tw
            print 'altogether:', Streams_td
            print 'datasource:', data_source
            print 'chart_name', chart_name
            print 'market', Market
            print 'releaseDate', releaseDate

            sql = "INSERT INTO songs_chart1 (Artist, Song, Chart_type, Chart_name, Chart_name_2, Date, Rank, SCDailyStreams, SCAllTimeStreams, releasedate) VALUES (%s, %s, %s, %s,%s,%s,%s,%s,%s,%s)"
            # cursor.execute(sql, (escape_string("".join(artist).encode('utf-8')).strip(), escape_string("".join(songname).encode('utf-8')).strip(), escape_string("".join(data_source).encode('utf-8')).strip(), escape_string("".join(chart_name).encode('utf-8')).strip(), escape_string("".join(Market).encode('utf-8')).strip(), Date, row_in_list, Streams_tw, Streams_td, releaseDate))
            cursor.execute(sql, (artist.encode('utf-8'), songname.encode('utf-8'), data_source.encode('utf-8'), chart_name.encode('utf-8'), Market.encode('utf-8'), Date, row_in_list, Streams_tw, Streams_td, releaseDate))
        db.commit()

db.close()
driver.close()

'''
    driver = webdriver.Firefox()
    driver.get("http://www.python.org")
    assert "Python" in driver.title
    elem = driver.find_element_by_name("q")
    elem.clear()
    elem.send_keys("pycon")
    elem.send_keys(Keys.RETURN)
    assert "No results found." not in driver.page_source
    driver.get("http://www.google.com")
'''
