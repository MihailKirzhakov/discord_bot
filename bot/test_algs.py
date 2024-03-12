label = '300'
while True:
    name = 'СтопарьВодяры'
    thousand = 'K'
    million = 'M'
    current_label = float(label[0])
    result = []
    if 300 <= current_label < 900:
        current_label += 100
        label = f'{int(current_label)} {thousand} {name}'


    # if 300 <= current_label < 900:
    #     current_label += 100
    #     label = f'{int(current_label)} {thousand} {name}'
    # elif current_label == 900:
    #     current_label += 100
    #     current_label /= 1000
    #     label = f'{round(current_label)} {million} {name}'
    # else:
    #     current_label += 0.1
    #     if current_label.is_integer():
    #         label = f'{round(current_label)} {million} {name}'
    #     else:
    #         label = f'{round(current_label, 1)} {million} {name}'