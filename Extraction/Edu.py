import re
from flair.data import Sentence


def check_missing(exp):
    keys = []
    for key in exp:
        if exp[key] == '':
            keys.append(key)
    return keys


def get_missing_company(Edu, position, model, last):
    all = []
    for index in range(position[0], position[1] + 1):
        for line in Edu[index]['lines']:
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


def get_missing_time(Edu, position, model, last):
    time = []
    all = []
    for index in range(position[0], position[1] + 1):
        for line in Edu[index]['lines']:
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


def get_missing_pos(Edu, position, model, last):
    all = []
    for index in range(position[0], position[1] + 1):
        for line in Edu[index]['lines']:
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
    try:
        if -block1['lines'][-1]['spans'][-1]['bbox'][1] + block2['lines'][0]['spans'][0]['bbox'][1] > 1:
            return False
    except:
        return True
    return True


def combine_blocks(block1, block2):
    block1['lines'].extend(block2['lines'])
    return block1


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


def complete_entiti(exp, type, text):
    print(exp, text)
    if type == 'NAME':
        if exp['school'] == '':
            exp['school'] = text
        else:
            exp['school'] += ' ' + text
        return exp
    if type == 'MAJOR':
        if exp['major'] == '':
            exp['major'] = text
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


def edu_extract_2(model, d):
    print(d)
    l = []
    exp = {'start': '', 'end': '', 'school': '', 'major': '', 'description': ''}
    d = d[1:]
    spans = []
    for block in d:
        for index in range(len(block['lines'])):
            block['lines'][index] = combine_text_in_line(block['lines'][index])
        block = combine_text_in_block(block)

    Edu = d

    if len(Edu) == 0:
        return [exp]
    for block in d:
        for line in block['lines']:
            for span in line['spans']:
                spans.append(span)
    first_flags = 0
    first_size = 0
    first_type = ''
    first_color = ''
    for span in spans:
        sentence = Sentence(span['text'])
        model.predict(sentence)
        result = sentence.to_dict(tag_type='ner')
        if len(result['entities']) > 0:
            if first_size == 0 and first_flags == 0:
                first_size = span['size']
                first_flags = span['flags']
                first_type = result['entities'][0]['type']
                first_color = span['color']
            else:
                break
    for span in spans:
        print(span['text'])
        sentence = Sentence(span['text'])
        model.predict(sentence)
        result = sentence.to_dict(tag_type='ner')
        if len(result['entities']) > 0:
            if result['entities'][0]['type'] == first_type and span['color'] == first_color:
                l.append(exp)
                exp = {'start': '', 'end': '', 'school': '', 'major': '', 'description': ''}
            for entiti in result['entities']:
                exp = complete_entiti(exp, entiti['type'], entiti['text'])
            exp['description'] += ' ' + span['text'][result['entities'][-1]['end_pos']:]

        else:
            exp['description'] += ' ' + span['text']
    l.append(exp)
    return l[1:]
