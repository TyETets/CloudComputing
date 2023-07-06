#Name: Tyler Ykema
#Student #: 1062564
#Date: 3/20/2021
#CIS*4010 Assignment 2

from database import get_country_info, get_all_info, create_table, load_records, delete_table
import add_missing_data
import boto3
import sys

session = boto3.Session()
dynamodb = session.resource('dynamodb')

def print_list(key):
    for i in key:
        return

def generate_reportA(country, table_name):
    info = get_country_info(table_name, country)
    area = int(info['area'][0])
    #print(info)
    print()
    print("\tReport A - Country Level Report")
    print()
    print("\t\t\t     Name of Country")
    print("\t\t\t[official Name: " + info['name'] + "]")
    print("\t\t\tArea: "+ str(area) +" sq km")
    print("\t\t\tOfficial/National Languages: " + str(info['languages']))
    print("\t\t\tCapital City: " + info['capital'][0])
    print()
    print("\tPopulation")
    print("\tTable of Population, Population Density, and their respective\n\tworld ranking for that year, ordered by year:")
    print()
    print("\t| Year | Population | Rank | Population Density | Rank |")
    for i in range (len(info['pop_years'])):
        population = int(info['population'][i])
        if info['population'][i]:
            print('\t| ' + str(info['pop_years'][i]) , end='')
            print(' | ' + str(population) , end='')
            print(' | x', end='')
            print(' | ' + str("{:.2f}".format(population / area)) , end='')
            print(' | x |')
        else:
            continue
    print()
    print("\tEconomics")
    print("\tCurrency: " + info['currency'])
    print("\tTable of GDP per capita (GDPCC) <from earliest year to latest year> and rank\n\twithin the world for that year")
    print("\t| Year | GDPPC | Rank |")
    for i in range (len(info['gdp_years'])):
        if info['gdppc'][i]:
            print('\t| ' + str(info['gdp_years'][i]) , end='')
            print(' | ' + str(info['gdppc'][i]) , end='')
            print(' | x |')
        else:
            continue
    return

def num_countries(info):
    count = 0
    for i in info:
        #print(i['population'][len(i['population']) - 1])
        count += 1
    return count

def year_to_data(info, year):
    year_count = 0
    for i in info['pop_years']:
        #print(str(i) + " year to " + str(year))
        if i == year:
            break
        year_count += 1
    #print(year_count)
    return year_count

def print_gdp_all(info, year_ind):
    try:
        for i in info:
            print('\t| ' + i['name'] , end='')
            print(' | ' + str(i['gdppc'][year_ind]) , end='')
            print(' | ' + str(i['gdppc'][year_ind + 1]) , end='')
            print(' | ' + str(i['gdppc'][year_ind + 2]) , end='')
            print(' | ' + str(i['gdppc'][year_ind + 3]) , end='')
            print(' | ' + str(i['gdppc'][year_ind + 4]) , end='')
            print(' | ' + str(i['gdppc'][year_ind + 5]) , end='')
            print(' | ' + str(i['gdppc'][year_ind + 6]) , end='')
            print(' | ' + str(i['gdppc'][year_ind + 7]) , end='')
            print(' | ' + str(i['gdppc'][year_ind + 8]) , end='')
            print(' | ' + str(i['gdppc'][year_ind + 9]))
    except:
        print()
    return

