class DriverA:
    bus_max_passangers = 20

    salary_per_day = 70_000 / 20

    max_work_time = 8 * 60

    min_rest_interval = 4 * 60
    max_rest_time = 1 * 60
    max_rests_per_day = 1

    max_days_of_work = 5
    min_days_of_rest = 2

    def __init__(self):
        self.moving_to_hub = False
        self.passangers = []
        self.time_to_destination = 0
        self.time_of_work = 0
        self.amount_of_rests = 0

    def __repr__(self):
        return f"t:{self.time_to_destination}|p:{len(self.passangers)}"
