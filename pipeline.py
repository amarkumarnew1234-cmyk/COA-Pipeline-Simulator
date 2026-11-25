class PipelineSimulator:

    STAGES = ["IF", "ID", "EX", "MEM", "WB"]

    def __init__(self, instructions, forwarding=False):

        self.instructions = instructions
        self.forwarding = forwarding

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
        self.stall_history = []

        self.total_stalls = 0

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

    def find_dependencies(self):

        consumer = self.pipeline["ID"]

        if consumer is None:
            return []

        sources = self.get_source_registers(consumer)

        dependencies = []

        for stage in ["EX", "MEM"]:

            producer = self.pipeline[stage]

            if producer is None:
                continue

            destination = producer.destination

            if destination is None:
                continue

            if destination in sources:

                dependencies.append({
                    "producer": producer,
                    "consumer": consumer,
                    "register": destination,
                    "producer_stage": stage
                })

        return dependencies

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

    def should_stall(self, dependencies):

        if not dependencies:
            return False

        # -----------------------------------
        # FORWARDING OFF
        # -----------------------------------

        if not self.forwarding:

            return True

        # -----------------------------------
        # FORWARDING ON
        # -----------------------------------
        #
        # ALU results can be forwarded.
        #
        # LOAD data is available only after
        # the MEM stage. Therefore a consumer
        # immediately behind a LOAD must stall
        # while LOAD is in EX.
        # -----------------------------------

        for dependency in dependencies:

            producer = dependency["producer"]
            producer_stage = dependency["producer_stage"]

            if (
                producer.opcode == "LOAD"
                and producer_stage == "EX"
            ):
                return True

        return False

    def run_cycle(self):

        self.cycle += 1

        dependencies = self.find_dependencies()

        # Record dependencies even if forwarding
        # prevents a stall.
        for dependency in dependencies:
            self.record_hazard(dependency)

        stall_required = self.should_stall(
            dependencies
        )

        if stall_required:

            self.total_stalls += 1

            # Older instructions continue.
            self.pipeline["WB"] = self.pipeline["MEM"]
            self.pipeline["MEM"] = self.pipeline["EX"]

            # Bubble inserted into EX.
            self.pipeline["EX"] = None

            # IF and ID remain frozen.
            stalled_instruction = self.pipeline["ID"]

            self.history.append(
                self.pipeline.copy()
            )

            self.stall_history.append(
                stalled_instruction
            )

            return

        # -----------------------------------
        # NORMAL PIPELINE MOVEMENT
        # -----------------------------------

        self.pipeline["WB"] = self.pipeline["MEM"]
        self.pipeline["MEM"] = self.pipeline["EX"]
        self.pipeline["EX"] = self.pipeline["ID"]
        self.pipeline["ID"] = self.pipeline["IF"]

        if self.next_instruction < len(self.instructions):

            self.pipeline["IF"] = self.instructions[
                self.next_instruction
            ]

            self.next_instruction += 1

        else:

            self.pipeline["IF"] = None

        self.history.append(
            self.pipeline.copy()
        )

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

        print(
            "\n========== PIPELINE TIMING TABLE ==========\n"
        )

        print(
            f"Forwarding: "
            f"{'ON' if self.forwarding else 'OFF'}\n"
        )

        print(
            f"{'Instruction':<22}",
            end=""
        )

        for cycle in range(
            1,
            len(self.history) + 1
        ):

            print(
                f"C{cycle:<4}",
                end=""
            )

        print()

        print(
            "-" * (
                22
                + len(self.history) * 5
            )
        )

        for instruction in self.instructions:

            print(
                f"{str(instruction):<22}",
                end=""
            )

            for cycle_index, state in enumerate(
                self.history
            ):

                current_stage = ""

                if (
                    self.stall_history[cycle_index]
                    is instruction
                ):

                    current_stage = "ST"

                else:

                    for stage in self.STAGES:

                        if (
                            state[stage]
                            is instruction
                        ):

                            current_stage = stage
                            break

                print(
                    f"{current_stage:<5}",
                    end=""
                )

            print()

    def print_hazard_report(self):

        print(
            "\n========== DATA HAZARD REPORT ==========\n"
        )

        print(
            "Forwarding:",
            "ON" if self.forwarding else "OFF"
        )

        print()

        if not self.data_hazards:

            print(
                "No RAW data hazards detected."
            )

        else:

            for number, hazard in enumerate(
                self.data_hazards,
                start=1
            ):

                print(
                    f"Hazard {number}"
                )

                print(
                    "  Type     : "
                    "RAW (Read After Write)"
                )

                print(
                    "  Producer :",
                    hazard["producer"]
                )

                print(
                    "  Consumer :",
                    hazard["consumer"]
                )

                print(
                    "  Register :",
                    hazard["register"]
                )

                print()

        print(
            "Unique Data Hazards :",
            len(self.data_hazards)
        )

        print(
            "Total Stall Cycles  :",
            self.total_stalls
        )

        print(
            "Total Execution Cycles :",
            len(self.history)
        )