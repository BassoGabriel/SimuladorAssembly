main:
lw $t0, valor1
lw $t1, valor2
beq $t0, $t1, igual
add $t2, $t0, $t1
j fim
igual:
sub $t2, $t0, $t1
fim:
sw $t2, resultado
