from time import sleep

import nidaqmx

from nidaqmx.constants import LineGrouping
from statemachine import StateMachine, State


class BinaryCounter(StateMachine):
    state_0000 = State(initial=True, name='0', value=(False, False, False, False))
    state_0001 = State(name='1', value=(False, False, False, True))
    state_0010 = State(name='2', value=(False, False, True, False))
    state_0011 = State(name='3', value=(False, False, True, True))
    state_0100 = State(name='4', value=(False, True, False, False))
    state_0101 = State(name='5', value=(False, True, False, True))
    state_0110 = State(name='6', value=(False, True, True, False))
    state_0111 = State(name='7', value=(False, True, True, True))
    state_1000 = State(name='8', value=(True, False, False, False))
    state_1001 = State(name='9', value=(True, False, False, True))
    state_1010 = State(name='10', value=(True, False, True, False))
    state_1011 = State(name='11', value=(True, False, True, True))
    state_1100 = State(name='12', value=(True, True, False, False))
    state_1101 = State(name='13', value=(True, True, False, True))
    state_1110 = State(name='14', value=(True, True, True, False))
    state_1111 = State(name='15', value=(True, True, True, True))

    cycle = (
            state_0000.to(state_0001)
            | state_0001.to(state_0010)
            | state_0010.to(state_0011)
            | state_0011.to(state_0100)
            | state_0100.to(state_0101)
            | state_0101.to(state_0110)
            | state_0110.to(state_0111)
            | state_0111.to(state_1000)
            | state_1000.to(state_1001)
            | state_1001.to(state_1010)
            | state_1010.to(state_1011)
            | state_1011.to(state_1100)
            | state_1100.to(state_1101)
            | state_1101.to(state_1110)
            | state_1110.to(state_1111)
            | state_1111.to(state_0000)
    )

    # async def before_cycle(self, event: str, source: State, target: State, message: str = ""):
    #     # message = ". " + message if message else ""
    #     # return f"Running {event} from {source.id} to {target.id}{message}"
    #     pass

    # def on_enter_state_0000(self):
    #     pass

    # def on_exit_0000(self):
    #     pass


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    sm = BinaryCounter()
    # img_path = "./binary_counter.png"
    # sm._graph().write_png(img_path)

    with nidaqmx.Task() as input_task, nidaqmx.Task() as output_task:
        input_task.di_channels.add_di_chan("PCI-6221/port0/line4:7", line_grouping=LineGrouping.CHAN_PER_LINE)
        output_task.do_channels.add_do_chan("PCI-6221/port0/line0:3", line_grouping=LineGrouping.CHAN_PER_LINE)
        d = 0.91
        d = d + 0.00
        while True:
            data = input_task.read()
            trigger_line_up = data[0]

            # cancel = data[1]
            # if cancel:
            #     break

            while trigger_line_up:
                data = input_task.read()
                trigger_line_down = not (data[0])

                while trigger_line_down:
                    trigger_line_up = False

                    output_task.write(list(sm.current_state_value))
                    sleep(d)
                    sm.send("cycle")

                    data = input_task.read()
                    cancel = data[1]
                    if cancel:
                        output_task.write([False, False, False, False])
                        sm = BinaryCounter()
                        break
