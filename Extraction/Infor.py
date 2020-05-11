import os
import re

from flair.data import Sentence
from flair.models import SequenceTagger

if os.path.exists("/home/juartaurus98/Sources/cv/NER_REF/data/best-model.pt"):
    model_ref = SequenceTagger.load('/home/juartaurus98/Sources/cv/NER_REF/data/best-model.pt')


def no_accent_vietnamese(s):
    s = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
    s = re.sub(r'[ÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪ]', 'A', s)
    s = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', s)
    s = re.sub(r'[ÈÉẸẺẼÊỀẾỆỂỄ]', 'E', s)
    s = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', s)
    s = re.sub(r'[ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ]', 'O', s)
    s = re.sub(r'[ìíịỉĩ]', 'i', s)
    s = re.sub(r'[ÌÍỊỈĨ]', 'I', s)
    s = re.sub(r'[ùúụủũưừứựửữ]', 'u', s)
    s = re.sub(r'[ƯỪỨỰỬỮÙÚỤỦŨ]', 'U', s)
    s = re.sub(r'[ỳýỵỷỹ]', 'y', s)
    s = re.sub(r'[ỲÝỴỶỸ]', 'Y', s)
    s = re.sub(r'[Đ]', 'D', s)
    s = re.sub(r'[đ]', 'd', s)
    return s


def SortSpans(spans):
    ''' Sort the spans of a line in ascending horizontal direction. See comment
    in SortBlocks function.
    '''
    sspans = []
    for s in spans:
        i = str(int(s["size"])).rjust(4, '0')
        sspans.append([i, s])
    sspans.sort(key=lambda x: x[0], reverse=True)
    return [s[1] for s in sspans]


def extract_Infor(dt):
    tmp = []
    for block in dt:
        for line in block['lines']:
            for span in line['spans']:
                if span['text'] != '':
                    tmp.append(span)
    infor = {"Name1": "", "Name2": "", "Date of birth": "", "Address": "", "Email": "", "Phone": "", "Phone_2": "",
             "Link": ""}

    check_name_1 = False
    check_name_2 = False
    # check_address = False
    check_birth = False
    check_phone = False
    sen = False
    # name_size = 0
    tmp = SortSpans(tmp)
    size = 0
    alls = []
    for item in tmp:
        if not alls:
            alls.append(item)
        elif alls[-1]['text'] == item['text'] and alls[-1]['size'] == item['size']:
            continue
        else:
            alls.append(item)
    all = []
    for item in alls:
        # print(item)
        # if item['size'] != size:
        all.append(item['text'])
        #     size = item['size']
        # else:
        #     all[-1] += ' '
        #     all[-1] += item['text']
    for item in all:
        # print(item)
        position = all.index(item)
        # NAME_2
        if check_name_2 is False:
            sentence = Sentence(item)
            model_ref.predict(sentence)
            result = sentence.to_dict(tag_type='ner')
            if len(result['entities']) > 0:
                end_name = -2
                for entity in result['entities']:
                    if entity['type'] == 'NAME' and end_name + 1 == entity['start_pos']:
                        # print(tmp)
                        # print(index)
                        infor['Name2'] += ' '
                        infor['Name2'] += entity['text']
                        end_name = entity['end_pos']
                    elif entity['type'] == 'NAME':
                        infor['Name2'] = entity['text']
                        end_name = entity['end_pos']
            if infor['Name2'] != '':
                check_name_2 = True
        # EMAIL
        if re.search(r'@', item):
            # print(item['text'])
            infor['Email'] = re.search(r'[\w\d\.-]+@+[\w\d\.-]+', item)[0]

        # DATE OF BIRTH
        if re.search(
                r'((\d){1,2}(/|-|.)(\d){1,2}(/|-|.)(\d){2,4})|([A-Za-z]{3,5}(/|-|.)(\d){1,2}(/|-|.)(\d){2,4})|(\d){1,2}(/|-|.)([A-Za-z]{3,5}(/|-|.)(\d){2,4})',
                item) and check_birth is False and not re.search(r'@', item):
            if 10 > len(re.sub(r'\D', '', item)) > 5:
                check_birth = True
                infor['Date of birth'] = re.search(
                    r'((\d){1,2}(/|-|.)(\d){1,2}(/|-|.)(\d){2,4})|([A-Za-z]{3,5}(/|-|.)(\d){1,2}(/|-|.)(\d){2,4})|(\d){1,2}(/|-|.)([A-Za-z]{3,5}(/|-|.)(\d){2,4})',
                    item).group()

        # PHONE
        if re.search(r'(\+84 )?(\+84)?(\d{2,5})( |.|-){0,2}\d{3,4}( |.|-){0,2}(\d{3,4})',
                     item) and check_phone is False and not re.search(r'(@|\|:)', item):
            if 12 > len(re.sub('\D', '', item)) >= 10:
                # print('**')
                # print(re.sub('\D', '', item))
                check_phone = True
                infor['Phone'] = re.search(r'(\+84 )?(\+84)?(\d{2,5})( |.|-){0,2}\d{3,4}( |.|-){0,2}(\d{3,4})',
                                           item).group()
            else:
                infor['Phone'] = ''
        # PHONE 2
        # if infor['Phone_2'] == '':
        #     tmp_ph = str(re.sub(r'\W', '', item))
        #     if re.search(r'^(01|0|840|84)([0-9]{9})$|^(01|0|840|84)([0-9]{9})(\D)+', tmp_ph):
        #         infor['Phone_2'] = re.search(r'^(01|0|840|84)([0-9]{9})$|^(01|0|840|84)([0-9]{9})(\D)+', tmp_ph).group()
        #
    if infor['Phone'] == '':
        infor['Phone'] = infor['Phone_2']
        del infor['Phone_2']
    else:
        del infor['Phone_2']
    return infor

