# * Copyright 2021 by SMU KHJ & KJT *
# * coding: utf-8 *
from collections import Counter
import pandas as pd
import os
from tkinter import *
from tqdm import tqdm
from difflib import SequenceMatcher
from AccuracyImprovementWSD import utagger_wsd, make_json
import re


def main(wordPath, filePath, file_option, morph, num, listnode, var, bar, program):
    global file_op, list_file, searchWord, changeWord, PATH, listnodes, p_var, progressbar, filepath, app, wsdwords
    file_op = file_option;
    listnodes = listnode;
    p_var = var;
    progressbar = bar;
    filepath = filePath;
    app = program

    wordPath = "../../../워드카운팅 리스트(WordCounting List)/" + wordPath
    PATH = "../../../크롤링 데이터(Crawling Data)/" + filePath + "/"

    list_file = dict((key, dict()) for key in os.listdir(PATH))
    searchWord, changeWord, wsdwords = load_searchWord(wordPath)  # wsdWord : 동형이의어 리스트 생성 이후에 활용

    print(list_file)

    if morph == 1:

        print("이 기능은 동음이의어 분석입니다. ※시간이 오래 걸릴 수 있습니다.")
        listnodes.insert(END, "이 기능은 동음이의어 분석입니다.")
        app.update()

        if num == 1:
            listnodes.insert(END, "※시간이 오래 걸릴 수 있습니다.※")
            listnodes.insert(END, "\n", "----------------------------------------------------------------------")
            wsd_count1()
        else:
            print(" + 이 기능은 기계분석입니다. ※시간이 오래 걸릴 수 있습니다.")
            listnodes.insert(END, "이 기능은 기계분석입니다.")
            listnodes.insert(END, "※시간이 오래 걸릴 수 있습니다.※")
            listnodes.insert(END, "\n", "----------------------------------------------------------------------")
            app.update()
            wsd_count2()
    else:
        if num == 1:
            count1()
        else:
            print("이 기능은 기계분석입니다. ※시간이 오래 걸릴 수 있습니다.")
            listnodes.insert(END, "이 기능은 기계분석입니다.")
            listnodes.insert(END, "※시간이 오래 걸릴 수 있습니다.※")
            listnodes.insert(END, "\n", "----------------------------------------------------------------------")
            app.update()
            count2()


