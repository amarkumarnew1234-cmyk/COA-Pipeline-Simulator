from parser import parse_instruction
from pipeline import PipelineSimulator


program = [
    "LOAD R1, 0(R2)",
    "ADD R3, R1, R4",
    "SUB R5, R3, R6"
]


def create_instructions():
    return [
        parse_instruction(text)
        for text in program
    ]


def run_test(forwarding):

    instructions = create_instructions()

    simulator = PipelineSimulator(
        instructions,
        forwarding=forwarding
    )

    simulator.run()

    print("\n")
    print("=" * 50)

    if forwarding:
        print("TEST: FORWARDING ON")
    else:
        print("TEST: FORWARDING OFF")

    print("=" * 50)

    simulator.print_timing_table()
    simulator.print_hazard_report()

    return simulator


# ==========================================
# FORWARDING OFF
# ==========================================

without_forwarding = run_test(False)


# ==========================================
# FORWARDING ON
# ==========================================

with_forwarding = run_test(True)


# ==========================================
# COMPARISON
# ==========================================

print(
    "\n========== LOAD-USE COMPARISON ==========\n"
)

print(
    f"{'Parameter':<25}"
    f"{'OFF':<12}"
    f"{'ON':<12}"
)

print("-" * 49)

print(
    f"{'Execution Cycles':<25}"
    f"{len(without_forwarding.history):<12}"
    f"{len(with_forwarding.history):<12}"
)

print(
    f"{'Stall Cycles':<25}"
    f"{without_forwarding.total_stalls:<12}"
    f"{with_forwarding.total_stalls:<12}"
)

print(
    f"{'Data Hazards':<25}"
    f"{len(without_forwarding.data_hazards):<12}"
    f"{len(with_forwarding.data_hazards):<12}"
)