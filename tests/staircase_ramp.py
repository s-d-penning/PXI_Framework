from src.daqmx.Voltage import VoltageSource, VoltageSensor
from nidaqmx.constants import TerminalConfiguration

import pandas as pd
import numpy as np

if __name__ == '__main__':
    vcc = VoltageSensor(input_channel='PXI_6251_0/ai1',
                        config=TerminalConfiguration.RSE,
                        max_voltage=10)
    print(vcc.voltage())

    vd = VoltageSensor(input_channel='PXI_6251_0/ai2',
                       config=TerminalConfiguration.DIFF,
                       max_voltage=10)
    print(vd.voltage())

    output_resolution_bits = 12
    input_resolution_bits = 16
    output_steps = 2**output_resolution_bits

    step_data = []
    max_voltage_output_data = []
    max_voltage_input_data = []
    output_resolution_data = []
    input_resolution_data = []
    set_voltage_data = []
    measured_output_voltage_data = []
    number_of_samples_data = []

    voltage_ranges = [0.1, 0.2, 0.5, 1.0, 2.0, 5, 10]

    size_1_data = []
    size_10_data = []
    size_100_data = []
    size_1000_data = []
    for v_out_max in voltage_ranges:
        input_ranges = [r for r in voltage_ranges if r >= v_out_max]
        for v_in_max in input_ranges:
            output_resolution = 20/(2**output_resolution_bits)
            input_resolution = (v_in_max * 2)/(2**input_resolution_bits)

            v_out = VoltageSource(output_channel='PXI_6713_0/ao0',
                                  input_channel='PXI_6251_0/ai0',
                                  max_voltage=v_out_max)

            output_steps = int(v_out_max/output_resolution)
            for step in range(-output_steps, output_steps, 1):

                set_voltage = step * output_resolution
                step_data.append(step)
                max_voltage_output_data.append(v_out_max)
                max_voltage_input_data.append(v_in_max)
                output_resolution_data.append(output_resolution)
                input_resolution_data.append(input_resolution)
                set_voltage_data.append(set_voltage)

                size_1_sample = v_out.set_output_voltage(set_voltage,sample_size=1)
                size_1_data.append(size_1_sample)

                size_10_sample = v_out.set_output_voltage(set_voltage, sample_size=10)
                size_10_data.append(size_10_sample)

                size_100_sample = v_out.set_output_voltage(set_voltage, sample_size=100)
                size_100_data.append(size_100_sample)

                size_1000_sample = v_out.set_output_voltage(set_voltage, sample_size=1000)
                size_1000_data.append(size_1000_sample)

                print(step, input_resolution, v_out_max)

    data_set = {'step': step_data,
                'set_voltage': set_voltage_data,
                'max_voltage_output': max_voltage_output_data,
                'max_voltage_input': max_voltage_input_data,
                'output_resolution': output_resolution_data,
                'input_resolution': input_resolution_data,
                'size_1': size_1_data,
                'size_10': size_10_data,
                'size_100': size_100_data,
                'size_1000': size_1000_data,}

    data_df = np.array(data_set)

    df = pd.DataFrame(data=data_set)
    df.to_csv("staircase.csv", mode='w', index_label='row')
