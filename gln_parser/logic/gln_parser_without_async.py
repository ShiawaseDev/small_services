import re

import requests
from bs4 import BeautifulSoup

params = {
    'base_url' : 'https://geoln.com{}', 
    'search_url' : 'https://geoln.com/ru/spain/pg{}',
    'page_number' : '1', #default value
    'list_of_urls' : [], #default value
    'minimal_year_of_building_finished' : 2021
}

def validate_construction_date(construction_date):
     #(IV квартал 2022)
    costruction_year = str(construction_date).split(' ')[1]
    if  int(costruction_year) == params['minimal_year_of_building_finished'] :
        return True    
    return False

#used only for one expected string
def normalize_data_from_html(data_from_html):
    return re.sub("^\s+|\n|\r|\s+$|  |квартал", '', str(data_from_html))

def get_all_urls(base_url_to_parce):
    response = response_handler(base_url_to_parce)
    # Comprehension
    urls_for_scanning = [i for i in response.find_all('a', attrs={"class" : "12u(xsmall)"})]
    context_urls=[]
    for i in urls_for_scanning:
        context_urls.append(str(i).split('"')[5])
    return context_urls

def response_handler(url):
    return BeautifulSoup(requests.get(url).text,'lxml')
    
def ready_state_info():
    for context_url in params['list_of_urls']:
        #Add exception for HTTP Response Code
        directional_url = str(params['base_url']).format(context_url)
        soup = response_handler(directional_url)
        #Add Exception when date of costruction building not found
        tr_tag_args = soup.find('tr',{'data-field': 'finished_at'})
        try:
            td_tag_args = tr_tag_args.find(text=re.compile('квартал')).text
        except AttributeError:
            #When we have tag <td> whithout text 
            pass
        else:
            if validate_construction_date(normalize_data_from_html(td_tag_args)):
                print(directional_url)
        

def main():
    # First information from user
    while True:
        try:     
            params['page_number'] =  abs(int(input('Enter a number page:')))
        except ValueError:
            print('The entered value is not a number, pls enter a number')
        #Exit from prog without warning on typing ctrl+z
        except EOFError:
            exit()
        else:
            #get number page for parcing from input
            search_url = str(params['search_url']).format(params['page_number'])    
            # return list did not parsed of scanned urls from html
            params['list_of_urls'] = get_all_urls(search_url)
            if len(params['list_of_urls']) > 0:
                ready_state_info()
            else:
                print('Page with this number : {} not found'.format(params['page_number']))

if __name__ == '__main__':
    main()
