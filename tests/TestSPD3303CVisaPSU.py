from src.pyvisa.Power import PowerChannel, VoltageSource, CurrentSource

import time

if __name__ == '__main__':
    with PowerChannel() as p1:
        p1.set_channel_power_on("CH1")
        p1.set_channel_power_off("CH1")
        p1.set_channel_power_on("CH2")
        p1.set_channel_power_off("CH2")
        p1.set_channel_power_on("CH3")
        p1.set_channel_power_off("CH3")

    p1 = None

    with PowerChannel() as p2:
        p2.set_channel_power_on("CH1")
        p2.set_channel_power_on("CH2")
        p2.set_channel_power_on("CH3")

    p2 = None

    output_voltages = [1.0, 0.5, 0.0, 0.5, 1.0]
    with VoltageSource() as p3:
        p3.set_channel_power_on("CH1")
        for output_voltage in output_voltages:
            p3.set_channel_voltage("CH1", output_voltage)
        p3.set_channel_power_off("CH1")

        p3.set_channel_power_on("CH2")
        for output_voltage in output_voltages:
            p3.set_channel_voltage("CH2", output_voltage)
        p3.set_channel_power_off("CH2")

    p3 = None

    output_voltages = [round((v/100)*6.4,2) for v in range(101)]
    # output_voltages = [0,1] * 100
    with VoltageSource() as p4:
        p4.set_channel_power_on("CH1")
        for output_voltage in output_voltages:
            # print(output_voltage)
            start = time.perf_counter()
            p4.set_channel_voltage("CH1", output_voltage)
            end = time.perf_counter()
            elapsed = end - start
            print(f'Voltage: Time taken: {elapsed:.6f} seconds')
        print(p4.delay)

    p4 = None

    # output_voltages = [round((v/100)*6.4,2) for v in range(101)]
    output_currents = [round((v / 100) * 3.1, 2) for v in range(101)]
    with CurrentSource() as p5:
        p5.set_channel_power_on("CH1")
        for output_current in output_currents:
            # print(output_current)
            start = time.perf_counter()
            p5.set_channel_current("CH1", output_current)
            end = time.perf_counter()
            elapsed = end - start
            print(f'Current: Time taken: {elapsed:.6f} seconds')
        print(p5.delay)

