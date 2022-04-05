import utils.info as info
from fake_headers import Headers
from selenium import webdriver
import requests
import os
import time
import chromedriver_autoinstaller
import sys
import pickle
import logging.handlers
import html_to_json
from tqdm import tqdm
from fpdf import FPDF

chromedriver_autoinstaller.install()


log_dir = "Miraen_DownIMAGE_model.log"

logger = logging.getLogger('Mirae_DownIMAGE_model')
fomatter = logging.Formatter(
    '[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')
fileHandler = logging.FileHandler(log_dir)
streamHandler = logging.StreamHandler()
fileHandler.setFormatter(fomatter)
streamHandler.setFormatter(fomatter)
logger.addHandler(fileHandler)
logger.addHandler(streamHandler)
logger.setLevel(logging.DEBUG)


class Miraen_DownIMAGE():
    def __init__(self, book_code, page_num):

        print('============ New Logging! ============')
        self.path = 'Data'
        self.check_dir()
        self.headers = Headers(headers=True).generate()
        self.book_code = book_code
        self.page_num = page_num
        self.driver = webdriver.Chrome()
        self.IMG_URL_List = []
        self.url_list = []
        self.makeURL_List()
        self.get_IMAGE_URL_List()
        self.download_PAGE()
        self.makePDF()
        self.driver.close()
        self.driver.quit()
        print('============ Done! ============')

    def check_dir(self):
        logger.info(f'============ Checking Directory ... ============')
        try:
            if not os.path.exists(f'Data'):
                os.mkdir(f'Data')
            if not os.path.exists(f'{self.path}/book'):
                os.makedirs(f'{self.path}/book')
            if not os.path.exists(f'{self.path}/logs'):
                os.makedirs(f'{self.path}/logs')
            if not os.path.exists(f'{self.path}/logs/wget_logs'):
                os.makedirs(f'{self.path}/logs/wget_logs')
            if not os.path.exists(f'{self.path}/binary_file'):
                os.makedirs(f'{self.path}/binary_file')
            if not os.path.exists(f'{self.path}/OutPut'):
                os.makedirs(f'{self.path}/OutPut')
        except Exception as e:
            logger.error(
                f'============ Error Occured at check_dir() {e} ============')
            sys.exit(1)

    def makeURL_List(self):
        logger.info(f'============ URL Listing ... ============')
        try:
            self.url_list.append(
                f'https://ebook.mirae-n.com/{self.book_code}/cover')
            for i in tqdm(range(1, self.page_num)):
                self.url_list.append(
                    f'https://ebook.mirae-n.com/{self.book_code}/{i}')
            # add list of cover image url
        except Exception as e:
            logger.error(
                f'============ Error Occured at makeURL_List() {e} ============')

    def get_IMAGE_URL_List(self):
        logger.info(f'============ Getting Image URL ... ============')
        try:
            for url in tqdm(self.url_list):
                self.driver.get(url)
                time.sleep(10)
                html = self.driver.page_source
                html2json = html_to_json.convert(html)
                image_url = html2json['html'][0]['body'][0]['app-root'][0]['viewer-buk-custom'][0]['div'][0]['viewer-book'][0][
                    'div'][0]['div'][0]['viewer-pdf-pages'][0]['viewer-pdf-page'][0]['div'][0]['div'][0]['img'][1]['_attributes']['src']
                self.IMG_URL_List.append(image_url)
        except Exception as e:
            logger.error(
                f'============ Error Occured at get_IMAGE_URL_List() {e} ============')
            pickle.dump(self.IMG_URL_List, open(
                f'{self.path}/binary_file/At_Exception_IMG_URL_List.pkl', 'wb'))

        except KeyboardInterrupt:
            logger.error(
                f'============ Error Occured at get_IMAGE_URL_List() at KeyboardInterrupt ============')
            pickle.dump(self.IMG_URL_List, open(
                f'{self.path}/binary_file/At_Exception_IMG_URL_List.pkl', 'wb'))

    def download_PAGE(self):
        pickle.dump(self.IMG_URL_List, open(
            f'{self.path}/binary_file/IMG_URL_List.pkl', 'wb'))
        pickle.dump(self.url_list, open(
            f'{self.path}/binary_file/URL_List.pkl', 'wb'))
        logger.info(f'============ Downloading ... ============')
        try:
            for i in tqdm(range(len(self.url_list))):
                self.response = requests.get(
                    self.url_list[i], headers=self.headers)
                os.system(
                    f'wget -o ../Data/logs/wget_logs/wget_{i}.log {self.IMG_URL_List[i]} -O {self.path}/book/{i}_{self.book_code}.jpg')

        except Exception as e:
            logger.error(
                f'============ Error Occured at download_PAGE() {e} ============')

    def makePDF(self):
        logger.info(f'============ Making PDF ... ============')
        try:
            pdf = FPDF()
            for i in range(len(self.IMG_URL_List)):
                pdf.add_page()
                pdf.image(
                    f'{self.path}/book/{i}_{self.book_code}.jpg', 0, 0, 200, 300)

            pdf.output(f'{self.path}/OutPut/{self.book_code}.pdf', 'F')
        except Exception as e:
            logger.error(
                f'============ Error Occured at makePDF() {e} ============')


if __name__ == '__main__':

    for book_name in info.BOOK_NAME_LIST:
        print(f"============ {book_name} ============")
        Miraen_DownIMAGE(info.BOOK_INFO[book_name]['book_code'],
                         info.BOOK_INFO[book_name]['page_num'])
