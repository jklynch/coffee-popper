import json
import time

import numpy as np
import zmq


class HeatEquationSolver:
    def __init__(self):
        # Set maximum iteration
        self.max_iter = 500

        # Set Dimension and delta
        self.len_x = 20
        self.len_y = 20
        self.delta = 1

        # Boundary condition
        self.t_top = 20
        self.t_bottom = 20
        self.t_left = 20
        self.t_right = 20

        # Initial guess of interior grid
        self.t_guess = 20

        # grid for plotting
        self.X, self.Y = np.meshgrid(np.arange(0, self.len_x), np.arange(0, self.len_y))

        # allocate and initialize
        self.T = np.empty((self.len_x, self.len_y))
        self.T.fill(self.t_guess)

        # boundary conditions
        self.T[(self.len_y-1):, :] = self.t_top
        self.T[:1, :] = self.t_bottom
        self.T[:, (self.len_x-1):] = self.t_right
        self.T[:, :1] = self.t_left

    def set_heater_temperature(self, t):
        print('HeatEqnSolver.set_heater_temperature(t={})'.format(t))
        self.t_top = t
        self.T[(self.len_y-1):, :] = self.t_top

    def get_temperature(self, i, j):
        return self.T[i, j]

    def advance(self, seconds):
        print('HeatEqnSolver.advance(seconds={})'.format(seconds))
        one_sec_iter = 10
        for iteration in range(0, int(seconds * one_sec_iter)):
            for i in range(1, self.len_x - 1, self.delta):
                for j in range(1, self.len_y - 1, self.delta):
                    self.T[i, j] = 0.25 * (self.T[i + 1][j] + self.T[i - 1][j] + self.T[i][j + 1] + self.T[i][j - 1])


class PopperSim:
    def __init__(self):
        self.heater_duty_cycle = 0.0
        self.fan_throttle = 0.0
        self.heat_eqn_solver = HeatEquationSolver()

        print('initial temperature: {:5.3f}'.format(self.heat_eqn_solver.get_temperature(10, 10)))

    def cleanup(self):
        print('cleaning up')

    def control_heater(self, duty_cycle):
        self.heater_duty_cycle = duty_cycle
        print('heater duty cycle: {:.5f}'.format(self.heater_duty_cycle))
        self.heat_eqn_solver.set_heater_temperature(t=duty_cycle * 4.0)

        return self.heater_duty_cycle

    def get_heater_duty_cycle(self):
        return self.heater_duty_cycle

    def control_fan(self, throttle):
        self.fan_throttle = throttle
        print('fan throttle: {:.5f}'.format(throttle))
        return self.fan_throttle

    def get_fan_throttle(self):
        return self.fan_throttle

    def read_temperature(self):
        temperature = self.heat_eqn_solver.get_temperature(10, 10)
        print('thermocouple temperature: {:.5f}'.format(temperature))
        return temperature


class PopperSimClient:
    def __init__(self):
        self.popper_sim = PopperSim()
        self.time = 0.0

        self.get_status()

    def get_status(self):
        print('PopperSimClient.get_status()')
        self.time += (1.01 - 0.99) * np.random.ranf() + 0.9
        self.popper_sim.heat_eqn_solver.advance(seconds=1.0)
        status = {
            'status': {
                'time': self.time,
                'temperature': self.popper_sim.read_temperature(),
                'fan_throttle': self.popper_sim.get_fan_throttle(),
                'heater_duty_cycle': self.popper_sim.get_heater_duty_cycle()
            }
        }
        return status['status']

    def set_heater_duty_cycle(self, duty_cycle):
        self.popper_sim.control_heater(duty_cycle=duty_cycle)

    def set_fan_throttle(self, throttle):
        self.popper_sim.control_fan(throttle=throttle)


def popper_sim():
    """
    Set up hardware and start event loop.
    """

    coffee_popper = PopperSim()

    try:
        context = zmq.Context()
        control_socket = context.socket(zmq.REP)
        control_socket.bind("tcp://*:5555")

        poller = zmq.Poller()
        poller.register(control_socket, zmq.POLLIN)

        status_socket = context.socket(zmq.PUB)
        status_socket.bind("tcp://*:5556")

        message_handlers = {
            'heater': coffee_popper.control_heater,
            'fan': coffee_popper.control_fan,
            'read_temperature': coffee_popper.read_temperature
        }

        #popper_time = 0.0
        next_status_msg_time = time.time()
        while True:
            #popper_time += 1.0

            socks = dict(poller.poll(timeout=10))
            if control_socket in socks:
                # get a list of messages
                json_messages = control_socket.recv_json()
                print("Received request:\n{}".format(json_messages))

                responses = []
                for function_name, function_kwargs in json_messages:
                    print('\tfunction name: {}'.format(function_name))
                    print('\tfunction args: {}'.format(function_kwargs))

                    message_handler = message_handlers[function_name]
                    response = message_handler(**function_kwargs)
                    responses.append(
                        {
                            function_name: response
                        }
                    )
                #  Send reply back to client
                control_socket.send_json(responses)

            else:
                pass

            # time for a status message?
            if time.time() >= next_status_msg_time:
                coffee_popper.heat_eqn_solver.advance(seconds=1.0)
                status = {
                    'status': {
                        'time': time.time(),
                        'temperature': coffee_popper.read_temperature(),
                        'fan_throttle': coffee_popper.get_fan_throttle(),
                        'heater_duty_cycle': coffee_popper.get_heater_duty_cycle()
                    }
                }
                print('sending a status message:\n{}'.format(status))
                status_msg = ("status {}".format(json.dumps(status)))
                print('status_msg: {}'.format(status_msg))
                status_socket.send_string(status_msg)
                # next status message 1s after the previous time
                next_status_msg_time += 1.0

            else:
                pass

    finally:
        print('Clean it up!')
        coffee_popper.cleanup()


if __name__ == '__main__':
    popper_sim()
