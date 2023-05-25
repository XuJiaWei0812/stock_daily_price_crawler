import json
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

class StockInfoListCrawler:

    def __init__(self):

        # 重複使用 TCP 連線
        self.req = requests.Session()
        self.url = "https://isin.twse.com.tw/isin/class_main.jsp"
        self.headers = self.req.headers

        # 偽裝 User-Agent
        ua = UserAgent()
        self.headers["User-Agent"] = ua.random

    def __get(self):
        res = self.req.get(self.url,
                           params={
                               "market": "1",
                               "issuetype": "1",
                               "Page": "1",
                               "chklike": "Y"
                           })
        res.encoding = "MS950"
        return res

    def __save_file(self, res_text):
        res_html = res_text
        soup = BeautifulSoup(res_html, "lxml")
        tr_list = soup.find_all("table")[1].find_all("tr")

        # 第一個是是欄位名稱，所以 pop 掉
        tr_list.pop(0)

        result = []
        for tr in tr_list:

            td_list = tr.find_all("td")

            # 股票代碼
            stock_no_val = td_list[2].text

            # 股票名稱
            stock_name_val = td_list[3].text

            # 股票產業類別
            stock_industry_val = td_list[6].text

            # 整理成 dict 存起來
            result.append({
                "stockNo": stock_no_val,
                "stockName": stock_name_val,
                "stockIndustry": stock_industry_val
            })


        # 將 dict 輸出成檔案
        stock_list_dict = {'stock': result}
        with open("stock_info_list.json", "w", encoding="utf-8") as f:
            f.write(
                json.dumps(stock_list_dict,
                        indent=3,
                        ensure_ascii=False)
            )
        return

    def scraper(self):
        res = self.__get()
        if res :
            self.__save_file(res.text)

        return res
