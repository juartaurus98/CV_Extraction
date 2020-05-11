# from flair.models import SequenceTagger
# from flair.data import Sentence
import re


# from flair.data import Sentence

def check_missing(exp):
    keys = []
    for key in exp:
        if exp[key] == '' or exp[key] == [{'text': ''}, {'keyword': ''}]:
            keys.append(key)
    return keys


def get_missing_company(Exp, position, model, last):
    all = []
    for index in range(position[0], position[1] + 1):
        for line in Exp[index]['lines']:
            for spans in line['spans']:
                all.append(spans)
    if last == -1:
        last = len(all)
        print(last)
    for index in range(last, len(all) - 1):
        text_small_group = all[index]['text'] + ' ' + all[index + 1]['text']
        sentence2 = Sentence(text_small_group)
        model.predict(sentence2)
        result2 = sentence2.to_dict(tag_type='ner')
        for entity in result2['entities']:
            if entity['type'] == 'NAME':
                return entity['text']
    return ''


def get_missing_time(Exp, position, model, last):
    time = []
    all = []
    for index in range(position[0], position[1] + 1):
        for line in Exp[index]['lines']:
            for spans in line['spans']:
                all.append(spans)

    if last == -1:
        last = len(all)
        print(all, last)
    for index in range(last - 1, -1, -1):
        text_small_group = all[index]['text']
        print(text_small_group)
        sentence2 = Sentence(text_small_group)
        model.predict(sentence2)
        result2 = sentence2.to_dict(tag_type='ner')
        for entity in result2['entities']:
            if entity['type'] == 'DATE':
                time.append(entity['text'])
                if len(time) == 2:
                    return time
    print(time)
    return time


def get_missing_pos(Exp, position, model, last):
    all = []
    for index in range(position[0], position[1] + 1):
        for line in Exp[index]['lines']:
            for spans in line['spans']:
                all.append(spans)
    # print(all,last)
    if last == -1:
        last = len(all)
    for index in range(last - 1, -1, -1):
        text_small_group = all[index]['text']
        print(text_small_group)
        sentence2 = Sentence(text_small_group)
        model.predict(sentence2)
        result2 = sentence2.to_dict(tag_type='ner')
        print(result2)
        for entity in result2['entities']:
            if entity['type'] == 'POS':
                return entity['text']
    return ''


def check_line(part1, part2, d):
    all = []
    for block in d:
        for line in block['lines']:
            for spans in line['spans']:
                all.append(spans)

    for index in range(0, len(all) - 1):
        if re.search(part1, all[index]['text']) and (
                re.search(part2, all[index]['text']) or re.search(part2, all[index + 1]['text'])):
            return True
    return False


def check_block(block1, block2):
    # print(block1['lines'][-1]['spans'][-1]['bbox'][1])
    # print(block2)
    # print(block2['lines'][0]['spans'][0]['bbox'][1])
    # print(-block1['lines'][-1]['spans'][-1]['bbox'][1]+block2['lines'][0]['spans'][0]['bbox'][1])
    try:
        if -block1['lines'][-1]['spans'][-1]['bbox'][1] + block2['lines'][0]['spans'][0]['bbox'][1] > 1:
            return False
    except:
        return True
    return True


def combine_blocks(block1, block2):
    block1['lines'].extend(block2['lines'])
    return block1


def get_last_size_and_position(block):
    first_size = 0
    last_size = 0
    last_position = 0
    first_position = 10000
    for line in block['lines']:
        for span in line['spans']:
            if span['bbox'][1] > last_position:
                last_position = span['bbox'][1]
                last_size = span['size']
            if span['bbox'][1] < first_position:
                first_position = span['bbox'][1]
                first_size = span['size']
    return first_size, first_position, last_size, last_position


def get_text_in_block(block):
    text = ''
    for line in block['lines']:
        for span in line['spans']:
            text += span['text'] + ' '
    return text


