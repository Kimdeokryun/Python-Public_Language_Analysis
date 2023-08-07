# -*- coding: utf-8-sig -*-
import pandas as pd
import numpy as np
from pandas import DataFrame
from collections import Counter
from tkinter import *
import os
from tqdm import tqdm
from AccuracyImprovementWSD import utagger_wsd, make_json
import re
from difflib import SequenceMatcher


def init(num, n1, n2, lnode, var, bar, file_option):
    global name1, name2, listnodes, p_var, progressbar, changewords, file_op
    name1 = n1;
    name2 = n2;
    listnodes = lnode;
    p_var = var;
    progressbar = bar;
    file_op = file_option
    global contents, searchwords, wordPath, filePath, wsdwords
    wordPath = str(name1.get())
    filePath = str(name2.get())

    name = ['날짜', '부서', '제목', '내용']  # 칼럼 이름
    searchwords, changewords, wsdwords = load_searchWord(
        "../../../워드카운팅 리스트(WordCounting List)/" + wordPath)  # wsdwords : 동형이의어 리스트 생성 이후에 활용
    contents = pd.read_csv("../../../크롤링 데이터(Crawling Data)/" + filePath, header=0, encoding="utf-8-sig", names=name)
    contents = data_info(contents)
    contents = contents.sort_values(by=['부서', '날짜'])

    if num == 1:
        main()
    elif num == 2:
        machine_wordcount()


