import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import requests
import os
from tkinter import *
import tkinter.ttk as ttk
import tkinter.messagebox as msgbox
from tkinter.messagebox import showinfo
import tkinter as tk
import custom_crawling as crawl
import datetime as dt
from threading import Thread
from urllib.parse import urlparse, urlunparse

def start_long_running_task(progress_window, crawl_class):
    # 프로그레스바 창 생성
    progress_window.title('크롤링 진행 상황')
    progress_window.geometry('300x80')

    # 프로그레스바 생성
    progressbar = ttk.Progressbar(progress_window, length=250, mode='determinate')
    progressbar.pack(pady=10)

    # 페이지별 업데이트 라벨 생성
    page_label = tk.Label(progress_window, text="페이지를 탐색 중입니다")
    page_label.pack()

    # 작업 스레드 시작
    task_thread = Thread(target=crawl_class.crawl_main, args=(progress_window, progressbar, page_label))
    task_thread.start()

def crawling():
    print("크롤링 시작")
    if checkbutton_var.get() == 0:
        class_cw.init_data3(otext_box1.get(), otext_box2.get(), otext_box3.get(), otext_box4.get(), otext_box5.get()
                            , "")
        print(otext_box1.get())
        print(otext_box2.get())
        print(otext_box3.get())
        print(otext_box4.get())
        print(otext_box5.get())
        print("한글파일 없음")
    else:
        class_cw.init_data3(otext_box1.get(), otext_box2.get(), otext_box3.get(), otext_box4.get(), otext_box5.get()
                            , otext_box6.get())
        print(otext_box1.get())
        print(otext_box2.get())
        print(otext_box3.get())
        print(otext_box4.get())
        print(otext_box5.get())
        print(otext_box6.get())
    progress_window = tk.Toplevel(window)
    start_long_running_task(progress_window, class_cw)


def remove_query(url):
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme
    netloc = parsed_url.netloc
    path = parsed_url.path
    params = parsed_url.params
    fragment = parsed_url.fragment

    # 쿼리 문자열 제거
    query = ""  # 쿼리 문자열을 비움
    new_url = urlunparse((scheme, netloc, path, params, query, fragment))
    return new_url

class crawler():
    def __init__(self):
        self.inst = ""
        self.start = ""
        self.end = ""
        self.hwp = 0

        self.mainurl = ""
        self.pagestr = ""
        self.starturl = ""
        self.endurl = ""
        self.page_lists = 0
        self.date1_element = ""
        self.date2_element = ""
        self.date_ex = ""

        self.crawl_date_element = ""
        self.crawl_date_ex = ""
        self.crawl_depart_element = ""
        self.crawl_title_element = ""
        self.crawl_content_element = ""
        self.crawl_hwp_element = ""

        self.start = ""
        self.end = ""
        self.inst = ""

        self.total_page = 0
        self.current_page = 0
        self.pass_page = 0
        self.crawl = "yet"
        self.repeat = True

        self.error = []
        self.errorurl = []
        self.errorno = -1
        self.fileurl = ""
        self.filename = ""
        self.driver = ""

    def init_data1(self, inst, start, end, hwp):
        self.start = start
        self.end = end
        self.inst = inst
        self.hwp = hwp

    def init_data2(self, mainurl, pagestr, starturl, endurl, page_lists, date1_element, date2_element, date_ex):
        self.mainurl = remove_query(mainurl)
        self.pagestr = pagestr
        self.starturl = starturl
        self.endurl = endurl
        self.page_lists = page_lists
        self.date1_element = date1_element
        self.date2_element = date2_element
        self.date_ex = date_ex

    def init_data3(self, crawl_date_element, crawl_date_ex, crawl_depart_element, crawl_title_element,
                   crawl_content_element, crawl_hwp_element):
        self.crawl_date_element = crawl_date_element
        self.crawl_date_ex = crawl_date_ex
        self.crawl_depart_element = crawl_depart_element
        self.crawl_title_element = crawl_title_element
        self.crawl_content_element = crawl_content_element
        self.crawl_hwp_element = crawl_hwp_element

    def set_driver(self):
        self.driver = webdriver.Chrome(service=Service('./설정/chromedriver.exe'), options=driver_option())

    def set_page(self, total_page):
        self.total_page = total_page

    def update_page(self, page):
        self.current_page = page

    def crawl_main(self, progress_window, progressbar, page_label):
        self.set_driver()
        print("crawl_main")
        backup_manage(self)
        postlist = crawl.get_list(self)
        rcount, scrap_list = crawl.scrap_content(progressbar, page_label, postlist, self)
        csv_name = crawl.main(self)
        self.driver.quit()
        progress_window.destroy()

        DATA_DIR = '../크롤링 데이터(Crawling Data)/'
        CSV_POST = os.path.join(DATA_DIR, csv_name)
        self.fileurl = CSV_POST
        cols = ['날짜', '부서', '제목', '내용']
        wcount = len(scrap_list)

        print("\n총 게시물 수: ", rcount)
        print("쓴 게시물 수: ", wcount)
        print("-------------------------------------------------\n")
        print(CSV_POST)
        csv_df = pd.DataFrame(scrap_list, columns=cols)
        csv_df.to_csv(CSV_POST, index=False, encoding='utf-8-sig')

        showinfo('알림창', '크롤링이 완료되었습니다!')
        print("완료")

        if len(self.error) == 0:
            pass
        else:
            error_manage(self)
        self.crawl = "done"


