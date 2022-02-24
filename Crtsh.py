import requests
import json
from datetime import datetime


class Crtsh:
    CRTSH_URL = "https://crt.sh/"

    def __init__(self, domain, output=None):
        self.__domain = domain
        if output:
            self.__output = f'{output}/{domain}_subdomains.json'
            self.__output_log = f'{output}/{domain}_subdomains.log'
        else:
            self.__output = f'{domain}_subdomains.json'
            self.__output_log = f'{domain}_subdomains.log'

    def __scrapper(self):
        print(f'Scrapping: {self.CRTSH_URL}?q=%25.{self.__domain}')
        response = requests.get(f'{self.CRTSH_URL}?q=%25.{self.__domain}&output=json')
        data = response.json()

        email_logged = []
        treated_data = []

        for crt in data:
            for email in crt['name_value'].split('\n'):
                if email not in email_logged:
                    email_logged.append(email)

                    expired = self.__date_before_now(crt['not_after'])
                    treated_data.append({"email": email, "record": crt['entry_timestamp'].split('.')[0],
                                         "not_after": crt['not_after'], "expired": expired})

        return treated_data

    @staticmethod
    def __date_before_now(date):
        if datetime.strptime(date, '%Y-%m-%dT%H:%M:%S') < datetime.now():
            return True
        else:
            return False

    @staticmethod
    def __compare_date(old_date, new_date):
        if datetime.strptime(old_date, '%Y-%m-%dT%H:%M:%S') < datetime.strptime(new_date, '%Y-%m-%dT%H:%M:%S'):
            return True
        else:
            return False

    @staticmethod
    def __save(data, output):
        try:
            with open(output, 'w') as fp:
                json.dump(data, fp)
        except IOError:
            print(f'Impossible to save data')

    def __load(self):
        try:
            with open(self.__output) as json_file:
                data = json.load(json_file)

            return data

        except IOError:
            print(f'File: {self.__output} doesn\'t exist')

    @staticmethod
    def __log_by_category(file, results):
        for result in results:
            file.write(f'Email: {result["email"]}, Record: {result["record"]}, Not_After: {result["not_after"]}, '
                       f'Expired: {result["expired"]}\n')

    def __log(self, new_subdomains, expired_subdomains, updated_subdomains):
        try:
            date = f'\n========================================================\n\n[{datetime.now()}]\n'
            file = open(self.__output_log, 'a', newline='')
            with file:
                file.write(date)
                if new_subdomains:
                    file.write(f'\nNew subdomains :\n')
                    self.__log_by_category(file, new_subdomains)
                if expired_subdomains:
                    file.write(f'\nExpired subdomains :\n')
                    self.__log_by_category(file, expired_subdomains)
                if updated_subdomains:
                    file.write(f'\nUpdated subdomains :\n')
                    self.__log_by_category(file, updated_subdomains)

        except IOError:
            print(f'Impossible to save data')

    def __comparator(self, old_data, new_data):

        new_subdomains = []
        expired_subdomains = []
        updated_subdomains = []

        for new in new_data:
            check = False
            for old in old_data:
                if new['email'].strip() == old['email'].strip():
                    crt_updated = self.__compare_date(old['not_after'], new['not_after'])

                    if crt_updated:
                        updated_subdomains.append(new)

                    if new['expired'] and not old['expired']:
                        expired_subdomains.append(new)

                    check = True

            if not check:
                new_subdomains.append(new)

        return new_subdomains, expired_subdomains, updated_subdomains

    @staticmethod
    def __update_crt(old_data, new_subdomains, expired_subdomains, updated_subdomains):
        for update in expired_subdomains + updated_subdomains:
            for i, old_crt in enumerate(old_data):
                if old_crt['email'] == update['email']:
                    old_data[i]['not_after'] = update['not_after']
                    old_data[i]['expired'] = update['expired']

        return old_data + new_subdomains

    def exec(self):
        new_data = self.__scrapper()
        old_data = self.__load()
        expired_subdomains = []
        updated_subdomains = []

        if old_data:
            new_subdomains, expired_subdomains, updated_subdomains = self.__comparator(old_data, new_data)
        else:
            new_subdomains = new_data
            old_data = []

        print(f'Results: ')
        print(f'- New subdomains: {len(new_subdomains)}')
        print(f'- Expired subdomains: {len(expired_subdomains)}')
        print(f'- Updated subdomains: {len(updated_subdomains)}')

        updated_crt = self.__update_crt(old_data, new_subdomains, expired_subdomains, updated_subdomains)
        self.__save(updated_crt, self.__output)
        self.__log(new_subdomains, expired_subdomains, updated_subdomains)

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
