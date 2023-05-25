import json
import re
import time
import requests
from pathlib import Path
from threading import Thread
from datetime import datetime
from fake_useragent import UserAgent
from progress_bar import ProgressBar
from stock_info_list_crawler import StockInfoListCrawler


class DailyPriceCrawler:

    def __init__(self, progress_bar=None):

        # 重複使用 TCP 連線
        self.req = requests.Session()
        self.url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"
        self.headers = self.req.headers

        # 偽裝 User-Agent
        ua = UserAgent()
        self.headers["User-Agent"] = ua.random

        # 加入 progress bar 這個類別
        if progress_bar:
            self.progress_bar = progress_bar

    def __get(self, date, stock_no):
        res = self.req.get(self.url,
                           headers=self.headers,
                           params={
                               "response": "csv",  # 這次抓的是 csv 格式
                               "date": date,
                               "stockNo": stock_no
                           })
        if res.status_code != 200:
            return 'error'
        else:
            return res

    def __save_file(self, res_text, path):
        # 去掉 res_text 裡多餘的空白行
        res_text = '\n'.join(filter(None, res_text.splitlines()))

        path = Path(path)
        
        # parents=True，如果父資料夾不存在則會一併創建
        # exist_ok=True，創建資料夾時，該資料夾已存在則不會 throw exception
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding="utf-8") as file:
            file.write(res_text)

        return

    def crawler(self, date, stock_no, save_path=""):
        res = self.__get(date, stock_no)

        if save_path:
            res_text = res.text
            self.__save_file(res_text, save_path)

        # 更新 progress bar
        if self.progress_bar:
            self.progress_bar.update()

        return res


if __name__ == '__main__':
    # 抓取股票清單
    stock_info_list_file = {}
    sfc = StockInfoListCrawler().scraper()
    with open("./stock_info_list.json", "r", encoding="utf-8") as f:
        stock_info_list_file = json.load(f)
    stock_info_list = stock_info_list_file.get("stock", [])

    # 將日期設定為今月的1號
    today_date = "{}01".format(datetime.now().strftime("%Y%m"))

    # 加入 progress bar
    progress_bar = ProgressBar(len(stock_info_list))
    dpc = DailyPriceCrawler(progress_bar=progress_bar)

    req_thread_list = []

    for stock_info in stock_info_list:

        stock_no = stock_info.get("stockNo")

        # 取消股票名稱的無效字符，避免目錄創建錯誤
        stock_name = stock_info.get("stockName")
        invalid_chars_regex = r'[<>:"/\\|?*]'
        valid_stock_name = re.sub(invalid_chars_regex, '', stock_name)

        stock_industry = stock_info.get("stockIndustry")
        file_name = "{}_{}_daily_price.csv".format(
            today_date[:-2],  # 字串只需要用到年跟月
            stock_no+valid_stock_name)

        save_path = "{}/{}/{}/{}".format("./daily_stock_price/",
                                         stock_industry,
                                         stock_no+valid_stock_name,
                                         file_name)

        if stock_no and stock_name and stock_industry:
            # daemon=True，就是 main 結束時，daemon=True 的執行緒也會跟著結束
            req_thread = Thread(target=dpc.crawler,
                                args=(today_date, stock_no, save_path),
                                daemon=True)
            req_thread.start()
            req_thread_list.append(req_thread)
            time.sleep(3)

    for req_thread in req_thread_list:
        req_thread.join()
