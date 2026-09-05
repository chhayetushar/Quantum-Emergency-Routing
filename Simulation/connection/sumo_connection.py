import os
import traci


class SumoConnection:

    def __init__(self, sumo_binary: str, config_file: str):
        self.sumo_binary = sumo_binary
        self.config_file = config_file

    def start(self):
        command = [
            self.sumo_binary,
            "-c",
            self.config_file
        ]

        traci.start(command)

    def close(self):
        traci.close()