Вакансии API <br>
Программа для получения вакансий с двух популярных платформ - HeadHunter и SuperJob.

Требования <br>
Для использования API HeadHunter и SuperJob необходимо установить Python 3.x и библиотеку requests.
Получить API ключ от сервиса SuperJob и сохранить его в переменную среды API_KEY_SUPER_JOB.

Использование
1. Запустите файл main.py.
2. Введите поисковый запрос, регион, минимальную и максимальную зарплату (если требуется).
3. Программа выполнит поиск вакансий на платформах HeadHunter и SuperJob с использованием указанных параметров.
4. Результаты поиска будут выведены на экран и сохранены в файл vacancies.json.
5. Можно осуществить поиск по сохраненным вакансиям из файла vacancies.json по критерию.

Классы и методы <br>

Классы
- API - абстрактный базовый класс для API.
- HeadHunterAPI - класс для работы с API HeadHunter.
- SuperJobAPI - класс для работы с API SuperJob.
- Vacancy - класс для представления вакансии.
- FileManager - абстрактный базовый класс для работы с файлами.
- JsonFileManager - класс для работы с вакансиями в формате JSON.

Методы
- get_vacancies(search_query) - метод для получения списка вакансий по поисковому запросу.
- get_area_id(area_name) - метод для получения идентификатора региона по названию (только для HeadHunterAPI).
- add_vacancy(vacancy) - метод для добавления вакансии в файл.
- get_vacancies(criteria) - метод для получения вакансий из файла по критерию.
- delete_vacancies() - метод для удаления всех вакансий из файла.

Зависимости
- requests - библиотека для выполнения запросов.
- json - модуль для работы с JSON-данными.
