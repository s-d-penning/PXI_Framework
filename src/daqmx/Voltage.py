import uuid

import nidaqmx
from nidaqmx.constants import TerminalConfiguration

import numpy as np


class VoltageSensor:
    def __init__(self, input_channel: str,
                 config=TerminalConfiguration.RSE,
                 max_voltage: float = 10.0,
                 number_of_samples=1):
        self.voltage_reading = 0.0
        self.name = str(uuid.uuid4())
        self.input_name = f'in_{self.name}'
        self.input_channel = input_channel
        self.config = config
        self.max_voltage = max_voltage

        self.input_task = nidaqmx.Task(new_task_name=self.input_name)
        self._set_measurement_channel(self.input_channel,
                                      config=self.config,
                                      max_voltage=self.max_voltage)
        self.voltage_reading = self.voltage(number_of_samples)

    def __del__(self):
        self.input_task.close()

    def _set_measurement_channel(self, physical_channel: str, max_voltage: float, config=TerminalConfiguration.RSE):
        self.input_channel = physical_channel
        self.input_task.ai_channels.add_ai_voltage_chan(physical_channel=self.input_channel,
                                                        terminal_config=config,
                                                        max_val=max_voltage,
                                                        min_val=-max_voltage)

    def read_output_voltage(self, sample_size: int = 1) -> np.floating:
        samples = self.input_task.read(number_of_samples_per_channel=sample_size)
        while True:
            if self.input_task.is_task_done():
                break
        self.input_task.stop()
        output_voltage = np.mean(samples)
        return output_voltage

    def voltage(self, sample_size: int = 1) -> np.floating:
        self.voltage_reading = self.read_output_voltage(sample_size=sample_size)
        return self.voltage_reading


class VoltageSource:
    def __init__(self,
                 output_channel: str,
                 input_channel: str,
                 max_voltage: float = 10.0,
                 output_voltage: float = 0.0):
        self.name = str(uuid.uuid4())
        self.output_name = f'out_{self.name}'
        self.input_name = f'in_{self.name}'
        self.out_channel = output_channel
        self.input_channel = input_channel
        self.max_voltage = max_voltage

        self.output_task: nidaqmx.Task = nidaqmx.Task(new_task_name=self.output_name)
        self._set_output_channel(physical_channel=output_channel,
                                 max_voltage=abs(max_voltage))

        self.input_task = nidaqmx.Task(new_task_name=self.input_name)
        self._set_measurement_channel(input_channel,
                                      max_voltage=abs(max_voltage))

        if abs(output_voltage) > abs(max_voltage):
            output_voltage = abs(max_voltage)

        self.set_output_voltage(abs(output_voltage))

    def __del__(self):
        self.set_output_voltage(0.0)
        self.output_task.close()
        self.input_task.close()

    def _set_output_channel(self, physical_channel: str, max_voltage: float):
        self.out_channel = physical_channel
        self.output_task.ao_channels.add_ao_voltage_chan(physical_channel=self.out_channel,
                                                         max_val=max_voltage,
                                                         min_val=-max_voltage)

    def _set_measurement_channel(self, physical_channel: str, max_voltage: float):
        self.input_channel = physical_channel
        self.input_task.ai_channels.add_ai_voltage_chan(physical_channel=self.input_channel,
                                                        max_val=max_voltage,
                                                        min_val=-max_voltage)

    def read_output_voltage(self, sample_size: int = 1) -> np.floating:
        samples = self.input_task.read(number_of_samples_per_channel=sample_size)
        while True:
            if self.input_task.is_task_done():
                break
        self.input_task.stop()
        output_voltage = np.mean(samples)
        return output_voltage

    def set_output_voltage(self, voltage: float, sample_size: int = 1) -> np.floating:
        self.output_task.write(voltage)
        while True:
            if self.output_task.is_task_done():
                break
        self.output_task.stop()
        output_voltage = self.read_output_voltage(sample_size=sample_size)
        return output_voltage

    def change_voltage(self, pct: float = 0.0, sample_size: int = 1) -> np.floating:
        output_voltage = self.read_output_voltage(sample_size=sample_size)
        dv = self.max_voltage * pct / 100.0
        new_output_voltage = output_voltage + dv
        if abs(new_output_voltage) <= self.max_voltage:
            output_voltage = self.set_output_voltage(new_output_voltage)
        else:
            output_voltage = self.read_output_voltage(sample_size=sample_size)
        return output_voltage

    def set_min_voltage(self, sample_size: int = 1) -> np.floating:
        output_voltage = self.set_output_voltage(-self.max_voltage, sample_size=sample_size)
        return output_voltage

    def set_max_voltage(self, sample_size:int = 1) -> np.floating:
        output_voltage = self.set_output_voltage(self.max_voltage, sample_size=sample_size)
        return output_voltage



