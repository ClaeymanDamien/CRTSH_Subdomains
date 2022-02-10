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

    def scrapper(self):
        print(f'Scrapping: {self.CRTSH_URL}?CN=%25.devoteam.com')
        response = requests.get(f'{self.CRTSH_URL}?CN=%25.devoteam.com')
        tree = html.fromstring(response.content)
        sub_domain = tree.xpath(
            f'//td[contains(text(),"{self.__domain}")]/text()'
        )
        return sorted(set(sub_domain))

    @staticmethod
    def save(data, output):
        try:
            file = open(output, 'a', newline='')
            with file:
                writer = csv.writer(file)
                for value in data:
                    writer.writerow([value])
        except IOError:
            print(f'Impossible to save data')

    def load(self):
        try:
            file = open(self.__output, 'r')
            data = []
            for row in csv.reader(file):
                data.append(row[0])
            return data

        except IOError:
            print(f'File: {self.__output} doesn\'t exist')

    def log(self, result):
        date = f'\n[{datetime.now()}]'
        self.save([date], self.__output_log)
        self.save(result, self.__output_log)

    @staticmethod
    def comparator(old_data, new_data):

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
        new_data = self.scrapper()
        old_data = self.load()

        if old_data:
            new_subdomains = self.comparator(old_data, new_data)
        else:
            new_subdomains = new_data

        if new_subdomains:
            self.log(new_subdomains)
            self.save(new_subdomains, self.__output)

            print(f'New subdomains found:')
            for new_subdomain in new_subdomains:
                print(new_subdomain)
        else:
            self.log(['No new subdomains'])
            print('No new subdomains')
