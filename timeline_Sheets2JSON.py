# -*- coding: utf-8 -*-

'''
Script for grabbing a csv from a Google Sheet id and outputting JSON [compatible with Timeline JS](https://timeline.knightlab.com/docs/json-format.html)

Todo:
- Support for slide types
- Support for eras
- Support for scale

Usage: Update gsheet_id with Google Sheet ID below and run script
'''

gsheet_id = '1Tb0kabLp4K8lP-s3wWqU5QwRo0RufcT-OmeHH-h7oP4'

import csv, json
import pandas as pd
from sys import argv

'''
Constants
'''

gsheet_url = ["https://docs.google.com/spreadsheet/pub?key=","&output=csv"]
tjs_json = {}

start_date = ['s_year','s_month','s_day','s_time']
end_date = ['e_year','e_month','e_day','e_time']
display_date = ['display_date']
media = ["url","credit","caption","thumbnail"]
text = ["headline","text"]
slide = ["type", "group"]
background = ["background"]

date = ["year", "month", "day", "time","display_date"]
time = ["hour","minute","second","millisecond"]

'''
Return Timeline JS objects
'''
def to_object(data,param):

    out_object = {}

    for i, col in enumerate(param):
        # handle background object
        if param == background:
            if data[i] != data[i]: pass
            elif data[i].find('http') > -1: out_object['url'] = data[i]
            else: out_object['color'] = data[i]
        # handle NaN
        elif not data.get(i) or data[i] != data[i]: out_object[col] = ''
        # handle floats
        elif type(data[i]) == float: out_object[col] = int(data[i])
        # default case
        else: out_object[col] = data[i]

    # return time object
    if out_object.get('time'):
        out_time = out_object['time'].split(':')
        for i,col in enumerate(out_time):
            out_object[time[i]] = int(out_time[i])
        out_object.pop('time',None)

    return out_object

'''
Parse Google Sheet CSV
'''
def parse_csv(gsheet_id, tjs_json):

    data = pd.read_csv(gsheet_url[0] + gsheet_id + gsheet_url[1], header=0, \
        names = start_date + end_date + display_date + text + media + slide + background)
    df = pd.DataFrame(data)

    # handle start date object
    df['start_date'] = df[start_date + display_date].apply(lambda x: to_object(x,date), axis=1)

    # handle end date object
    df['end_date'] = df[end_date].apply(lambda x: to_object(x,date), axis=1)

    # handle text object
    df['text'] = df[text].apply(lambda x: to_object(x,text), axis=1)

    # handle media object
    df['media'] = df[media].apply(lambda x: to_object(x,media), axis=1)
    
    # handle title slide if present
    if df.iloc[0].s_year != df.iloc[0].s_year:
        # drop unused columns
        del_cols = ["url","credit","caption","thumbnail"]
        media = df.iloc[0].drop(url + credit + caption + del_cols)
        # handle NaN
        media = meadia.apply(lambda x: '' if x !=x else x)
        # convert to dictionary
        media= media.to_dict()
        df = df.iloc[1:]

        tjs_json["media"] = media
        
    # handle background object
    df['background'] = df[background].apply(lambda x: to_object(x,background), axis=1)

    # handle title slide if present
    if df.iloc[0].s_year != df.iloc[0].s_year:
        # drop unused columns
        del_cols = ["start_date","end_date","headline"]
        title = df.iloc[0].drop(start_date + end_date + display_date + del_cols)
        # handle NaN
        title = title.apply(lambda x: '' if x !=x else x)
        # convert to dictionary
        title= title.to_dict()
        df = df.iloc[1:]

        tjs_json["title"] = title

    # drop unused columns
    df.drop( start_date + end_date + display_date + media + ['headline'], \
        axis=1,inplace=True)

    # reset NaN values
    df = df.applymap(lambda x: '' if x != x else x)

    # append events array
    tjs_json['events'] = df.to_dict(orient="records")
    write_json(tjs_json)

'''
write json
'''

def write_json(tjs_json):
    with open('out2.json','w') as out:
        json.dump(tjs_json, out,indent=2)

'''
Main
'''
def main(gsheet_id,out_filename=""):
    parse_csv(gsheet_id, tjs_json)

if __name__ == '__main__':

    # if len(argv) > 1: print('Please enter a Google Sheet ID')
    main(gsheet_id)