def driver_option():
    options = Options()
    # options.binary_location = './설정/chromedriver.exe'
    options.add_argument('window-size=1920,1080')
    options.add_argument('--headless')
    options.add_argument("disable-gpu")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    return options


def backup_manage(self):
    path = "../크롤링 데이터(Crawling Data)/backup/"
    filename = self.inst + " " + self.start + " " + self.end + ".txt"
    now = dt.datetime.now()
    now = now.strftime('%Y-%m-%d %H:%M:%S')

    message = f"메인url: {self.mainurl}\n" \
              f"page를 나타내는 값: {self.pagestr}\n" \
              f"첫 게시물 url element: {self.starturl}\n" \
              f"마지막 게시물 url element: {self.endurl}\n" \
              f"페이지 당 보도자료 수: {self.page_lists}\n" \
              f"첫 게시물 날짜 element: {self.date1_element}\n" \
              f"마지막 게시물 날짜 elemnet: {self.date2_element}\n" \
              f"날짜 예시: {self.date_ex}\n" \
              f"크롤링 날짜 element: {self.crawl_date_element}\n" \
              f"크롤링 날짜 예시: {self.crawl_date_ex}\n" \
              f"크롤링 부서 element: {self.crawl_depart_element}\n" \
              f"크롤링 제목 element: {self.crawl_title_element}\n" \
              f"크롤링 내용 element: {self.crawl_content_element}\n" \
              f"크롤링 hwp element: {self.crawl_hwp_element}\n"

    f = open(path + filename, "a")
    f.write(now + "\n" + message + "\n==============================================\n")
    f.close()


def error_manage(self):
    path = "../크롤링 데이터(Crawling Data)/error/"
    filename = self.inst + " " + self.start + " " + self.end + ".txt"
    now = dt.datetime.now()
    now = now.strftime('%Y-%m-%d %H:%M:%S')
    f = open(path + filename, "a")
    f.write(now + "\n")
    for err, errurl in zip(self.error, self.errorurl):
        f.write("error: " + err + "\nurl: " + errurl + "\n")
    f.close()

    if self.errorno == 1:
        showinfo('알림창', '기관 보도자료 첫 게시물\n 날짜 요소를 가져오지 못했습니다')
    elif self.errorno == 2:
        showinfo('알림창', '기관 보도자료 마지막 게시물\n 날짜 요소를 가져오지 못했습니다')
    elif self.errorno == 3:
        showinfo('알림창', '기관 보도자료 게시물의\n 날짜 요소를 가져오지 못했습니다')
    elif self.errorno == 4:
        showinfo('알림창', '기관 보도자료 게시물의\n url 요소를 가져오지 못했습니다')
    elif self.errorno == 5:
        showinfo('알림창', '보도자료 내 날짜 가져오기 오류')
    elif self.errorno == 6:
        showinfo('알림창', '보도자료 내 제목 가져오기 오류')
    elif self.errorno == 7:
        showinfo('알림창', '보도자료 내 부서 가져오기 오류')
    elif self.errorno == 8:
        if self.hwp == 0:
            showinfo('알림창', '보도자료 내 내용 가져오기 오류')
        else:
            showinfo('알림창', '보도자료 내 한글파일 가져오기 오류')


