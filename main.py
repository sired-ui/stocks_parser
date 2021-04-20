from openapi_client import openapi
from bs4 import BeautifulSoup
import requests
import json
import datetime
from time import sleep
import time
# токен телеграм бота
token = ""
URL = 'https://api.telegram.org/bot' + token +'/'
# название канала или чата или их id
TCHANEL = '-1001397342149'
# true_stocks = ['nasdaq-bbby','nasdaq-gthx','nasdaq-zyne','nasdaq-dbx','nasdaq-aapl','nyse-pbi','nyse-evh','nyse-m','nasdaq-atvi','nyse-dal','nasdaq-play','nyse-ccl','nasdaq-form','nyse-ge','nasdaq-rrgb']
webull_ids = []
# часовой пояс, сейчас МСК
offset = datetime.timezone(datetime.timedelta(hours=3))
# токен тинькофф
token = 't.YrMhm83LzzS9piKHlgBFyM4LZ62ysw0GLqRwQ_aIDwaLuBr9IkJTO_lhu7_4R2vbs-FTvIbpC5KWqD3ExHA24w'
client = openapi.api_client(token)
# процент, сейчас стоит 0.5%
percent = 0.5

percent/=100
# время молчания, сейчас стоит 2 минуты
timepause = 2

timepause*=60
# время считывания данных, сейчас стоит 3 сек.
timeget = 3

now = datetime.datetime.now()

# временной промежуток с 12:00
time1 = datetime.datetime(now.year,now.month,now.day,12,0)
# временной промежуток с 17:30
time2 = datetime.datetime(now.year,now.month,now.day,17,30)
# временной промежуток до 00:00
time3 = datetime.datetime(now.year,now.month,now.day,23,59)
# временной промежуток с 00:00
time4 = datetime.datetime(now.year,now.month,now.day,0,1)
# временной промежуток до 04:00
time5 = datetime.datetime(now.year,now.month,now.day,4,0)

# список для хранения времени сигнала
timedata = {'BBBY NASDAQ BBBY SPB': 0, 'GTHX NASDAQ GTHX SPB': 0, 'ZYNE NASDAQ ZYNE SPB': 0, 'DBX NASDAQ DBX SPB': 0, 'AAPL NASDAQ AAPL SPB': 0, 'PBI NYSE PBI SPB': 0, 'EVH NYSE EVH SPB': 0, 'M NYSE M SPB': 0, 'ATVI NASDAQ ATVI SPB': 0, 'DAL NYSE DAL SPB': 0, 'PLAY NASDAQ PLAY SPB': 0, 'CCL NYSE CCL SPB': 0, 'FORM NASDAQ FORM SPB': 0, 'GE NYSE GE SPB': 0, 'RRGB NASDAQ RRGB SPB': 0}

# функция отправки в телеграм
def send_message(chat_id,m_text='wait please...'):
	url = URL + 'sendmessage?chat_id={}&text={}'.format(chat_id,m_text)
	r = requests.get(url)


# функция получения id компаний из базы base.json
def get_base(p):
	with open('base.json','r') as  file:
		if p == 0:
			data = json.load(file)['ids']
		elif p == 1:
			data = json.load(file)['tids']
	return data

# функция для получения id компании с webull
def get_webull_ids(t):
	r = requests.get('https://www.webull.com/quote/'+t)
	soup = BeautifulSoup(r.text,'lxml')
	print(list(json.loads(soup.find('script').text.replace('window.__initState__ = ',''))['tickerMap'].keys())[0])

# функция для получения id компании с tinkoff
def get_tinkoff_ids(t):
	instr = client.market.market_search_by_ticker_get(t)
	print(instr.payload.instruments[0].figi)


def get_signals():
	data = get_base(0)
	data1 = get_base(1)
	for d  in range(len(data)):
		price = ''
		r = requests.get('https://quoteapi.webullfintech.com/api/quote/tickerRealTimes/v5/'+data[d]+'?includeSecu=1&includeQuote=1&more=1')
		name = r.json()['symbol']+' '+r.json()['disExchangeCode']
		now = datetime.datetime.now()
		try:
			if now>time1 and now<time2:
				price = r.json()['pPrice']
			elif now>=time2 and now<time3:
				price = r.json()['close']
			elif now>=time4 and now<time5:
				price = r.json()['pPrice']
		except:
			price=''
		if price!='':
			namet = client.market.market_search_by_figi_get(data1[d]).payload.ticker+' SPB'
			askt = client.market.market_orderbook_get(data1[d],1).payload.asks[0].price
			bidt = client.market.market_orderbook_get(data1[d],1).payload.bids[0].price
			if float(price)/askt-1>percent:
				if int(time.time()) - timedata[name+' '+namet]>timepause:
					message = name+' '+str(price)+'\n'+namet+' '+str(askt)+'/'+str(bidt) +'\nпо ASK\nРазница:'+str(round((float(price)/askt-1)*100,2))+'%'
					send_message(TCHANEL,message)
					timedata.update({name+' '+namet:int(time.time())})
				else:
					pass
			elif float(price)/bidt-1>percent:
				if int(time.time()) - timedata[name+' '+namet]>timepause:
					message = name+' '+str(price)+'\n'+namet+' '+str(askt)+'/'+str(bidt)+'\nпо BID\nРазница:'+str(round((float(price)/bidt-1)*100,2))+'%'
					send_message(TCHANEL,message)
					timedata.update({name+' '+namet:int(time.time())})
				else:
					pass
		sleep(0.2)


if __name__ == '__main__':
	while True:
		try:
			get_signals()
			sleep(timeget)
		except:
			sleep(1)