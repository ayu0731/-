import re

def run(text):

    #情報1
    print('-----読み取り結果-----')
    print(text)
    print('-----抽出結果-----')
    match = re.search(
        r'(?:MODEL|MDL)\s+([A-Z0-9\- ]+)',
        text,
        re.IGNORECASE
    )

    if not match:
        print("MODEL/MDLが見つかりません")
        return

    model = match.group(1).strip()

    parts = re.split(r'[- ]+', model)
    
    if len(parts) >= 2:
        print("モデル:", parts[0])
        print("情報1:", parts[1])
    else:
        print("モデル:", model)

    
    #情報2
    match = re.search(r'(?:S/N|SH)\s+([A-Z0-9 ]+)', text)

    if not match:
        print("S/Nが見つかりません")
        return

    serial = match.group(1).replace(" ", "")
    serial = serial.replace("WCCZ", "WCC2")

    if len(serial) >= 5:
        print("情報2:", serial[2:5])


    #情報4
    match = re.search(
        r'DCM[:\s]+([A-Z0-9]+)',
        text,
        re.IGNORECASE
    )

    if not match:
        print("DCMが見つかりません")
        return

    dcm = match.group(1)

    print("DCM:", dcm)

    patterns = {
    "V2": ["V2"],
    "T2": ["T2", "IZ"],
    "VJ": ["VJ"],
    "TJ": ["TJ"]
    }

    for name, words in patterns.items():
        if any(word in dcm for word in words):
            print("情報3:", name)
        if not match:
            print("対象文字列なし")
            return
        
    return {
        "model": parts[0],
        "model1" : parts[1],
        "serial": serial[2:5],
        "dcm": name
    }
        