def count1():
    p_var_i = 0
    p_var_len = len(list_file)
    p_var_wid = 100 / p_var_len

    for file_path in tqdm(list_file.keys()):
        text = open(PATH + file_path, 'rt', encoding='utf8').read()

        str0 = text.split(".")
        strs = text.split("\n")

        if len(str0) > len(strs):
            title = ""
            strs = str0
        else:
            title = strs[0]
            strs = strs[1:]

        text = "\n".join(strs)

        for word in searchWord:
            cntNum = text.count(word)

            if cntNum > 0:
                if list_file[file_path].get(word):
                    list_file[file_path][word] += cntNum
                    # print(" Add countNum :", word, " : ", cntNum)
                else:
                    list_file[file_path][word] = cntNum
                    # print(" New word in department : ", word, " : ", cntNum)

        p_var_i += p_var_wid
        p_var.set(p_var_i)
        progressbar.update()

    print(list_file)
    sort_length(list_file)
    deduplicate_word(list_file)
    view_count_department(list_file)
    totalCount = count_total(list_file)

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
    for i in searchWord:
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
    # Excel 저장 부분
    departmentData = pd.DataFrame.from_dict(list_file, orient="index")
    #print(departmentData)
    departmentData = departmentData.T

    totalData = pd.DataFrame(data=[totalCount], index=["빈도수"])
    totalData = totalData.T

    # ../워드카운트결과값에 저장  (기존의 result 값)
    DATA_DIR = '../../워드카운팅 리포트(WordCounting Report)'

    xlsxname = filepath
    try:
        xlsxname = xlsxname.rstrip('.txt')
        #xlsxname = xlsxname.rstrip('post.csv')
    except:
        pass

    xlsxname = xlsxname +" "+ file_op + " 결과값.xlsx"

    listnodes.insert(END, "카운트가 끝났습니다 ")
    listnodes.insert(END, xlsxname + " 입니다")
    listnodes.insert(END, "\n", "----------------------------------------------------------------------")

    xlsxname = os.path.join(DATA_DIR, xlsxname)


    with pd.ExcelWriter(xlsxname) as writer:
        departmentData.to_excel(writer, sheet_name="파일별")
        totalData.to_excel(writer, sheet_name="총 합")
    
    """


def count2():
    p_var_i = 0
    p_var_len = len(list_file)
    p_var_wid = 100 / p_var_len

    new_wordcount_df = pd.DataFrame(columns=["파일이름", "제목", "대상어", "대체어", "횟수", "내용"])
    dup_check_df = pd.DataFrame(columns=["제목", "대상어", "횟수", "내용"])

    for file_path in tqdm(list_file.keys()):
        text = open(PATH + file_path, 'rt', encoding='utf8').read()

        str0 = text.split(".")
        strs = text.split("\n")

        if len(str0) > len(strs):
            title = ""
            strs = str0
        else:
            title = strs[0]
            strs = strs[1:]

        text = "\n".join(strs)

        for word in searchWord:
            cntNum = text.count(word)

            if cntNum > 0:
                for line in strs:
                    o_line = line
                    cntlinenum = line.count(word)
                    if cntlinenum > 0:
                        check_dup = 1

                        for record_word in dup_check_df[dup_check_df["내용"] == o_line]["대상어"]:
                            i = dup_check_df.index[
                                (dup_check_df["내용"] == o_line) & (dup_check_df["대상어"] == record_word)].tolist()
                            if record_word.find(word) != -1:
                                # print("dupcheck0 " , word, record_word, line)
                                if dup_check_df.loc[i[0], "횟수"] == cntlinenum:
                                    check_dup = 0
                                    continue
                                else:
                                    cntlinenum = cntlinenum - dup_check_df["횟수"][i]
                            # word : ****   record_word **
                            elif word.find(record_word) != -1:
                                # print("dupcheck1 " , word, record_word, line)
                                if dup_check_df.loc[i[0], "횟수"] == cntlinenum:
                                    dup_check_df.drop(index=i, inplace=True)
                                    new_wordcount_df.drop(index=i, inplace=True)
                                    dup_check_df.reset_index(drop=True, inplace=True)
                                    new_wordcount_df.reset_index(drop=True, inplace=True)
                                else:
                                    dup_check_df.loc[i[0], "횟수"] = dup_check_df.loc[i[0], "횟수"] - cntlinenum

                        if check_dup == 1:
                            line = line_slicing(word, line)
                            line = line.replace(word, ' | ' + word + ' | ')
                            # print("replace ", line)
                            new_data = [file_path.rstrip('.txt'), title, word, changeWord[word], cntlinenum, line]
                            new_wordcount_df.loc[len(new_wordcount_df)] = new_data
                            dup_check_data = [title, word, cntlinenum, o_line]
                            dup_check_df.loc[len(dup_check_df)] = dup_check_data

        p_var_i += p_var_wid
        p_var.set(p_var_i)
        progressbar.update()

    print("기계 분석 카운트가 끝났습니다.")
    print("데이터 저장중.....")

    DATA_DIR = '../../../워드카운팅 리포트(WordCounting Report)'

    xlsxname2 = filepath

    try:
        xlsxname2 = xlsxname2.rstrip('.txt')
        # xlsxname2 = xlsxname2.rstrip('post.csv')
    except:
        pass

    xlsxname2 = xlsxname2 + " " + file_op + " 기계분석 결과값.xlsx"

    listnodes.insert(END, "기계분석 카운트가 끝났습니다 ")
    listnodes.insert(END, xlsxname2 + " 입니다")
    listnodes.insert(END, "\n", "----------------------------------------------------------------------")

    xlsxname2 = os.path.join(DATA_DIR, xlsxname2)

    with pd.ExcelWriter(xlsxname2) as writer2:
        new_wordcount_df.to_excel(writer2, sheet_name="기계분석", index=False)
        # dup_check_df.to_excel(writer2, sheet_name="원문", index=False)


def wsd_count1():
    p_var_i = 0
    p_var_len = len(list_file)
    p_var_wid = 100 / p_var_len

    for file_path in tqdm(list_file.keys()):
        text = open(PATH + file_path, 'rt', encoding='utf8').read()
        str0 = text.split(".")
        strs = text.split("\n")

        if len(str0) > len(strs):
            title = ""
            strs = str0
        else:
            title = strs[0]
            strs = strs[1:]

        text = "\n".join(strs)

        for word in searchWord:
            cntNum = text.count(word)

            if cntNum > 0:
                syn_number = "nan" if str(wsdwords[word]) == "nan" else str(int(wsdwords[word]))
                if syn_number == "nan":
                    pass
                else:
                    syn_number = "0" + str(syn_number) if len(str(syn_number)) == 1 else str(syn_number)
                    cntwsd, cnt_list, trans_list = utagger_wsd(text, word, syn_number)
                    cntNum = cntwsd

                if cntNum == 0:  # cntwsd도 나중에 추가할 것임
                    continue

                if list_file[file_path].get(word):
                    list_file[file_path][word] += cntNum
                    # print(" Add countNum :", word, " : ", cntNum)
                else:
                    list_file[file_path][word] = cntNum
                    # print(" New word in department : ", word, " : ", cntNum)

        p_var_i += p_var_wid
        p_var.set(p_var_i)
        progressbar.update()

    print(list_file)
    sort_length(list_file)
    deduplicate_word(list_file)
    view_count_department(list_file)
    totalCount = count_total(list_file)

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
    for i in searchWord:
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
    # Excel 저장 부분
    departmentData = pd.DataFrame.from_dict(list_file, orient="index")
    # print(departmentData)
    departmentData = departmentData.T

    totalData = pd.DataFrame(data=[totalCount], index=["빈도수"])
    totalData = totalData.T

    print("워드 카운트가 끝났습니다.")
    print("데이터 저장중.....")

    # ../워드카운트결과값에 저장  (기존의 result 값)
    DATA_DIR = '../../워드카운팅 리포트(WordCounting Report)'

    xlsxname = filepath
    try:
        xlsxname = xlsxname.rstrip('.txt')
        # xlsxname = xlsxname.rstrip('post.csv')
    except:
        pass

    xlsxname = xlsxname + " " + file_op + " 분석 결과값.xlsx"

    listnodes.insert(END, "카운트가 끝났습니다 ")
    listnodes.insert(END, xlsxname + " 입니다")
    listnodes.insert(END, "\n", "----------------------------------------------------------------------")

    xlsxname = os.path.join(DATA_DIR, xlsxname)

    with pd.ExcelWriter(xlsxname) as writer:
        departmentData.to_excel(writer, sheet_name="파일별")
        totalData.to_excel(writer, sheet_name="총 합")
    
"""