def next_init1():
    print("다음1")

    class_cw.init_data1(text_box1.get(), text_box2_1.get(), text_box2_2.get(), checkbutton_var.get())

    print(text_box1.get())
    print(text_box2_1.get())
    print(text_box2_2.get())
    print(checkbutton_var.get())

    label1.grid_remove()
    text_box1.grid_remove()

    label2_1.grid_remove()
    text_box2_1.grid_remove()
    label2_2.grid_remove()
    text_box2_2.grid_remove()

    label3.grid_remove()
    check_button.grid_remove()

    btn1.grid_remove()
    c_label.grid_remove()

    phase2()


def next_init2():
    print("다음2")
    class_cw.init_data2(o_text_box1.get(), o_text_box2.get(), o_text_box3_1.get(), o_text_box3_2.get(),
                        o_text_box4.get(), o_text_box5_1.get(), o_text_box5_2.get(), o_text_box6.get())
    print(o_text_box1.get())
    print(o_text_box2.get())
    print(o_text_box3_1.get())
    print(o_text_box3_2.get())
    print(o_text_box4.get())
    print(o_text_box5_1.get())
    print(o_text_box5_2.get())
    print(o_text_box6.get())

    o_label1.grid_remove()
    o_text_box1.grid_remove()

    o_label2.grid_remove()
    o_text_box2.grid_remove()

    o_label3_1.grid_remove()
    o_text_box3_1.grid_remove()
    o_label3_2.grid_remove()
    o_text_box3_2.grid_remove()

    o_label4.grid_remove()
    o_text_box4.grid_remove()

    o_label5_1.grid_remove()
    o_text_box5_1.grid_remove()
    o_label5_2.grid_remove()
    o_text_box5_2.grid_remove()

    o_label6.grid_remove()
    o_text_box6.grid_remove()

    o_btn1.grid_remove()
    o_btn2.grid_remove()

    phase3()


def before_init1():
    window.geometry("600x400")
    window.minsize(600, 400)

    print("이전1")

    o_label1.grid_remove()
    o_text_box1.grid_remove()

    o_label2.grid_remove()
    o_text_box2.grid_remove()

    o_label3_1.grid_remove()
    o_text_box3_1.grid_remove()
    o_label3_2.grid_remove()
    o_text_box3_2.grid_remove()

    o_label4.grid_remove()
    o_text_box4.grid_remove()

    o_label5_1.grid_remove()
    o_text_box5_1.grid_remove()
    o_label5_2.grid_remove()
    o_text_box5_2.grid_remove()

    o_label6.grid_remove()
    o_text_box6.grid_remove()

    o_btn1.grid_remove()
    o_btn2.grid_remove()

    label1.grid(row=0, column=0, pady=20)  # 라벨 위치 지정 및 패딩 설정
    text_box1.grid(row=0, column=1, pady=20)  # 텍스트 상자 위치 지정 및 패딩 설정

    label2_1.grid(row=1, column=0, pady=5)  # 라벨 위치 지정 및 패딩 설정
    text_box2_1.grid(row=1, column=1, pady=5)  # 텍스트 상자 위치 지정 및 패딩 설정

    label2_2.grid(row=2, column=0, pady=5)  # 라벨 위치 지정 및 패딩 설정
    text_box2_2.grid(row=2, column=1, pady=5)  # 텍스트 상자 위치 지정 및 패딩 설정

    label3.grid(row=3, column=0, pady=20)  # 라벨 위치 지정 및 패딩 설정
    check_button.grid(row=3, column=1, pady=20)  # 체크박스 위치 지정 및 패딩 설정

    btn1.grid(row=4, column=1, padx=5, pady=20)

    c_label.grid(row=5, columnspan=2, pady=20)


