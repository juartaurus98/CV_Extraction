import json
import os
import re
from pdf_reader.merge_multiple_pdfs import pdf_reader
import fitz
from pprint import pprint

base = os.path.dirname(__file__)


def normalize_block(block):
    for line in block['lines']:
        for span in line['spans']:
            if list(span['text']).count(' ') == len(span['text']):
                line['spans'].remove(span)
            if span['text'] == '' or span['font'] == 'FontAwesome':
                line['spans'].remove(span)
    x0 = 100000
    x1 = 0
    y0 = 100000
    y1 = 0
    for line in block['lines']:
        for span in line['spans']:
            x0 = min(x0, span['bbox'][0])
            x1 = max(x1, span['bbox'][2])
            y0 = min(y0, span['bbox'][1])
            y1 = max(y1, span['bbox'][3])
    block['bbox'] = [x0, y0, x1, y1]
    return block


def sort_by_left(blocks):
    minsize = 100000
    for block in blocks:
        if block['bbox'][0] < minsize:
            minsize = block['bbox'][0]
    for block in blocks:
        if abs(block['bbox'][0] - minsize):
            pass
    return sorted(blocks, key=lambda i: round(i['bbox'][0]))


def sort_by_top(blocks):
    return sorted(blocks, key=lambda i: round(i['bbox'][1]))


def sort_block(all_block):
    for block in all_block:
        block = normalize_block(block)
    pages = [sort_by_left(sort_by_top(all_block))]

    layout_page = []
    for page in pages:
        if len(page) == 0:
            break
        layout = [[page[0]]]
        for index in range(1, len(page)):
            if abs(page[index]['bbox'][0] - layout[-1][0]['bbox'][0]) <= 5:
                layout[-1].append(page[index])
            else:
                layout.append([page[index]])
        layout_page.append(layout)

    for page in layout_page:
        for index in range(len(page)):
            page[index] = sort_by_top(page[index])
            min_left = 1000000
            max_left = 0
            for index_block in range(len(page[index])):
                if page[index][index_block]['bbox'][0] < min_left:
                    min_left = page[index][index_block]['bbox'][0]
                if page[index][index_block]['bbox'][2] > max_left:
                    max_left = page[index][index_block]['bbox'][2]
            page[index].append((min_left, max_left))

    true_layout = []
    for page in layout_page:
        true_layout.append([])
        for index in page:
            for index_block in (index[:-1]):
                if 'lines' not in index_block:
                    index.remove(index_block)
            if len(index) == 1:
                page.remove(index)
    for page in layout_page:
        curent_blocks = page[0]
        distant = curent_blocks[-1]
        for index in range(1, len(page)):
            if ((page[index][-1][0] >= curent_blocks[-1][0] or abs(page[index][-1][0] - curent_blocks[-1][0]) <= 10) and
                (curent_blocks[-1][1] - page[index][-1][0] >= abs(page[index][-1][1] - page[index][-1][0]) / 2 or
                 page[index][-1][1] <= curent_blocks[-1][1] or curent_blocks[-1][1] - page[index][-1][0] >= abs(
                            curent_blocks[-1][1] - curent_blocks[-1][0]) / 2) or
                abs(page[index][-1][1] - curent_blocks[-1][1]) <= 10) \
                    or ((page[index][-1][0] <= curent_blocks[-1][0] or abs(
                page[index][-1][0] - curent_blocks[-1][0]) <= 10) and
                        (curent_blocks[-1][1] - page[index][-1][0] >= abs(
                            page[index][-1][1] - page[index][-1][0]) / 2 or
                         page[index][-1][1] <= curent_blocks[-1][1] or curent_blocks[-1][1] - page[index][-1][0] >= abs(
                                    curent_blocks[-1][1] - curent_blocks[-1][0]) / 2)):
                distant = curent_blocks[-1]
                del curent_blocks[-1]
                curent_blocks.extend(page[index][:-1])
                curent_blocks = sort_by_top(curent_blocks)
                curent_blocks.append((min(distant[0], page[index][-1][0]), max(distant[1], page[index][-1][1])))
                if index == len(page) - 1:
                    true_layout[-1].append(curent_blocks)
            else:
                true_layout[-1].append(curent_blocks)
                curent_blocks = page[index]
                distant = curent_blocks[-1]
                if index == len(page) - 1:
                    true_layout[-1].append(curent_blocks)
    return 1, true_layout


