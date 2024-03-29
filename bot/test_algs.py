values = ['1.5M СтопарьВодяры', '900K ПенаМонтажная', '300K ПенаМонтажная', '2.8M СтопарьВодяры']
sorted_values = sorted(values, reverse=True)
result = []
while len(result) < len(values):
    for i in range(0, len(values) - 1):
        if 'M' in sorted_values[i]:
            result.append(sorted_values[i])
            sorted_values.pop(i)
            if 'K' in sorted_values[i]:
                result.append(sorted_values[i])
        continue
    

