from random import random, randint, choice

from DriverA import DriverA


class Passanger:
    max_waiting_time = 20

    def __init__(self, waypint_num: int):
        self.destination = waypint_num
        self.waiting_time = 0

    def __repr__(self):
        return f"{self.destination}|{self.waiting_time}"


class Waypoint:
    route_time = 5

    def __init__(self, waypint_num: int):
        self.waypoint_num = waypint_num
        self.busses_in_route = []
        self.passangers = []

    def __repr__(self):
        return f"num: {self.waypoint_num}||| Psg: {self.passangers} busses: {self.busses_in_route}"


time_of_day = 0

first_rush_hour_start = 7 * 60
first_rush_hour_end = 9 * 60

second_rush_hour_start = 17 * 60
second_rush_hour_end = 19 * 60

usual_passanger_spawn = 0.3
rush_hour_passanger_spawn = 0.7


def check_rush_hour(_time_of_day):
    return (first_rush_hour_start < _time_of_day < first_rush_hour_end) or \
        (second_rush_hour_start < _time_of_day < second_rush_hour_end)


def spawn_passanger(_rush_hour):
    if _rush_hour:
        return random() < rush_hour_passanger_spawn
    else:
        return random() < usual_passanger_spawn


last_waypoint = 6


def get_random_destination(_current_waypoint):
    l = [_i for _i in range(last_waypoint + 1)]
    l.remove(_current_waypoint)
    return choice(l)


time_between_waypoints = 5

money_earned_per_passanger = 50

spawned_passangers = 0
delivered_passanders = 0
lost_passangers = 0
money_earned = 0

waypoints = []
for i in range(0, last_waypoint + 1):
    waypoints.append(Waypoint(i))


class Hub:
    def __init__(self):
        self.total_busses = 2
        self.free_busses = 2
        # timetable содержит время запуска на маршрут новых водителей
        # self.timetable = [0]
        # self.timetable = [0, 4 * 60]
        # self.timetable = [
        #                       0,
        #                       0 + 30,
        #                       4 * 60,
        #                       4 * 60 + 30,
        #                       13 * 60,
        #                       13 * 60 + 30,
        #                       17 * 60,
        #                       17 * 60 + 30,
        #                   ]
        self.timetable = [i for i in range(0, 24*60, 30)]


main_hub = Hub()


def simulate():
    global time_of_day, waypoints, lost_passangers, delivered_passanders, spawned_passangers, money_earned, main_hub

    print(f"{time_of_day // 60}:{time_of_day % 60}")
    for waypoint in waypoints:
        print(waypoint.__repr__())
    print()

    rush_hour = check_rush_hour(time_of_day)
    for waypoint in waypoints:
        if waypoint.waypoint_num == 0:
            # логика для нулевого километра
            if time_of_day in main_hub.timetable:
                main_hub.free_busses -= 1
                if main_hub.free_busses < 0:
                    print("error: less than 0 busses")
                waypoint.busses_in_route.append(DriverA())

        for bus in waypoint.busses_in_route:
            if bus.time_to_destination > 0:
                bus.time_to_destination -= 1
            else:
                if waypoint.waypoint_num == last_waypoint:
                    bus.moving_to_hub = True
                for passanger in bus.passangers:
                    if passanger.destination == waypoint.waypoint_num:
                        bus.passangers.remove(passanger)
                        money_earned += money_earned_per_passanger
                        delivered_passanders += 1

                for passanger in waypoint.passangers:
                    if len(bus.passangers) < bus.bus_max_passangers:
                        if passanger.destination < waypoint.waypoint_num and bus.moving_to_hub:
                            bus.passangers.append(passanger)
                            waypoint.passangers.remove(passanger)
                        elif passanger.destination > waypoint.waypoint_num and (not bus.moving_to_hub):
                            bus.passangers.append(passanger)
                            waypoint.passangers.remove(passanger)

                # автобус продолжает движение
                if bus.moving_to_hub:
                    bus.time_to_destination = time_between_waypoints
                    waypoints[waypoint.waypoint_num - 1].busses_in_route.append(bus)
                    waypoint.busses_in_route.remove(bus)
                else:
                    bus.time_to_destination = time_between_waypoints
                    waypoints[waypoint.waypoint_num + 1].busses_in_route.append(bus)
                    waypoint.busses_in_route.remove(bus)

        for passanger in waypoint.passangers:
            # удаляем пассажиров которые слишком долго ждут
            passanger.waiting_time += 1
            if passanger.waiting_time > passanger.max_waiting_time:
                lost_passangers += 1
                waypoint.passangers.remove(passanger)

        if spawn_passanger(rush_hour):
            spawned_passangers += 1
            # генерируем пассажира с целью назначения
            waypoint.passangers.append(Passanger(get_random_destination(waypoint.waypoint_num)))
    time_of_day += 1


def start_day_simulation():
    for i in range(60 * 24):
        simulate()

    print(f"delivered passangers: {delivered_passanders}/{spawned_passangers}")
    print(f"money_earned:{money_earned}")


start_day_simulation()
