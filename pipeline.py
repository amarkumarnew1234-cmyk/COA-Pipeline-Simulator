class PipelineSimulator:

    STAGES = ["IF", "ID", "EX", "MEM", "WB"]

    def __init__(self, instructions):
        self.instructions = instructions

        self.pipeline = {
            "IF": None,
            "ID": None,
            "EX": None,
            "MEM": None,
            "WB": None
        }

        self.next_instruction = 0
        self.cycle = 0
        self.history = []

    def pipeline_empty(self):
        return all(
            instruction is None
            for instruction in self.pipeline.values()
        )

    def finished(self):
        return (
            self.next_instruction >= len(self.instructions)
            and self.pipeline_empty()
        )

    def run_cycle(self):

        self.cycle += 1

        # Move instructions to the next pipeline stage
        self.pipeline["WB"] = self.pipeline["MEM"]
        self.pipeline["MEM"] = self.pipeline["EX"]
        self.pipeline["EX"] = self.pipeline["ID"]
        self.pipeline["ID"] = self.pipeline["IF"]

        # Fetch next instruction
        if self.next_instruction < len(self.instructions):

            self.pipeline["IF"] = self.instructions[
                self.next_instruction
            ]

            self.next_instruction += 1

        else:
            self.pipeline["IF"] = None

        # Store current pipeline state
        self.history.append(self.pipeline.copy())

    def run(self):

        while not self.finished():
            self.run_cycle()

        # Remove the final completely empty cycle
        if self.history and all(
            value is None
            for value in self.history[-1].values()
        ):
            self.history.pop()
            self.cycle -= 1

        return self.history

    def print_timing_table(self):

        print("\n========== PIPELINE TIMING TABLE ==========\n")

        # Print cycle headings
        print(f"{'Instruction':<22}", end="")

        for cycle in range(1, len(self.history) + 1):
            print(f"C{cycle:<4}", end="")

        print()

        print("-" * (22 + len(self.history) * 5))

        # Print pipeline stages for every instruction
        for instruction in self.instructions:

            print(f"{str(instruction):<22}", end="")

            for state in self.history:

                current_stage = ""

                for stage in self.STAGES:

                    if state[stage] is instruction:
                        current_stage = stage
                        break

                print(f"{current_stage:<5}", end="")

            print()