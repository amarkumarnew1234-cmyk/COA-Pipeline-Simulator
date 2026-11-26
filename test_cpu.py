from parser import parse_instruction
from cpu import CPU


cpu = CPU()


# ==========================================
# INITIAL REGISTER VALUES
# ==========================================

cpu.set_register("R1", 10)
cpu.set_register("R2", 20)
cpu.set_register("R3", 5)

cpu.set_register("R10", 100)


print("\n========== INITIAL CPU STATE ==========")

cpu.print_registers()


# ==========================================
# ARITHMETIC TEST
# ==========================================

print(
    "\n========== ARITHMETIC TEST ==========\n"
)


arithmetic_program = [
    "ADD R4, R1, R2",
    "SUB R5, R4, R3",
    "MUL R6, R5, R3"
]


for text in arithmetic_program:

    instruction = parse_instruction(text)

    result = cpu.execute(
        instruction
    )

    print(
        "Executed :",
        instruction
    )

    print(
        "Result   :",
        result
    )

    print()


# ==========================================
# STORE TEST
# ==========================================

print(
    "\n========== STORE TEST ==========\n"
)


store_instruction = parse_instruction(
    "STORE R6, 4(R10)"
)

store_result = cpu.execute(
    store_instruction
)

print(
    "Executed :",
    store_instruction
)

print(
    "Result   :",
    store_result
)


# ==========================================
# LOAD TEST
# ==========================================

print(
    "\n========== LOAD TEST ==========\n"
)


load_instruction = parse_instruction(
    "LOAD R7, 4(R10)"
)

load_result = cpu.execute(
    load_instruction
)

print(
    "Executed :",
    load_instruction
)

print(
    "Result   :",
    load_result
)


# ==========================================
# BRANCH TEST - TAKEN
# ==========================================

print(
    "\n========== BRANCH TEST: TAKEN ==========\n"
)


cpu.set_register("R8", 50)
cpu.set_register("R9", 50)


branch_taken = parse_instruction(
    "BEQ R8, R9, TARGET"
)

branch_taken_result = cpu.execute(
    branch_taken
)

print(
    "Executed :",
    branch_taken
)

print(
    "Result   :",
    branch_taken_result
)


# ==========================================
# BRANCH TEST - NOT TAKEN
# ==========================================

print(
    "\n========== BRANCH TEST: NOT TAKEN ==========\n"
)


cpu.set_register("R9", 60)


branch_not_taken = parse_instruction(
    "BEQ R8, R9, TARGET"
)

branch_not_taken_result = cpu.execute(
    branch_not_taken
)

print(
    "Executed :",
    branch_not_taken
)

print(
    "Result   :",
    branch_not_taken_result
)


# ==========================================
# FINAL STATE
# ==========================================

cpu.print_registers()

cpu.print_memory()