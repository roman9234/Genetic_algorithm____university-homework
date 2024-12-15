from random import random, randint, choice

from DriverA import DriverA
import matplotlib.pyplot as plt
import numpy as np


class Passanger:
    max_waiting_time = 30

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
        self.resting_drivers = []

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

money_earned_per_passanger = 40

money_for_bus_maintance = 7000

spawned_passangers = 0
delivered_passanders = 0
lost_passangers = 0
money_earned = 0

waypoints = []
for i in range(0, last_waypoint + 1):
    waypoints.append(Waypoint(i))


class Hub:
    def __init__(self):
        self.total_busses = 0
        self.free_busses = 0
        self.total_drivers = 0
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
        self.timetable = [i for i in range(30, 24*60, 120)]
        # self.timetable += [10]



main_hub = Hub()
spawned_passangers_events = []
delivered_passanders_events = []
lost_passangers_events = []


def simulate():
    global time_of_day, waypoints, lost_passangers, delivered_passanders, spawned_passangers, money_earned, main_hub

    print(f"{time_of_day // 60}:{time_of_day % 60}")
    for waypoint in waypoints:
        print(waypoint.__repr__())
    print()

    rush_hour = check_rush_hour(time_of_day)
    for waypoint in waypoints:
        if waypoint.waypoint_num == 0:

            for resting_driver in waypoint.resting_drivers:
                resting_driver[0] -= 1
                if resting_driver[0] == 0:
                    main_hub.free_busses -= 1
                    if main_hub.free_busses < 0:
                        main_hub.free_busses = 0
                        main_hub.total_busses += 1
                    new_driver = DriverA()
                    new_driver.time_of_work = resting_driver[1]
                    new_driver.amount_of_rests = 1
                    waypoint.resting_drivers.remove(resting_driver)
                    waypoint.busses_in_route.append(new_driver)




            # логика для нулевого километра
            if time_of_day in main_hub.timetable:
                main_hub.free_busses -= 1
                if main_hub.free_busses < 0:
                    main_hub.free_busses = 0
                    main_hub.total_busses += 1
                main_hub.total_drivers+=1
                waypoint.busses_in_route.append(DriverA())

        for bus in waypoint.busses_in_route:
            bus.time_of_work += 1
            if bus.time_to_destination > 0:
                bus.time_to_destination -= 1
            else:
                if waypoint.waypoint_num == 0:

                    # Проверка что водителю пора на отдых
                    if bus.time_of_work >= bus.min_rest_interval and bus.amount_of_rests == 0:
                        main_hub.free_busses += 1
                        waypoint.resting_drivers.append([bus.max_rest_time, bus.time_of_work])
                        for passanger in bus.passangers:
                            waypoint.passangers.append(passanger)
                        waypoint.busses_in_route.remove(bus)
                        break

                    # Проверка что водитель отработал смену
                    elif bus.time_of_work >= bus.max_work_time:
                        main_hub.free_busses += 1
                        for passanger in bus.passangers:
                            waypoint.passangers.append(passanger)
                        waypoint.busses_in_route.remove(bus)
                        break


                    elif waypoint.waypoint_num == 0:
                        bus.moving_to_hub = False



                elif waypoint.waypoint_num == last_waypoint:
                    bus.moving_to_hub = True
                i = 0
                while i < len(bus.passangers):
                    # Успешная доставка пассажира
                    if bus.passangers[i].destination == waypoint.waypoint_num:
                        bus.passangers.remove(bus.passangers[i])
                        i-=1
                        money_earned += money_earned_per_passanger
                        delivered_passanders_events.append(time_of_day)
                        delivered_passanders += 1
                    i+=1

                i = 0
                while i < len(waypoint.passangers):
                    if len(bus.passangers) < bus.bus_max_passangers:
                        if waypoint.passangers[i].destination < waypoint.waypoint_num and bus.moving_to_hub:
                            bus.passangers.append(waypoint.passangers[i])
                            waypoint.passangers.remove(waypoint.passangers[i])
                            i-=1
                        elif waypoint.passangers[i].destination > waypoint.waypoint_num and (not bus.moving_to_hub):
                            bus.passangers.append(waypoint.passangers[i])
                            waypoint.passangers.remove(waypoint.passangers[i])
                            i-=1
                    i+=1

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
                lost_passangers_events.append(time_of_day)
                waypoint.passangers.remove(passanger)

        if spawn_passanger(rush_hour):
            spawned_passangers += 1
            spawned_passangers_events.append(time_of_day)
            # генерируем пассажира с целью назначения
            waypoint.passangers.append(Passanger(get_random_destination(waypoint.waypoint_num)))

    time_of_day += 1


def start_day_simulation():
    for i in range(60 * 24):
        simulate()

    print(f"Успешно доставлено пассажиров: {delivered_passanders}/{spawned_passangers}")
    print(f"Заработано денег с продажи билетов:{money_earned}")

    print(f"Всего водителей:{main_hub.total_drivers}")
    print(f"Потрачено денег на зарплаты водителям:{main_hub.total_drivers * DriverA.salary_per_day}")
    print(f"Прибыль:{money_earned - main_hub.total_drivers * DriverA.salary_per_day}")

    print(f"Всего автобусов: {main_hub.total_busses}")

    print(f"Прибыль / число автобусов (показатель эффективности): {(money_earned - main_hub.total_drivers * DriverA.salary_per_day) / main_hub.total_busses}")

    # анализ:
    # График спавна пассажиров:
    event_hours_spawn = [time // 60 for time in spawned_passangers_events]

    event_data = [
        spawned_passangers_events,
        lost_passangers_events,
        delivered_passanders_events,
    ]
    event_labels = [
        "Появление пассажиров",
        "Не дождавшиеся пассажиры",
        "Успешно доставленные пассажиры"
    ]


    fig, axes = plt.subplots(len(event_data), 1, figsize=(6, len(event_data) * 4), sharex=True)

    # Построение графиков
    for i, (event_times, label) in enumerate(zip(event_data, event_labels)):
        # Переводим минуты в часы
        event_hours = [time // 60 for time in event_times]

        # Подсчитываем количество событий по часам
        hour_bins = np.arange(0, 25)
        event_counts, _ = np.histogram(event_hours, bins=hour_bins)

        # Построение графика
        axes[i].bar(hour_bins[:-1], event_counts, width=1, edgecolor='black', align='edge')
        axes[i].set_title(label)
        axes[i].set_ylabel('Количество событий')
        axes[i].grid(axis='y', linestyle='--', alpha=0.7)

    # Настройка общей оси X
    axes[-1].set_xlabel('Час дня')
    plt.xticks(range(0, 24))  # Отображение всех часов на оси X

    # Уменьшение расстояния между графиками
    plt.tight_layout()

    # Отображение окна с графиками
    plt.show()



    # График исчезающих пассажиров


    # График успешно перевезённых пассажиров


    ...


start_day_simulation()
