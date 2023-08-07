import pandas as pd
from AccuracyImprovementWSD import make_wsd
from tqdm import tqdm

def load_searchWord(file_path):
    df = pd.read_excel(file_path, sheet_name=0)  # can also name of sheet
    my_list = df['대상어'].tolist()

    cols = ["구분", "대상어", "대체어", "비고", "출처", "동음이의어"]
    wsd_list = []
    new_df = []

    for i in tqdm(my_list):
        wsd = make_wsd(i)

        if wsd != '':
            pass
        else:
            wsd = ""

        wsd_list.append(wsd)

    for i in df.index:
        con1 = df._get_value(i, '구분')
        con2 = df._get_value(i, '대상어')
        con3 = df._get_value(i, '대체어')
        con4 = df._get_value(i, '비고')
        con5 = df._get_value(i, '출처')
        con6 = wsd_list[i]

        row = [con1, con2, con3, con4, con5, con6]
        new_df.append(row)


    xlsx_df = pd.DataFrame(new_df, columns=cols)

    with pd.ExcelWriter("../../../워드카운팅 리스트(WordCounting List)/Searchwords_지자체(동).xlsx") as writer:
        xlsx_df.to_excel(writer, index=False, sheet_name="평가대상어")

    print("완료")
    # 동형이의어 리스트 생성 이후 구현
    #sub_list = df['동형이의어'].tolist()
    #wsd_list = dict(zip(my_list, sub_list))



load_searchWord("../../../워드카운팅 리스트(WordCounting List)/Searchwords_지자체.xlsx")