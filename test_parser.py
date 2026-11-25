from parser import parse_instruction


# ==========================================
# VALID INSTRUCTION TESTS
# ==========================================

test_instructions = [
    "ADD R1, R2, R3",
    "SUB R4, R1, R5",
    "MUL R6, R4, R2",
    "LOAD R7, 0(R1)",
    "STORE R7, 4(R1)",
    "BEQ R1, R2, LOOP"
]


print("\n========== VALID INSTRUCTIONS ==========\n")

for text in test_instructions:

    try:
        instruction = parse_instruction(text)

        print("Instruction :", instruction)
        print("Opcode      :", instruction.opcode)
        print("Destination :", instruction.destination)
        print("Source 1    :", instruction.source1)
        print("Source 2    :", instruction.source2)
        print("Immediate   :", instruction.immediate)
        print("Label       :", instruction.label)

        print("-" * 45)

    except ValueError as error:
        print("ERROR:", error)


# ==========================================
# INVALID INSTRUCTION TESTS
# ==========================================

invalid_instructions = [
    "ADD R1, R2",
    "ADD R20, R2, R3",
    "LOAD R1, ABC",
    "STORE R99, 4(R1)",
    "HELLO R1, R2, R3",
    ""
]


print("\n========== INVALID INSTRUCTIONS ==========\n")

for text in invalid_instructions:

    try:
        instruction = parse_instruction(text)

        print("Unexpectedly accepted:", instruction)

    except ValueError as error:

        print(
            f"{text!r:<25} -> ERROR: {error}"
        )