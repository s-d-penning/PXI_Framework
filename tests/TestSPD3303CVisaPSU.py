from src.pyvisa.Power import PowerChannel, VoltageSource, CurrentSource

if __name__ == '__main__':
    with PowerChannel() as p:
        p.set_channel_power_on("CH1")
        p.set_channel_power_off("CH1")
        p.set_channel_power_on("CH2")
        p.set_channel_power_off("CH2")
        p.set_channel_power_on("CH3")
        p.set_channel_power_off("CH3")

    p = None

    with PowerChannel() as p:
        p.set_channel_power_on("CH1")
        p.set_channel_power_on("CH2")
        p.set_channel_power_on("CH3")

    p = None

    output_voltages = [1.0, 0.5, 0.0, 0.5, 1.0]
    with VoltageSource() as p:
        p.set_channel_power_on("CH1")
        for output_voltage in output_voltages:
            p.set_channel_voltage("CH1", output_voltage)
        p.set_channel_power_off("CH1")

        p.set_channel_power_on("CH2")
        for output_voltage in output_voltages:
            p.set_channel_voltage("CH2", output_voltage)
        p.set_channel_power_off("CH2")

    p = None

    # output_voltages = [round((v/100)*6.4,2) for v in range(101)]
    output_voltages = [0,1] * 100
    with VoltageSource() as p:
        p.set_channel_power_on("CH1")
        for output_voltage in output_voltages:
            # print(output_voltage)
            p.set_channel_voltage("CH1", output_voltage)
        print(p.delay)

    p = None

    # output_voltages = [round((v/100)*6.4,2) for v in range(101)]
    output_currents = [round((v / 100) * 3.1, 2) for v in range(101)]
    with CurrentSource() as p:
        p.set_channel_power_on("CH1")
        for output_current in output_currents:
            print(output_current)
            p.set_channel_current("CH1", output_current)
        print(p.delay)

    p = None