from parser import parse_instruction
from pipeline import PipelineSimulator


program = [
    "ADD R1, R2, R3",
    "SUB R4, R5, R6",
    "MUL R7, R8, R9"
]


instructions = [
    parse_instruction(text)
    for text in program
]


simulator = PipelineSimulator(instructions)

history = simulator.run()


print("\n========== PIPELINE EXECUTION ==========\n")


for cycle_number, state in enumerate(history, start=1):

    print(f"Cycle {cycle_number}")

    for stage in PipelineSimulator.STAGES:

        instruction = state[stage]

        if instruction is None:
            print(f"  {stage:<4}: EMPTY")

        else:
            print(f"  {stage:<4}: {instruction}")

    print()


simulator.print_timing_table()