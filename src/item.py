import json
import os
from abc import ABC, abstractmethod
import requests

api_key = os.environ.get('API_KEY_SUPER_JOB')


class API(ABC):
    @abstractmethod
    def get_vacancies(self, search_query):
        pass


class HeadHunterAPI(API):
    def get_vacancies(self, search_query, location=None, page=0, per_page=100, only_with_salary=True):
        url = "https://api.hh.ru/vacancies"
        params = {
            "text": f"NAME:{search_query}",
            "area": location,
            "page": str(page),
            "per_page": str(per_page),
            "only_with_salary": str(only_with_salary)
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


class FileManager(ABC):
    @abstractmethod
    def add_vacancy(self, vacancy):
        pass

    @abstractmethod
    def get_vacancies(self, criteria):
        pass

    @abstractmethod
    def delete_vacancies(self):
        pass


class JsonFileManager(FileManager):
    def __init__(self, filename):
        self.filename = filename

    def add_vacancy(self, vacancy):
        with open(self.filename, 'a', encoding='utf-8') as file:
            vacancy_dict = {
                'title': vacancy.title,
                'link': vacancy.link,
                'salary': vacancy.salary,
                'description': vacancy.description
            }
            json.dump(vacancy_dict, file)
            file.write('\n')

    def get_vacancies(self, criteria):
        vacancies = []
        with open(self.filename, 'r', encoding='utf-8') as file:
            for line in file:
                vacancy_dict = json.loads(line)
                if criteria in vacancy_dict['title']:
                    title = vacancy_dict['title']
                    link = vacancy_dict['link']
                    salary = vacancy_dict['salary']
                    description = vacancy_dict['description']

                    vacancy = Vacancy(title, link, salary, description)
                    vacancies.append(vacancy)

        return vacancies

    def delete_vacancies(self):
        open(self.filename, 'w', encoding='utf-8').close()


def user_interaction():
    search_query = input("Введите поисковый запрос: ")
    location = input("Регион: ")

    headhunter_api = HeadHunterAPI()
    superjob_api = SuperJobAPI()

    vacancies_hh = headhunter_api.get_vacancies(search_query, location)
    vacancies_sj = superjob_api.get_vacancies(search_query)

    json_file_manager = JsonFileManager("vacancies.json")

    print("\nРезультаты поиска из HeadHunter:")
    for vacancy in vacancies_hh:
        json_file_manager.add_vacancy(vacancy)
        print(vacancy)
        print()

    print("Результаты поиска из SuperJob:")
    for vacancy in vacancies_sj:
        json_file_manager.add_vacancy(vacancy)
        print(vacancy)
        print()

    criteria = input("Введите критерий для поиска из сохраненных вакансий: ")
    saved_vacancies = json_file_manager.get_vacancies(criteria)

    print(f"\nРезультаты поиска из сохраненных вакансий по критерию '{criteria}':")
    for vacancy in saved_vacancies:
        print(vacancy)
        print()


if __name__ == "__main__":
    user_interaction()
