# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By
from datetime import datetime
import pandas as pd
import xml.etree.ElementTree as et
from requests import get
import zipfile
import shutil
import re
import os

ORIGIN_DIR = os.getcwd()
TEMP_DIR = '../temp/'
TEMP_TXT_FILE = "temp.txt"
TEMP_HW_FILE = "temp.hwp"

TEMP_DIR = ORIGIN_DIR + TEMP_DIR
TEMP_TXT = TEMP_DIR + TEMP_TXT_FILE
TEMP_HW = TEMP_DIR + TEMP_HW_FILE


def main(self):
    inst = self.inst
    d1 = self.start
    d2 = self.end
    csv_name = inst + " " + d1 + " - " + d2 + " post.csv"
    return csv_name


def download_hwp(self):
    driver = self.driver
    text = ".pdf"
    downList = driver.find_elements(By.XPATH, '/html/body/div/div[1]/div[3]/ul/li')
    for add_file in downList:

        a = add_file.find_element_by_tag_name("a")
        href = a.get_attribute("href")
        if ".hwp" in a.text:
            text = a.text
            result = href

            # print('pFileName', pFileName, 'pRealName', pRealName, 'pPath', pPath)
            downloadUrl = result
            # print('downloadUrl:', downloadUrl)
            # download
            hwpPath = TEMP_HW

            # *** hwpx는 ole파일로 인식하지 않음 ***
            with open(hwpPath, "wb") as file:
                response = get(downloadUrl)
                file.write(response.content)
            break

    return text


# Use hwp5txt
# hwp5txt 사용법: https://hyyoka-ling-nlp.tistory.com/6
# hwp5txt 공식문서: https://pyhwp.readthedocs.io/en/latest/converters.html#hwp5txt-text-conversion
def hwp_to_txt_hwp5txt():  # path = TEMP_DIR
    output = '--output ' + '"' + TEMP_TXT + '"'
    result = '"' + TEMP_HW + '"'
    os.system("hwp5txt " + output + " " + result)


def hwpx_to_txt():
    hwpx_file = TEMP_HW
    os.chdir(os.path.dirname(hwpx_file))
    path = os.path.join(os.getcwd(), "hwpx")  # 압축해제한 디렉토리명

    with zipfile.ZipFile(hwpx_file, 'r') as zf:
        zf.extractall(path=path)

    tree = et.parse(os.path.join(os.getcwd(), "hwpx", "Contents", "section0.xml"))
    root = tree.getroot()  # 생성된 폴더 안의 Contents/section0.xml file을
    # xml.etree.ElementTree로 open
    content = ''
    out_list = ['Clickhere:set:',
                '이곳을 마우스로 누르고 본문 내용을 입력하세요.',
                '본문 내용 입력',
                '{"name":"#본문"}'
                ]
    m = ['이곳을 마우스로 누르고 본문 내용을 입력하세요.']

    for child in root[3:]:
        p_list = []
        # print('Out:', child.tag, child.text)#, child.items())
        for i, ch in enumerate(child.iter()):  # .itertext():
            chx = ch.text
            if chx is not None:
                # print(ch.tag, ch.items())
                if ('<표> ' in chx) or ('[표] ' in chx) or ('.jpg' in chx) or ('.png' in chx) or ('.bmp' in chx) or (
                        '원본 그림의 이름: ' in chx):  # p(문단) 단위로 text 제거
                    # print('*********표/그림/etc 구간********')
                    break
                # t(줄) 단위로 text 제거
                if not ((out_list[0] in chx) or (out_list[1] in chx) or (out_list[2] in chx) or (
                        out_list[3] in chx) or (chx == '9')):
                    # print('In:', chx)
                    p_list.append(chx)
        p_join = ''.join(p_list)
        # print(p_join)
        content = content + '\n' + p_join

    shutil.rmtree(path)  # 압축해제폴더 삭제
    return content


