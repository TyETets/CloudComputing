#Name: Tyler Ykema
#Student #: 1062564
#Date: 3/20/2021
#CIS*4010 Assignment 2

import sys
import os
import boto3
from boto3.dynamodb.conditions import Key
import csv
import operator

session = boto3.Session()
dynamodb = session.resource('dynamodb')

def delete_table(table_name, dynamodb = None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

    try:
        table = dynamodb.Table(table_name)
        table.delete()
        print("Table status:", table.table_status, table.table_name)
        return table
    except:
        print("Could not delete table")
    return

def create_table(table_name, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'iso3',
                    'KeyType': 'HASH'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'iso3',
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )
        print("Table status:", table.table_status, table.table_name)
        table.wait_until_exists()
        return table
    except:
        print("Could not create table")
    return

def get_column_names(file_name):
    column_names = []
    with open(file_name, 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        for row in reader:
            column_names.append(row)
            break
    return column_names

def if_record_exists(record, table_name):
    db = dynamodb.Table(table_name)
    response = db.scan()
    for i in response['Items']:
        #if i['iso3'] == record['iso3'] or i['name'] == record['name']:
        if i['name'] == record['name']:
            #print("SAME COUNTRY @ " + str(i['name']))
            record = i | record
    return record

def add_record(item, table_name):
    try:
        db = dynamodb.Table(table_name)
        item = if_record_exists(item, table_name)
        print(item)
        db.put_item(
            Item = item
        )
    except:
        print("could not add item")
        return -1
    return 0

def delete_record(item, table_name):
    try:
        db = dynamodb.Table(table_name)
        response = db.delete_item(
            Key={
                'iso3': item['iso3']
            }
        )
    except:
        print("Could not delete record")
    return

def display_all_data(table_name, data_type):
    db = dynamodb.Table(table_name)
    response = db.scan()
    print ('iso3, country name, ' + data_type)
    #print(response['Items'])
    for i in response['Items']:
        print(i['iso3'] + ', ' + i['name'] + ', ' + str(i[data_type]))
        #print(str(i))
    return

def get_area_ranks(file_name, table_name):
    countries = []
    ranks = {}
    column_names = get_column_names(file_name)
    with open(file_name, 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == 'ISO3':
                continue
            ranks = {
            'iso3': row[0],
            'area': int(row[2])
            }
            countries.append(ranks)

    sCountries = sorted(countries, key=lambda d: d['area'], reverse=True)
    #print(sCountries)
    return sCountries

def load_records(file_name, table_name, data_type): #change to be able to accept different input files
    db = dynamodb.Table(table_name)
    column_names = get_column_names(file_name)

    with open(file_name, 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        for row in reader:
            if not row in column_names:
                new_record = {}
                if 'ISO3' in column_names[0]:
                    #print('found iso3')
                    new_record = {
                    'iso3': row[0],
                    'name': row[1],
                    data_type: row[2:]
                    }
                elif 'Country' and 'Currency' in column_names[0]:
                    #print('found country and currency')
                    new_record = {
                    'name': row[0],
                    'currency': row[1],
                    data_type: row[2:],
                    'pop_years': column_names[0][3:]
                    }
                elif 'Country' in column_names[0]:
                    #print("only country found")
                    new_record = {
                    'name': row[0],
                    'gdppc': row[1:],
                    'gdp_years': column_names[0][3:]
                    }
                else:
                    continue
                new_record = if_record_exists(new_record, table_name)
                item1 = db.put_item (
                    Item = new_record
                )
            else:
                continue
    return

def get_country_info(table_name, country):
    table = dynamodb.Table(table_name)
    response = table.query(
        KeyConditionExpression=Key('iso3').eq(country)
    )
    return response['Items'][0]

def get_all_info(table_name):
    db = dynamodb.Table(table_name)
    response = db.scan()
    #print(response['Items'])
    return response['Items']

def query_area(table_name, country):
    table = dynamodb.Table(table_name)
    response = table.query(
        KeyConditionExpression=Key('iso3').eq(country)
    )
    area = response['Items'][0]['area'][0]
    return area

'''
table_name = 'tykema_UN_country_codes'

#Tests of functions
table = create_table(table_name, dynamodb)


#load_records('shortlist_area.csv', table_name, 'area')
#load_records('shortlist_capitals.csv', table_name, 'capital')
#load_records('shortlist_languages.csv', table_name, 'languages')
#load_records('shortlist_curpop.csv', table_name, 'population')
#load_records('shortlist_gdppc.csv', table_name, 'gdppc')

#get_area_ranks('shortlist_area.csv', table_name)


item = {
    'iso3': "USA",
    'name': 'United States of America',
    'capital': "Washington DC"
}
add_record(item, table_name)

item1 = {
    'iso3': "USA",
    'name': 'United States of America',
    'area': 8750000
}

item2 = if_record_exists(item1, table_name)
add_record(item2, table_name)
#print(item2)

#print (query_area(table_name, 'CAN'))
#isplay_all_data(table_name, 'area')



#table = delete_table(table_name, dynamodb)
'''
