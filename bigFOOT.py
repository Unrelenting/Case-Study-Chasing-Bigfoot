import pandas as pd
import json
from bs4 import BeautifulSoup
import requests



def parse_one_report(html):
    soup = BeautifulSoup(html,'html.parser')
    # title = [p.text.split(':')[0] for p in soup.find_all('span',class_='field')]
    ps = [p for p in soup.find_all('p')]
    body =  [p.text.split(':') for p in ps]
    title = [p.text for p in soup.find_all('span',class_='field')]
    content = {}
    for b in body:
        content[b[0]] = b[-1]
    if len(title) < 2:
        t  = 'No title available'
    else:
        t = title[1]
    content['Title'] = t
    return content


def parse_one_title(html):
    soup = BeautifulSoup(html,'html.parser')
    title = [p.text for p in soup.find_all('span',class_='field')]
    if len(title) < 2:
        t  = ' '
    else:
        t = title[1]
    return t


def parse_all_title(htmls):
    titles = []
    for html in htmls:
        titles.append(parse_one_title(html))
    return titles


def parse_all_report(htmls):
    contents = []
    for html in htmls:
        contents.append(parse_one_report(html))
    return contents


def parse_column(des,contents):
    col = []
    for content in contents:
            if des in content.keys():
                col.append(content[des])
            else:
                col.append(None)
    return col


def parse_year(yr):
    res = re.findall('\d+',yr)
    if len(res)>0:
        return res[0]
    else:
        return -2000


def convert_yr_to_int(df):
    df_ = df.copy()
    df_['Year'] = df_['Year'].apply(parse_year).astype(int)
    df_['Year'][df_['Year']<100] = df_['Year'][df_['Year']<100] + 1900
    return df_


def convert_to_df(contents):
    observations = parse_column('OBSERVED',contents)
    year = parse_column('YEAR',contents)
    season = parse_column('SEASON',contents)
    county = parse_column('COUNTY',contents)
    state = parse_column('STATE',contents)
    title = parse_column('Title',contents)

    df = pd.DataFrame({'State':state,'County':county,'Year':year,'Season':season,'Title':title,'Obs':observations})
    return df


def parse_table():
    bigfoot_loc = 'http://www.bfro.net/gdb/'
    res = requests.get(bigfoot_loc)
    soup = BeautifulSoup(res.content, 'html.parser')

    locations = soup.find_all('table', class_='countytbl')

    sitings = []
    for table in xrange(len(locations)):
        list_loc = []
        for string in locations[table].strings:
            s = repr(string)[2:-1]
            list_loc.append(s)
        sitings.append(list_loc[8:])

    loc_dict = {}
    for i in xrange(len(sitings)):
        for j in xrange(0, len(sitings[i])-3, 4):
            loc_dict[sitings[i][j]] = sitings[i][j+1]


if __name__ == '__main__':
    reports = []
    with open('../data/bigfoot_data.json') as f:
        for i in f:
            reports.append(json.loads(i))

    htmls = [rep['html'] for rep in reports]


    contents = parse_all_report(htmls)
    clean_contents = [content for content in contents if 'OBSERVED' in content.keys()]

    df = convert_to_df(clean_contents)
    df = convert_yr_to_int(df)