def before_init2():
    window.geometry("600x700")
    window.minsize(600, 700)

    print("이전2")

    olabel1.grid_remove()
    otext_box1.grid_remove()

    olabel2.grid_remove()
    otext_box2.grid_remove()

    olabel3.grid_remove()
    otext_box3.grid_remove()

    olabel4.grid_remove()
    otext_box4.grid_remove()

    olabel5.grid_remove()
    otext_box5.grid_remove()

    olabel6.grid_remove()
    otext_box6.grid_remove()

    obtn1.grid_remove()
    obtn2.grid_remove()

    o_label1.grid(row=0, column=0, pady=20)  # 라벨 위치 지정 및 패딩 설정
    o_text_box1.grid(row=0, column=1, pady=20)  # 텍스트 상자 위치 지정 및 패딩 설정

    o_label2.grid(row=1, column=0, pady=20)  # 라벨 위치 지정 및 패딩 설정
    o_text_box2.grid(row=1, column=1, pady=20)  # 텍스트 상자 위치 지정 및 패딩 설정

    o_label3_1.grid(row=2, column=0, pady=20)  # 라벨 위치 지정 및 패딩 설정
    o_text_box3_1.grid(row=2, column=1, pady=20)  # 텍스트 상자 위치 지정 및 패딩 설정
    o_label3_2.grid(row=3, column=0, pady=20)  # 라벨 위치 지정 및 패딩 설정
    o_text_box3_2.grid(row=3, column=1, pady=20)  # 텍스트 상자 위치 지정 및 패딩 설정

    o_label4.grid(row=4, column=0, pady=20)  # 라벨 위치 지정 및 패딩 설정
    o_text_box4.grid(row=4, column=1, pady=20)  # 텍스트 상자 위치 지정 및 패딩 설정

    o_label5_1.grid(row=5, column=0, pady=20)  # 라벨 위치 지정 및 패딩 설정
    o_text_box5_1.grid(row=5, column=1, pady=20)  # 텍스트 상자 위치 지정 및 패딩 설정

    o_label5_2.grid(row=6, column=0, pady=20)  # 라벨 위치 지정 및 패딩 설정
    o_text_box5_2.grid(row=6, column=1, pady=20)  # 텍스트 상자 위치 지정 및 패딩 설정

    o_label6.grid(row=7, column=0, pady=20)  # 라벨 위치 지정 및 패딩 설정
    o_text_box6.grid(row=7, column=1, pady=20)  # 텍스트 상자 위치 지정 및 패딩 설정

    o_btn1.grid(row=8, column=0, padx=5, pady=20)
    o_btn2.grid(row=8, column=1, padx=5, pady=20)