def find_entity_position(entity_text, Exp):
    all = []
    for block in Exp:
        for line in block['lines']:
            for span in line['spans']:
                all.append(span)
    # print(all)
    for index in range(len(all)):
        if index == len(all) - 1:
            return -1
        if re.search(entity_text, all[index]['text']):
            return index
    return 0


def get_description(Exp, last_last, first_new):
    all = []
    text = ''
    for block in Exp:
        for line in block['lines']:
            for span in line['spans']:
                all.append(span)
    if first_new == -1:
        first_new = len(all)
    for index in range(last_last + 1, first_new):
        text += all[index]['text']
    return text


def get_special_des2(Exp, current_entiti):
    all = []
    print('special des', current_entiti)
    for block in Exp:
        for line in block['lines']:
            for span in line['spans']:
                all.append(span)
    position = []
    for entity in current_entiti:
        position.append(find_entity_position(entity, Exp))

    print(position)
    text = ''
    for index in range(len(all)):
        if index not in position:
            print(index)
            text += all[index]['text'] + ' '
    return text


def get_special_des(Exp, current_entiti, mark=None):
    all = []
    print('special des', current_entiti)
    for block in Exp:
        for line in block['lines']:
            for span in line['spans']:
                all.append(span)
    position = []
    for entity in current_entiti:
        position.append(find_entity_position(entity, Exp))

    print(position)
    if -1 in position:
        return ''
    text = ''
    if mark == -1:
        for index in range(len(all) - 1, -1, -1):
            if index not in position:
                text = all[index]['text'] + ' ' + text
            else:
                break
    else:
        for index in range(len(all)):
            if index not in position:
                print(index)
                text += all[index]['text'] + ' '
    return text


def distant_bewteen_2_block(block1, block2):
    curren_first_size, curen_first_pos1, current_last_size, current_last_post = get_last_size_and_position(block1)
    last_first_size, last_first_pos1, last_last_size, last_last_pos = get_last_size_and_position(block2)
    # print(curen_pos1,curren_size)
    # 2/0
    return curen_first_pos1 - last_last_pos - last_last_size


def combine_text_in_line(line):
    if len(line['spans']) == 1:
        return line
    index = 0
    while index > len(line['spans']):
        if not re.search('[a-z0-9A-Z]', line['spans'][index]['text']):
            del line['spans'][index]
        else:
            index += 1
    for index in range(1, len(line['spans'])):
        # if not re.search('[a-z0-9A-Z]',line['spans'][index]['text']):
        # 	del line['spans'][index]
        if line['spans'][index]['text'] == line['spans'][index - 1]['text']:
            del line['spans'][index]
    if len(line['spans']) == 1:
        return line
    index = 0
    while index < len(line['spans']) - 1:
        if (line['spans'][index]['font'] == line['spans'][index + 1]['font'] and line['spans'][index]['size'] ==
                line['spans'][index + 1]['size']):

            line['spans'][index]['text'] += ' ' + line['spans'][index + 1]['text']
            del line['spans'][index + 1]
        else:
            index += 1
    return line


def combine_text_in_block(block):
    if len(block['lines']) == 1:
        return block
    index = 0
    while index < len(block['lines']) - 1:
        # for index in range(1,len(block['lines'])):
        print(len(block['lines']), index)
        # print(index)
        if len(block['lines'][index]['spans']) == 1 and len(block['lines'][index + 1]['spans']) == 1 and \
                block['lines'][index]['spans'][0]['text'] == block['lines'][index + 1]['spans'][0]['text']:
            del block['lines'][index]
        else:
            index += 1
    if len(block['lines']) == 1:
        return block

    index = 0
    while index < len(block['lines']) - 1:
        # for index in range(1,len(block['lines'])):
        if len(block['lines'][index]['spans']) == 1 and len(block['lines'][index + 1]['spans']) == 1 and \
                block['lines'][index]['spans'][0]['font'] == block['lines'][index + 1]['spans'][0]['font'] and \
                block['lines'][index]['spans'][0]['size'] == block['lines'][index + 1]['spans'][0]['size']:
            block['lines'][index]['spans'][0]['text'] += ' ' + block['lines'][index + 1]['spans'][0]['text']
            del block['lines'][index + 1]
        else:
            index += 1
    return block