def sort_spans(all_block):
    pages = [sort_by_left(sort_by_top(all_block))]
    layout_page = []
    for page in pages:
        if len(page) == 0:
            break
        layout = [[page[0]]]
        for index in range(1, len(page)):
            if abs(page[index]['bbox'][0] - layout[-1][0]['bbox'][0]) <= 2.99999:
                layout[-1].append(page[index])
            else:
                layout.append([page[index]])
        layout_page.append(layout)

    for page in layout_page:

        for index in range(len(page)):
            page[index] = sort_by_top(page[index])
            min_left = 1000000
            max_left = 0
            for index_block in range(len(page[index])):
                if page[index][index_block]['bbox'][0] < min_left:
                    min_left = page[index][index_block]['bbox'][0]
                if page[index][index_block]['bbox'][2] > max_left:
                    max_left = page[index][index_block]['bbox'][2]
            page[index].append((min_left, max_left))

    true_layout = [[]]
    for page in layout_page:
        curent_blocks = page[0]
        distant = curent_blocks[-1]
        for index in range(1, len(page)):
            if ((page[index][-1][0] >= curent_blocks[-1][0] or abs(page[index][-1][0] - curent_blocks[-1][0]) <= 10) and
                ((curent_blocks[-1][1] - page[index][-1][0]) >= (page[index][-1][1] - page[index][-1][0]) * 0.4 or
                 page[index][-1][1] <= curent_blocks[-1][1] or curent_blocks[-1][1] - page[index][-1][0] >= abs(
                            curent_blocks[-1][1] - curent_blocks[-1][0]) / 2) or
                abs(page[index][-1][1] - curent_blocks[-1][1]) <= 10) \
                    or ((page[index][-1][0] <= curent_blocks[-1][0] or abs(
                page[index][-1][0] - curent_blocks[-1][0]) <= 10) and
                        (curent_blocks[-1][1] - page[index][-1][0] >= abs(
                            page[index][-1][1] - page[index][-1][0]) / 2 or
                         page[index][-1][1] <= curent_blocks[-1][1] or curent_blocks[-1][1] - page[index][-1][0] >= abs(
                                    curent_blocks[-1][1] - curent_blocks[-1][0]) / 2)):
                distant = curent_blocks[-1]
                del curent_blocks[-1]
                curent_blocks.extend(page[index][:-1])
                curent_blocks = sort_by_top(curent_blocks)
                curent_blocks.append((min(distant[0], page[index][-1][0]), max(distant[1], page[index][-1][1])))
                if index == len(page) - 1:
                    true_layout[-1].append(curent_blocks)
            else:
                true_layout[-1].append(curent_blocks)
                curent_blocks = page[index]
                distant = curent_blocks[-1]
                if index == len(page) - 1:
                    true_layout[-1].append(curent_blocks)
    return 1, true_layout


def get_all_spans(block):
    spans = []
    for line in block['lines']:
        for span in line['spans']:
            spans.append(span)
    return spans