def get_text_file():
    with open(TEMP_TXT, mode='r', encoding='utf-8-sig') as f:
        content = f.read()
        f.close()

    return content


def get_content(self):
    name = download_hwp(self)
    if ".hwpx" in name:
        content = hwpx_to_txt()
    elif ".hwp" in name:
        hwp_to_txt_hwp5txt()
        content = get_text_file()
    elif ".pdf" in name:
        content = 'Only pdf'
    else:
        content = self.driver.find_element(By.XPATH, self.crawl_hwp_element).text
    return content


def scrap_content(progressbar, page_label, postlist, self):
    driver = self.driver
    df_list = []
    count = 0
    no_content = 0
    totalpost = len(postlist)

    for posturl in postlist:
        if self.repeat == False:
            break
        count += 1
        self.current_page = count
        print("읽을 번호: ", count)
        print("게시물 url: ", posturl)
        driver.get(url=posturl)
        driver.implicitly_wait(time_to_wait=5)  # 암묵적 대기 단위 초

        date, department, title, content = "", "", "", ""

        try:
            contentdate = driver.find_element(By.XPATH, self.crawl_date_element).text
            contentdate = contentdate.replace("\n", "")
            contentdate = contentdate.replace("\t", "")
            contentdate = contentdate.replace("\r", "")
            date = contentdate.replace(" ", "")
            date = re.sub(r'\D', ".", date)
        except:
            error = f"보도자료 내 날짜 가져오기 오류.\n{self.crawl_date_element}"
            self.errorno = 5
            self.error.append(error)
            self.errorurl.append(posturl)
            print(error)
            continue
        try:
            title = driver.find_element(By.XPATH, self.crawl_title_element).text
            title = title.replace("\n", "")
            title = title.replace("\t", "")
            title = title.replace("\r", "")
        except:
            error = f"보도자료 내 제목 가져오기 오류.\n{self.crawl_title_element}"
            self.errorno = 6
            self.error.append(error)
            self.errorurl.append(posturl)
            print(error)
            continue
        try:
            department = driver.find_element(By.XPATH, self.crawl_depart_element).text
            department = department.replace("\n", "")
            department = department.replace("\t", "")
            department = department.replace("\r", "")
        except:
            error = f"보도자료 내 부서 가져오기 오류.\n{self.crawl_depart_element}"
            self.errorno = 7
            self.error.append(error)
            self.errorurl.append(posturl)
            print(error)
            continue
        try:
            if self.hwp == 0:
                content = driver.find_element(By.XPATH, self.crawl_content_element).text
            else:
                content = get_content(self)
            content = remove_whitespaces(content)
            print(content)
        except:
            error = f"보도자료 내 내용 가져오기 오류.{self.crawl_content_element}"
            self.errorno = 8
            self.error.append(error)
            self.errorurl.append(posturl)
            print(error)
            no_content += 1
            continue

        # print(date, department, title, content)

        row = [date, department, title, content]
        df_list.append(row)
        print("해당 보도자료의 데이터를 저장했습니다\n")
        progressbar['value'] = (count / totalpost) * 100
        progressbar.update()

        # 페이지별 업데이트 라벨 설정
        page_label.config(text=f"총 {totalpost} 중 {count}")
        page_label.update()

    print("\n no content : ", no_content)
    return count, df_list


