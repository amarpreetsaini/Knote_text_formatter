import cv2
from ghostscript.ghostscript import gs_pdf_to_png
import glob


def create_pages(file_name):
    gs_pdf_to_png(file_name, '300')
    for file in glob.glob(file_name[:-4] + '*.png'):
        all_images = [file for file in glob.glob('*.png')]
    print all_images


def create_coord_dict(page_path):
    img = cv2.imread(page_path)
    curr_height, curr_width = img.shape[:2]
    org_height = 792
    org_width = 612
    width_ratio = round(org_width / float(curr_width), 2)
    height_ratio = round(org_height / float(curr_height), 2)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(thresh,
                                           cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)

    coordinates = []
    table_coordinates = []

    for index, cnt in enumerate(contours):
        if cv2.contourArea(cnt) > 10000:
            [point_x, point_y, width, height] = cv2.boundingRect(cnt)
            point_x = int(point_x * width_ratio)
            width = int(width * width_ratio)
            point_y = int(point_y * height_ratio)
            height = int(height * height_ratio)
            approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)
            if len(approx) >= 4:
                if hierarchy[0][index][3] > 0:
                    coordinates.append((point_x, point_y,
                                        point_x + width, point_y + height))
                elif hierarchy[0][index][3] == 0:
                    table_coordinates.append((point_x, point_y,
                                              point_x + width,
                                              point_y + height))

    round_off = 5

    table_dict = {}
    for tab_cord in table_coordinates:
        for cell_coord in coordinates:
            if tab_cord[0] < cell_coord[0] + round_off and tab_cord[1] < cell_coord[1] + round_off and tab_cord[2] > cell_coord[2] - round_off and tab_cord[3] > cell_coord[3] - round_off:
                if tab_cord in table_dict:
                    table_dict[tab_cord]['cell'].append(cell_coord)
                else:
                    table_dict.update({tab_cord: {'cell': [cell_coord]}})

    table_dict_cpy = table_dict.copy()

    for tab_items in table_dict_cpy.values():
        if len(tab_items['cell']) == 1:
            del table_dict[tab_items]

    print table_dict

    table_dict_cpy = table_dict.copy()

    for table_key in table_dict_cpy:
        table = table_dict_cpy[table_key]['cell']
        top = [cell[1] for cell in table]
        top = list(set(top))
        top.sort()
        header_top = min(list(set(top)))
        table_dict[table_key]['header_cells'] = []
        for cell in table:
            if cell[1] == header_top:
                print cell
                table_dict[table_key]['header_cells'].append(cell)

        left = [cell[0] for cell in table]
        left = list(set(left))
        left.sort()
        left_min = min(list(set(left)))

        table_dict[table_key].update({'left': left})

        table_dict[table_key]['left_cells'] = []

        for cell in table:
            if cell[0] == left_min:
                table_dict[table_key]['left_cells'].append(cell)
        print "top", top
        table_dict[table_key].update({'top': top})

        table_dict[table_key]['columns'] = {}
        for left_cell in left:
            if left_cell == left_min:
                continue
            else:
                i = 1
                for cell in table:
                    if cell[0] == left_cell:
                        i += 1
                        if left_cell in table_dict[table_key]['columns']:
                            table_dict[table_key]['columns'][left_cell].append(cell)
                        else:
                            table_dict[table_key]['columns'].update({left_cell:[cell]})
                            table_dict[table_key]['columns'][left_cell].sort()
        if len(left) > 2:
            print "table is 2d"
            table_type = 2
        else:
            print "table is 1D"
            table_type = 1

        table_dict[table_key]['table_type'] = table_type
        table_dict[table_key]['page_no'] = 1

        return table_dict


if __name__ == '__main__':
    all_images = create_pages('/home/amarpreet/nlp/KnoteBinder.pdf')
    for page_path in all_images:
        print page_path
        table_dict = create_coord_dict(page_path)
        print table_dict