def query_infor_without_keyword(all_data, olther, key, key_size, key_flags, minsize):
    for item in key:
        olther.append(item)

    all_content = all_data[0]

    true = []
    check_break = False
    if len(all_content) == 1:
        for item in all_content[0][:-1]:
            spans = get_all_spans(item)
            for span in spans:
                for o in olther:
                    if re.search(o, span['text'].lower()):
                        if key_size > minsize:
                            if (span['flags'] >= key_flags or span['text'].isupper()) and span['size'] >= key_size:
                                return true
                        else:
                            return true
            true.append(item)

    true_multi_block = []
    for index in range(3):
        if len(true_multi_block) > 0:
            break
        for o in olther:
            if check_content_of_block(all_content[0][index], o, key_size, key_flags, minsize)[0]:
                true_multi_block = all_content[1]
                break
    if len(true_multi_block) == 0:
        for index in range(3):
            if len(true_multi_block) > 0:
                break
            for o in olther:
                try:
                    if check_content_of_block(all_content[1][index], o, key_size, key_flags, minsize)[0]:
                        true_multi_block = all_content[0]
                        break
                except:
                    pass
    if len(true_multi_block) == 0 and len(all_content[1]) < 3:
        true_multi_block = all_content[0]

    for multi_block in all_content:
        break_point = False
        for item in multi_block:
            if break_point:
                break
            if type(item) == dict:
                spans = get_all_spans(item)
                for span in spans:
                    if break_point:
                        break
                    for o in olther:
                        if re.search(o, span['text'].lower()):
                            if key_size > minsize:
                                if (span['flags'] >= key_flags or span['text'].isupper()) and span[
                                    'size'] >= key_size - 1:
                                    break_point = True
                                    break
                            else:
                                break_point = True
                                break
                if not break_point:
                    true.append(item)
    return true


def check_content_of_block(block, key, key_size, key_flags, minsize):
    if 'lines' in block:
        for line in block['lines']:
            for span in line['spans']:

                if (re.search(key.lower(), span['text'].lower()) and not re.search('thông tin thêm',
                                                                                   span['text'].lower()) and len(
                    span['text'].split()) - len(key.split()) <= 3):
                    if (re.search('bold', span['font'].lower()) or span['text'].isupper() or key_flags >= 10) and (
                            span['size'] >= key_size) and \
                            (span['flags'] >= key_flags or re.search('bold', span['font'].lower())):
                        return (True, span)
        if key_flags < 10:
            for line in block['lines']:
                for span in line['spans']:
                    if re.search(key.lower(), span['text'].lower()):
                        if span['size'] >= key_size and key_size > minsize:
                            return (True, span)
    return False, 1


def Sort_size(spans):
    sspans = []
    for s in spans:
        i = str(int(s["size"])).rjust(4, '0')
        sspans.append([i, s])
    sspans.sort(key=lambda x: x[0], reverse=True)
    return [s[1] for s in sspans]


def find_col(all_blocks):
    sp = []
    for block in all_blocks:
        for line in block['lines']:
            for span in line['spans']:
                if span['text'] != '':
                    sp.append(span)
    sp = Sort_size(sp)
    return sp