def search_page(self, page, searchtime):
    driver = self.driver
    check = 0
    while True:
        if self.repeat == False:
            break
        date1 = 0
        date2 = 0
        url = self.mainurl + ("&" if self.mainurl.find("?") != -1 else "?") + self.pagestr + "=" + str(page)
        print(url)
        driver.get(url=url)
        driver.implicitly_wait(time_to_wait=5)  # 암묵적 대기 단위 초
        try:
            date1 = driver.find_element(By.XPATH,
                                        self.date1_element).text
            date1 = re.sub(r'\D', "", date1)
            date1 = int(date1)
        except:
            error = "기관 보도자료 첫 게시물 날짜 element 가져오기 오류"
            self.errorno = 1
            self.error.append(error)
            self.errorurl.append(url)
            print(error, url)
        try:
            date2 = driver.find_element(By.XPATH,
                                        self.date2_element).text
            date2 = re.sub(r'\D', "", date2)
            date2 = int(date2)
        except:
            error = "기관 보도자료 마지막 게시물 날짜 element 가져오기 오류"
            self.errorno = 2
            self.error.append(error)
            self.errorurl.append(url)
            print(error, url)

        if date2 <= searchtime and searchtime <= date1:
            break

        if date1 < searchtime:
            page -= 1
            check = 1
            if page == 0:
                page += 1
                break
            continue
        elif date2 > searchtime:
            if check == 1:
                page += 1
                break
            else:
                page += 5
                continue

    return page


def make_xpath(xpath1, xpath2):
    # [과 ] 사이에 있는 숫자 추출
    pattern = r'\[(\d+)\]'
    match1 = re.finditer(pattern, xpath1)
    match2 = re.finditer(pattern, xpath2)
    path1 = ""
    path2 = ""

    for m1, m2 in zip(match1, match2):
        print("====================================================")
        if m1.group(1) != m2.group(1):
            print(m1.group(1))
            print(m2.group(1))
            path1 = xpath1[:m1.start(1)]
            path2 = xpath1[m1.end(1):]
            break
    return path1, path2


def get_list(self):
    driver = self.driver
    postlist = []
    pass_page = 0
    starttime = int(self.start)
    endtime = int(self.end)

    frontdate, backdate = make_xpath(self.date1_element, self.date2_element)
    fronturl, backurl = make_xpath(self.starturl, self.endurl)

    print("지정 날짜에 해당하는 페이지를 탐색중입니다.")

    while_loop = True
    # first_page 찾기 알고리즘.
    first_page = 1
    page = search_page(self, first_page, endtime)
    while while_loop:
        if not self.repeat:
            break
        print("현재 탐색중인 page ", page)
        url = self.mainurl + ("&" if self.mainurl.find("?") != -1 else "?") + self.pagestr + "=" + str(page)
        driver.get(url=url)
        driver.implicitly_wait(time_to_wait=5)  # 암묵적 대기 단위 초
        page += 1
        for i in range(1, int(self.page_lists) + 1):
            try:
                # 날짜 element
                contentdate = driver.find_element(By.XPATH, frontdate + str(i) + backdate).text
                contentdate = re.sub(r'\D', "", contentdate)
                date = int(contentdate)
            except:
                error = "기관 보도자료 게시물 날짜 element 가져오기 오류"
                self.errorno = 3
                self.error.append(error)
                self.errorurl.append(url)
                print(error)
                pass_page += 1
                continue
            if starttime <= date and date <= endtime:
                try:
                    url2 = driver.find_element(By.XPATH, fronturl + str(i) + backurl)
                    url2 = url2.get_attribute("href")
                    postlist.append(url2)
                except:
                    error = "기관 보도자료 게시물 url element 가져오기 오류"
                    self.errorno = 4
                    self.error.append(error)
                    self.errorurl.append(url)
                    print(error)
                    pass_page += 1
                continue
            elif date < starttime:
                # 날짜가 오버됨.
                while_loop = False
                break
        self.total_page = len(postlist)

    self.pass_page = pass_page
    self.search = "done"
    print("선택한 날짜의 총 게시물 수: ", len(postlist))
    print("선택한 날짜의 넘어간 게시물 수: ", pass_page)
    return postlist


# content 내용의 빈 여백 줄 삭제
def remove_whitespaces(text):
    lines = text.split('\n')
    lines = lines[:-1]
    lines = (l.strip() for l in lines)
    lines = (l for l in lines if len(l) > 0)
    return '\n'.join(lines)
