from random import randint


values = ['Стопарь', 'Аня']
result = dict()

for i in values:
    rand_value = randint(1, 100)
    result[i] = rand_value

message = '\n'.join([f'{key} - {val}' for key, val in result.items()])

print(message)
