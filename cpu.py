class CPU:
    def __init__(self):

        # R0 to R15
        self.registers = {
            f"R{i}": 0
            for i in range(16)
        }

        # Simple simulated data memory
        self.memory = {}

    # ==========================================
    # REGISTER OPERATIONS
    # ==========================================

    def set_register(self, register, value):

        if register == "R0":
            return

        self.registers[register] = value

    def get_register(self, register):

        return self.registers[register]

    # ==========================================
    # MEMORY OPERATIONS
    # ==========================================

    def set_memory(self, address, value):

        self.memory[address] = value

    def get_memory(self, address):

        return self.memory.get(address, 0)

    # ==========================================
    # EXECUTE INSTRUCTION
    # ==========================================

    def execute(self, instruction):

        opcode = instruction.opcode

        # --------------------------------------
        # ADD
        # --------------------------------------

        if opcode == "ADD":

            value1 = self.get_register(
                instruction.source1
            )

            value2 = self.get_register(
                instruction.source2
            )

            result = value1 + value2

            self.set_register(
                instruction.destination,
                result
            )

            return {
                "type": "ALU",
                "operation": "ADD",
                "result": result
            }

        # --------------------------------------
        # SUB
        # --------------------------------------

        if opcode == "SUB":

            value1 = self.get_register(
                instruction.source1
            )

            value2 = self.get_register(
                instruction.source2
            )

            result = value1 - value2

            self.set_register(
                instruction.destination,
                result
            )

            return {
                "type": "ALU",
                "operation": "SUB",
                "result": result
            }

        # --------------------------------------
        # MUL
        # --------------------------------------

        if opcode == "MUL":

            value1 = self.get_register(
                instruction.source1
            )

            value2 = self.get_register(
                instruction.source2
            )

            result = value1 * value2

            self.set_register(
                instruction.destination,
                result
            )

            return {
                "type": "ALU",
                "operation": "MUL",
                "result": result
            }

        # --------------------------------------
        # LOAD
        # LOAD R1, 4(R2)
        # --------------------------------------

        if opcode == "LOAD":

            base = self.get_register(
                instruction.source1
            )

            address = (
                base
                + instruction.immediate
            )

            value = self.get_memory(
                address
            )

            self.set_register(
                instruction.destination,
                value
            )

            return {
                "type": "MEMORY",
                "operation": "LOAD",
                "address": address,
                "result": value
            }

        # --------------------------------------
        # STORE
        # STORE R1, 4(R2)
        # --------------------------------------

        if opcode == "STORE":

            value = self.get_register(
                instruction.source1
            )

            base = self.get_register(
                instruction.source2
            )

            address = (
                base
                + instruction.immediate
            )

            self.set_memory(
                address,
                value
            )

            return {
                "type": "MEMORY",
                "operation": "STORE",
                "address": address,
                "value": value
            }

        # --------------------------------------
        # BEQ
        # --------------------------------------

        if opcode == "BEQ":

            value1 = self.get_register(
                instruction.source1
            )

            value2 = self.get_register(
                instruction.source2
            )

            taken = value1 == value2

            return {
                "type": "BRANCH",
                "operation": "BEQ",
                "taken": taken,
                "label": instruction.label
            }

        raise ValueError(
            f"Cannot execute opcode: {opcode}"
        )

    # ==========================================
    # DISPLAY REGISTERS
    # ==========================================

    def print_registers(self):

        print(
            "\n========== REGISTER FILE ==========\n"
        )

        for i in range(16):

            register = f"R{i}"

            print(
                f"{register:<4} = "
                f"{self.registers[register]}"
            )

    # ==========================================
    # DISPLAY MEMORY
    # ==========================================

    def print_memory(self):

        print(
            "\n========== DATA MEMORY ==========\n"
        )

        if not self.memory:

            print("Memory is empty.")
            return

        for address in sorted(
            self.memory.keys()
        ):

            print(
                f"Address {address:<5} = "
                f"{self.memory[address]}"
            )