def transform(type):
    if type == 'NAME':
        return 'company_name'
    if type == 'POS':
        return 'position'
    if type == 'DATE':
        return 'start'


def get_text_in_list_of_span(list_index, spans):
    text = ''
    if list_index[-1] - list_index[0] >= 3:
        for index in range(list_index[0], list_index[-1]):
            if 'text' in spans[index]:
                text += ' ' + spans[index]['text']
    else:
        for index in range(list_index[0], list_index[0] + 3):
            try:
                if 'text' in spans[index]:
                    text += ' ' + spans[index]['text']
            except:
                pass
    return text


def complete_entiti(exp, type, text):
    # exp={'start': '', 'end': '', 'company_name': '', 'position': '', 'description': ''}
    print(exp, text)
    if type == 'NAME':
        if exp['company_name'] == '':
            exp['company_name'] = text
        else:
            exp['description'][0]['text'] += ' ' + text
            exp['description'][1]['keyword'] += ' ' + text
        # print(exp)
        return exp

    if type == 'POS':
        if exp['position'] == '':
            exp['position'] = text
        else:
            exp['description'][0]['text'] += ' ' + text
            exp['description'][1]['keyword'] += ' ' + text
        return exp
    if type == 'DATE' and exp['start'] == '':
        exp['start'] = text
        return exp
    if type == 'DATE' and exp['end'] == '':
        exp['end'] = text
        return exp
    return exp


def segment_by_color(list_span):
    color = []
    for span in list_span:
        color.append(span['color'])
    pass


def check_position(entiti, curent_position, spans):
    length1 = len(spans[curent_position[0]]['text'])
    length2 = len(spans[curent_position[0]]['text']) + len(spans[curent_position[1]]['text']) + 1
    if spans[curent_position[0]]['size'] != spans[curent_position[1]]['size'] or spans[curent_position[0]]['flags'] != \
            spans[curent_position[1]]['flags'] and spans[curent_position[0]]['bbox'][1] != \
            spans[curent_position[1]]['bbox'][1]:
        return False
    if entiti['start_pos'] < length1 and entiti['end_pos'] > length1:
        print(length1)
        print(length2)
        print(entiti)
        return True

    return False


def check_distant_left(spans):
    spans2 = sorted(spans, key=lambda i: round(i['bbox'][0]))
    print(spans2[0]['bbox'])
    print(spans2[-1]['bbox'])
    for index in range(len(spans2) - 1):
        # print(spans2[index]['bbox'],spans2[-1]['bbox'])
        if abs(spans2[index]['bbox'][1] - spans2[-1]['bbox'][1]) <= 2:
            return False
    if abs(spans2[0]['bbox'][0] - spans2[-1]['bbox'][0]) <= 5 and spans2[0]['bbox'][2] != spans2[-1]['bbox'][2]:
        return False
    return True


def check_span_entiti(entities, current_index, spans):
    # print(len(spans[current_index[0]]['text']))
    if len(entities) == 0:
        return False
    if entities[0]['start_pos'] >= len(spans[current_index[0]]['text']) - 1:
        return False
    check_not_date = False
    check_date = False
    for entiti in entities:
        print(entiti['type'])
        if entiti['type'] == 'DATE':
            check_date = True
        if entiti['type'] != 'DATE':
            check_not_date = True

    print(check_date, check_not_date)
    if check_date and check_not_date:
        return True
    return False


# def get_entiti_in_first_span(entities,index,spans):