def main():
    print("이 기능은 동음이의어 분석입니다. ※시간이 오래 걸릴 수 있습니다.")

    allDepartments = get_allDepartments(contents)  # 데이터의 모든 부서 조회(중복O)
    departments_unique = get_unique(allDepartments)  # 부서 중복 제거 및 정렬
    contents_Departments(allDepartments, departments_unique)
    # print(contents)
    # 딕셔너리 형태
    wordcount_dict = dict((key, dict()) for key in departments_unique)  # 횟수 기입용
    dateset_dict = dict((key, dict()) for key in departments_unique)  # 날짜 기입용
    titleset_dict = dict((key, dict()) for key in departments_unique)  # 같은 날짜에 두번 이상의 기사를 쓴 경우 제목으로 구분용

    p_var_i = 0
    p_var_len = len(contents)
    p_var_wid = 100 / p_var_len

    for i in tqdm(contents.index):
        # print(i)
        department = contents._get_value(i, '부서')
        if str(department) == "nan":
            department = "부서 없음"
        content = contents._get_value(i, '내용')
        date = contents._get_value(i, '날짜')
        title = contents._get_value(i, '제목')
        date = str(date)

        for word in searchwords:
            cntNum = content.count(word)
            if cntNum > 0:
                # print(department, " : ", word, " : ", str(cntNum))
                syn_number = "nan" if str(wsdwords[word]) == "nan" else str(int(wsdwords[word]))

                if syn_number == "nan":  # 해당 단어가 동음이의어가 아닌 경우
                    pass
                else:  # 해당 단어가 동음이의어인 경우
                    syn_number = "0" + str(syn_number) if len(str(syn_number)) == 1 else str(syn_number)
                    cntwsd, cnt_list, trans_list = utagger_wsd(content, word, syn_number)
                    cntNum = cntwsd

                # 대상어 중복 체크
                cntNum = dedup(wordcount_dict, dateset_dict, titleset_dict, word, department, content, cntNum, date,
                               title)
                if cntNum == 0:
                    continue

                if wordcount_dict[department].get(word):  # 같은 날짜에 두번 이상의 기사를 쓴 경우?
                    wordcount_dict[department][word] += cntNum
                    dateset_dict[department][word] += "\n" + str(cntNum) + "번 : " + date  # \n은 엑셀파일에 줄바꿈으로 저장할 것임.
                    titleset_dict[department][word] += " " + title
                    # print(" Add countNum :", word)
                else:

                    wordcount_dict[department][word] = cntNum
                    dateset_dict[department][word] = str(cntNum) + "번 : " + date
                    titleset_dict[department][word] = title
                    # print(" New word in department ")

        p_var_i += p_var_wid
        p_var.set(p_var_i)
        progressbar.update()

    sort_length(wordcount_dict, dateset_dict)
    print("값 넣은 딕셔너리\n", wordcount_dict)
    print("\n")
    print("date 딕셔너리\n", dateset_dict)
    print("\n")
    departmentData = pd.DataFrame.from_dict(wordcount_dict, orient="index")  # 부서단어별
    departmentData = departmentData.T

    dateData = pd.DataFrame.from_dict(dateset_dict, orient="index")  # 단어 날짜
    dateData = dateData.T

    totalcount_dict = dict((key, dict()) for key in departments_unique)  # 부서별 총합
    count_dep_total(wordcount_dict, totalcount_dict)

    depcountData = pd.DataFrame.from_dict(totalcount_dict)
    depcountData = depcountData.T

    totalCount = count_total(wordcount_dict)  # 총합

    print("\n")

    #   단어별 사용횟수 출력
    totalwordcount = totalCount
    totalwordcount = sorted(totalwordcount.items(), key=lambda x: (-x[1], x[0]))

    # print(totalwordcount)
    print("단어별 사용횟수 출력 (한 줄에 20개씩), 사용된 단어의 개수: ", len(totalwordcount))
    print("\n")
    num_count = 0
    usewords = []
    for key, word in totalwordcount:
        num_count += 1
        print(key + '(' + str(word) + '), ', end="")
        usewords.append(key)
        if num_count % 20 == 0:
            print("")

    # 사용하지 않은 단어 출력을 위한 세팅
    allwords = []
    for i in searchwords:
        i = i.lstrip()
        allwords.append(i)

    usedwords = []
    for i in usewords:
        i = i.lstrip()
        usedwords.append(i)

    nonusewords = list(set(allwords).difference(usedwords))
    nonusewords.sort(reverse=False)
    print("\n\n사용하지 않은 단어 출력 (한 줄에 20개씩), 사용되지 않은 단어의 개수: ", len(nonusewords))
    print("\n")
    num_count = 0

    for word in nonusewords:
        num_count += 1
        print(word + '(' + str(0) + '), ', end="")
        if num_count % 20 == 0:
            print("")

    listnodes.insert(END, "카운트가 끝났습니다 ")
    listnodes.insert(END, "\n", "----------------------------------------------------------------------")

    print("\n\n사용된 단어의 횟수는 빈도순으로, 빈도가 같은 경우 글자 순으로 배치 하였습니다.")
    print("사용되지 않은 단어의 횟수는 글자 순으로 배치 하였습니다.")
    print("워드 카운트가 끝났습니다.")

    # 일반 카운트 분석의 경우에는 더이상 엑셀파일을 만들지 않음.
    """        
    totalcountData = pd.DataFrame(data=[totalCount], index=["빈도수"])
    totalcountData = totalcountData.T

    #for i in range(len(totalwordcount)):
    #    print(totalwordcount.loc[i])

    print("\n\n사용된 단어의 횟수는 빈도순으로, 빈도가 같은 경우 글자 순으로 배치 하였습니다.")
    print("사용되지 않은 단어의 횟수는 글자 순으로 배치 하였습니다.")

    print("워드 카운트가 끝났습니다.")
    print("데이터 저장중.....")

    # ../워드카운트결과값에 저장  (기존의 result 값)
    DATA_DIR = '../../워드카운팅 리포트(WordCounting Report)'

    xlsxname = str(name2.get())
    try:
        xlsxname = xlsxname.rstrip('post.xlsx')
        xlsxname = xlsxname.rstrip('post.csv')
    except:
        pass

    xlsxname = xlsxname + file_op + " 분석 결과값.xlsx"

    listnodes.insert(END, "카운트가 끝났습니다 ")
    listnodes.insert(END, xlsxname + " 입니다")
    listnodes.insert(END, "\n", "----------------------------------------------------------------------")

    xlsxname = os.path.join(DATA_DIR, xlsxname)


    with pd.ExcelWriter(xlsxname) as writer:
        departmentData.to_excel(writer, sheet_name="부서단어별")
        dateData.to_excel(writer, sheet_name="단어날짜")
        depcountData.to_excel(writer, sheet_name="부서별 총합")
        totalcountData.to_excel(writer, sheet_name="총 합")
    """


