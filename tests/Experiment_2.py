from src.pyvisa.Power import PowerChannel, VoltageSource, CurrentSource

import nidaqmx, time, pandas as pd
from nidaqmx.constants import AcquisitionType, READ_ALL_AVAILABLE

if __name__ == '__main__':
    """
    1. Increment the current in the peltier cell by 100mA at a time from 0 to 1.5 A and allow the cell to cool
    2. Hunt for plate equilibrium
    """

    output_currents = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5]
    v_ambient = []
    v_case = []
    v_plate = []
    v_shunt = []
    v_peltier = []
    timestamp = []

    data = []

    equilibrium_average_samples = 10
    resample_delay = 300.0
    equilibrium_sample_intervals = 1  # resample_delay/10.0

    fan_max_load_current = 0.35

    run_ts = str(int(time.time()))
    data_file_name = f'experiment_2_{run_ts}.csv'

    with CurrentSource() as current_source, nidaqmx.Task() as task:
        # Turn on the sensors
        current_source.set_channel_power_on("CH3")

        # Turn on the peltier power with current set to zero (the default)
        current_source.set_channel_power_on("CH1")

        # Turn on the heat sink fan and set it to max load
        current_source.set_channel_power_on("CH2")
        current_source.set_channel_current("CH2", fan_max_load_current)

        task.ai_channels.add_ai_voltage_chan(physical_channel="PXI_6251_1/ai0", name_to_assign_to_channel="Ambient", min_val = -1, max_val = 1)
        task.ai_channels.add_ai_voltage_chan(physical_channel="PXI_6251_1/ai1", name_to_assign_to_channel="Case", min_val = -1, max_val = 1)
        task.ai_channels.add_ai_voltage_chan(physical_channel="PXI_6251_1/ai2", name_to_assign_to_channel="Plate", min_val = -1, max_val = 1)
        task.ai_channels.add_ai_voltage_chan(physical_channel="PXI_6251_1/ai3", name_to_assign_to_channel="Shunt", min_val = -0.5, max_val = 0.5)
        task.ai_channels.add_ai_voltage_chan(physical_channel="PXI_6251_1/ai4", name_to_assign_to_channel="Peltier", min_val = -10, max_val = 10)

        for output_current in output_currents:
            print(output_current)

            t1 = 0
            is_equilibrium =False
            current_source.set_channel_current("CH1", output_current)
            time.sleep(resample_delay)
            convergence_attempts = 0
            while not is_equilibrium:
                data = task.read()
                print(data)
                v2 = data[2]
                t2 = (v2-0.5)*100
                delta = abs((t2 - t1)) / t2 * 100  # Percentage difference between two readings
                t1 = t2
                convergence_percentage = 1
                if delta <= convergence_percentage:
                    print(f'v1: {t1}, delta: {delta}, Forced = False')
                    is_equilibrium = True
                else:
                    time.sleep(resample_delay)
                    convergence_attempts += 1
                    if convergence_attempts == 10:
                        print(f'v1: {t1}, delta: {delta}, Forced = True')
                        is_equilibrium = True

            equilibrium_average_sample = [0,0,0,0,0,0]
            for sample in range(equilibrium_average_samples):
                time.sleep(equilibrium_sample_intervals)
                data = task.read()
                equilibrium_average_sample[0] += data[0]
                equilibrium_average_sample[1] += data[1]
                equilibrium_average_sample[2] += data[2]
                equilibrium_average_sample[3] += data[3]
                equilibrium_average_sample[4] += data[4]
            equilibrium_average_sample = [sample/equilibrium_average_samples for sample in equilibrium_average_sample]
            equilibrium_average_sample[5] = time.time()

            v_ambient.append(equilibrium_average_sample[0])
            v_case.append(equilibrium_average_sample[1])
            v_plate.append(equilibrium_average_sample[2])
            v_shunt.append(equilibrium_average_sample[3])
            v_peltier.append(equilibrium_average_sample[4])
            timestamp.append(equilibrium_average_sample[5])

    df = pd.DataFrame({'v_ambient': v_ambient,'v_case': v_case, 'v_plate': v_plate, 'v_shunt': v_shunt, 'v_peltier': v_peltier, 'time': timestamp})
    df.to_csv(path_or_buf=data_file_name, header=['v_ambient', 'v_case', 'v_plate', 'v_shunt', 'v_peltier', 'timestamp'], index=True, index_label="sample")
