from src.api.hh_api import HeadHunterAPI
from src.api.storage import JSONVacancyStorage
from typing import List
from src.api.vacancy import Vacancy
import os


def filter_vacancies(vacancies: List[Vacancy], filter_words: List[str]) -> List[Vacancy]:
    """
    Фильтрация вакансий по ключевым словам
    
    Args:
        vacancies: Список вакансий
        filter_words: Список ключевых слов для фильтрации
        
    Returns:
        List[Vacancy]: Отфильтрованный список вакансий
    """
    return [v for v in vacancies if v.contains_keywords(filter_words)]


def get_vacancies_by_salary(vacancies: List[Vacancy], salary_range: str) -> List[Vacancy]:
    """
    Фильтрация вакансий по диапазону зарплат
    
    Args:
        vacancies: Список вакансий
        salary_range: Строка с диапазоном зарплат (например, "100000-150000")
        
    Returns:
        List[Vacancy]: Отфильтрованный список вакансий
    """
    return [v for v in vacancies if v.salary_in_range(salary_range)]


def sort_vacancies(vacancies: List[Vacancy]) -> List[Vacancy]:
    """
    Сортировка вакансий по зарплате (по убыванию)
    
    Args:
        vacancies: Список вакансий
        
    Returns:
        List[Vacancy]: Отсортированный список вакансий
    """
    return sorted(vacancies, reverse=True)


def get_top_vacancies(vacancies: List[Vacancy], n: int) -> List[Vacancy]:
    """
    Получение топ N вакансий
    
    Args:
        vacancies: Список вакансий
        n: Количество вакансий для вывода
        
    Returns:
        List[Vacancy]: Топ N вакансий
    """
    return vacancies[:n]


def print_vacancies(vacancies: List[Vacancy]) -> None:
    """Вывод списка вакансий"""
    if not vacancies:
        print("Вакансии не найдены")
        return

    for i, vacancy in enumerate(vacancies, 1):
        print(f"\n{'-' * 50}\n{i}. {vacancy}\n{'-' * 50}")


def user_interaction():
    """Функция для взаимодействия с пользователем"""
    api = HeadHunterAPI()
    
    # Создаем путь к файлу в директории data
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    storage = JSONVacancyStorage(os.path.join(data_dir, "vacancies.json"))

    # Проверка подключения к API
    if not api.connect():
        print("Ошибка подключения к API HeadHunter")
        return

    while True:
        print("\nВыберите действие:")
        print("1. Поиск вакансий")
        print("2. Работа с сохраненными вакансиями")
        print("0. Выход")

        choice = input("\nВаш выбор: ")

        if choice == "1":
            # Поиск новых вакансий
            search_query = input("Введите поисковый запрос: ")
            location = input("Введите город (или нажмите Enter для пропуска): ")
            
            print("\nПоиск вакансий...")
            vacancies_data = api.get_vacancies(search_query, location)
            vacancies_list = Vacancy.cast_to_object_list(vacancies_data)
            
            # Сохраняем вакансии
            for vacancy in vacancies_list:
                storage.add_vacancy(vacancy)
            
            # Фильтрация и сортировка
            filter_words = input("Введите ключевые слова для фильтрации вакансий (через пробел): ").split()
            salary_range = input("Введите диапазон зарплат (например, 100000-150000): ")
            top_n = int(input("Введите количество вакансий для вывода в топ N: "))

            # Применяем фильтры
            filtered_vacancies = filter_vacancies(vacancies_list, filter_words)
            if salary_range:
                filtered_vacancies = get_vacancies_by_salary(filtered_vacancies, salary_range)
            
            # Сортируем и получаем топ N
            sorted_vacancies = sort_vacancies(filtered_vacancies)
            top_vacancies = get_top_vacancies(sorted_vacancies, top_n)
            
            print_vacancies(top_vacancies)

        elif choice == "2":
            # Работа с сохраненными вакансиями
            print("\nРабота с сохраненными вакансиями:")
            print("1. Показать все вакансии")
            print("2. Фильтрация и сортировка")
            print("3. Очистить сохраненные вакансии")
            
            sub_choice = input("\nВаш выбор: ")
            
            if sub_choice == "1":
                vacancies = storage.get_vacancies()
                print_vacancies(vacancies)
                
            elif sub_choice == "2":
                vacancies = storage.get_vacancies()
                filter_words = input("Введите ключевые слова для фильтрации вакансий (через пробел): ").split()
                salary_range = input("Введите диапазон зарплат (например, 100000-150000): ")
                top_n = int(input("Введите количество вакансий для вывода в топ N: "))

                filtered_vacancies = filter_vacancies(vacancies, filter_words)
                if salary_range:
                    filtered_vacancies = get_vacancies_by_salary(filtered_vacancies, salary_range)
                
                sorted_vacancies = sort_vacancies(filtered_vacancies)
                top_vacancies = get_top_vacancies(sorted_vacancies, top_n)
                print_vacancies(top_vacancies)
                
            elif sub_choice == "3":
                confirm = input("Вы уверены, что хотите очистить все сохраненные вакансии? (y/n): ")
                if confirm.lower() == 'y':
                    storage.clear()
                    print("Все сохраненные вакансии удалены")

        elif choice == "0":
            break

        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    user_interaction()
