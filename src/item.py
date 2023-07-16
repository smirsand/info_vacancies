import json
import os
from abc import ABC, abstractmethod

import requests

api_key = os.environ.get('API_KEY_SUPER_JOB')


class API(ABC):
    """
    Абстрактный базовый класс для API.
    """

    @abstractmethod
    def get_vacancies(self, search_query):
        """
        Абстрактный метод для получения вакансий по поисковому запросу.
        """
        pass


class HeadHunterAPI(API):
    """
    Класс для работы с API HeadHunter.
    """

    def get_vacancies(self, search_query, location=None, page=0, per_page=100, only_with_salary=True,
                      salary_min=None, salary_max=None):
        """
        Метод для получения вакансий с API HeadHunter
        :param search_query: поисковый запрос
        :param location: регион поиска
        :param page: страница результатов
        :param per_page: количество результатов на странице
        :param only_with_salary: информация о зарплате в вакансии
        :param salary_min: минимальная зарплата
        :param salary_max: максимальная зарплата
        :return: список объектов Vacancy
        """
        url = "https://api.hh.ru/vacancies"
        params = {
            "text": f"NAME:{search_query}",
            "area": location,
            "page": str(page),
            "per_page": str(per_page),
            "only_with_salary": str(only_with_salary),
            "salary_from": str(salary_min),
            "salary_to": str(salary_max)
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
            print("Ошибка получения данных с API HeadHunter")
            return []

    def get_area_id(self, area_name):
        """
        Метод для получения идентификатора региона по названию.
        """
        url = "https://api.hh.ru/areas"
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            for country in data:
                for area in country['areas']:
                    if area['name'] == area_name:
                        return area['id']
        return None


class SuperJobAPI(API):
    """
    Класс для работы с API SuperJob.
    """

    def get_vacancies(self, search_query, salary_min=None, salary_max=None):
        """
        Метод для получения вакансий с API SuperJob
        :param search_query: поисковый запрос
        :param salary_min: минимальная зарплата
        :param salary_max: максимальная зарплата
        :return: список объектов Vacancy
        """
        url = "https://api.superjob.ru/2.33/vacancies"
        headers = {"X-Api-App-Id": api_key}
        params = {"keyword": search_query, "count": 100}

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if response.status_code == 200:
            vacancies = []
            for item in data["objects"]:
                title = item["profession"]
                link = item["link"]
                salary = item["payment_from"] if item.get("payment_from") else "Зарплата не указана"
                description = " ".join([
                    "Образование: " + item.get("education", {}).get("title", "") + ".",
                    "Опыт работы: " + item.get("experience", {}).get("title", "") + ".",
                    "Место работы: " + item.get("place_of_work", {}).get("title", "") + ".",
                    "Режим работы: " + item.get("type_of_work", {}).get("title", "") + "."
                ])

                vacancy = Vacancy(title, link, salary, description)
                vacancies.append(vacancy)

            return vacancies
        else:
            print("Ошибка получения данных с API SuperJob")
            return []


class Vacancy:
    """
    Класс для представления вакансии.
    """

    def __init__(self, title, link, salary, description):
        self.title = title
        self.link = link
        self.salary = salary
        self.description = description

    def __str__(self):
        """
        Метод для получения строкового представления вакансии.
        """
        if self.description:
            return f"Title: {self.title}\nLink: {self.link}\nSalary: {self.salary}\nDescription: {self.description}"
        else:
            return f"Title: {self.title}\nLink: {self.link}\nSalary: {self.salary}\n" \
                   f"Description: Описание вакансии отсутствует"


class FileManager(ABC):
    """
    Абстрактный класс для работы с файлами.
    """

    @abstractmethod
    def add_vacancy(self, vacancy):
        """
        Абстрактный метод для добавления вакансии в файл.
        """
        pass

    @abstractmethod
    def get_vacancies(self, criteria):
        """
        Абстрактный метод для получения вакансий из файла по критерию.
        """
        pass

    @abstractmethod
    def delete_vacancies(self):
        """
        Абстрактный метод для удаления всех вакансий из файла.
        """
        pass


class JsonFileManager(FileManager):
    """
    Класс для работы с вакансиями в формате JSON.
    """

    def __init__(self, filename):
        self.filename = filename

    def add_vacancy(self, vacancy):
        """
        Метод для добавления вакансии в файл.
        """
        with open(self.filename, 'a', encoding='utf-8') as file:
            vacancy_dict = {
                'title': vacancy.title,
                'link': vacancy.link,
                'salary': vacancy.salary,
                'description': vacancy.description
            }
            json.dump(vacancy_dict, file, ensure_ascii=False)
            file.write('\n')

    def get_vacancies(self, criteria):
        """
        Метод для получения вакансий из файла по критерию.
        """
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
        """
        Метод для удаления всех вакансий из файла.
        """
        open(self.filename, 'w', encoding='utf-8').close()


def user_interaction():
    """
    Функция для взаимодействия с пользователем.
    """
    search_query = input("Введите поисковый запрос: ")
    location = input("Регион: ")
    salary_min = input("Минимальная зарплата (если не требуется, оставьте пустым): ")
    salary_max = input("Максимальная зарплата (если не требуется, оставьте пустым): ")

    headhunter_api = HeadHunterAPI()
    superjob_api = SuperJobAPI()

    area_id = headhunter_api.get_area_id(location)
    vacancies_hh = headhunter_api.get_vacancies(search_query, location=area_id, salary_min=salary_min,
                                                salary_max=salary_max)
    vacancies_sj = superjob_api.get_vacancies(search_query, salary_min=salary_min, salary_max=salary_max)
    json_file_manager = JsonFileManager("vacancies.json")
    json_file_manager.delete_vacancies()

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
        if vacancy.title.lower() == criteria.lower():
            print(vacancy)
            print()


if __name__ == "__main__":
    user_interaction()