def phase2():
    global o_label1, o_text_box1, o_label2, o_text_box2, o_label3_1, o_text_box3_1, o_label3_2, o_text_box3_2, o_label4, o_text_box4, \
        o_label5_1, o_text_box5_1, o_label5_2, o_text_box5_2, o_label6, o_text_box6, o_btn1, o_btn2
    window.geometry("600x700")
    window.minsize(600, 700)

    # 라벨1 생성
    o_label1 = ttk.Label(frame, text="메인 url", font=("Arial", 14))
    o_label1.configure(background="#f8f9fa", foreground='#212529')
    # 텍스트1 상자 생성
    o_text_box1 = ttk.Entry(frame, font=("Arial", 14))
    o_text_box1.configure(background="#dee2e6", foreground="#212529")

    # 라벨2 생성
    o_label2 = ttk.Label(frame, text="page를 나타내는 값", font=("Arial", 14))
    o_label2.configure(background="#f8f9fa", foreground='#212529')
    # 텍스트2 상자 생성
    o_text_box2 = ttk.Entry(frame, font=("Arial", 14))
    o_text_box2.configure(background="#dee2e6", foreground="#212529")

    # 라벨3_1 생성
    o_label3_1 = ttk.Label(frame, text="첫 게시물 url element", font=("Arial", 14))
    o_label3_1.configure(background="#f8f9fa", foreground='#212529')
    # 텍스트3_1 상자 생성
    o_text_box3_1 = ttk.Entry(frame, font=("Arial", 14))
    o_text_box3_1.configure(background="#dee2e6", foreground="#212529")

    # 라벨3_2 생성
    o_label3_2 = ttk.Label(frame, text="마지막 게시물 url element", font=("Arial", 14))
    o_label3_2.configure(background="#f8f9fa", foreground='#212529')
    # 텍스트3_2 상자 생성
    o_text_box3_2 = ttk.Entry(frame, font=("Arial", 14))
    o_text_box3_2.configure(background="#dee2e6", foreground="#212529")

    # 라벨4 생성
    o_label4 = ttk.Label(frame, text="페이지 당 보도자료 수", font=("Arial", 14))
    o_label4.configure(background="#f8f9fa", foreground='#212529')
    # 텍스트4 상자 생성
    o_text_box4 = ttk.Entry(frame, font=("Arial", 14))
    o_text_box4.configure(background="#dee2e6", foreground="#212529")

    # 라벨5 생성
    o_label5_1 = ttk.Label(frame, text="첫 게시물 날짜 element", font=("Arial", 14))
    o_label5_1.configure(background="#f8f9fa", foreground='#212529')
    # 텍스트5 상자 생성
    o_text_box5_1 = ttk.Entry(frame, font=("Arial", 14))
    o_text_box5_1.configure(background="#dee2e6", foreground="#212529")

    # 라벨5 생성
    o_label5_2 = ttk.Label(frame, text="마지막 게시물 날짜 element", font=("Arial", 14))
    o_label5_2.configure(background="#f8f9fa", foreground='#212529')
    # 텍스트5 상자 생성
    o_text_box5_2 = ttk.Entry(frame, font=("Arial", 14))
    o_text_box5_2.configure(background="#dee2e6", foreground="#212529")

    # 라벨6 생성
    o_label6 = ttk.Label(frame, text="날짜 예시", font=("Arial", 14))
    o_label6.configure(background="#f8f9fa", foreground='#212529')
    # 텍스트6 상자 생성
    o_text_box6 = ttk.Entry(frame, font=("Arial", 14))
    o_text_box6.configure(background="#dee2e6", foreground="#212529")

    # 다음 버튼 생성
    o_btn1 = Button(frame, text="이전", command=before_init1, foreground="#212529", font=("Arial", 12))
    o_btn2 = Button(frame, text="다음", command=next_init2, foreground="#212529", font=("Arial", 12))

    o_label1.grid(row=0, column=0, pady=20)  # 라벨 위치 지정 및 패딩 설정
    o_text_box1.grid(row=0, column=1, pady=20)  # 텍스트 상자 위치 지정 및 패딩 설정

    o_label2.grid(row=1, column=0, pady=20)  # 라벨 위치 지정 및 패딩 설정
    o_text_box2.grid(row=1, column=1, pady=20)  # 텍스트 상자 위치 지정 및 패딩 설정

    o_label3_1.grid(row=2, column=0, pady=20)  # 라벨 위치 지정 및 패딩 설정
    o_text_box3_1.grid(row=2, column=1, pady=20)  # 텍스트 상자 위치 지정 및 패딩 설정
    o_label3_2.grid(row=3, column=0, pady=20)  # 라벨 위치 지정 및 패딩 설정
    o_text_box3_2.grid(row=3, column=1, pady=20)  # 텍스트 상자 위치 지정 및 패딩 설정

    o_label4.grid(row=4, column=0, pady=20)  # 라벨 위치 지정 및 패딩 설정
    o_text_box4.grid(row=4, column=1, pady=20)  # 텍스트 상자 위치 지정 및 패딩 설정

    o_label5_1.grid(row=5, column=0, pady=20)  # 라벨 위치 지정 및 패딩 설정
    o_text_box5_1.grid(row=5, column=1, pady=20)  # 텍스트 상자 위치 지정 및 패딩 설정

    o_label5_2.grid(row=6, column=0, pady=20)  # 라벨 위치 지정 및 패딩 설정
    o_text_box5_2.grid(row=6, column=1, pady=20)  # 텍스트 상자 위치 지정 및 패딩 설정

    o_label6.grid(row=7, column=0, pady=20)  # 라벨 위치 지정 및 패딩 설정
    o_text_box6.grid(row=7, column=1, pady=20)  # 텍스트 상자 위치 지정 및 패딩 설정

    o_btn1.grid(row=8, column=0, padx=5, pady=20)
    o_btn2.grid(row=8, column=1, padx=5, pady=20)


