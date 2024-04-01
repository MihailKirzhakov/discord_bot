from decimal import Decimal

label = '800K'
while True:
    bid_step = 500000
    name = 'СтопарьВодяры'
    original_label = Decimal(label.split()[0][:-1])
    if len(label.split()) == 1:
        if 'K' in label:
            label = f'{original_label}K {name}'
        else:
            label = f'{original_label}M {name}'
    else:    
        if 'K' in label:
            if original_label < 900 and (original_label + (Decimal(bid_step) / Decimal('1000'))) < 1000:
                label = f'{original_label + (Decimal(bid_step) / Decimal('1000'))}K {name}'
            else:
                label = f'{(original_label + (Decimal(bid_step) / Decimal('1000'))) / Decimal('1000')}M {name}'
        else:
            label = f'{original_label + (Decimal(bid_step) / Decimal('1000000'))}M {name}'