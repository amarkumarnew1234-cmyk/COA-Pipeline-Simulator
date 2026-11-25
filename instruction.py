class Instruction:
    def __init__(self, opcode, destination=None, source1=None,
                 source2=None, immediate=None, label=None,
                 original_text=""):

        self.opcode = opcode
        self.destination = destination
        self.source1 = source1
        self.source2 = source2
        self.immediate = immediate
        self.label = label
        self.original_text = original_text

    def __str__(self):
        return self.original_text