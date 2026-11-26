from program import Program


program_lines = [

    "ADD R1, R2, R3",

    "BEQ R1, R4, TARGET",

    "SUB R5, R6, R7",

    "MUL R8, R9, R10",

    "TARGET:",

    "ADD R11, R12, R13",

    "STORE R11, 0(R14)"
]


program = Program(
    program_lines
)


program.print_program()


print(
    "\n========== BRANCH TARGET TEST ==========\n"
)


target_index = program.get_target_index(
    "TARGET"
)


print(
    "TARGET points to instruction index:",
    target_index
)


print(
    "Instruction at TARGET:",
    program.instructions[target_index]
)