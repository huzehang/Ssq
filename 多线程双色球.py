# 运用多线程技术获取每期双色球开奖号码储存到本地
# 流程：获取页面数量-根据页面数量创建线程-线程中解析页面数据-等待所有线程结束-保存数据到本地

import requests
import threading
import pandas as pd
from lxml import etree

# 每期期数
ssq_nums = []
# 每期开奖日期
ssq_dates = []
# 每期开奖蓝球号码
ssq_blues = []
# 每期开奖红球号码
ssq_reds = []
# 多线程同步锁
threadLock = threading.Lock()

# 获取页面数量
def getPageNum():
	try:
		html = etree.HTML(requests.get('http://kaijiang.zhcw.com/zhcw/html/ssq/list_1.html').text)
		return html.xpath("//p[@class='pg']/strong")[0].text
	except requests.exceptions.RequestException:
		print('错误：获取页面数量失败')
		return None

# 多线程类
class myThread(threading.Thread):
	def __init__(self, num):
		threading.Thread.__init__(self)
		self.num = num
	
	def run(self):
		parsePage(self.num)

# 解析页面数据
def parsePage(num):
	try:
		html = etree.HTML(requests.get(f'http://kaijiang.zhcw.com/zhcw/html/ssq/list_{num+1}.html').text)
		ssq_num = html.xpath("//tr/td[@align='center'][2]/text()")
		ssq_date = html.xpath("//tr/td[not(@colspan) and @align='center'][1]/text()")
		ssq_blue = html.xpath("//em[not(@class)]/text()")
		reds = html.xpath("//em[@class='rr']/text()")
		ssq_red = []
		for r in range(0, len(reds), 6):
			ssq_red.append(reds[r]+' '+reds[r+1]+' '+reds[r+2]+' '+reds[r+3]+' '+reds[r+4]+' '+reds[r+5])
		# 使用线程同步锁保存数据
		threadLock.acquire()
		for j in range(len(ssq_num)):
			ssq_nums.append(ssq_num[j])
			ssq_dates.append(ssq_date[j])
			ssq_blues.append(ssq_blue[j])
			ssq_reds.append(ssq_red[j])
		threadLock.release()
	except requests.exceptions.RequestException:
		print('错误：解析网页数据失败')
		return None

# 程序入口
if __name__ == '__main__':
	threads = []
	# 根据页面数量创建线程
	for i in range(int(getPageNum())):
		threads.append(myThread(i))
		threads[i].start()
	# 等待所有线程结束
	for t in threads:
		t.join()
	# 储存数据到本地
	df = pd.DataFrame({'期数':ssq_nums, '日期':ssq_dates, '红球':ssq_reds, '蓝球':ssq_blues})
	df = df.sort_values('期数', ignore_index=True, ascending=False)
	df.to_csv('./多线程双色球.csv')
	print('成功：获取双色球数据完成')