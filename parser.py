import requests
import csv

from bs4 import BeautifulSoup as bs


class FloridaParser():

    def __init__(self, output_filename='out.csv'):
        self.file = open(output_filename, 'w')
        self.writer = csv.writer(self.file)
        headers = ['LLA', 'Main Address', 'Mailing Address']
        self.writer.writerow(headers)

    base_url = 'https://www.myfloridalicense.com/wl11.asp?mode=2&search=City&SID=&brd=&typ='
    license_list_url = 'https://www.myfloridalicense.com/wl11.asp?mode=3&search=City&SID=&brd=&typ='
    # Hotels and Restaurants
    #index xpaths: //*[@id="main"]/tbody/tr[1]/td/table[3]/tbody/tr/td[2]/form/table/tbody/tr/td/table/tbody/tr[4]/td[2]/font/select
    license_category = 200
    
    # index xpaths: //*[@id="main"]/tbody/tr[1]/td/table[3]/tbody/tr/td[2]/form/table/tbody/tr/td/table/tbody/tr[5]/td[2]/font/select
    license_types = [
        # Vacation Rental - Condo
        2006,
        # Vacation Rental - Dwelling
        2007,
        # Hotel
        2001,
        # Motel
        2002
    ]
    # index xpaths: //*[@id="main"]/tbody/tr[1]/td/table[3]/tbody/tr/td[2]/form/table/tbody/tr/td/table/tbody/tr[7]/td[2]/font/select
    counties = [
        # Dade
        23,
        #Breward
        16
    ]
    licenses_per_page = 50

    headers = {
        'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding':
        'gzip, deflate, br',
        'Accept-Language':
        'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control':
        'no-cache',
        'Connection':
        'keep-alive',
        'Content-Length':
        '415',
        'Content-Type':
        'application/x-www-form-urlencoded',
        'Host':
        'www.myfloridalicense.com',
        'Origin':
        'https://www.myfloridalicense.com',
        'Pragma':
        'no-cache',
        'Referer':
        'https://www.myfloridalicense.com/wl11.asp?mode=3&search=City&SID=&brd=&typ=',
        'sec-ch-ua':
        '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile':
        '?0',
        'Sec-Fetch-Dest':
        'document',
        'Sec-Fetch-Mode':
        'navigate',
        'Sec-Fetch-Site':
        'same-origin',
        'Sec-Fetch-User':
        '?1',
        'Upgrade-Insecure-Requests':
        '1',
        'User-Agent':
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36',
    }

    writer = open('result.csv', 'w')

    data = {
        'hSID': '',
        'hSearchType': 'City',
        'hLastName': '',
        'hFirstName': '',
        'hMiddleName': '',
        'hOrgName': '',
        'hSearchOpt': 'Organization',
        'hSearchOpt2': '',
        'hSearchAltName': 'Alt',
        'hSearchPartName': '',
        'hSearchFuzzy': '',
        'hDivision': 'ALL',
        'hBoard': '200',
        'hLicenseType': '2006',
        'hSpecQual': '',
        'hAddrType': '',
        'hCity': '',
        'hCounty': '',
        'hState': 'FL',
        'hLicNbr': '',
        'hAction': '',
        'hCurrPage': '',
        'hTotalPages': '',
        'hTotalRecords': '',
        'hPageAction': '4',
        'hDDChange': '',
        'hBoardType': '',
        'hLicTyp': '',
        'hSearchHistoric': '',
        'hRecsPerPage': '50',
        'Board': '200',
        'LicenseType': '2006',
        'City': '',
        'County': '23',
        'State': 'FL',
        'SpecQual2': '',
        'RecsPerPage': '50',
        'Search1': 'Search',
    }

    counter = 0

    def parse(self):
        for license in self.license_types:
            self.data['hLicenseType'] = license
            self.data['LicenseType'] = license
            self.parse_license_type()

    #parses all licenses of a given type
    def parse_license_type(self):
        licensies = []
        for county in self.counties:
            self.data['County'] = county
            self.data['hCounty'] = county

            # get first page for parse page count
            r = requests.post(self.base_url,
                              headers=self.headers,
                              data=self.data)
            sel = bs(r.text, 'lxml')
            licensies.append(self.parse_license_page(sel))

            pages = int(sel.find('input', {'name': 'hTotalPages'})['value'])
            total_records = int(
                sel.find('input', {'name': 'hTotalRecords'})['value'])

            self.data['hTotalPages'] = pages
            self.data['hTotalRecords'] = total_records
            for page in range(2, pages):
                self.data['hCurrPage'] = page
                r = requests.post(self.license_list_url,
                                  headers=self.headers,
                                  data=self.data)
                sel = bs(r.text, 'lxml')

                with open('page.html', 'w') as file:
                    file.write(r.text)

                parsed_page = self.parse_license_page(sel)
                if parsed_page:
                    licensies.append(parsed_page)

            for page_licensies in licensies:
                self.writer.writerows(page_licensies)

    def parse_license_page(self, sel):
        licensies = []
        self.counter += 1
        rows = sel.find('table', {'bgcolor': '#f1f1f1'}).find_all('tr')
        for row in rows:
            try:
                LLA = row.find('table').find_all('tr')[0].find_all('td')[1].text
                MainAddress = row.find('table').find_all('tr')[1].find_all('td')[1].text
                if row.find('table').find_all('tr')[2]:
                    MailAddress = row.find('table').find_all('tr')[2].find_all('td')[1].text

                if MainAddress == MailAddress:
                    MailAddress = ''

                licensies.append([
                    LLA,
                    MainAddress,
                    MailAddress,
                ])

            except:
                pass
        return licensies


if __name__ == '__main__':
    parser = FloridaParser()
    parser.parse()
