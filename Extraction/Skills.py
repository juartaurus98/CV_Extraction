import json

START_SKILL_EXPAND = ['-', '+']
import re


# fileJs = open("../../pdf_reader/Skill.json", "r", encoding="utf-8")
#
# skill = json.load(fileJs)


def SortSpans(spans):
    ''' Sort the spans of a line in ascending horizontal direction. See comment
    in SortBlocks function.
    '''
    sspans = []
    for s in spans:
        x0 = str(int(s["bbox"][1] + 0.99999)).rjust(4, "0")
        sspans.append([x0, s])
    sspans.sort(key=lambda x: x[0], reverse=False)
    return [s[1] for s in sspans]


def skill_extraction(skill):
    skills = []
    # print(skill)
    for block in skill[0:]:
        for line in block['lines']:
            for span in line['spans']:
                skills.append(span)
                # print(span['text'])
    # print(skills)
    sk_tmp = skills

    for x in sk_tmp:
        if x.get('font') == 'FontAwesome':
            # print(x)
            skills.remove(x)

    # print(skills)
    if bool(skills):
        if skills[0] == skills[1]:
            skills = skills[2:]
        else:
            skills = skills[1:]
        skills = SortSpans(skills)
        size = {}
        flag = {}
        # color = {}
        font = {}
        for x in skills:
            size[x.get('size')] = size.get(x.get('size'), 0) + 1
            flag[x.get('flags')] = flag.get(x.get('flags'), 0) + 1
            font[x.get('font')] = font.get(x.get('font'), 0) + 1
            # color[x.get('color')] = color.get(x.get('color'), 0) + 1

        size = sorted(size.items(), reverse=True)
        flag = sorted(flag.items(), reverse=True)
        font = sorted(font.items(), key=lambda kv: kv[1])
        # color = sorted(color.items(), key=lambda kv: kv[1])
        check_size = True
        check_flag = True
        list_skills = []
        key_flag = flag[0][0]
        key_size = size[0][0]
        key_font = font[0][0]
        # key_color = color[0][0]
        # print(key_font)
        # print(key_flag)
        # print(key_size)
        for x in skills:
            if x.get('size') != key_size:
                check_size = False
                break
        if check_size is True:
            for x in skills:
                if x.get('flags') != key_flag:
                    check_flag = False
                    break
        check_font = True
        if check_flag is True and check_size is True:
            for x in skills:
                if x.get('font') != key_font:
                    check_font = False
                    break
        # print(skills)
        if check_size is False:
            des = False
            sk = False
            for x in skills:
                if x.get('text') in START_SKILL_EXPAND:
                    continue
                if x.get('size') == key_size and sk is False:
                    list_skills.append({'skill': x.get('text'), 'description': ''})
                    sk = True
                    des = False
                elif x.get('size') == key_size and sk is True:
                    list_skills[len(list_skills) - 1]['skill'] += " "
                    list_skills[len(list_skills) - 1]['skill'] += x.get('text')
                    des = False
                elif x.get('size') < key_size and des is False:
                    sk = False
                    des = True
                    list_skills[len(list_skills) - 1]['description'] += x.get('text')
                else:
                    sk = True
                    list_skills[len(list_skills) - 1]['description'] += ' '
                    list_skills[len(list_skills) - 1]['description'] += x.get('text')
        elif check_flag is False:
            des = False
            sk = False
            for x in skills:
                print(x)
                if x.get('text') in START_SKILL_EXPAND:
                    continue
                if x.get('flags') == key_flag and sk is False:
                    list_skills.append({'skill': x.get('text'), 'description': ''})
                    sk = True
                    des = False
                elif x.get('flags') == key_flag and sk is True:
                    list_skills[len(list_skills) - 1]['skill'] += " "
                    list_skills[len(list_skills) - 1]['skill'] += x.get('text')
                    des = False
                elif x.get('flags') != key_flag and des is False:
                    sk = False
                    des = True
                    list_skills[len(list_skills) - 1]['description'] += x.get('text')
                else:
                    sk = False
                    list_skills[len(list_skills) - 1]['description'] += ' '
                    list_skills[len(list_skills) - 1]['description'] += x.get('text')
        elif check_font is False:
            des = False
            sk = False
            for x in skills:
                if x.get('text') in START_SKILL_EXPAND:
                    break
                if x.get('font') == key_font and sk is False:
                    list_skills.append({'skill': x.get('text'), 'description': ''})
                    sk = True
                    des = False
                elif x.get('font') == key_font and sk is True:
                    list_skills[len(list_skills) - 1]['skill'] += " "
                    list_skills[len(list_skills) - 1]['skill'] += x.get('text')
                    des = False
                elif x.get('font') != key_font and des is False:
                    sk = False
                    des = True
                    list_skills[len(list_skills) - 1]['description'] += x.get('text')
                else:
                    sk = False
                    list_skills[len(list_skills) - 1]['description'] += ' '
                    list_skills[len(list_skills) - 1]['description'] += x.get('text')
        else:
            check_first = ''
            check_last = False
            for x in skills:
                des = False
                if not list_skills:
                    if x.get('text')[0] in START_SKILL_EXPAND:
                        check_first = x.get('text')[0]
                    elif x.get('text')[0].isupper():
                        check_first = '0'
                    if bool(re.search(':', x.get('text'))):
                        if bool(re.search(':$', x.get('text'))):
                            list_skills.append({'skill': str(x.get('text').split(':', 1)[0]), 'description': []})
                            check_last = True
                        else:
                            list_skills.append({'skill': str(x.get('text').split(':', 1)[0]), 'description': []})
                            list_skills.append({'skill': str(x.get('text').split(':', 1)[0]),
                                                'description': str(x.get('text').split(':', 1)[1])})
                    else:
                        list_skills.append({'skill': x.get('text'), 'description': []})
                elif x.get('text')[0] in START_SKILL_EXPAND:
                    if x.get('text')[0] == check_first:
                        list_skills.append({'skill': x.get('text'), 'description': []})
                    else:
                        list_skills[len(list_skills) - 1]['description'] += ' '
                        list_skills[len(list_skills) - 1]['description'] += x.get('text')
                elif x.get('text').isupper():
                    if check_first in START_SKILL_EXPAND:
                        list_skills[len(list_skills) - 1]['skill'] += " "
                        list_skills[len(list_skills) - 1]['skill'] += x.get('text')
                    else:
                        list_skills.append({'skill': x.get('text'), 'description': ''})

        return list_skills
    else:
        return "Skills none"