def phase3():
    global olabel1, otext_box1, olabel2, otext_box2, olabel3, otext_box3, olabel4, otext_box4, olabel5, otext_box5, \
        olabel6, otext_box6, obtn1, obtn2

    if checkbutton_var.get() == 1:
        window.geometry("600x600")
        window.minsize(600, 600)
    else:
        window.geometry("600x500")
        window.minsize(600, 500)

    # 라벨1 생성
    olabel1 = ttk.Label(frame, text="크롤링 날짜 element", font=("Arial", 14))
    olabel1.configure(background="#f8f9fa", foreground='#212529')
    # 텍스트2 상자 생성
    otext_box1 = ttk.Entry(frame, font=("Arial", 14))
    otext_box1.configure(background="#dee2e6", foreground="#212529")

    # 라벨2 생성
    olabel2 = ttk.Label(frame, text="크롤링 날짜 예시", font=("Arial", 14))
    olabel2.configure(background="#f8f9fa", foreground='#212529')
    # 텍스트2 상자 생성
    otext_box2 = ttk.Entry(frame, font=("Arial", 14))
    otext_box2.configure(background="#dee2e6", foreground="#212529")

    # 라벨3 생성
    olabel3 = ttk.Label(frame, text="크롤링 부서 element", font=("Arial", 14))
    olabel3.configure(background="#f8f9fa", foreground='#212529')
    # 텍스트3 상자 생성
    otext_box3 = ttk.Entry(frame, font=("Arial", 14))
    otext_box3.configure(background="#dee2e6", foreground="#212529")

    # 라벨4 생성
    olabel4 = ttk.Label(frame, text="크롤링 제목 element", font=("Arial", 14))
    olabel4.configure(background="#f8f9fa", foreground='#212529')
    # 텍스트4 상자 생성
    otext_box4 = ttk.Entry(frame, font=("Arial", 14))
    otext_box4.configure(background="#dee2e6", foreground="#212529")

    # 라벨5 생성
    olabel5 = ttk.Label(frame, text="크롤링 내용 element", font=("Arial", 14))
    olabel5.configure(background="#f8f9fa", foreground='#212529')
    # 텍스트4 상자 생성
    otext_box5 = ttk.Entry(frame, font=("Arial", 14))
    otext_box5.configure(background="#dee2e6", foreground="#212529")

    # 라벨6 생성
    olabel6 = ttk.Label(frame, text="한글파일 element", font=("Arial", 14))
    olabel6.configure(background="#f8f9fa", foreground='#212529')
    # 텍스트4 상자 생성
    otext_box6 = ttk.Entry(frame, font=("Arial", 14))
    otext_box6.configure(background="#dee2e6", foreground="#212529")

    # 다음 버튼 생성
    obtn1 = Button(frame, text="이전", command=before_init2, foreground="#212529", font=("Arial", 12))
    obtn2 = Button(frame, text="크롤링 시작", command=crawling, foreground="#212529", font=("Arial", 12))

    olabel1.grid(row=0, column=0, pady=20)  # 라벨 위치 지정 및 패딩 설정
    otext_box1.grid(row=0, column=1, pady=20)  # 텍스트 상자 위치 지정 및 패딩 설정

    olabel2.grid(row=1, column=0, pady=20)  # 라벨 위치 지정 및 패딩 설정
    otext_box2.grid(row=1, column=1, pady=20)  # 텍스트 상자 위치 지정 및 패딩 설정

    olabel3.grid(row=2, column=0, pady=20)  # 라벨 위치 지정 및 패딩 설정
    otext_box3.grid(row=2, column=1, pady=20)  # 텍스트 상자 위치 지정 및 패딩 설정

    olabel4.grid(row=3, column=0, pady=20)  # 라벨 위치 지정 및 패딩 설정
    otext_box4.grid(row=3, column=1, pady=20)  # 텍스트 상자 위치 지정 및 패딩 설정

    olabel5.grid(row=4, column=0, pady=20)  # 라벨 위치 지정 및 패딩 설정
    otext_box5.grid(row=4, column=1, pady=20)  # 텍스트 상자 위치 지정 및 패딩 설정

    if checkbutton_var.get() == 1:
        olabel6.grid(row=5, column=0, pady=20)  # 라벨 위치 지정 및 패딩 설정
        otext_box6.grid(row=5, column=1, pady=20)  # 텍스트 상자 위치 지정 및 패딩 설정

    obtn1.grid(row=6, column=0, padx=5, pady=20)
    obtn2.grid(row=6, column=1, padx=5, pady=20)


# gui환경의 초기화 버튼 기능
def reset():
    print("값 초기화")


