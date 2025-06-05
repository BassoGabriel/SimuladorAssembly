Config_CPU=[ 20GHZ, I=1, J=2, R=1 ]

main:
lw $t0, 0($s0)
lw $t1, 4($s0)
add $t2, $t0, $t1
sw $t2, 8($s0)
