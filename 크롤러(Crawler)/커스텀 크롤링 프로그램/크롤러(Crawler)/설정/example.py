import re
from urllib.parse import urlparse, urlunparse

def ex1():
    xpath1 = '//*[@id="txt"]/table/tbody/tr[1]/td[5]'
    xpath2 = '//*[@id="txt"]/table/tbody/tr[10]/td[5]'

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
    print(path1 + path2)

    """numbers1 = []
    indexes1 = []
    numbers2 = []
    indexes2 = []

    for match in match1:
        number = match.group(1)
        index = match.start(1)
        index1 = match.start(1)
        index2 = match.end(1)
        numbers1.append(number)
        indexes1.append(index)

    for match in match2:
        number = match.group(1)
        index = match.start(1)
        index1 = match.start(1)
        index2 = match.end(1)
        numbers2.append(number)
        indexes2.append(index)"""


def ex2():
    url = "https://www.cheongyang.go.kr/cop/bbs/BBSMSTR_000000000064/selectBoardList.do?pageIndex=2&pagecnt=10"
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme
    netloc = parsed_url.netloc
    path = parsed_url.path
    params = parsed_url.params
    fragment = parsed_url.fragment

    # 쿼리 문자열 제거
    query = ""  # 쿼리 문자열을 비움
    new_url = urlunparse((scheme, netloc, path, params, query, fragment))
    print(new_url)


ex2()