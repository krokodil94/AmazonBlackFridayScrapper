from requests_html import HTMLSession
from bs4 import BeautifulSoup
import pandas as pd

s = HTMLSession()
dealslist = []
searchterm = 'nintendo'
url = f'https://www.amazon.de/s?k={searchterm}&i=black-friday'

def getdata(url):
    r = s.get(url)
    r.html.render(sleep=1)
    soup = BeautifulSoup(r.html.html,'html.parser')
    return soup

def getdeals(soup):
    products = soup.find_all('div',{'data-component-type': 's-search-result'})
    for item in products:
        link = item.find('a', {'class':'a-link-normal s-no-outline'})['href']
        short_title = item.find('span', {'class': 'a-size-medium a-color-base a-text-normal'}).text.strip()[:25]
        title = item.find('span', {'class':'a-size-medium a-color-base a-text-normal'}).text.strip()
        try:
            saleprice = float(item.find_all('span', {'class':'a-offscreen'})[0].text.replace('€','').replace(',','.').strip())
            oldprice = float(item.find_all('span', {'class': 'a-offscreen'})[1].text.replace('€', '').replace(',','.').strip())
        except:
            oldprice = 0
        try:
            reviews = float(item.find('span', {'class':'a-size-base'}).text.strip())
        except:
            reviews = 0

        saleitem = {
            'title': title,
            'short_title':short_title,
            'link':link,
            'saleprice':saleprice,
            'oldprice':oldprice,
            'reviews':reviews
            }
        dealslist.append(saleitem)
    return

def getnextpage(soup):
        if not soup.find('span', {'class':'s-pagination-next'}):
            pages = soup.find('a', {'class': 's-pagination-next'})['href']
            url = 'https://www.amazon.de/' + str(pages)
            return url
        else:
            return


while True:
    soup = getdata(url)
    getdeals(soup)
    url = getnextpage(soup)

    if not url:
        break
    else:
        print(url)
        print(len(dealslist))

df = pd.DataFrame(dealslist)
df['percentoff'] = 100 - ((df.saleprice / df.oldprice)* 100)
df = df.sort_values(by=['percentoff'],ascending = False)
df.to_csv(searchterm + '-bfdeals.csv', index=False)
print('fin.')