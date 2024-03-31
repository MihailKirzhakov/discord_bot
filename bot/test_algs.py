button_mentions = {
    'ПенаМонтажная': '@ПенаМонтажная',
    'СтопарьВодяры': '@СтопарьВодяры',
}
values = ['1.2M СтопарьВодяры', '1.8M СтопарьВодяры', '2.5M СтопарьВодяры', '300K ПенаМонтажная', '900K ПенаМонтажная', '800K']
def convert_to_mention(values):
    result = []
    for value in values:
        split_value = value.split()
        if len(split_value) > 1:
            split_value[-1] = button_mentions[split_value[-1]]
            result.append(' '.join(split_value))
        else:
            result.append('Лот не был выкуплен')
    return result
convert_label_values = convert_to_mention(values)
sorted_values = sorted(convert_label_values, reverse=False)
result = []
check = 0
for i in range(0, len(sorted_values)):
    if 'M' in sorted_values[i]:
        result.insert(0, sorted_values[i])
        check += 1
    elif 'K' in sorted_values[i]:
        result.insert(check, sorted_values[i])
    else:
        result.append(sorted_values[i])
message = '\n'.join([f'{i+1}. {val}' for i, val in enumerate(result)])
print(message)