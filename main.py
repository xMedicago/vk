# info about the users friends

import asyncio
import warnings
from dataclasses import dataclass

from colorama import Fore
from vkbottle import API

from data import config

warnings.filterwarnings('ignore')


@dataclass
class INFO:
    first_name: str
    last_name: str
    is_closed: bool
    domain: str
    city: str


class VK:
    def __init__(self, page_id: int):
        self.__api = API(token=config.access_token)
        self.__page_id = page_id
        self.__data = []

    async def __get_friends(self, user_id: int) -> list:
        ids_friends = (await self.__api.friends.get(user_id=user_id, order="hints", count=600)).items
        return ids_friends

    async def __extended_user_information(self, user_ids: list | tuple) -> list:
        result = await self.__api.users.get(user_ids=user_ids, fields=["city"])
        for user in result:
            deactivated = user.deactivated
            if deactivated not in ("deleted", "banned"):
                first_name = user.first_name
                last_name = user.last_name
                is_closed = user.is_closed
                domain = f"https://vk.com/id{user.id}"
                try:
                    city = user.city.title
                except AttributeError:
                    city = "-"

                self.__data.append(INFO(first_name=first_name, last_name=last_name, is_closed=is_closed, domain=domain, city=city))
            else:
                continue
        return self.__data

    def get_data(self):
        loop = asyncio.get_event_loop()
        friends = loop.run_until_complete(self.__get_friends(self.__page_id))
        user_information = loop.run_until_complete(self.__extended_user_information(friends))
        print(Fore.RED + "{:^20} {:^49} {} {:^69}".format("ФИО", "Закрыт профиль", "Ссылка", "Город" + Fore.RESET))
        for info in user_information:
            print("{:<40s} {:<20s} {:<40s} {}".format(info.first_name + " " + info.last_name, ("Нет", "Да")[info.is_closed], info.domain, info.city))


if __name__ == '__main__':
    page_id = None
    while not page_id:
        try:
            page_id = int(input("Введите id страницы >> "))
        except ValueError:
            print("id должен быть целым числом\n")

    vk = VK(page_id=page_id)
    vk.get_data()