def generate_reportB(table_name, year):
    info = get_all_info(table_name)
    num_count = num_countries(info)
    #print(info)
    print()
    print("\tReport B - Global Report")
    print(end='\n\n')
    print("\t\t\tGlobal Report")
    print()
    print('\tYear: ' + str(year))
    print('\tNumber of Countries: ' + str(num_count))
    print()
    print('\tTable of Countries Ranked by Population (largest to smallest)')
    print("\t| Country Name | Population | Rank |")
    for i in info:
        print('\t| ' + i['name'] , end='')
        print(' | ' + str(i['population'][len(i) - 1]) , end='') #change for different years
        print(' | x |')
        year = year_to_data(i, year)
    print()
    print('\tTable of Countries Countries Ranked by Area (largest to smallest)')
    print("\t| Country Name | Area (sq km) | Rank |")
    for i in info:
        print('\t| ' + i['name'] , end='')
        try:
            print(' | ' + str(i['area'][0]) , end='') #change for different years
        except:
            print(' | ' + ' x' , end='')
        print(' | x |')
        year = year_to_data(i, year)
    print()
    print('\tTable of Countries Ranked by Density (largest to smallest)')
    print("\t| Country Name | Density (people / sq km) | Rank |")
    for i in info:
        print('\t| ' + i['name'] , end='')
        try:
            print(' | ' + str("{:.2f}".format(int(i['population'][len(i) - 1]) / int(i['area'][0]))) , end='')
        except:
            print(' | ' + ' x' , end='')
        print(' | x |')
    print()
    print('\tGDP Per Capita for all Countries')
    try:
        print("\t1970's Table")
        print("\t| Country Name | 1970 | 1971 | 1972 | 1973 | 1974 | 1975 | 1975 | 1976 | 1977 | 1978 | 1979 |")
        print_gdp_all(info, 0)
        print()
        print("\t1980's Table")
        print("\t| Country Name | 1980 | 1981 | 1982 | 1983 | 1984 | 1985 | 1985 | 1986 | 1987 | 1988 | 1989 |")
        print_gdp_all(info, 10)
        print()
        print("\t1990's Table")
        print("\t| Country Name | 1990 | 1991 | 1992 | 1993 | 1994 | 1995 | 1995 | 1996 | 1997 | 1998 | 1999 |")
        print_gdp_all(info, 20)
        print()
        print("\t2000's Table")
        print("\t| Country Name | 2000 | 2001 | 2002 | 2003 | 2004 | 2005 | 2005 | 2006 | 2007 | 2008 | 2009 |")
        print_gdp_all(info, 30)
        print()
        print("\t2010's Table")
        print("\t| Country Name | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2015 | 2016 | 2017 | 2018 | 2019 |")
        print_gdp_all(info, 40)
    except:
        print("Error creating tables")

    return

table_name = 'tykema_countrydata'

#generate_reportA('AUS', table_name)
#generate_reportB(table_name, 2018)


choice = input("Would you like to enter new data? (Y or n):")
if choice == 'y' or choice == 'Y':
    table_name = input("Enter your table name: ")
    create_table(table_name, dynamodb)
    area_file = input("Enter file name containing area data: ")
    cap_file = input("Enter file name containing capital data: ")
    pop_file = input("Enter file name containing population data: ")
    gdp_file = input("Enter file name containing GDPPC data: ")
    lang_file = input("Enter file name containing langauge data: ")

    try:
        load_records(area_file, table_name, 'area')
        load_records(cap_file, table_name, 'capital')
        load_records(lang_file, table_name, 'languages')
        load_records(pop_file, table_name, 'population')
        load_records(gdp_file, table_name, 'gdppc')
    except:
        print("Files you entered could not be loaded - please ensure all files are correct")

while(True):
    inVar = input("Enter which report you would like to make (<A> or <B>) or <q> to quit: ")
    if inVar == 'A' or inVar == 'a':
        table_name = input("Enter the table you would like to search in: ")
        country_code = input("Enter the ISO3 code for the country: ")
        try:
            generate_reportA(country_code, table_name)
        except:
            print("Error while generating report - please try again")
    elif inVar == 'B' or inVar == 'b':
        table_name = input("Enter the table you would like to search in: ")
        year = input("Enter the year you would like to do the report on: ")
        try:
            generate_reportB(table_name, year)
        except:
            print("Error while generating report - please try again")
    elif inVar == 'delete' or inVar == 'd':
        table_name = input("Enter the table you would like to delete: ")
        delete_table(table_name, dynamodb)
    elif inVar == 'q' or inVar == 'Q':
        break
