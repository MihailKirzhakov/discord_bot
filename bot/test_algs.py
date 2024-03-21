label = str(round(int(1000000) / 1000))
while True:
    thousand = 'K'
    million = 'M'
    original_label = label.split()
    current_label = float(original_label[0])
    if 300 <= current_label < 900:
        current_label += 100
        label = f'{int(current_label)} {thousand} СтопарьВодяры'
    elif current_label >= 900:
        current_label += 100
        current_label /= 1000
        label = f'{round(current_label)} {million} СтопарьВодяры'
    else:
        current_label += 0.1
        if current_label.is_integer():
            label = f'{round(current_label)} {million} СтопарьВодяры'
        else:
            label = f'{round(current_label, 1)} {million} СтопарьВодяры'