def machine_wordcount():
    print("이 기능은 동음이의어 기계분석입니다. ※시간이 오래 걸릴 수 있습니다.")
    # content를 한 줄 씩 읽어서 new_wordcount_df 에 추가하기 위한 세팅              (new_wordcount_df: xlsx에 저장용), (dup_check_df: 대상어 포함중복여부 확인용), LAE: 지자체명
    new_wordcount_columns = ["지자체", "부서", "날짜", "제목", "대상어", "대체어", "동음이의어", "영어 번역", "횟수", "내용"]
    new_wordcount_df = pd.DataFrame(columns=new_wordcount_columns)
    dup_check_df = pd.DataFrame(columns=["부서", "날짜", "제목", "대상어", "횟수", "내용"])
    error_check_df = pd.DataFrame(columns=["대상어", "대체어", "대상어 의미 번호", "문장내 의미 번호", "영어 번역", "의미부여 점수", "내용", "동음이의어(내용)"])

    LAE = str(name2.get())
    LAE = LAE[:5]

    p_var_i = 0
    p_var_len = len(contents)
    p_var_wid = 100 / p_var_len

    count = 0
    for i in tqdm(contents.index):
        # print(i)
        count += 1
        department = contents._get_value(i, '부서')
        content = contents._get_value(i, '내용')
        date = contents._get_value(i, '날짜')
        title = contents._get_value(i, '제목')
        date = str(date)

        if str(content) == "nan":
            continue
        strs = content.split('\n')

        for line in strs:
            if ("붙임1" in line) or ("붙임 1" in line):
                break
            dupcheck_line = line
            o_line = ""
            for word in searchwords:

                cntlinenum = line.count(word)
                if cntlinenum > 0:
                    syn_number = "nan" if str(wsdwords[word]) == "nan" else str(int(wsdwords[word]))
                    res_ma = ""
                    search_list = []
                    sc_list = []
                    syntax_list = []
                    ml = ""
                    if syn_number == "nan":
                        pass
                    else:
                        if o_line != "":
                            pass
                        else:
                            o_line = make_json(line)

                        syn_number = "0" + str(syn_number) if len(str(syn_number)) == 1 else str(syn_number)
                        cntwsd, cnt_list, trans_list, res_ma, ml, score_list, syn_list = utagger_wsd(o_line, word, syn_number)
                        cntlinenum = cntwsd
                        ind = -1
                        for search in cnt_list:
                            if search == 2:
                                ind += 1
                                search_list.append(trans_list[ind])
                                sc_list.append(score_list[ind])
                                syntax_list.append(syn_list[ind])

                    slice_line = line_slicing(word, line)
                    slice_line = slice_line.replace(word, ' | ' + word + ' | ')
                    slice_res_ma = line_slicing(word, res_ma)
                    slice_res_ma = slice_res_ma.replace(word, ' | ' + word + ' | ')
                    if cntlinenum == 0:
                        for iii in range(len(search_list)):
                            wsd_error = [word, changewords[word],syn_number, syntax_list[iii], search_list[iii], sc_list[iii], slice_line, slice_res_ma]
                            error_check_df.loc[len(error_check_df)] = wsd_error
                        continue
                    check_dup = 1

                    for record_word in dup_check_df[dup_check_df["내용"] == dupcheck_line]["대상어"]:
                        # word : **   record_word ****
                        i = dup_check_df.index[
                            (dup_check_df["내용"] == dupcheck_line) & (dup_check_df["대상어"] == record_word)].tolist()
                        if record_word.find(word) != -1:
                            if dup_check_df.loc[i[0], "횟수"] == cntlinenum:
                                check_dup = 0
                                continue
                            else:
                                cntlinenum = cntlinenum - dup_check_df.loc[i[0], "횟수"]
                        # word : ****   record_word **
                        elif word.find(record_word) != -1:
                            if dup_check_df.loc[i[0], "횟수"] == cntlinenum:
                                dup_check_df.drop(index=i, inplace=True)
                                new_wordcount_df.drop(index=i, inplace=True)
                                dup_check_df.reset_index(drop=True, inplace=True)
                                new_wordcount_df.reset_index(drop=True, inplace=True)
                            else:
                                dup_check_df.loc[i[0], "횟수"] = dup_check_df.loc[i[0], "횟수"] - cntlinenum

                    if check_dup == 1:
                        # print("replace ", line)
                        new_data = [LAE, department, date, title, word, changewords[word],
                                    syn_number if syn_number != "nan" else "", ml, cntlinenum, slice_line]
                        new_wordcount_df.loc[len(new_wordcount_df)] = new_data
                        dup_check_data = [department, date, title, word, cntlinenum, dupcheck_line]
                        dup_check_df.loc[len(dup_check_df)] = dup_check_data

                        for iii in range(len(search_list)):
                            wsd_error = [word, changewords[word], syn_number, syntax_list[iii], search_list[iii], sc_list[iii], slice_line, slice_res_ma]
                            error_check_df.loc[len(error_check_df)] = wsd_error

        p_var_i += p_var_wid
        p_var.set(p_var_i)
        progressbar.update()

    print("기계 분석 카운트가 끝났습니다.")
    print("데이터 저장중.....")

    DATA_DIR = '../../../워드카운팅 리포트(WordCounting Report)'

    xlsxname2 = str(name2.get())
    try:
        xlsxname2 = xlsxname2.rstrip('post.xlsx')
        xlsxname2 = xlsxname2.rstrip('post.csv')
    except:
        pass
    xlsxname2 = xlsxname2 + file_op + " 기계 분석 결과값.xlsx"

    listnodes.insert(END, "기계분석 카운트가 끝났습니다 ")
    listnodes.insert(END, xlsxname2 + " 입니다")
    listnodes.insert(END, "\n", "----------------------------------------------------------------------")

    xlsxname2 = os.path.join(DATA_DIR, xlsxname2)

    # ../워드카운트결과값에 저장   (언어정보연구원의 result 값과 유사)
    with pd.ExcelWriter(xlsxname2) as writer2:
        new_wordcount_df.to_excel(writer2, sheet_name="기계분석", index=False)
        error_check_df.to_excel(writer2, sheet_name="확인이 필요함", index=False)
        #dup_check_df.to_excel(writer2, sheet_name="2", index=False)


