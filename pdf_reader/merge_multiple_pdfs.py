import glob
import os
import uuid
from pprint import pprint

import cv2
import fitz
import numpy as np


def SortBlocks(blocks):
    '''
    Sort the blocks of a TextPage in ascending vertical pixel order,
    then in ascending horizontal pixel order.
    This should sequence the text in a more readable form, at least by
    convention of the Western hemisphere: from top-left to bottom-right.
    If you need something else, change the sortkey variable accordingly ...
    '''

    sblocks = []
    for b in blocks:
        x0 = str(int(b["bbox"][0] + 0.99999)).rjust(4, "0")  # x coord in pixels
        y0 = str(int(b["bbox"][1] + 0.99999)).rjust(4, "0")  # y coord in pixels
        sortkey = y0 + x0  # = "yx"
        # print(x0 + " " + y0)
        sblocks.append([sortkey, b])

    sblocks.sort(key=lambda x: x[0], reverse=False)
    # print(sblocks[0][0])
    # print('\n')
    # pprint(sblocks)
    return [b[1] for b in sblocks]  # return sorted list of blocks


def SortLines(lines):
    ''' Sort the lines of a block in ascending vertical direction. See comment
    in SortBlocks function.
    '''
    slines = []
    for l in lines:
        y0 = str(int(l["bbox"][1] + 0.99999)).rjust(4, "0")
        slines.append([y0, l])
    slines.sort(key=lambda x: x[0], reverse=False)
    return [l[1] for l in slines]


def SortSpans(spans):
    ''' Sort the spans of a line in ascending horizontal direction. See comment
    in SortBlocks function.
    '''
    sspans = []
    for s in spans:
        x0 = str(int(s["bbox"][0] + 0.99999)).rjust(4, "0")
        sspans.append([x0, s])
    sspans.sort(key=lambda x: x[0], reverse=False)
    return [s[1] for s in sspans]