def query_param_follow_keyword(keyword, all_block):
    with open(os.path.join(base, 'keyword.txt'), 'r', encoding='utf-8') as file:
        key_data = file.read().split('\n\n')
    all_data = sort_block(all_block)[1]
    data = {}

    for block in key_data:
        l = block.split('\n')
        data.update({l[0]: l[1:]})
    l = []
    other = []
    if keyword == 'Profile':
        l = data['Profile']
        other = []
        for typer in ['Exp', 'Edu', 'Objective', 'Skill', 'Reference', 'Project', 'Activity', 'Interests', 'Reward',
                      'Certificate', 'Other']:
            try:
                for item in data[typer]:
                    other.append(item)
            except:
                pass
    elif keyword == 'Exp':
        l = data['Exp']
        other = []
        for typer in ['Profile', 'Edu', 'Objective', 'Skill', 'Reference', 'Project', 'Activity', 'Interests', 'Reward',
                      'Certificate', 'Other']:
            try:
                for item in data[typer]:
                    other.append(item)
            except:
                pass
    elif keyword == 'Edu':
        l = data['Edu']
        other = []
        for typer in ['Profile', 'Exp', 'Objective', 'Skill', 'Reference', 'Project', 'Activity', 'Interests', 'Reward',
                      'Certificate', 'Other']:
            try:
                for item in data[typer]:
                    other.append(item)
            except:
                pass
    elif keyword == 'Objective':
        l = data['Objective']
        other = []
        for typer in ['Profile', 'Edu', 'Exp', 'Skill', 'Reference', 'Project', 'Activity', 'Interests', 'Reward',
                      'Certificate', 'Other']:
            try:
                for item in data[typer]:
                    other.append(item)
            except:
                pass
    elif keyword == 'Skill':
        l = data['Skill']
        other = []
        for typer in ['Profile', 'Edu', 'Objective', 'Exp', 'Reference', 'Project', 'Activity', 'Interests', 'Reward',
                      'Certificate', 'Other']:
            try:
                for item in data[typer]:
                    # print(item)
                    other.append(item)
            except:
                pass
    elif keyword == 'Reference':
        l = data['Reference']
        other = []
        for typer in ['Profile', 'Edu', 'Objective', 'Skill', 'Exp', 'Project', 'Activity', 'Interests', 'Reward',
                      'Certificate', 'Other']:
            try:
                for item in data[typer]:
                    other.append(item)
            except:
                pass
    elif keyword == 'Project':
        l = data['Project']
        other = []
        for typer in ['Profile', 'Edu', 'Objective', 'Skill', 'Exp', 'Reference', 'Activity', 'Interests', 'Reward',
                      'Certificate', 'Other']:
            try:
                for item in data[typer]:
                    other.append(item)
            except:
                pass
    elif keyword == 'Activity':
        l = data['Activity']
        other = []
        for typer in ['Profile', 'Edu', 'Objective', 'Skill', 'Exp', 'Reference', 'Project', 'Interests', 'Reward',
                      'Certificate', 'Other']:
            try:
                for item in data[typer]:
                    other.append(item)
            except:
                pass
    elif keyword == 'Interests':
        l = data['Interests']
        other = []
        for typer in ['Profile', 'Edu', 'Objective', 'Skill', 'Exp', 'Reference', 'Project', 'Activity', 'Reward',
                      'Certificate', 'Other']:
            try:
                for item in data[typer]:
                    other.append(item)
            except:
                pass
    elif keyword == 'Reward':
        l = data['Reward']
        other = []
        for typer in ['Profile', 'Edu', 'Objective', 'Skill', 'Exp', 'Reference', 'Project', 'Activity', 'Interests',
                      'Certificate', 'Other']:
            try:
                for item in data[typer]:
                    other.append(item)
            except:
                pass
    elif keyword == 'Certificate':
        l = data['Certificate']
        other = []
        for typer in ['Profile', 'Edu', 'Objective', 'Skill', 'Exp', 'Reference', 'Project', 'Activity', 'Interests',
                      'Reward', 'Other']:
            try:
                for item in data[typer]:
                    other.append(item)
            except:
                pass
    elif keyword == 'Other':
        l = data['Other']
        other = []
        for typer in ['Profile', 'Edu', 'Objective', 'Skill', 'Exp', 'Reference', 'Project', 'Activity', 'Interests',
                      'Certificate', 'Reward']:
            try:
                for item in data[typer]:
                    other.append(item)
            except:
                pass
    no_key_word = []
    all_content = []

    for page in all_data:
        for blocks in page:
            for block in blocks[:-1]:
                if block['type'] == 0:
                    all_content.append(block)

    value = []
    color = []
    most_color = 0
    minsize = 100000
    max = 0
    for block in all_content:
        for line in block['lines']:
            for span in line['spans']:
                value.append(float(span['size']))
                color.append(span['color'])
                span['text'] = re.sub('\t|\r', ' ', span['text']).strip()

    for item in value:
        if value.count(item) > max:
            minsize = item
            max = value.count(item)

    max = 0
    for item in color:
        if color.count(item) > max:
            most_color = item
            max = color.count(item)

    all_key = []
    all_key.extend(l)
    all_key.extend(other)
    break_all = False
    for block in all_content:
        for line in block['lines']:
            for span in line['spans']:
                for key in all_key:
                    if re.search(key.lower(), span['text'].lower()) and len(span['text'].split()) - len(
                            key.split()) <= 3:
                        if ((re.search('bold', span['font'].lower()) or span['text'].isupper() or span[
                            'color'] != most_color or span['flags'] >= 12) and span['size'] >= minsize - 0.3) or span[
                            'size'] > minsize + 1:
                            break_all = True
                            break
                if break_all:
                    break
            if break_all:
                break
        if break_all:
            end_index = all_content.index(block)
            break
        no_key_word.append(block)

    all_content = []
    for page in all_data:
        for blocks in page:
            for block in blocks[:-1]:
                if block['type'] == 0:
                    all_content.append(block)

    break_all = False
    most_size = []
    most_flags = []
    for block in all_content:
        if break_all:
            break
        for line in block['lines']:
            for span in line['spans']:
                for key in all_key:
                    if re.search(key.lower(), span['text'].lower()) and len(span['text'].split()) - len(
                            key.split()) <= 3:
                        if ((re.search('bold', span['font'].lower()) or span['text'].isupper() or span[
                            'color'] != most_color or span['flags'] >= 12) and span['size'] >= minsize - 0.3) or span[
                            'size'] > minsize + 1:
                            most_size.append(span['size'])
                            most_flags.append(span['flags'])
                            break
    max_count = 0
    key_size = 0
    for item in most_size:
        if max_count < most_size.count(item):
            key_size = item
            max_count = most_size.count(item)
    max_count = 0
    key_flags = 0
    for item in most_flags:
        if max_count < most_flags.count(item):
            key_flags = item
            max_count = most_flags.count(item)
    font = ''
    true = []
    check = False
    check_other = False
    key_span = []
    for block in all_content:

        if check_other:
            check = False
            check_other = False
        for key in other:
            if check_content_of_block(block, key, key_size, key_flags, minsize)[0]:
                if check and check_content_of_block(block, key, key_size, key_flags, minsize)[1]['font'] == font:
                    check_other = True
                    break

        if check is True and not check_other:
            if abs(block['bbox'][1] - true[-1]['lines'][-1]['bbox'][1]) <= 250:
                true.append(block)
                continue
            else:
                break

        for key in l:
            if check_content_of_block(block, key, key_size, key_flags, minsize)[0] and not check:
                key_span = check_content_of_block(block, key, key_size, key_flags, minsize)[1]
                size = key_span['size']
                font = key_span['font']
                true.append(block)
                check = True
                break
    maybe_infor = no_key_word
    check_profile_key = False
    if len(true) > 0 and keyword == 'Profile':
        break_point = False
        check_profile_key = True
        for multi_block in all_data[0]:
            break_point = False
            for item in multi_block:
                if break_point:
                    break
                if type(item) == dict:
                    spans = get_all_spans(item)
                    for span in spans:
                        if break_point:
                            break
                        for o in all_key:
                            if re.search(o, span['text'].lower()):
                                if key_size > minsize:
                                    if (span['flags'] >= key_flags or span['text'].isupper()) and span[
                                        'size'] >= key_size:
                                        break_point = True
                                        break
                                else:
                                    break_point = True
                                    break
                    if break_point:
                        continue
                    maybe_infor.append(item)
        maybe_infor.extend(true)
        true = maybe_infor
    if not check_profile_key:
        true = []
    if len(true) == 0 and keyword == 'Profile':
        true = query_infor_without_keyword(all_data, other, l, key_size, key_flags, minsize)
        no_key_word.extend(true)
        true = no_key_word

    if keyword != 'Profile':
        for block in true:
            for line in block['lines']:
                for span in line['spans']:
                    if span['text'] == '' or re.sub(' ', '', span['text']) == '':
                        line['spans'].remove(span)
    return true, key_span


with open('../Output/Profile.json', 'w+', encoding='utf-8') as fileSkill:
    json.dump(
        query_param_follow_keyword('Profile', pdf_reader('/home/juartaurus98/Sources/cv_by_Kien/Documents/1.pdf')[0])[
            0],
        fileSkill)