"""
def find_wsd(line, word, cntnum):
    wsd = []
    wsd_list = []
    wordlen = len(word)
    ind = -1
    while True:
        ind = line.find(word, ind + 1)
        if ind == -1:
            break
        wsd_list.append(ind)

    if len(wsd_list) == cntnum:
        for i in wsd_list:
            wsd.append(line[i:i + wordlen])
        return wsd
    else:
        for i in range(cntnum):
            repeat_num = 0
            while True:
                if (repeat_num > 10):
                    find1 = -1
                    break
                else:
                    repeat_num += 1
                find1 = line.find(word[0], 0)
                find2 = line.find(word[-1], find1 + 1)
                if find1 == -1 and find2 == -1:
                    break

                score = SequenceMatcher(None, line[find1:find2 + 1], word).ratio() * 100
                # print("score: ", score)
                if score > 90:
                    break
                else:

                    if find2 - find1 > wordlen:
                        score2 = SequenceMatcher(None, line[find1:find1 + wordlen], word).ratio() * 100
                        # print("score2: ", score2)
                        if score2 > 80:
                            find1 = find1
                            find2 = find1 + wordlen - 1
                            break
                        else:
                            ind = find1 + 1
                            line = line[ind:]

                    elif find2 - find1 < 0:
                        score2 = SequenceMatcher(None, line[find1:find1 + wordlen], word).ratio() * 100
                        # print("score2: ", score2)
                        if score2 > 80:
                            find1 = find1
                            find2 = find1 + wordlen - 1
                            break
                    else:
                        ind = find2 + 1
                        line = line[ind:]
            if find1 != -1:
                wsd.append(line[find1:find2 + 1])
            else:
                pass
        return wsd
"""