def wsd_count2():
    new_wordcount_df = pd.DataFrame(columns=["파일이름", "제목", "대상어", "대체어", "동음이의어", "영어 번역", "횟수", "내용"])
    dup_check_df = pd.DataFrame(columns=["제목", "대상어", "횟수", "내용"])
    error_check_df = pd.DataFrame(columns=["대상어", "대체어","대상어 의미 번호", "문장내 의미 번호", "영어 번역", "의미부여 점수", "내용", "동음이의어(내용)"])

    p_var_i = 0
    p_var_len = len(list_file)
    p_var_wid = 100 / p_var_len

    for file_path in tqdm(list_file.keys()):
        text = open(PATH + file_path, 'rt', encoding='utf8').read()

        str0 = text.split(".")
        strs = text.split("\n")

        if len(str0) > len(strs):
            title = ""
            strs = str0
        else:
            title = strs[0]
            strs = strs[1:]

        for line in strs:
            if ("붙임1" in line) or ("붙임 1" in line):
                break

            dupcheck_line = line
            o_line = ""
            for word in searchWord:
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
                            wsd_error = [word, changeWord[word],syn_number, syntax_list[iii], search_list[iii], sc_list[iii], slice_line, slice_res_ma]
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
                                cntlinenum = cntlinenum - dup_check_df[i[0], "횟수"]
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
                        new_data = [file_path.rstrip('.txt'), title, word, changeWord[word],
                                    syn_number if syn_number != "nan" else "", ml, cntlinenum, slice_line]
                        new_wordcount_df.loc[len(new_wordcount_df)] = new_data
                        dup_check_data = [title, word, cntlinenum, dupcheck_line]
                        dup_check_df.loc[len(dup_check_df)] = dup_check_data

                        for iii in range(len(search_list)):
                            wsd_error = [word, changeWord[word],syn_number, syntax_list[iii], search_list[iii], sc_list[iii], slice_line, slice_res_ma]
                            error_check_df.loc[len(error_check_df)] = wsd_error

        p_var_i += p_var_wid
        p_var.set(p_var_i)
        progressbar.update()

    print("기계 분석 카운트가 끝났습니다.")
    print("데이터 저장중.....")

    DATA_DIR = '../../../워드카운팅 리포트(WordCounting Report)'

    xlsxname2 = filepath

    try:
        xlsxname2 = xlsxname2.rstrip('.txt')
        # xlsxname2 = xlsxname2.rstrip('post.csv')
    except:
        pass

    xlsxname2 = xlsxname2 + " " + file_op + " 기계 분석 결과값.xlsx"

    listnodes.insert(END, "기계분석 카운트가 끝났습니다 ")
    listnodes.insert(END, xlsxname2 + " 입니다")
    listnodes.insert(END, "\n", "----------------------------------------------------------------------")

    xlsxname2 = os.path.join(DATA_DIR, xlsxname2)

    # ../워드카운트결과값에 저장   (언어정보연구원의 result 값과 유사)
    with pd.ExcelWriter(xlsxname2) as writer2:
        new_wordcount_df.to_excel(writer2, sheet_name="기계분석", index=False)
        error_check_df.to_excel(writer2, sheet_name="확인이 필요함", index=False)
        # dup_check_df.to_excel(writer2, sheet_name="원문", index=False)

    # Excel 저장 부분


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
        lineend = len(line) - 1
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


def sort_length(dictList):
    for i in list(dictList):
        dictList[i] = dict(sorted(dictList[i].items(), key=lambda x: len(x[0]), reverse=True))


def view_count_department(dictList):
    for listUnique in list(dictList):
        res = sorted(dictList[listUnique].items(), key=(lambda x: x[1]), reverse=True)
        print(listUnique, " : ", res)


def count_total(dictList: dict):
    totalCount = Counter()

    for listDict in dictList.values():
        totalCount = totalCount + Counter(listDict)

    return totalCount


# str.count() 중복 제거
def deduplicate_word(dictList: dict):
    for file in dictList:
        for i in dictList[file]:
            for j in dictList[file]:
                if i != j:
                    if i in j:
                        dictList[file][i] = dictList[file][i] - dictList[file][j]


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


def remove_whitespaces(text):
    lines = text.split('\n')
    lines = (l.strip() for l in lines)
    lines = (l for l in lines if len(l) > 0)

    return '\n'.join(lines)
