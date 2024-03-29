values = ['900K ПенаМонтажная', '300K ПенаМонтажная', '2.8M СтопарьВодяры', '1.5M СтопарьВодяры', '1.2M СтопарьВодяры']
sorted_values = sorted(values, reverse=True)
result = []
check = 0
for i in range(0, len(sorted_values)):
    if 'M' in sorted_values[i]:
        result.insert(0 + check, sorted_values[i])
        check += 1
    else:
        result.append(sorted_values[i])
message = '\n'.join([f'{i+1}. {val}' for i, val in enumerate(result)])
print(message)