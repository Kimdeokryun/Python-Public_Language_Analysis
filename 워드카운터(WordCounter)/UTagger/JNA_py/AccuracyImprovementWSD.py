#-*- coding: utf-8-sig -*-
import sys
import re
from utagger_py import UTagger
import json


def init(num):
    global ut, rt
    rt = UTagger.Load_global('../bin/UTaggerR64.dll', '../Hlxcfg.txt')  # window dll

    if rt != '':
        sys.exit(1)

    ut = UTagger(num)  # 0은 객체 고유번호. 0~99 지정 가능. 같은 번호로 여러번 생성하면 안됨. 한 스레드당 하나씩 지정 필요.
    rt = ut.new_ucma()  # 객체 생성. 객체가 있어야 유태거 이용 가능.
    if rt != '':
        sys.exit(1)

init(0)

def make_wsd(word):
    rt = ut.analyze1(word, 3, 1)  # 분석!
    js = json.loads(rt)
    bsp = js[1]['BSP']
    ck_num = bsp[1]
    return ck_num

def example(content):
    strs = content.split('\n')
    for line in strs:
        o_line = make_json(line)
        print(o_line)

def make_json(s):
    try:
        rt = ut.analyze1(s, 3, 1)  # 분석!
        js = json.loads(rt)
    except:
        s = re.sub(r"[^\uAC00-\uD7A30-9a-zA-Z\s]", "", s)
        try:
            rt = ut.analyze1(s, 3, 1)  # 분석!
            js = json.loads(rt)
        except:
            print(s)
            rt = ut.analyze1(s, 3, 1)  # 분석!
            js = json.loads(rt)

    return js




def utagger_wsd(js, word, syntax_number):
    # 이 기능은 동음이의어 분석 기능으로 워드카운트 리스트에서 동음이의어 여부가 있는 단어에 기반하여 분석합니다.
    #rt = ut.analyze1(s, 3, 1)  # 분석!
    #js = json.loads(rt)
    #print(js)
    res_ma = js[0]['RES_MA']
    #print(res_ma)

    count = 0
    count_list = []
    index_list = []
    ml_list = []
    score_list = []
    syn_list = []
    originml = ""

    for i in range(1, len(js)):
        #print(js[i])

        if str(js[i]['BSP'][0]) == word:
            index_list.append(i)

    for index in index_list:
        ml = ""
        bsp = js[index]['BSP']
        # ck_word = bsp[0]
        ck_num = bsp[1]
        # ck_tag = bsp[2]

        if str(ck_num) != "":
            try:
                cand = js[index]['CAND'][0]
                score = cand['SCORE']
                tag = cand['TAGGED']
                if str(ck_num) == syntax_number:
                    # 동음이의어 분석 결과. 단어를 카운트 함.
                    try:
                        ml = js[index]['ML']
                        # print("ML:", ml)
                    except:
                        # JSON 파일에 ML 부분 없음. 영단어 분석 불가.
                        pass

                    if float(score) >= 1:
                        # 의미부여 점수가 1을 넘기 때문에 UTagger가 잘 분석한 것임.
                        count += 1
                        count_list.append(1)
                        originml = ml

                    else:
                        # 의미 부여 점수가 1을 넘지 않기 때문에 ML(영단어) 분석이 필요함.
                        # print("영단어 분석이 필요합니다.")
                        # count += 1
                        count_list.append(2)
                        ml_list.append(ml)
                        score_list.append(score)
                        syn_list.append(str(ck_num))

                else:
                    # 동음이의어 분석 결과. 단어를 카운트 하지 않음.
                    #count += 1
                    count_list.append(0)

            except:
                # JSON 파일에 CAND 부분 없음. SCORE 책정 불가.
                if str(ck_num) == syntax_number:
                    # 의미 부여 점수를 책정할 수 없기 때문에 ML(영단어) 분석으로 넘어감.
                    try:
                        ml = js[index]['ML']
                        # print("ML:", ml)
                    except:
                        # JSON 파일에 ML 부분 없음. 영단어 분석 불가.
                        print("", end='')
                    # count += 1
                    count_list.append(2)
                    ml_list.append(ml)
                    score_list.append("점수 없음")
                    syn_list.append(str(ck_num))

                else:
                    # count += 1
                    count_list.append(0)

            # print("BSP:", bsp, " WORD:", ck_word, " NUM:", ck_num, " TAG:", ck_tag)
            # print("CAND:", cand, " SCORE:", score, " TAGGED:", tag, " ML:", ml)

        else:
            # 동음이의어 여부가 판단되는 단어의 경우지만 문장 내에서는 의미가 없는 단어로 분류됨.
            # print("의미 번호 없음")
            # count += 1
            count_list.append(0)


    return count, count_list, ml_list, res_ma, originml, score_list, syn_list


'''
print('\n')
number_cnt = 0
number_cnt += utagger_wsd("이런 스케일을 일제는 무지 비능률 따위로 비하 왜곡시켰지요.", "는", "01")
print(number_cnt)
utagger_wsd("그는 '4대강 사업과 달리, 가덕도 건 김해 건 동남권 신공항 건설이 필요하다는 점에 대한 국민적 합의가 이루어졌다'며 '위치 문제만 논란이 있었을 뿐'이라고 항변했다. ")
'''