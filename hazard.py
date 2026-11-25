class HazardDetector:

    @staticmethod
    def get_source_registers(instruction):

        sources = []

        if instruction.source1 is not None:
            sources.append(instruction.source1)

        if instruction.source2 is not None:
            sources.append(instruction.source2)

        return sources

    @staticmethod
    def detect_data_hazards(instructions):

        hazards = []

        for consumer_index in range(len(instructions)):

            consumer = instructions[consumer_index]

            consumer_sources = (
                HazardDetector.get_source_registers(consumer)
            )

            for producer_index in range(consumer_index):

                producer = instructions[producer_index]

                destination = producer.destination

                if destination is None:
                    continue

                if destination in consumer_sources:

                    hazards.append({
                        "type": "DATA",
                        "producer": producer,
                        "consumer": consumer,
                        "register": destination,
                        "producer_index": producer_index,
                        "consumer_index": consumer_index
                    })

        return hazards