def check_entiti_last_span(entities, current_index, spans):
    if entities[-1]['start_pos'] >= len(spans[current_index[0]]['text']):
        for index in range(len(entities)):
            if entities[index]['start_pos'] >= len(spans[current_index[0]]['text']):
                return True, entities[index:]
    return False, []


def exp_extract(model, d, key_span):
    # print(key_span)
    l = []
    exp = {'start': '', 'end': '', 'company_name': '', 'position': '', 'description': [{'text': ''}, {'keyword': ''}]}
    break_line = False
    break_block = False
    for block in d:
        if 'lines' in block:
            for line in block['lines']:
                for span in line['spans']:
                    # print(span)
                    if span['text'] == key_span['text']:
                        print(span)
                        span['text'] = ''
                        break_line = True
                        break_block = True
                        if line['spans'].index(span) > 0:
                            for i in range(line['spans'].index(span)):
                                line['spans'][i]['text'] = ''
                        break
                if break_line:
                    break
            if break_block:
                break
    # print(key_span)
    # 1/0
    # print(d)
    # 1/0
    spans = []
    Exp = d

    if len(Exp) == 0:
        return [exp]
    for block in d:
        for line in block['lines']:
            for span in line['spans']:
                spans.append(span)
    first_flags = 0
    first_size = 0
    first_type = ''
    first_position = 0
    first_color = ''
    first_font = ''
    curent_entiti = ''
    previous_index = []
    previous_entiti = ''
    for index in range(len(spans)):
        senten = spans[index]['text']
        print('senten to find first entiti:', senten)
        sentence = Sentence(senten)
        model.predict(sentence)
        result = sentence.to_dict(tag_type='ner')
        if len(result['entities']) > 0:
            if first_type == '':
                first_size = spans[index]['size']
                first_flags = spans[index]['flags']
                first_type = result['entities'][0]['type']
                first_position = spans[index]['bbox']
                first_color = spans[index]['color']
                first_font = spans[index]['font']
                print(result['entities'][0])
                print(spans[index])
                break
            else:
                break
    print(first_type)
    print(len(spans))
    index = 0
    first_index = 0
    while index < len(spans):
        print('index', index)
        check = False
        print(exp)
        curent_index = []
        if index < len(spans) - 1:
            senten = spans[index]['text'] + ' ' + spans[index + 1]['text']
            curent_index.append(index)
            curent_index.append(index + 1)
        else:
            senten = spans[index]['text']
            curent_index.append(index)
        print(senten)
        sentence = Sentence(senten)
        model.predict(sentence)
        result = sentence.to_dict(tag_type='ner')
        print(len(curent_index), 'span')
        print('entti', result['entities'])

        if len(curent_index) > 1:

            for entiti in result['entities']:
                if check_position(entiti, curent_index, spans):
                    check = True
                    print('bewten', entiti)
                    break
            if check_span_entiti(result['entities'], curent_index, spans) and first_type != 'DATE':
                check = True
            print('check:', check)
            if check:
                index += 2
            else:
                senten = spans[index]['text']
                sentence = Sentence(senten)
                model.predict(sentence)
                result = sentence.to_dict(tag_type='ner')
                print('1 spans', result['entities'])
                index += 1
        else:
            index += 1

        if check:
            index2 = index - 2
        else:
            index2 = index - 1
        print('before', result)
        print('before', senten)
        if index2 > 0 and not check:
            if len(result['entities']) == 0:
                # print(spans[index2-1]['text'])
                # print(spans[index2]['text'])
                senten2 = spans[index2 - 1]['text'] + ' ' + spans[index2]['text']
                sentence2 = Sentence(senten2)
                model.predict(sentence2)
                result2 = sentence2.to_dict(tag_type='ner')
                if len(result2['entities']) > 0:
                    check_entiti = check_entiti_last_span(result2['entities'], [index2 - 1, index2], spans)
                    if check_entiti[0]:
                        result['entities'] = check_entiti[1]
                        senten = spans[index2]['text']
                        print('affter', result)
                        print('affter', senten)

        if len(result['entities']) > 0:
            if first_type == 'DATE':
                print('curent entiti', curent_entiti)
                print((result['entities'][0]['type'] == first_type))
                print(curent_entiti != result['entities'][0]['type'])
                print(curent_entiti == result['entities'][0]['type'] and 'start' not in check_missing(exp) and
                      'end' not in check_missing(exp))
                # print(check_distant_left(spans))
                if (result['entities'][0]['type'] == first_type and (curent_entiti != result['entities'][0]['type'] or
                                                                     (curent_entiti == result['entities'][0][
                                                                         'type'] and 'start' not in check_missing(
                                                                         exp) and
                                                                      'end' not in check_missing(exp)))):
                    # if check_distant_left(spans):
                    print(222222222222)
                    print(first_position)
                    print(spans[index - 2])
                    print(spans[index - 1])
                    if ((check and (
                            abs(spans[index - 2]['bbox'][0] - first_position[0]) <= 5 or spans[index - 2]['bbox'][2] ==
                            first_position[2])) or
                            (not check and (abs(spans[index - 1]['bbox'][0] - first_position[0]) <= 5 or
                                            spans[index - 1]['bbox'][2] == first_position[2]))):
                        print('ádasd')
                        # if 'company_name' in check_missing(exp) or 'position' in check_missing(exp):
                        # 	if check:
                        # 		senten3=get_text_in_list_of_span([first_index,index-2],spans)
                        # 	else:
                        # 		senten3=get_text_in_list_of_span([first_index,index-1],spans)
                        # 	print('senten date:',senten3)
                        # 	sentence3 = Sentence(senten3)
                        # 	model.predict(sentence3)
                        # 	result3 = sentence3.to_dict(tag_type='ner')
                        # 	print(result3)
                        # 	for entiti in result3['entities']:
                        # 		if 'position' in check_missing(exp) and entiti['type']=='POS':
                        # 	exp['position']=entiti['text']
                        # 	if 'company_name' in check_missing(exp) and entiti['type']=='NAME':
                        # 		exp['company_name']=entiti['text']
                        l.append(exp)
                        exp = {'start': '', 'end': '', 'company_name': '', 'position': '',
                               'description': [{'text': ''}, {'keyword': ''}]}
                        print(1)


            elif result['entities'][0]['type'] == first_type:
                print('why not append')
                print('spans:', spans[index - 2], spans[index - 1])
                print('first position :', first_position)
                print(first_size)
                print(first_flags)
                print('not check:', not check)
                print(abs(spans[index - 1]['bbox'][0] - first_position[0]) <= 5)
                print(spans[index - 1]['size'] == first_font)
                print(spans[index - 1]['flags'] == first_flags)
                # if check_distant_left(spans):
                if ((check and abs(spans[index - 2]['bbox'][0] - first_position[0]) <= 5 and spans[index - 2][
                    'size'] == first_size and spans[index - 2]['flags'] == first_flags) or
                        (not check and abs(spans[index - 1]['bbox'][0] - first_position[0]) <= 5 and spans[index - 1][
                            'size'] == first_size and spans[index - 1]['flags'] == first_flags)):
                    print('exp append:', exp)
                    if 'company_name' in check_missing(exp) or 'position' in check_missing(exp):
                        if check:
                            senten3 = get_text_in_list_of_span([first_index, index - 2], spans)
                        else:
                            senten3 = get_text_in_list_of_span([first_index, index - 1], spans)
                        sentence3 = Sentence(senten3)
                        model.predict(sentence3)
                        result3 = sentence3.to_dict(tag_type='ner')
                        for entiti in result3['entities']:
                            if 'position' in check_missing(exp) and entiti['type'] == 'POS':
                                exp['position'] = entiti['text']
                            if 'company_name' in check_missing(exp) and entiti['type'] == 'NAME':
                                exp['company_name'] = entiti['text']
                    print((check_missing(exp)))
                    print(first_type)
                    print(exp['description'][0]['text'] == '')
                    # print(exp['description'][1]['keyword']=='')
                    if first_type not in check_missing(exp) and len(check_missing(exp)) == 3 and len(
                            exp['description'][0]['text']) <= 3:
                        print(exp[transform(first_type)])
                        exp[transform(first_type)] += ' ' + result['entities'][0]['text']
                        print(exp)
                    else:
                        l.append(exp)
                        exp = {'start': '', 'end': '', 'company_name': '', 'position': '',
                               'description': [{'text': ''}, {'keyword': ''}]}
                    if check:
                        first_index = index - 2
                    else:
                        first_index = index - 1

                    print(2)
                    print(check_distant_left(spans))
            else:

                if ((check == True and (
                        spans[index - 2]['flags'] == first_flags or spans[index - 1]['flags'] == first_flags) \
                     and (spans[index - 2]['color'] == first_color or spans[index - 1]['color'] == first_color) and
                     (spans[index - 2]['font'] == first_font or spans[index - 1]['font'] == first_font)) or (
                            check == False and spans[index - 1]['flags'] == first_flags and
                            spans[index - 1]['color'] == first_color and spans[index - 1]['font'] == first_font)) and \
                        ((check and abs(spans[index - 2]['bbox'][0] - first_position[0]) <= 5) or
                         (not check and abs(spans[index - 1]['bbox'][0] - first_position[0]) <= 5)):
                    print('exp append:', exp)
                    if 'company_name' in check_missing(exp) or 'position' in check_missing(exp):
                        if check:
                            senten3 = get_text_in_list_of_span([first_index, index - 2], spans)
                        else:
                            senten3 = get_text_in_list_of_span([first_index, index - 1], spans)
                        sentence3 = Sentence(senten3)
                        model.predict(sentence3)
                        result3 = sentence3.to_dict(tag_type='ner')
                        for entiti in result3['entities']:
                            if 'position' in check_missing(exp) and entiti['type'] == 'POS':
                                exp['position'] = entiti['text']
                            if 'company_name' in check_missing(exp) and entiti['type'] == 'NAME':
                                exp['company_name'] = entiti['text']
                    l.append(exp)
                    if check:
                        first_index = index - 2
                    else:
                        first_index = index - 1
                    exp = {'start': '', 'end': '', 'company_name': '', 'position': '',
                           'description': [{'text': ''}, {'keyword': ''}]}
                    print(5)
                    print(check)
                    print(first_flags)
                    print(first_color)
                    print(spans[index - 2])
                    print(spans[index - 1])
                    first_type = result['entities'][0]['type']
                    print(first_type)

            for entiti in result['entities']:
                # print(entiti)
                # print(exp)
                if not re.search('mô tả công việc', entiti['text'].lower().strip()):
                    exp2 = exp
                    print(exp2)
                    exp = complete_entiti(exp2, entiti['type'], entiti['text'])
                    curent_entiti = entiti['type']
            exp['description'][0]['text'] += ' ' + senten[result['entities'][-1]['end_pos']:]
            previous_index = curent_index
            previous_entiti = result['entities']
        else:
            # print(exp)
            exp['description'][0]['text'] += ' ' + senten
            previous_index = curent_index
            previous_entiti = result['entities']
    # if index==len(spans)-1:
    # 	break
    l.append(exp)
    if len(l) == 0:
        return []
    if len(check_missing(l[0])) >= 3:
        return l[1:]
    else:
        return l
# from pdf_reader.analysis_file import query_param_follow_keyword
# from pdf_reader.pdf_connector import pdf_reader
# import os
# base=os.path.dirname(__file__)
# model=SequenceTagger.load('C:/Users/long/PycharmProjects/new_cv/Flair_model/ner/ner_exp/best-model.pt')
# print(exp_extract(model,query_param_follow_keyword('Exp',pdf_reader('E:/work/CV/VI/test.pdf')[0])))
