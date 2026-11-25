import re
from instruction import Instruction

ARITHMETIC_OPS = {"ADD", "SUB", "MUL"}
MEMORY_OPS = {"LOAD", "STORE"}
BRANCH_OPS = {"BEQ"}

VALID_REGISTERS = {f"R{i}" for i in range(16)}

def validate_register(register):
    register = register.upper()

    if register not in VALID_REGISTERS:
        raise ValueError(
            f"Invalid register '{register}'. Valid registers are R0 to R15."
        )

    return register


def parse_instruction(text):
    original_text = text.strip()

    if not original_text:
        raise ValueError("Instruction cannot be empty.")

    # ---------------------------------
    # Separate opcode from operands
    # ---------------------------------

    first_split = original_text.split(maxsplit=1)

    opcode = first_split[0].upper()

    operands_text = first_split[1] if len(first_split) > 1 else ""

    operands = [
        operand.strip()
        for operand in operands_text.split(",")
        if operand.strip()
    ]

    # =================================
    # ARITHMETIC INSTRUCTIONS
    # ADD R1, R2, R3
    # SUB R4, R1, R5
    # MUL R6, R4, R2
    # =================================

    if opcode in ARITHMETIC_OPS:

        if len(operands) != 3:
            raise ValueError(
                f"{opcode} requires 3 registers: "
                f"{opcode} destination, source1, source2"
            )

        destination = validate_register(operands[0])
        source1 = validate_register(operands[1])
        source2 = validate_register(operands[2])

        return Instruction(
            opcode=opcode,
            destination=destination,
            source1=source1,
            source2=source2,
            original_text=original_text
        )

    # =================================
    # LOAD
    # Example: LOAD R7, 4(R1)
    # =================================

    if opcode == "LOAD":

        if len(operands) != 2:
            raise ValueError(
                "LOAD format: LOAD destination, offset(base)"
            )

        destination = validate_register(operands[0])

        match = re.fullmatch(
            r"(-?\d+)\((R\d+)\)",
            operands[1].upper()
        )

        if not match:
            raise ValueError(
                "Invalid LOAD address. Example: LOAD R7, 4(R1)"
            )

        immediate = int(match.group(1))
        base_register = validate_register(match.group(2))

        return Instruction(
            opcode=opcode,
            destination=destination,
            source1=base_register,
            immediate=immediate,
            original_text=original_text
        )

    # =================================
    # STORE
    # Example: STORE R7, 4(R1)
    # =================================

    if opcode == "STORE":

        if len(operands) != 2:
            raise ValueError(
                "STORE format: STORE source, offset(base)"
            )

        value_register = validate_register(operands[0])

        match = re.fullmatch(
            r"(-?\d+)\((R\d+)\)",
            operands[1].upper()
        )

        if not match:
            raise ValueError(
                "Invalid STORE address. Example: STORE R7, 4(R1)"
            )

        immediate = int(match.group(1))
        base_register = validate_register(match.group(2))

        return Instruction(
            opcode=opcode,
            source1=value_register,
            source2=base_register,
            immediate=immediate,
            original_text=original_text
        )

    # =================================
    # BRANCH
    # Example: BEQ R1, R2, LOOP
    # =================================

    if opcode == "BEQ":

        if len(operands) != 3:
            raise ValueError(
                "BEQ format: BEQ register1, register2, label"
            )

        source1 = validate_register(operands[0])
        source2 = validate_register(operands[1])

        label = operands[2].upper()

        if not label:
            raise ValueError("Branch label cannot be empty.")

        return Instruction(
            opcode=opcode,
            source1=source1,
            source2=source2,
            label=label,
            original_text=original_text
        )

    raise ValueError(
        f"Unsupported instruction '{opcode}'."
    )