import schedule
import time
import gspread
import json
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import requests
import proj_secrets


def check():
    gc = gspread.service_account(filename='credentials.json')
    workbook = gc.open_by_url(proj_secrets.secrets['workbook_link'])
    # Update the time_of_last_scan_for_changes
    log = workbook.worksheet('Update Log')
    log.update_cell(1, 2, str(datetime.now()))
    print(str(datetime.now()))
    # if (isQuotaAvailable()):
    #     print("Generate New Link")
    urls = workbook.worksheet('URLs')
    row = 2
    while (urls.cell(row, 1).value != None):
        if (urls.cell(row, 3).value != "GENERATED"):
            print("Generating new link for " + urls.cell(row, 1).value)
            headers = {
                'Authorization': 'Bearer '+proj_secrets.secrets['token'],
                'Content-Type': 'application/json',
            }
            data = '{ "long_url": "'+urls.cell(row,1).value+'", "domain": "bit.ly"}'
            response = requests.post('https://api-ssl.bitly.com/v4/shorten', headers=headers, data=data)
            responseObj = response.json()
            print(responseObj["link"])
            urls.update_cell(row,2,responseObj["link"])
            urls.update_cell(row, 3, "GENERATED")
            quotaRemaining = int(log.cell(2, 2).value) - 1
            log.update_cell(2,2,str(quotaRemaining))

        row+=1
        
def setQuota():
    gc = gspread.service_account(filename='credentials.json')
    workbook = gc.open_by_url(proj_secrets.secrets['workbook_link'])
    # Update the quota
    log = workbook.worksheet('Update Log')
    log.update_cell(2, 2, "1000")

def checkForChanges():
    schedule.every(10).seconds.do(check)
    schedule.every(30).days.do(setQuota)
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    
    checkForChanges()

if __name__ == '__main__':
    main()