import cv2

img = cv2.imread('/home/amarpreet/nlp/KnoteBinder1.png')
curr_height, curr_width = img.shape[:2]
org_height = 792
org_width = 612
width_ratio = round(org_width / float(curr_width),2)
height_ratio = round(org_height / float(curr_height),2)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

ret, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

# thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
#             cv2.THRESH_BINARY,11,2)

contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)



lt = len(contours)

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
        # if len(approx)== 4 and hierarchy[0][index][2] == -1:
        #     print (point_x, point_y, point_x + width, point_y + height)
        if len(approx) >= 4:
            if hierarchy[0][index][3] > 0:
                coordinates.append((point_x, point_y,
                                    point_x + width, point_y + height))
            elif hierarchy[0][index][3] == 0:
                table_coordinates.append((point_x, point_y,
                                         point_x + width, point_y + height))

round_off = 5

table_dict = {}
for tab_cord in table_coordinates:
    for cell_coord in coordinates:
        if tab_cord[0] < cell_coord[0] + round_off and tab_cord[1] < cell_coord[1] + round_off and tab_cord[2] > cell_coord[2] - round_off and tab_cord[3] > cell_coord[3] - round_off:
            if tab_cord in table_dict:
                table_dict[tab_cord]['cell'].append(cell_coord)
            else:
                table_dict.update({tab_cord: {'cell':[cell_coord]}})

table_dict_cpy = table_dict.copy()

#remove table with 1 cell

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
    print "left",left
    table_dict[table_key]['left_cells'] = []

    for cell in table:
        if cell[0] == left_min:
            table_dict[table_key]['left_cells'].append(cell)
    print "top", top
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

print table_dict

img = cv2.resize(img, (612, 792))
for cord in coordinates:
    cv2.rectangle(img,(cord[0],cord[1]),(cord[2],cord[3]),(0,255,0),3)
cv2.imwrite('output1.png',img)

