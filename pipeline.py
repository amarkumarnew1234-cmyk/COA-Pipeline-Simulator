class PipelineSimulator:

    STAGES = ["IF", "ID", "EX", "MEM", "WB"]

    def __init__(
        self,
        instructions,
        forwarding=False,
        shared_memory=False
    ):
        self.instructions = instructions
        self.forwarding = forwarding
        self.shared_memory = shared_memory

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
        self.data_stalls = 0
        self.structural_stalls = 0

        self.data_hazards = []
        self.structural_hazards = []

        self._data_hazard_keys = set()
        self._structural_hazard_cycles = set()

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

    def find_data_dependencies(self):
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

    def record_data_hazard(self, hazard):
        key = (
            id(hazard["producer"]),
            id(hazard["consumer"]),
            hazard["register"]
        )

        if key not in self._data_hazard_keys:
            self._data_hazard_keys.add(key)

            self.data_hazards.append({
                "producer": hazard["producer"],
                "consumer": hazard["consumer"],
                "register": hazard["register"]
            })

    def should_data_stall(self, dependencies):
        if not dependencies:
            return False

        if not self.forwarding:
            return True

        for dependency in dependencies:
            producer = dependency["producer"]
            producer_stage = dependency["producer_stage"]

            # LOAD-use hazard:
            # data is not ready early enough when LOAD is in EX.
            if (
                producer.opcode == "LOAD"
                and producer_stage == "EX"
            ):
                return True

        return False

    def memory_resource_busy(self):
        """
        In shared-memory mode, a LOAD or STORE using the MEM
        stage occupies the same memory resource needed by IF.
        """

        if not self.shared_memory:
            return False

        memory_instruction = self.pipeline["MEM"]

        if memory_instruction is None:
            return False

        return memory_instruction.opcode in {
            "LOAD",
            "STORE"
        }

    def record_structural_hazard(self, instruction):
        if self.cycle in self._structural_hazard_cycles:
            return

        self._structural_hazard_cycles.add(self.cycle)

        self.structural_hazards.append({
            "cycle": self.cycle,
            "memory_instruction": instruction
        })

    def run_cycle(self):
        self.cycle += 1

        # ==========================================
        # DATA HAZARD CHECK
        # ==========================================

        dependencies = self.find_data_dependencies()

        for dependency in dependencies:
            self.record_data_hazard(dependency)

        data_stall_required = self.should_data_stall(
            dependencies
        )

        if data_stall_required:
            self.total_stalls += 1
            self.data_stalls += 1

            self.pipeline["WB"] = self.pipeline["MEM"]
            self.pipeline["MEM"] = self.pipeline["EX"]

            # Bubble in EX
            self.pipeline["EX"] = None

            # IF and ID freeze
            stalled_instruction = self.pipeline["ID"]

            self.history.append(
                self.pipeline.copy()
            )

            self.stall_history.append(
                stalled_instruction
            )

            return

        # ==========================================
        # CHECK STRUCTURAL HAZARD
        # BEFORE NORMAL MOVEMENT
        # ==========================================

        structural_conflict = (
            self.memory_resource_busy()
            and
            self.next_instruction < len(self.instructions)
        )

        memory_instruction = self.pipeline["MEM"]

        # ==========================================
        # NORMAL MOVEMENT OF EXISTING INSTRUCTIONS
        # ==========================================

        self.pipeline["WB"] = self.pipeline["MEM"]
        self.pipeline["MEM"] = self.pipeline["EX"]
        self.pipeline["EX"] = self.pipeline["ID"]
        self.pipeline["ID"] = self.pipeline["IF"]

        # ==========================================
        # FETCH
        # ==========================================

        if structural_conflict:
            # IF cannot access shared memory this cycle.
            self.pipeline["IF"] = None

            self.total_stalls += 1
            self.structural_stalls += 1

            self.record_structural_hazard(
                memory_instruction
            )

        elif self.next_instruction < len(
            self.instructions
        ):
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
            "Forwarding   :",
            "ON" if self.forwarding else "OFF"
        )

        print(
            "Shared Memory:",
            "ON" if self.shared_memory else "OFF"
        )

        print()

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
            "\n========== HAZARD REPORT ==========\n"
        )

        print(
            "Forwarding   :",
            "ON" if self.forwarding else "OFF"
        )

        print(
            "Shared Memory:",
            "ON" if self.shared_memory else "OFF"
        )

        # ------------------------------------------
        # DATA HAZARDS
        # ------------------------------------------

        print(
            "\n--- DATA HAZARDS ---\n"
        )

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
                    f"Data Hazard {number}"
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

        # ------------------------------------------
        # STRUCTURAL HAZARDS
        # ------------------------------------------

        print(
            "\n--- STRUCTURAL HAZARDS ---\n"
        )

        if not self.structural_hazards:
            print(
                "No structural hazards detected."
            )

        else:
            for number, hazard in enumerate(
                self.structural_hazards,
                start=1
            ):
                print(
                    f"Structural Hazard {number}"
                )

                print(
                    "  Cycle    :",
                    hazard["cycle"]
                )

                print(
                    "  Resource : Shared Memory"
                )

                print(
                    "  MEM uses :",
                    hazard["memory_instruction"]
                )

                print(
                    "  Effect   : Instruction fetch stalled"
                )

                print()

        print(
            "Unique Data Hazards   :",
            len(self.data_hazards)
        )

        print(
            "Structural Hazards    :",
            len(self.structural_hazards)
        )

        print(
            "Data Stall Cycles     :",
            self.data_stalls
        )

        print(
            "Structural Stall Cycles:",
            self.structural_stalls
        )

        print(
            "Total Stall Cycles    :",
            self.total_stalls
        )

        print(
            "Total Execution Cycles:",
            len(self.history)
        )