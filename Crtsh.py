import csv
import requests
from lxml import html
from datetime import datetime


class Crtsh:
    CRTSH_URL = "https://crt.sh/"

    def __init__(self, domain, output=None):
        print(domain)
        self.__domain = domain
        if output:
            self.__output = f'{output}/{domain}_subdomains.csv'
            self.__output_log = f'{output}/{domain}_subdomains.log'
        else:
            self.__output = f'{domain}_subdomains.csv'
            self.__output_log = f'{domain}_subdomains.log'

    def __scrapper(self):
        print(f'Scrapping: {self.CRTSH_URL}?CN=%25.devoteam.com')
        response = requests.get(f'{self.CRTSH_URL}?CN=%25.devoteam.com')
        tree = html.fromstring(response.content)
        sub_domain = tree.xpath(
            f'//td[contains(text(),"{self.__domain}")]/text()'
        )
        return sorted(set(sub_domain))

    @staticmethod
    def __save(data, output):
        try:
            file = open(output, 'a', newline='')
            with file:
                writer = csv.writer(file)
                for value in data:
                    writer.writerow([value])
        except IOError:
            print(f'Impossible to save data')

    def __load(self):
        try:
            file = open(self.__output, 'r')
            data = []
            for row in csv.reader(file):
                data.append(row[0])
            return data

        except IOError:
            print(f'File: {self.__output} doesn\'t exist')

    def __log(self, result):
        date = f'\n[{datetime.now()}]'
        self.__save([date], self.__output_log)
        self.__save(result, self.__output_log)

    @staticmethod
    def __comparator(old_data, new_data):

        new_subdomains = []

        for new in new_data:
            check = False
            for old in old_data:
                if new.strip() == old.strip():
                    check = True
            if not check:
                new_subdomains.append(new)

        return new_subdomains

    def exec(self):
        new_data = self.__scrapper()
        old_data = self.__load()

        if old_data:
            new_subdomains = self.__comparator(old_data, new_data)
        else:
            new_subdomains = new_data

        if new_subdomains:
            self.__log(new_subdomains)
            self.__save(new_subdomains, self.__output)

            print(f'New subdomains found:')
            for new_subdomain in new_subdomains:
                print(new_subdomain)
        else:
            self.__log(['No new subdomains'])
            print('No new subdomains')

    @property
    def domain(self):
        return self.__domain

    @domain.setter
    def domain(self, value):
        self.__domain = value

    @property
    def output(self):
        return self.__output

    @output.setter
    def output(self, value):
        self.__output = f'{value}/{self.__domain}_subdomains.csv'
        self.__output_log = f'{value}/{self.__domain}_subdomains.log'
