import json
import pandas as pd
from get_table_data import create_pages
from get_table_data import create_coord_dict


def main(table_cord_dict):
    try:
        with open("./jsonDump.txt","r") as f:
            jsonDump = f.read()
    except Exception as ex:
        print "Error: Make sure jsonDump.txt exists in current directory before running"
        exit()

    page_json = json.loads(jsonDump)

    matrix = {}
    for page_no, page in enumerate(page_json, start=1):
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

                                        if matrix[table_key][t] in ["VIA: ", "Endorsements "]:
                                            skip_table = True
                if not skip_table:
                    if table_cord_dict[table_key]['table_type'] == 2:
                        df = create_2d_data_frame(matrix, skip_table, table_key)
                        result_dict = {}
                        for elem in matrix[table_key]:
                            if elem[1] == 0 and elem[0] > 0:
                                result_dict[matrix[table_key][(elem[0],0)]] = {}
                            for elem2 in matrix[table_key]:
                                if elem[1] == 0 and elem[0] > 0 and elem2[0] == 0 and elem2[1] >0:
                                    result_dict[matrix[table_key][(elem[0],0)]].update({ matrix[table_key][(0,elem2[1])]: df[matrix[table_key][elem2]][matrix[table_key][elem]]})

                        print result_dict
                    else:
                        final_dict = create_1d_data_frame(matrix, skip_table, table_key)
                        print final_dict


def create_1d_data_frame(matrix, skip_table, table_key):
    if skip_table:
        return None
    else:
        final_dict = {}
        final_dict[matrix[table_key][(0, 0)]] = {}
        for elem in matrix[table_key]:
            for elem2 in matrix[table_key]:
                if ':' in matrix[table_key][(0, 0)]:
                    if elem[0] > 0 and elem[1] == 0 and elem2[1] == 1 and elem[0] == elem2[0]:
                        final_dict[matrix[table_key][(0, 0)]].update({matrix[table_key][elem]: matrix[table_key][(elem[0], 1)]})
                else:
                    if elem[1] == 0 and elem2[1] == 1 and elem[0] == elem2[0]:
                        final_dict[matrix[table_key][elem]] =\
                            matrix[table_key][(elem[0], 1)]

    return final_dict


def create_2d_data_frame(matrix, skip_table, table_key):
    df = None
    if skip_table:
        return None
    else:
        final_dict = {}
        for elem in matrix[table_key]:
            if elem[1] == 0 and elem[0] > 0:
                final_dict[matrix[table_key][(elem[0],0)]] = {}
            for elem2 in matrix[table_key]:
                if elem[0] > 0 and elem[1] == 0 and elem2[0] == 0 and elem2[1] > 0:
                    try:
                        final_dict[matrix[table_key][(elem[0],0)]][matrix[table_key][(0,elem2[1])]] = matrix[table_key][(elem[0], elem2[1])]
                    except Exception as exc:
                        pass
    if not skip_table:
        df = pd.DataFrame.from_dict(final_dict, orient='index').fillna(method='ffill')
    return df


if __name__ == '__main__':
    all_images = create_pages('KnoteBinder.pdf')
    for page_path in all_images:
        table_cord_dict = create_coord_dict(page_path)
        if table_cord_dict:
            main(table_cord_dict)
