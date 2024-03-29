result = ['1.5M СтопарьВодяры', '900K ПенаМонтажная', '300K ПенаМонтажная', '2.8M СтопарьВодяры']
values = [label for label in result]
message = '\n'.join([f'{i+1}. {val}' for i, val in enumerate(values)])
print(message)
