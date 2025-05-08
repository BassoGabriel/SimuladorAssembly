#instruções específica que precisa estar no código LI


# Funções aritméticas
def add(s1, s2, s3):
    s1 = s2 + s3
    return s1

def sub(s1, s2, s3):
    s1 = s2 - s3
    return s1

def addi(s1, s2):
    s1 = s2 + 20
    return s1


#conversores 
def hex_to_bin(hex_num):
    return bin(int(hex_num, 16))[2:].zfill(8)

