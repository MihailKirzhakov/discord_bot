label = '300'
while True:
    current_label = float(label.split()[0])
    if 300 <= current_label < 900:
        current_label += 100
        label = f'{current_label}'
    elif current_label == 900:
        current_label += 100
        label = f'{current_label / 1000}'
    else:
        current_label *= 1000
        current_label += 100
        label = f'{current_label / 1000}'