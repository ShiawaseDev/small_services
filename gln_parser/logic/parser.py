import requests
from bs4 import BeautifulSoup
import re

params = {
    'base_url' : 'https://geoln.com', 
    'search_url' : 'https://geoln.com/ru/spain/pg{}',
    'page_number' : '1', #default value
    'list_of_urls' : ['123'], #default value
    'minimal_year_of_building_finished' : 2022
}

def validate_construction_date(date_of_construction):
    year_of_costruction = str(date_of_construction).split(' ')[1] #(IV квартал 2022)
    if int(year_of_costruction) >= params['minimal_year_of_building_finished']:
        return True    
    return False

#used only for one expected string
def normalize_data_from_html(data_from_html):
    return re.sub("^\s+|\n|\r|\s+$|  |квартал", '', str(data_from_html))

def all_urls(base_url_to_parce):
    response_html_with_all_urls = requests.get(base_url_to_parce)
    context_urls = BeautifulSoup(response_html_with_all_urls.text,'lxml')
    urls_for_scanning = [i for i in context_urls.find_all('a', attrs={"class" : "12u(xsmall)"})]
    new_urls_for_scanning=[]
    for i in urls_for_scanning:
        new_urls_for_scanning.append(str(i).split('"')[5])
    return new_urls_for_scanning
def main():
    # First information from user
    while True:
        try:     
            params['page_number'] =  abs(int(input('Enter a number page:')))
        except ValueError:
            print('The entered value is not a number, pls enter a number')
        except EOFError:
            exit()
        else:
            #get number page for parcing from input
            search_url = str(params['search_url']).format(params['page_number'])    
            # return list not parsed of scanned urls from html
            params['list_of_urls'] = all_urls(search_url)
            if len(params['list_of_urls']) > 0:
                break
            else:
                print('Page with this number : {} not found'.format(params['page_number']))
    
    for directional_url in params['list_of_urls']:
        #Add exception for HTTP Response Code
        response_html = requests.get(params['base_url']+directional_url)
        soup = BeautifulSoup(response_html.text,'lxml')
        #Add Exception when date of costruction building not found
        try:
            #Scan <tr> with att {data-field} with value {finished_at} ,then scan in this <tr> new data which conaints value 'квартал'
            tr_tag_args = soup.find('tr', attrs={'data-field' : 'finished_at'})
            td_tag_args = tr_tag_args.find(lambda tag: tag.name == 'td' and str(tag).__contains__('квартал')).text
        except Exception as excep:
            #Add logger for exception and select type of exception 
            pass
        else:
            if validate_construction_date(normalize_data_from_html(td_tag_args)):
                print(params['base_url']+directional_url)
    main()

if __name__ == '__main__':
    main()