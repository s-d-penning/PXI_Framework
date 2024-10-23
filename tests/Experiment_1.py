from src.pyvisa.Power import PowerChannel, VoltageSource, CurrentSource

import nidaqmx, time, pandas as pd
from nidaqmx.constants import AcquisitionType, READ_ALL_AVAILABLE

if __name__ == '__main__':
    """
    1. Increment the current in the peltier cell by 100mA at a time from 0 to 1.5 A and allow the cell to cool for 10 seconds
    2. For 10 seconds, measure the Ambient, Case, Cold-plate temperatures and the Peltier currents and Voltages.
    """

    output_currents = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5]
    v_ambient = []
    v_case = []
    v_plate = []
    v_shunt = []
    v_peltier = []
    data = []
    with CurrentSource() as current_source, nidaqmx.Task() as task:
        current_source.set_channel_power_on("CH1")
        current_source.set_channel_power_on("CH2")
        current_source.set_channel_current("CH2", 0.33)
        current_source.set_channel_power_on("CH3")

        task.ai_channels.add_ai_voltage_chan(physical_channel="PXI_6251_1/ai0", name_to_assign_to_channel="Ambient", min_val = -1, max_val = 1)
        task.ai_channels.add_ai_voltage_chan(physical_channel="PXI_6251_1/ai1", name_to_assign_to_channel="Case", min_val = -1, max_val = 1)
        task.ai_channels.add_ai_voltage_chan(physical_channel="PXI_6251_1/ai2", name_to_assign_to_channel="Plate", min_val = -1, max_val = 1)
        task.ai_channels.add_ai_voltage_chan(physical_channel="PXI_6251_1/ai3", name_to_assign_to_channel="Shunt", min_val = -0.5, max_val = 0.5)
        task.ai_channels.add_ai_voltage_chan(physical_channel="PXI_6251_1/ai4", name_to_assign_to_channel="Peltier", min_val = -10, max_val = 10)

        sample_rate = 100  # samples per second
        sample_duration = 10  # seconds
        number_of_samples = sample_duration * sample_rate

        task.timing.cfg_samp_clk_timing(rate=sample_rate, sample_mode=AcquisitionType.FINITE, samps_per_chan=number_of_samples)

        for output_current in output_currents:
            print(output_current)
            task.start()
            current_source.set_channel_current("CH1", output_current)
            data = task.read(number_of_samples_per_channel=number_of_samples)
            task.stop()
            v_ambient.extend(data[0])
            v_case.extend(data[1])
            v_plate.extend(data[2])
            v_shunt.extend(data[3])
            v_peltier.extend(data[4])

    df = pd.DataFrame({'v_ambient': v_ambient,'v_case': v_case, 'v_plate': v_plate, 'v_shunt': v_shunt, 'v_peltier': v_peltier})
    df.to_csv(path_or_buf='experiment1.csv', header=['v_ambient', 'v_case', 'v_plate', 'v_shunt', 'v_peltier'], index=True, index_label="sample")
