from cpu import CPU


class PipelineSimulator:

    STAGES = ["IF", "ID", "EX", "MEM", "WB"]

    def __init__(
        self,
        program,
        forwarding=True,
        shared_memory=False
    ):
        self.program = program
        self.instructions = program.instructions

        self.forwarding = forwarding
        self.shared_memory = shared_memory

        self.cpu = CPU()

        # Program Counter = instruction index
        self.pc = 0

        self.pipeline = {
            "IF": None,
            "ID": None,
            "EX": None,
            "MEM": None,
            "WB": None
        }

        self.cycle = 0

        # Complete cycle-by-cycle history
        self.history = []

        # Which instruction was stalled in each cycle
        self.stall_history = []

        # Instructions flushed in each cycle
        # Example:
        # [
        #     [],
        #     [],
        #     [instruction1, instruction2],
        #     ...
        # ]
        self.flush_history = []

        # ------------------------------------------
        # Hazard statistics
        # ------------------------------------------

        self.data_hazards = []
        self.structural_hazards = []
        self.control_hazards = []

        self._data_hazard_keys = set()
        self._structural_hazard_cycles = set()
        self._executed_instructions = set()
        self._resolved_branches = set()

        self.data_stalls = 0
        self.structural_stalls = 0
        self.control_penalty = 0

        self.completed_instructions = 0

        # Execution log
        self.execution_log = []

    # ==============================================
    # BASIC PIPELINE STATE
    # ==============================================

    def pipeline_empty(self):

        return all(
            instruction is None
            for instruction in self.pipeline.values()
        )

    def program_finished(self):

        return (
            self.pc >= len(self.instructions)
            and self.pipeline_empty()
        )

    # ==============================================
    # REGISTER / MEMORY INITIALIZATION
    # ==============================================

    def set_register(self, register, value):

        self.cpu.set_register(
            register,
            value
        )

    def set_memory(self, address, value):

        self.cpu.set_memory(
            address,
            value
        )

    # ==============================================
    # SOURCE REGISTERS
    # ==============================================

    def get_source_registers(
        self,
        instruction
    ):

        sources = []

        if instruction is None:
            return sources

        if instruction.source1 is not None:
            sources.append(
                instruction.source1
            )

        if instruction.source2 is not None:
            sources.append(
                instruction.source2
            )

        return sources

    # ==============================================
    # DATA HAZARDS
    # ==============================================

    def find_data_dependencies(self):

        consumer = self.pipeline["ID"]

        if consumer is None:
            return []

        sources = self.get_source_registers(
            consumer
        )

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

    def record_data_hazard(
        self,
        dependency
    ):

        key = (
            id(dependency["producer"]),
            id(dependency["consumer"]),
            dependency["register"]
        )

        if key in self._data_hazard_keys:
            return

        self._data_hazard_keys.add(key)

        self.data_hazards.append({
            "producer":
                dependency["producer"],

            "consumer":
                dependency["consumer"],

            "register":
                dependency["register"]
        })

    def should_data_stall(
        self,
        dependencies
    ):

        if not dependencies:
            return False

        # Without forwarding:
        # consumer waits while producer is
        # still in EX or MEM.
        if not self.forwarding:
            return True

        # With forwarding:
        # ordinary ALU dependencies can forward.
        # Immediate LOAD-use still needs one stall.
        for dependency in dependencies:

            producer = dependency["producer"]

            producer_stage = dependency[
                "producer_stage"
            ]

            if (
                producer.opcode == "LOAD"
                and producer_stage == "EX"
            ):
                return True

        return False

    # ==============================================
    # STRUCTURAL HAZARD
    # ==============================================

    def memory_resource_busy(self):

        if not self.shared_memory:
            return False

        instruction = self.pipeline["MEM"]

        if instruction is None:
            return False

        return instruction.opcode in {
            "LOAD",
            "STORE"
        }

    # ==============================================
    # EXECUTION
    # ==============================================

    def execute_instruction(
        self,
        instruction
    ):

        if instruction is None:
            return None

        key = id(instruction)

        if key in self._executed_instructions:
            return None

        result = self.cpu.execute(
            instruction
        )

        self._executed_instructions.add(
            key
        )

        self.execution_log.append({
            "cycle": self.cycle,
            "instruction": instruction,
            "result": result
        })

        return result

    # ==============================================
    # BRANCH RESOLUTION
    # ==============================================

    def resolve_branch(self):

        branch = self.pipeline["EX"]

        if branch is None:
            return None

        if branch.opcode != "BEQ":
            return None

        branch_key = id(branch)

        if branch_key in self._resolved_branches:
            return None

        self._resolved_branches.add(
            branch_key
        )

        result = self.execute_instruction(
            branch
        )

        if result is None:
            return None

        taken = result["taken"]

        # ------------------------------------------
        # BRANCH NOT TAKEN
        # ------------------------------------------

        if not taken:

            self.control_hazards.append({
                "cycle": self.cycle,
                "branch": branch,
                "taken": False,
                "target": branch.label,
                "flushed": 0,
                "flushed_instructions": []
            })

            return {
                "taken": False,
                "flushed_instructions": []
            }

        # ------------------------------------------
        # BRANCH TAKEN
        # ------------------------------------------

        target_index = (
            self.program.get_target_index(
                branch.label
            )
        )

        flushed_instructions = []

        if self.pipeline["ID"] is not None:
            flushed_instructions.append(
                self.pipeline["ID"]
            )

        if self.pipeline["IF"] is not None:
            flushed_instructions.append(
                self.pipeline["IF"]
            )

        flushed_count = len(
            flushed_instructions
        )

        self.control_hazards.append({
            "cycle": self.cycle,
            "branch": branch,
            "taken": True,
            "target": branch.label,
            "target_index": target_index,
            "flushed": flushed_count,
            "flushed_instructions":
                flushed_instructions.copy()
        })

        self.control_penalty += (
            flushed_count
        )

        # Redirect Program Counter
        self.pc = target_index

        # Remove wrong-path younger instructions
        self.pipeline["ID"] = None
        self.pipeline["IF"] = None

        return {
            "taken": True,
            "flushed_instructions":
                flushed_instructions
        }

    # ==============================================
    # FETCH
    # ==============================================

    def fetch_instruction(self):

        if self.pc >= len(
            self.instructions
        ):
            return None

        instruction = (
            self.instructions[self.pc]
        )

        self.pc += 1

        return instruction

    # ==============================================
    # ONE CLOCK CYCLE
    # ==============================================

    def run_cycle(self):

        self.cycle += 1

        # Every cycle starts with no flush.
        flushed_this_cycle = []

        # ------------------------------------------
        # 1. RESOLVE BRANCH CURRENTLY IN EX
        # ------------------------------------------

        branch_result = (
            self.resolve_branch()
        )

        if (
            branch_result is not None
            and branch_result["taken"]
        ):

            flushed_this_cycle = (
                branch_result[
                    "flushed_instructions"
                ]
            )

            # Older instructions continue.
            self.pipeline["WB"] = (
                self.pipeline["MEM"]
            )

            self.pipeline["MEM"] = (
                self.pipeline["EX"]
            )

            self.pipeline["EX"] = None

            # ID and IF were flushed by
            # resolve_branch().

            # Immediately fetch from correct target.
            self.pipeline["IF"] = (
                self.fetch_instruction()
            )

            self.history.append(
                self.pipeline.copy()
            )

            self.stall_history.append(
                None
            )

            self.flush_history.append(
                flushed_this_cycle.copy()
            )

            return

        # ------------------------------------------
        # 2. DATA HAZARD
        # ------------------------------------------

        dependencies = (
            self.find_data_dependencies()
        )

        for dependency in dependencies:

            self.record_data_hazard(
                dependency
            )

        if self.should_data_stall(
            dependencies
        ):

            self.data_stalls += 1

            # Older instructions continue.
            self.pipeline["WB"] = (
                self.pipeline["MEM"]
            )

            self.pipeline["MEM"] = (
                self.pipeline["EX"]
            )

            # Bubble inserted into EX.
            self.pipeline["EX"] = None

            # IF and ID remain frozen.
            stalled_instruction = (
                self.pipeline["ID"]
            )

            self.history.append(
                self.pipeline.copy()
            )

            self.stall_history.append(
                stalled_instruction
            )

            self.flush_history.append(
                []
            )

            return

        # ------------------------------------------
        # 3. STRUCTURAL HAZARD
        # ------------------------------------------

        structural_conflict = (
            self.memory_resource_busy()
            and
            self.pc < len(self.instructions)
        )

        memory_instruction = (
            self.pipeline["MEM"]
        )

        # ------------------------------------------
        # 4. COMPLETE WB
        # ------------------------------------------

        if self.pipeline["WB"] is not None:

            self.completed_instructions += 1

        # ------------------------------------------
        # 5. MOVE PIPELINE
        # ------------------------------------------

        self.pipeline["WB"] = (
            self.pipeline["MEM"]
        )

        self.pipeline["MEM"] = (
            self.pipeline["EX"]
        )

        self.pipeline["EX"] = (
            self.pipeline["ID"]
        )

        self.pipeline["ID"] = (
            self.pipeline["IF"]
        )

        # ------------------------------------------
        # 6. EXECUTE NEW EX INSTRUCTION
        # ------------------------------------------

        ex_instruction = (
            self.pipeline["EX"]
        )

        if (
            ex_instruction is not None
            and
            ex_instruction.opcode != "BEQ"
        ):

            self.execute_instruction(
                ex_instruction
            )

        # ------------------------------------------
        # 7. FETCH
        # ------------------------------------------

        if structural_conflict:

            self.pipeline["IF"] = None

            self.structural_stalls += 1

            if (
                self.cycle
                not in
                self._structural_hazard_cycles
            ):

                self._structural_hazard_cycles.add(
                    self.cycle
                )

                self.structural_hazards.append({
                    "cycle": self.cycle,
                    "memory_instruction":
                        memory_instruction
                })

        else:

            self.pipeline["IF"] = (
                self.fetch_instruction()
            )

        # ------------------------------------------
        # 8. SAVE CYCLE STATE
        # ------------------------------------------

        self.history.append(
            self.pipeline.copy()
        )

        self.stall_history.append(
            None
        )

        self.flush_history.append(
            []
        )

    # ==============================================
    # RUN COMPLETE PROGRAM
    # ==============================================

    def run(self):

        while not self.program_finished():

            self.run_cycle()

        # Remove final completely empty state.
        if self.history and all(
            value is None
            for value
            in self.history[-1].values()
        ):

            self.history.pop()

            self.stall_history.pop()

            self.flush_history.pop()

            self.cycle -= 1

        return self.history

    # ==============================================
    # TIMING TABLE
    # ==============================================

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
            f"{'Instruction':<24}",
            end=""
        )

        for cycle in range(
            1,
            len(self.history) + 1
        ):

            print(
                f"C{cycle:<5}",
                end=""
            )

        print()

        print(
            "-" * (
                24
                + len(self.history) * 6
            )
        )

        for instruction in self.instructions:

            print(
                f"{str(instruction):<24}",
                end=""
            )

            for index, state in enumerate(
                self.history
            ):

                stage_name = ""

                # Flush gets highest display priority.
                if (
                    instruction
                    in self.flush_history[index]
                ):

                    stage_name = "FL"

                elif (
                    self.stall_history[index]
                    is instruction
                ):

                    stage_name = "ST"

                else:

                    for stage in self.STAGES:

                        if (
                            state[stage]
                            is instruction
                        ):

                            stage_name = stage
                            break

                print(
                    f"{stage_name:<6}",
                    end=""
                )

            print()

    # ==============================================
    # EXECUTION LOG
    # ==============================================

    def print_execution_log(self):

        print(
            "\n========== EXECUTION LOG ==========\n"
        )

        for entry in self.execution_log:

            print(
                f"Cycle {entry['cycle']}: "
                f"{entry['instruction']}"
            )

            print(
                "  Result:",
                entry["result"]
            )

    # ==============================================
    # HAZARD REPORT
    # ==============================================

    def print_hazard_report(self):

        print(
            "\n========== HAZARD REPORT ==========\n"
        )

        print(
            "Data Hazards       :",
            len(self.data_hazards)
        )

        print(
            "Structural Hazards :",
            len(self.structural_hazards)
        )

        print(
            "Control Hazards    :",
            len(self.control_hazards)
        )

        print(
            "Data Stall Cycles  :",
            self.data_stalls
        )

        print(
            "Structural Stalls  :",
            self.structural_stalls
        )

        print(
            "Control Penalty    :",
            self.control_penalty
        )

        print()

        if self.control_hazards:

            print(
                "--- CONTROL HAZARD DETAILS ---\n"
            )

            for number, hazard in enumerate(
                self.control_hazards,
                start=1
            ):

                print(
                    f"Branch {number}:",
                    hazard["branch"]
                )

                print(
                    "  Taken   :",
                    hazard["taken"]
                )

                print(
                    "  Target  :",
                    hazard["target"]
                )

                print(
                    "  Flushed :",
                    hazard["flushed"]
                )

                if (
                    hazard[
                        "flushed_instructions"
                    ]
                ):

                    print(
                        "  Flushed Instructions:"
                    )

                    for instruction in (
                        hazard[
                            "flushed_instructions"
                        ]
                    ):

                        print(
                            "    -",
                            instruction
                        )

                print()