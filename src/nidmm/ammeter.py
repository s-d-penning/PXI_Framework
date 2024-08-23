import nidmm


class Ammeter:
    def __init__(self, resource_name: str):
        self.session = nidmm.Session(resource_name=resource_name)
        self.session.configure_measurement_digits(measurement_function=nidmm.Function.DC_CURRENT,
                                                  range=0.02,
                                                  resolution_digits=6.5)


if __name__ == '__main__':
    ammeter = Ammeter(resource_name='PXI4::10::INSTR')


