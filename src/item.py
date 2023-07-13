import os
from abc import ABC, abstractmethod
import requests

api_key = os.environ.get('API_KEY_SUPER_JOB')


class API(ABC):
    @abstractmethod
    def get_vacancies(self, search_query):
        pass


class HeadHunterAPI(API):
    def get_vacancies(self, search_query):
        url = "https://api.hh.ru/vacancies"
        params = {
            "text": search_query,
            "per_page": 10
        }

        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code == 200:
            vacancies = []
            for item in data["items"]:
                title = item["name"]
                link = item["alternate_url"]
                salary = item["salary"]["from"] if item.get("salary") else "Зарплата не указана"
                description = item.get("snippet", {}).get("requirement", "")

                vacancy = Vacancy(title, link, salary, description)
                vacancies.append(vacancy)

            return vacancies
        else:
            print("Ошибка при получении данных с API HeadHunter")
            return []


class SuperJobAPI(API):
    def get_vacancies(self, search_query):
        url = "https://api.superjob.ru/2.33/vacancies"
        headers = {"X-Api-App-Id": api_key}
        params = {"keyword": search_query, "count": 10}

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if response.status_code == 200:
            vacancies = []
            for item in data["objects"]:
                title = item["profession"]
                link = item["link"]
                salary = item["payment_from"] if item.get("payment_from") else "Зарплата не указана"
                description = item.get("description", "")

                vacancy = Vacancy(title, link, salary, description)
                vacancies.append(vacancy)

            return vacancies
        else:
            print("Ошибка при получении данных с API SuperJob")
            return []


class Vacancy:
    def __init__(self, title, link, salary, description):
        self.title = title
        self.link = link
        self.salary = salary
        self.description = description

    def __str__(self):
        return f"Title: {self.title}\nLink: {self.link}\nSalary: {self.salary}\nDescription: {self.description}"


def user_interaction():
    search_query = input("Введите поисковый запрос: ")

    headhunter_api = HeadHunterAPI()
    superjob_api = SuperJobAPI()

    vacancies_hh = headhunter_api.get_vacancies(search_query)
    vacancies_sj = superjob_api.get_vacancies(search_query)

    print("\nРезультаты поиска из HeadHunter:")
    for vacancy in vacancies_hh:
        print(vacancy)
        print()

    print("Результаты поиска из SuperJob:")
    for vacancy in vacancies_sj:
        print(vacancy)
        print()


if __name__ == "__main__":
    user_interaction()