def line_slicing(word, line):
    linestart = 1000
    lineend = 0
    for wordindex in re.finditer(word, line):
        if linestart > wordindex.start():
            linestart = wordindex.start()
        else:
            pass
        if lineend < wordindex.end():
            lineend = wordindex.end()
        else:
            pass
    if linestart - 25 < 0:
        linestart = 0
    else:
        linestart -= 25
    if lineend + 25 > len(line) - 1:
        lineend = -1
    else:
        lineend += 25

    line = line[linestart:lineend]

    linestart = 1000
    lineend = 0
    for wordindex in re.finditer(word, line):
        if linestart > wordindex.start():
            linestart = wordindex.start()
        else:
            pass
        if lineend < wordindex.end():
            lineend = wordindex.end()
        else:
            pass

    lindex = line.find(' ')
    rindex = line.rfind(' ')

    if linestart < lindex and rindex < lineend:
        line = line[linestart:lineend]

    elif linestart < lindex:
        line = line[linestart:rindex]
    elif rindex < lineend:
        line = line[lindex + 1:lineend]
    else:
        if len(line) - lineend > 10:
            line = line[lindex + 1:rindex]
        else:
            line = line[lindex + 1:]

    return line


def count_dep_total(wordcount_dict, totalcount_dict):
    for dep in list(wordcount_dict):
        dep_values = sum(list(wordcount_dict[dep].values()))
        totalcount_dict[dep]['총합'] = dep_values
    print("부서별 사용 횟수\n", totalcount_dict)


def count_total(dictList: dict):
    totalCount = Counter()

    for listDict in dictList.values():
        totalCount = totalCount + Counter(listDict)

    return totalCount


def dedup(wordcount_dict, dateset_dict, titleset_dict, word, department, content, cntNum, date, title):
    for dup in list(wordcount_dict[department].keys()):
        if dup.find(word) != -1 or word.find(dup) != -1:
            if date == dateset_dict[department][dup][-10:] and titleset_dict[department][dup].find(title) != -1:
                if dup.find(word) != -1:  # 이미 기입된 리스트에 현재 word가 포함 되어 있다면 현재 word 횟수 줄임.
                    cntNum -= content.count(dup)
                    # print("현재 word 값 줄임", word, dup, cntNum, date)

                else:  # 현재 word에 이미 기입된 리스트의 값이 포함되어 있다면 기입된 리스트의 값 조정.
                    wordcount_dict[department][dup] -= cntNum
                    # print("리스트의 값 줄임", word, dup, cntNum, wordcount_dict[department][dup], date)
                    if wordcount_dict[department][dup] == 0:
                        del wordcount_dict[department][dup]
                        del dateset_dict[department][dup]
                    else:
                        # print("년도 삭제 전", department, dup, dateset_dict[department][dup])
                        dateset_dict[department][dup] = dateset_dict[department][dup].rstrip(
                            str(content.count(dup)) + "번 : " + date)
                        # print("년도 삭제 후", department, dup, dateset_dict[department][dup])

                        # 년도에서 줄바꿈이 맨 끝 부분에 남아 있다면 앞 부분에 다른 년도가 있다는 것을 의미하므로 줄바꿈을 다시 넣고 횟수 및 년도를 다시 재기입
                        if dateset_dict[department][dup].rfind("\n") != -1:
                            if dateset_dict[department][dup].rfind("\n") == len(dateset_dict[department][dup]) - 1:
                                dateset_dict[department][dup] = dateset_dict[department][dup].rstrip("\n")
                                if content.count(dup) != cntNum:
                                    new_cnt = content.count(dup) - cntNum
                                    dateset_dict[department][dup] += "\n" + str(new_cnt) + "번 : " + date
                                # print("줄바꿈 지웠다가 다시 채움", dateset_dict[department][dup])
                        # 줄바꿈이 없는 경우 "" 상태에서 횟수와 년도 재기입
                        if content.count(dup) != cntNum:
                            new_cnt = content.count(dup) - cntNum
                            dateset_dict[department][dup] = str(new_cnt) + "번 : " + date
                        # print("줄바꿈 없어서 그냥 다시 채움", dateset_dict[department][dup])
    return cntNum


