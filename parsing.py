import requests
from bs4 import BeautifulSoup
from config import db


class Bankier:
    def __init__(self):
        self.url_bankier='https://www.bankier.pl'
        self.status=False
        #self.bankier_dict={}

    def add_new_url_to_dict(self,url,id_telegram):
        index=url.rfind("=")
        name_page=url[index+1:]
        href_last_news, href_last_communicate=self.last_href_response_url(url)
        db.add_company_for_user(id_telegram,name_page,url,href_last_news,href_last_communicate)
        #self.bankier_dict[name_page]={"url":url,'href last news':href_last_news,'href last communicate':href_last_communicate}
        #print(self.bankier_dict)

    def last_href_response_url(self,url):
        soup = self.url_request(url)
        news_all = soup.find_all('div', {'class': 'boxContent boxList'})
        href_last_news=news_all[0].find('a').get('href')
        href_last_communicate = news_all[1].find('a').get('href')
        return href_last_news,href_last_communicate

    def href_response_url(self,url):
        href_news_list=[]
        href_communicate_list = []
        soup = self.url_request(url)
        box_all = soup.find_all('div', {'class': 'boxContent boxList'})
        news_list=box_all[0].find_all('a')
        for news in news_list:
            href_news_list.append(news.get('href'))
        communicate_list = box_all[1].find_all('a')
        for communicate in communicate_list:
            href_communicate_list.append(communicate.get('href'))
        return href_news_list,href_communicate_list

    def url_request(self,url):
        response = requests.get(url)
        if response:
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
        else:
            print(response.status_code, "status request")

    def check_aktualization_for_all_url(self):
        companies=db.all_companies()
        list_actualization=[]
        for company in companies:
            href_news_list, href_communicate_list = self.href_response_url(company.url_page)
            index=0
            href_last_news_db=company.href_last_news
            href_last_communicate_db=company.href_last_communicate
            while index < len(href_news_list) and href_news_list[index] != href_last_news_db:
                soup = self.url_request(company.url_page)
                news = soup.find('a', {'href': href_news_list[index]})
                text_news = news.text
                if index==0:
                    db.update_href_last_for_company(id_company=company.id, href_last_news=href_news_list[0])
                list_actualization.append((text_news, self.url_bankier + href_news_list[index], company.users))
                index += 1
            index=0
            while index < len(href_communicate_list) and href_communicate_list[index] != href_last_communicate_db:
                soup = self.url_request(company.url_page)
                comunicate = soup.find('a', {'href': href_communicate_list[index]})
                text_communicate = comunicate.text
                if index==0:
                    db.update_href_last_for_company(id_company=company.id,href_last_communicate=href_communicate_list[0])
                list_actualization.append(
                    (text_communicate, self.url_bankier + href_communicate_list[index], company.users))
                index+=1
        return list_actualization

    def news_company(self,name_company):
        companies=db.return_company(name_company)
        soup=self.url_request(companies.url_page)
        news= soup.find('a', {'href': companies.href_last_news})
        text_news=news.text
        comunicate= soup.find('a', {'href': companies.href_last_communicate})
        text_communicate=comunicate.text
        return [text_news,self.url_bankier+companies.href_last_news,text_communicate,self.url_bankier+companies.href_last_communicate]

    def all_companies_gpw(self):
        db.all_companies_gpw_actualization()
        url_all_companies='https://www.bankier.pl/gielda/notowania/akcje'
        soup = self.url_request(url_all_companies)
        all_companies=soup.find_all('td', {'class': 'colWalor textNowrap'})
        for company in all_companies:
            company=company.find('a')
            name_company=company.text
            url_page_company=company.get('href')
            db.save_to_all_companies_gpw(name_company=name_company,url_company=url_page_company)

    def all_companies_nc(self):
        url_all_companies='https://www.bankier.pl/gielda/notowania/new-connect'
        soup = self.url_request(url_all_companies)
        all_companies=soup.find_all('td', {'class': 'colWalor textNowrap'})
        for company in all_companies:
            company=company.find('a')
            name_company=company.text
            url_page_company=company.get('href')
            db.save_to_all_companies_nc(name_company=name_company,url_company=url_page_company)

    def status_actualization(self,breaking=None):

        if self.status:
            return self.status
        elif breaking:
            self.status=False
        else:
            self.status = True
            return False

