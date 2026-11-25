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

        # Stores which instruction was stalled in each cycle
        self.stall_history = []

        self.total_stalls = 0

        # Stores unique RAW hazards encountered
        self.data_hazards = []
        self._hazard_keys = set()

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

    def get_source_registers(self, instruction):
        sources = []

        if instruction is None:
            return sources

        if instruction.source1 is not None:
            sources.append(instruction.source1)

        if instruction.source2 is not None:
            sources.append(instruction.source2)

        return sources

    def detect_data_hazard(self):
        """
        Forwarding is OFF.

        The instruction in ID cannot proceed to EX if it needs
        a register that an instruction currently in EX or MEM
        is still going to write.

        We use a simplified register-file timing assumption:
        a value written in WB can be read by ID in that cycle.
        """

        consumer = self.pipeline["ID"]

        if consumer is None:
            return None

        sources = self.get_source_registers(consumer)

        for stage in ["EX", "MEM"]:
            producer = self.pipeline[stage]

            if producer is None:
                continue

            destination = producer.destination

            if destination is None:
                continue

            if destination in sources:
                return {
                    "producer": producer,
                    "consumer": consumer,
                    "register": destination,
                    "producer_stage": stage
                }

        return None

    def record_hazard(self, hazard):
        key = (
            id(hazard["producer"]),
            id(hazard["consumer"]),
            hazard["register"]
        )

        if key not in self._hazard_keys:
            self._hazard_keys.add(key)

            self.data_hazards.append({
                "producer": hazard["producer"],
                "consumer": hazard["consumer"],
                "register": hazard["register"]
            })

    def run_cycle(self):
        self.cycle += 1

        hazard = self.detect_data_hazard()

        if hazard is not None:
            self.total_stalls += 1
            self.record_hazard(hazard)

            # Older instructions continue moving forward.
            self.pipeline["WB"] = self.pipeline["MEM"]
            self.pipeline["MEM"] = self.pipeline["EX"]

            # Bubble inserted into EX.
            self.pipeline["EX"] = None

            # IF and ID are frozen.
            stalled_instruction = self.pipeline["ID"]

            self.history.append(self.pipeline.copy())
            self.stall_history.append(stalled_instruction)

            return

        # Normal pipeline movement
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

        self.history.append(self.pipeline.copy())
        self.stall_history.append(None)

    def run(self):
        while not self.finished():
            self.run_cycle()

        # Remove final completely empty cycle
        if self.history and all(
            value is None
            for value in self.history[-1].values()
        ):
            self.history.pop()
            self.stall_history.pop()
            self.cycle -= 1

        return self.history

    def print_timing_table(self):
        print("\n========== PIPELINE TIMING TABLE ==========\n")

        print(f"{'Instruction':<22}", end="")

        for cycle in range(1, len(self.history) + 1):
            print(f"C{cycle:<4}", end="")

        print()
        print("-" * (22 + len(self.history) * 5))

        for instruction in self.instructions:
            print(f"{str(instruction):<22}", end="")

            for cycle_index, state in enumerate(self.history):
                current_stage = ""

                if self.stall_history[cycle_index] is instruction:
                    current_stage = "ST"

                else:
                    for stage in self.STAGES:
                        if state[stage] is instruction:
                            current_stage = stage
                            break

                print(f"{current_stage:<5}", end="")

            print()

    def print_hazard_report(self):
        print("\n========== DATA HAZARD REPORT ==========\n")

        if not self.data_hazards:
            print("No RAW data hazards detected.")

        else:
            for number, hazard in enumerate(
                self.data_hazards,
                start=1
            ):
                print(f"Hazard {number}")
                print("  Type     : RAW (Read After Write)")
                print("  Producer :", hazard["producer"])
                print("  Consumer :", hazard["consumer"])
                print("  Register :", hazard["register"])
                print()

        print("Unique Data Hazards :", len(self.data_hazards))
        print("Total Stall Cycles  :", self.total_stalls)