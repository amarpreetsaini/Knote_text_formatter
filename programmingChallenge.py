import json
import pandas as pd
try:
    with open("./jsonDump.txt","r") as f:
        jsonDump = f.read()
except Exception as ex:
    print "Error: Make sure jsonDump.txt exists in current directory before running"
    exit()

page_json = json.loads(jsonDump)
coords = [(78, 710, 133, 729), (106, 711, 131, 728), (103, 539, 533, 652), (335, 637, 433, 649), (254, 637, 334, 649), (104, 637, 253, 649), (335, 623, 433, 635), (254, 623, 334, 635), (104, 623, 253, 635), (335, 594, 433, 621), (254, 594, 334, 621), (104, 594, 253, 621), (434, 569, 532, 649), (335, 569, 433, 593), (254, 569, 334, 593), (104, 569, 253, 593), (434, 540, 532, 566), (335, 540, 433, 566), (254, 540, 334, 566), (104, 540, 253, 566), (120, 130, 544, 219), (362, 190, 543, 218), (291, 190, 361, 218), (170, 190, 289, 218), (121, 190, 169, 218), (362, 160, 543, 188), (291, 160, 361, 188), (170, 160, 289, 188), (121, 160, 169, 188), (362, 131, 543, 159), (291, 131, 361, 159), (170, 131, 289, 159), (121, 131, 169, 159), (101, 71, 144, 110), (104, 67, 146, 106)]

table_cord_dict = {(103, 539, 533, 652): {'header_cells': [(434, 540, 532, 566), (335, 540, 433, 566), (254, 540, 334, 566), (104, 540, 253, 566)], 'top': [540, 569, 594, 623, 637], 'cell': [(335, 637, 433, 649), (254, 637, 334, 649), (104, 637, 253, 649), (335, 623, 433, 635), (254, 623, 334, 635), (104, 623, 253, 635), (335, 594, 433, 621), (254, 594, 334, 621), (104, 594, 253, 621), (434, 569, 532, 649), (335, 569, 433, 593), (254, 569, 334, 593), (104, 569, 253, 593), (434, 540, 532, 566), (335, 540, 433, 566), (254, 540, 334, 566), (104, 540, 253, 566)], 'left_cells': [(104, 637, 253, 649), (104, 623, 253, 635), (104, 594, 253, 621), (104, 569, 253, 593), (104, 540, 253, 566)], 'page_no': 1, 'table_type': 2, 'columns': {434: [(434, 569, 532, 649), (434, 540, 532, 566)], 254: [(254, 637, 334, 649), (254, 623, 334, 635), (254, 594, 334, 621), (254, 569, 334, 593), (254, 540, 334, 566)], 335: [(335, 637, 433, 649), (335, 623, 433, 635), (335, 594, 433, 621), (335, 569, 433, 593), (335, 540, 433, 566)]}, 'left': [104, 254, 335, 434]}, (120, 130, 544, 219): {'header_cells': [(362, 131, 543, 159), (291, 131, 361, 159), (170, 131, 289, 159), (121, 131, 169, 159)], 'top': [131, 160, 190, 199], 'cell': [(362, 190, 543, 218), (369, 199, 533, 210), (291, 190, 361, 218), (170, 190, 289, 218), (121, 190, 169, 218), (362, 160, 543, 188), (291, 160, 361, 188), (170, 160, 289, 188), (121, 160, 169, 188), (362, 131, 543, 159), (291, 131, 361, 159), (170, 131, 289, 159), (121, 131, 169, 159)], 'left_cells': [(121, 190, 169, 218), (121, 160, 169, 188), (121, 131, 169, 159)], 'page_no': 1, 'table_type': 2, 'columns': {369: [(369, 199, 533, 210)], 170: [(170, 190, 289, 218), (170, 160, 289, 188), (170, 131, 289, 159)], 291: [(291, 190, 361, 218), (291, 160, 361, 188), (291, 131, 361, 159)], 362: [(362, 190, 543, 218), (362, 160, 543, 188), (362, 131, 543, 159)]}, 'left': [121, 170, 291, 362, 369]}}



matrix = {}
for page_no, page in enumerate(page_json, start=1):
    #import pdb;pdb.set_trace()
    print page_no
    for table_key in table_cord_dict:
        if page_no == table_cord_dict[table_key]['page_no']:
            table_values = table_cord_dict[table_key]
            table = table_values['cell']
            left = table_values['left']
            top = table_values['top']
            skip_table = False

            round_off = 5
            matrix[table_key] = {}
            for child in page['blocks']:
                for line in child['lines']:
                    for span in line['spans']:
                        #we encode to ascii to ignore strange unicode characters.
                        #if you need them for some purpose, you can remove the
                        #'.encode()' call and replace it.
                        current_text = span['text'].encode('ascii',errors='ignore')
                        current_bbox = span['bbox']
                        for coord in table:
                            if current_bbox[0] > (coord[0] - round_off) and current_bbox[1] > (coord[1] - round_off) and current_bbox[2] < (coord[2] + round_off) and current_bbox[3] < (coord[3] + round_off):
                                x, y = 0, 0
                                for l in left:
                                    if l == coord[0]: y = left.index(l)
                                for t in top:
                                    if t == coord[1]: x = top.index(t)

                                t = x, y
                                if t in matrix[table_key]:
                                    matrix[table_key][t] += current_text
                                else:
                                    matrix[table_key][t] = current_text

                                    if matrix[table_key][t] == "VIA: ":
                                        skip_table = True

            final_dict = {}
            if table_cord_dict[table_key]['table_type'] == 2:
                print skip_table
                for elem in matrix[table_key]:
                    if skip_table:
                        continue
                    else:
                        if elem[0] > 0:
                            if matrix[table_key][(elem[0],0)] not in final_dict:
                                final_dict[matrix[table_key][(elem[0],0)]] = {}
                        for elem2 in matrix[table_key]:
                            if elem[0] > 0 and elem[1] == 0 and elem2[0] == 0 and elem2[1] > 0:
                                try:
                                    final_dict[matrix[table_key][(elem[0],0)]][matrix[table_key][(0,elem2[1])]] = matrix[table_key][(elem[0], elem2[1])]
                                except Exception as exc:
                                    pass
                if not skip_table:
                    df = pd.DataFrame.from_dict(final_dict, orient='index').fillna(method='ffill')
                    print df