def sort_length(dictList, datedictList):
    for i in list(dictList):
        for j in list(dictList[i].keys()):
            if j[0] == " ":
                # print("기존 값", j)
                # print("변경 값", j[1:])
                dictList[i][j[1:]] = dictList[i][j]
                datedictList[i][j[1:]] = datedictList[i][j]
                del dictList[i][j]
                del datedictList[i][j]

        dictList[i] = dict(sorted(dictList[i].items()))
        datedictList[i] = dict(sorted(datedictList[i].items()))


# def deduplicate_word(dictList, datedictList):


def data_info(contents):  # + '내용' 부분 중복 삭제
    # print("\n 중복 제거 전 내용들 \n", contents)
    print("\n전체 글 수 : ", len(contents))
    contents = contents.drop_duplicates(['부서', '제목', '내용'], keep="last")
    # print("\n 중복 제거 후 내용들 \n", contents)
    print("\n중복 제거 후 글 수 : ", len(contents))
    print("\n")

    return contents


def get_allDepartments(contents):
    departments = []
    for i in contents.index:
        # departments.append(contents.loc[i, '부서'])
        val = contents._get_value(i, '부서')
        departments.append(val)

    print("부서 수 확인용(중복O) : ", len(departments))
    return departments


def get_unique(departments):
    departments_unique = pd.unique(departments)
    # print("부서 수(중복X) : ", len(departments_unique))
    # print("정렬 전 부서 목록 ", departments_unique)
    departments_unique.sort()
    # print("부서 목록 ", departments_unique)             # 부서 목록 가나다순 정렬
    return departments_unique


def contents_Departments(allDepartments, departments_unique):
    total_cnt = 0
    count = []
    for i in departments_unique:
        cnt = allDepartments.count(i)
        total_cnt += cnt
        departments_list = []
        departments_list.append(str(i))
        departments_list.append(cnt)
        # print(departments_cnt)
        count.append(departments_list)

    departments_df = pd.DataFrame(count, columns=["부서", "횟수"])

    pd.set_option('display.max_rows', None)
    departments_df = departments_df.set_index("부서")
    # print(departments_df.sort_values(by = ["횟수"], axis=0, ascending=False))
    # print(total_cnt)
    # print("\n")


def load_searchWord(file_path):
    df = pd.read_excel(file_path, sheet_name=0)  # can also name of sheet
    my_list = df['대상어'].tolist()
    # print("대상어 리스트 \n", my_list)

    re_list = df['대체어'].tolist()
    return_list = dict(zip(my_list, re_list))
    # print("대체어 리스트 \n", return_list)

    # 동형이의어 리스트 생성 이후 구현
    sub_list = df['동음이의어'].tolist()
    for data in range(0, len(sub_list)):
        if type(sub_list[data]) != float:
            sub_list[data] = sub_list[data].replace("\n", "")
        else:
            pass

    wsd_list = dict(zip(my_list, sub_list))

    return my_list, return_list, wsd_list