# gui환경의 기본 구성
def gui():
    global window, frame, label1, text_box1, label2_1, text_box2_1, label2_2, text_box2_2, label3, \
        check_button, btn1, c_label, checkbutton_var, class_cw
    print("GUI 환경 실행")

    class_cw = crawler()

    window = Tk()
    ico = tk.PhotoImage(file='설정/상명대logo.png')
    window.iconphoto(False, ico)
    window.title("보도자료 크롤링")
    window.geometry("600x400")
    window.minsize(600, 400)  # 최소 크기 설정
    window.configure(background='#f8f9fa')
    style = ttk.Style()
    style.configure("TCheckbutton", background="#f8f9fa", foreground="#212529", font=10)

    style.configure("nextbutton", background="#f8f9fa", foreground="#212529", font=("Arial", 10))

    # 윈도우 크기 비율 설정
    window.aspect(3, 2, 3, 2)

    # 프레임 생성 (그리드 사용을 위해)
    frame = tk.Frame(window, bg='#f8f9fa')
    frame.place(relwidth=1, relheight=1)  # 프레임을 윈도우 전체에 맞춤

    # 라벨1 생성
    label1 = ttk.Label(frame, text="기관명", font=("Arial", 14))
    label1.configure(background="#f8f9fa", foreground='#212529')

    # 텍스트1 상자 생성
    text_box1 = ttk.Entry(frame, font=("Arial", 14))
    text_box1.configure(background="#dee2e6", foreground="#212529")

    # 라벨2 생성
    label2_1 = ttk.Label(frame, text="시작 날짜", font=("Arial", 14))
    label2_1.configure(background="#f8f9fa", foreground='#212529')

    # 텍스트2 상자 생성
    text_box2_1 = ttk.Entry(frame, font=("Arial", 14))
    text_box2_1.configure(background="#dee2e6", foreground="#212529")

    # 라벨2 생성
    label2_2 = ttk.Label(frame, text="끝 날짜", font=("Arial", 14))
    label2_2.configure(background="#f8f9fa", foreground='#212529')

    # 텍스트2 상자 생성
    text_box2_2 = ttk.Entry(frame, font=("Arial", 14))
    text_box2_2.configure(background="#dee2e6", foreground="#212529")

    # 라벨3 생성
    label3 = ttk.Label(frame, text="한글파일", font=("Arial", 14))
    label3.configure(background="#f8f9fa", foreground='#212529')

    #
    checkbutton_var = tk.IntVar()  # 체크박스 상태를 저장할 변수 생성
    check_button = ttk.Checkbutton(frame, text="파일 여부", variable=checkbutton_var, style="TCheckbutton")

    # 다음 버튼 생성
    btn1 = Button(frame, text="다음", command=next_init1, foreground="#212529", font=("Arial", 12))

    # 저작권 라벨 생성
    copyright = u"\u00A9"
    c_label = ttk.Label(frame, text=copyright + ' SMU KLCC  ', font="Arial", background='#f8f9fa',
                        foreground='#212529')

    label1.grid(row=0, column=0, pady=20)  # 라벨 위치 지정 및 패딩 설정
    text_box1.grid(row=0, column=1, pady=20)  # 텍스트 상자 위치 지정 및 패딩 설정

    label2_1.grid(row=1, column=0, pady=5)  # 라벨 위치 지정 및 패딩 설정
    text_box2_1.grid(row=1, column=1, pady=5)  # 텍스트 상자 위치 지정 및 패딩 설정
    label2_2.grid(row=2, column=0, pady=5)  # 라벨 위치 지정 및 패딩 설정
    text_box2_2.grid(row=2, column=1, pady=5)  # 텍스트 상자 위치 지정 및 패딩 설정

    label3.grid(row=3, column=0, pady=20)  # 라벨 위치 지정 및 패딩 설정
    check_button.grid(row=3, column=1, pady=20)  # 체크박스 위치 지정 및 패딩 설정

    btn1.grid(row=4, column=1, padx=5, pady=20)

    c_label.grid(row=5, columnspan=2, pady=20)

    # 프레임에 그리드 설정 (라벨과 텍스트 상자 크기 조정을 위해)
    frame.grid_columnconfigure((0, 1), weight=1)  # 열 가중치 설정

    # 이벤트 루프 실행
    window.mainloop()


if __name__ == '__main__':
    gui()
