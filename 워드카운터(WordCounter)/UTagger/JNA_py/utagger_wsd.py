#-*- coding: utf-8-sig -*-
import sys
import re
from utagger_py import UTagger

rt = UTagger.Load_global('../bin/UTaggerR64.dll', '../Hlxcfg.txt')  # window dll

if rt != '':
    sys.exit(1)

ut = UTagger(0)  # 0은 객체 고유번호. 0~99 지정 가능. 같은 번호로 여러번 생성하면 안됨. 한 스레드당 하나씩 지정 필요.
rt = ut.new_ucma()  # 객체 생성. 객체가 있어야 유태거 이용 가능.
if rt != '':
    sys.exit(1)

def wsd_counter(text):
    #print("동형이의어 카운터")

    rt = ut.tag_line(text, 3)  # 분석! 문장을 분석하여 단순한 bsp의 나열로 출력. json 형태 아님. 2번째 인자 '3'은 hlxcfg의 영향을 덜 받게 해주는 옵션.
    rt = re.sub('[/][A-Z][A-Z][A-Z]', '' ,rt)
    rt = re.sub('[/][A-Z][A-Z]', '', rt)

    #print(rt)

    #ut.release_ucma() #객체 해제
    #UTagger.Release_global() #사전 해제
    return rt



def wsd_word(word):
    rt = ut.tag_line(word, 3)  # 분석! 문장을 분석하여 단순한 bsp의 나열로 출력. json 형태 아님. 2번째 인자 '3'은 hlxcfg의 영향을 덜 받게 해주는 옵션.
    #print(rt)
    rt = re.sub('[/][A-Z][A-Z][A-Z]', '' ,rt)

    rt = re.sub('[/][A-Z][A-Z]', '', rt)

    #print(rt)
    # ut.release_ucma() #객체 해제
    # UTagger.Release_global() #사전 해제
    return rt


