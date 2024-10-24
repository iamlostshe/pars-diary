for x in range(32):
    for y in range(32):
        for z in range(32):
            if (x+y+z == 32) and (x*1+y*2+z*3==57) and (y-7==z):
                print(f'с одной лампочкой: {x}')
                print(f'с двумя лампочками: {y}')
                print(f'с тремя лампочками: {z}')