def pdf_reader(pdf_path):
    rand_str = str(uuid.uuid1())
    os.system('cd Merge_file && cd crop && mkdir %s' % rand_str)
    os.system('cd Merge_file && cd img_pdf && mkdir %s' % rand_str)

    doc = fitz.Document(pdf_path)
    pages = doc.pageCount
    (_, _, pg_w, pg_h) = doc[0].bound()
    pg_w = int(pg_w)
    pg_h = int(pg_h)
    cutout_list = [(0, pg_h)]
    all_block = []
    offset_top = 0
    for i in range(pages):
        # print(i)
        pg = doc.loadPage(i)  # load page number i
        pix = pg.getPixmap()
        pix.writePNG("Merge_file/img_pdf/%s/%s.png" % (rand_str, str(i)))

        text = pg.getText(output='dict')
        # print(pg.getText(output='text'))
        pgdict = text
        # pprint(pgdict)
        top = 0
        is_set_top = False
        if 'blocks' in pgdict:
            blocks = SortBlocks(pgdict["blocks"])  # now re-arrange ... blocks
            # pprint(blocks)
            for block in blocks:
                if 'lines' in block and not is_set_top:
                    flines = SortLines(block["lines"])  # ... lines
                    for line in flines:
                        if 'spans' in line and not is_set_top:
                            fspans = SortSpans(line["spans"])  # ... spans
                            for f in fspans:
                                if bool(f.get('text').strip()) and not is_set_top:
                                    top = int(f['bbox'][1])
                                    is_set_top = True
                                    # print(f.get('text'))
                                else:
                                    continue
                        else:
                            continue
                else:
                    continue

        last_span = ''
        is_set_bottom = False
        bottom = pg_h
        if 'blocks' in pgdict:
            blocks = SortBlocks(pgdict["blocks"])  # now re-arrange ... blocks
            blocks.reverse()
            for block in blocks:
                if 'lines' in block and not is_set_bottom:
                    flines = SortLines(block["lines"])  # ... lines
                    flines.reverse()
                    for line in flines:
                        if 'spans' in line and not is_set_bottom:
                            fspans = SortSpans(line["spans"])  # ... spans
                            fspans.reverse()
                            if len(fspans) == 1 and fspans[0].get('text').replace("Trang ", "").replace("Page ",
                                                                                                        "").strip().isdigit():
                                # print("ádfasdf")
                                continue
                            for f in fspans:
                                # print(f.get("text"))
                                if bool(f.get('text').strip()) and not is_set_bottom:
                                    bottom = int(f['bbox'][3])
                                    is_set_bottom = True
                                    last_span = f
                                else:
                                    continue
                        else:
                            continue
                else:
                    continue

        offset_page = 0
        if i < pages - 1:
            pg1 = doc.loadPage(i + 1)  # load page number i
            pgdict1 = pg1.getText(output='dict')  # create a dict out of it
            first_next_span = ''
            is_find_top = False
            if 'blocks' in pgdict1:
                blocks = SortBlocks(pgdict1["blocks"])  # now re-arrange ... blocks
                for block in blocks:
                    if 'lines' in block and not is_find_top:
                        flines = SortLines(block["lines"])  # ... lines
                        for line in flines:
                            if 'spans' in line and not is_find_top:
                                fspans = SortSpans(line["spans"])  # ... spans
                                for f in fspans:
                                    if bool(f.get('text').strip()) and not is_find_top:
                                        first_next_span = f
                                        is_find_top = True
                                    else:
                                        continue
                            else:
                                continue
                    else:
                        continue

            if bool(last_span) and bool(first_next_span):
                list_lines = []
                is_calculated = False
                if 'blocks' in pgdict:
                    blocks = SortBlocks(pgdict["blocks"])  # now re-arrange ... blocks
                    for block in blocks:
                        if 'lines' in block:
                            flines = SortLines(block["lines"])  # ... lines
                            list_lines.extend(flines)

                list_lines = SortLines(list_lines)
                list_lines.reverse()
                for l in range(len(list_lines) - 2):
                    if 'spans' in list_lines[l] and 'spans' in list_lines[l + 1]:
                        fspans1 = SortSpans(list_lines[l]["spans"])[0]  # ... spans
                        fspans2 = SortSpans(list_lines[l + 1]["spans"])[0]
                        if fspans2["size"] == last_span["size"] and fspans1["flags"] == last_span["flags"] and \
                                fspans2["font"] == last_span["font"] and fspans1["color"] == last_span["color"] and \
                                fspans1["size"] == first_next_span["size"] and fspans2["flags"] == first_next_span[
                            "flags"] and \
                                fspans1["font"] == first_next_span["font"] and fspans2["color"] == first_next_span[
                            "color"] and \
                                abs(fspans2['bbox'][0] - last_span["bbox"][0]) < 10 and abs(
                            fspans1['bbox'][0] - first_next_span["bbox"][0]) < 10 and \
                                offset_page == 0:
                            offset_page = list(fspans1["bbox"])[1] - list(fspans2["bbox"])[3]
                            is_calculated = True

                if not is_calculated:
                    list_lines.clear()
                    if 'blocks' in pgdict:
                        blocks = SortBlocks(pgdict1["blocks"])  # now re-arrange ... blocks
                        for block in blocks:
                            if 'lines' in block:
                                flines = SortLines(block["lines"])  # ... lines
                                list_lines.extend(flines)

                        list_lines = SortLines(list_lines)
                        for l in range(len(list_lines) - 2):
                            if 'spans' in list_lines[l] and 'spans' in list_lines[l + 1]:
                                fspans1 = SortSpans(list_lines[l]["spans"])[0]  # ... spans
                                fspans2 = SortSpans(list_lines[l + 1]["spans"])[0]
                                if fspans1["size"] == last_span["size"] and fspans1["flags"] == last_span["flags"] and \
                                        fspans1["font"] == last_span["font"] and fspans1["color"] == last_span[
                                    "color"] and \
                                        fspans2["size"] == first_next_span["size"] and fspans2["flags"] == \
                                        first_next_span["flags"] and \
                                        fspans2["font"] == first_next_span["font"] and fspans2["color"] == \
                                        first_next_span["color"] and \
                                        abs(fspans1['bbox'][0] - last_span["bbox"][0]) < 10 and abs(
                                    fspans2['bbox'][0] - first_next_span["bbox"][0]) < 10 and \
                                        offset_page == 0:
                                    offset_page = list(fspans2["bbox"])[1] - list(fspans1["bbox"])[3]
                                    is_calculated = True
            else:
                pass
                # print("Not ss")
        # print("Offset %s" % offset_page)

        occ = int((abs(offset_page) / 2))

        if i == pages - 1:
            bottom = pg_h
        else:
            bottom += occ

        if i == 0:
            top = 0
        else:
            top -= int(offset_top)
            offset_top = occ

        # print("Offset %s" %offset_page)
        # bottom += int(abs(offset_page))

        img = cv2.imread("Merge_file/img_pdf/" + rand_str + "/" + str(i) + ".png")

        # print(img)
        # 2/0
        crop_img = img[top:bottom, 0:pg_w]
        cv2.imwrite("Merge_file/crop/" + rand_str + "/" + str(i) + ".png", crop_img)
        cutout_list.append((top, bottom))
        offset = 0
        for x in range(1, i + 2):
            offset += cutout_list[x - 1][0] + (pg_h - cutout_list[x - 1][1])
        offset += cutout_list[x][0]
        for b in pgdict["blocks"]:
            added = False
            b["bbox"] = list(b["bbox"])
            b["bbox"][1] = b["bbox"][1] + i * pg_h - offset
            b["bbox"][3] = b["bbox"][3] + i * pg_h - offset
            # b["bbox"] = tuple(b["bbox"])
            if 'lines' in b:
                lines = b["lines"]  # ... lines
                for l in lines:
                    added = True
                    l["bbox"] = list(l["bbox"])
                    l["bbox"][1] = l["bbox"][1] + i * pg_h - offset
                    l["bbox"][3] = l["bbox"][3] + i * pg_h - offset
                    # l["bbox"] = tuple(l["bbox"])
                    if "spans" in l:
                        spans = l["spans"]  # ... spans
                        for s in spans:
                            s["bbox"] = list(s['bbox'])
                            s["bbox"][1] = s["bbox"][1] + i * pg_h - offset
                            s["bbox"][3] = s["bbox"][3] + i * pg_h - offset
                            # s["bbox"] = tuple(s['bbox'])
            if added:
                all_block.append(b)

    crop_imgs = glob.glob("Merge_file/crop/" + rand_str + "/*.png")
    # crop_imgs = [x.replace('\\', '/') for x in crop_imgs]
    crop_imgs = sorted(crop_imgs, key=lambda x: int(x.split('.')[0].rpartition("/")[2]))
    np_imgs = []
    for img in crop_imgs:
        np_imgs.append(cv2.imread(img))

    vis = np.concatenate(np_imgs, axis=0)

    cv2.imwrite('Merge_file/img_connector/' + rand_str + '.png', vis)

    return all_block, rand_str


pdf_reader('/home/juartaurus98/Sources/cv_by_Kien/Documents/2.pdf')
