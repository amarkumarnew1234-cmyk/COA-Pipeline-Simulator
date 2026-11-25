from parser import parse_instruction
from pipeline import PipelineSimulator


program = [
    "LOAD R1, 0(R2)",
    "ADD R3, R4, R5",
    "SUB R6, R7, R8",
    "MUL R9, R10, R11",
    "ADD R12, R13, R14",
    "SUB R15, R3, R4"
]


def create_instructions():
    return [
        parse_instruction(text)
        for text in program
    ]


def run_test(shared_memory):
    instructions = create_instructions()

    simulator = PipelineSimulator(
        instructions,
        forwarding=True,
        shared_memory=shared_memory
    )

    simulator.run()

    print("\n")
    print("=" * 55)

    if shared_memory:
        print(
            "TEST: SHARED MEMORY - STRUCTURAL HAZARDS ENABLED"
        )
    else:
        print(
            "TEST: SEPARATE MEMORY - NO IF/MEM CONFLICT"
        )

    print("=" * 55)

    simulator.print_timing_table()
    simulator.print_hazard_report()

    return simulator


# ==========================================
# TEST 1: SEPARATE INSTRUCTION/DATA MEMORY
# ==========================================

separate_memory = run_test(False)


# ==========================================
# TEST 2: SHARED MEMORY
# ==========================================

shared_memory = run_test(True)


# ==========================================
# COMPARISON
# ==========================================

print(
    "\n========== STRUCTURAL HAZARD COMPARISON ==========\n"
)

print(
    f"{'Parameter':<28}"
    f"{'Separate':<12}"
    f"{'Shared':<12}"
)

print("-" * 52)

print(
    f"{'Execution Cycles':<28}"
    f"{len(separate_memory.history):<12}"
    f"{len(shared_memory.history):<12}"
)

print(
    f"{'Structural Hazards':<28}"
    f"{len(separate_memory.structural_hazards):<12}"
    f"{len(shared_memory.structural_hazards):<12}"
)

print(
    f"{'Structural Stall Cycles':<28}"
    f"{separate_memory.structural_stalls:<12}"
    f"{shared_memory.structural_stalls:<12}"
)