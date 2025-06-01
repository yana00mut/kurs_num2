import pytest
from src.hh_api import HeadHunterAPI
from src.api.vacancy import Vacancy, Salary

@pytest.fixture
def hh_api():
    """Fixture for creating HeadHunterAPI instance"""
    return HeadHunterAPI()

def test_get_vacancies_basic_search(hh_api):
    """Test basic vacancy search"""
    vacancies = hh_api.get_vacancies("Python Developer")
    assert len(vacancies) > 0
    assert all(isinstance(v, Vacancy) for v in vacancies)
    
    # Check basic vacancy attributes
    for vacancy in vacancies:
        assert vacancy.vacancy_id
        assert vacancy.title
        assert "Python" in vacancy.title.lower() or "Python" in vacancy.description.lower()
        assert vacancy.url.startswith("https://hh.ru/vacancy/")
        assert vacancy.employer

def test_get_vacancies_with_salary_range(hh_api):
    """Test vacancy search with salary range"""
    min_salary = 150000
    max_salary = 300000
    vacancies = hh_api.get_vacancies("Python", salary_from=min_salary, salary_to=max_salary)
    
    assert len(vacancies) > 0
    for vacancy in vacancies:
        if vacancy.salary:
            if vacancy.salary.from_amount:
                assert vacancy.salary.from_amount >= min_salary
            if vacancy.salary.to_amount:
                assert vacancy.salary.to_amount <= max_salary

def test_get_vacancies_with_experience(hh_api):
    """Test vacancy search with different experience levels"""
    experience_levels = ["noExperience", "between1And3", "between3And6", "moreThan6"]
    
    for exp in experience_levels:
        vacancies = hh_api.get_vacancies("Python", experience=exp)
        assert len(vacancies) >= 0  # Может быть 0 для некоторых уровней опыта
        
        if vacancies:
            # Проверяем, что опыт соответствует фильтру
            if exp == "noExperience":
                assert any("без опыта" in v.experience.lower() for v in vacancies)
            elif exp == "between1And3":
                assert any("1" in v.experience and "3" in v.experience for v in vacancies)
            elif exp == "between3And6":
                assert any("3" in v.experience and "6" in v.experience for v in vacancies)
            elif exp == "moreThan6":
                assert any("6" in v.experience for v in vacancies)

def test_get_vacancies_with_area(hh_api):
    """Test vacancy search in different areas"""
    # Тестируем поиск в Москве (1) и Санкт-Петербурге (2)
    areas = [1, 2]
    
    for area in areas:
        vacancies = hh_api.get_vacancies("Python", area=area)
        assert len(vacancies) > 0

def test_get_vacancies_pagination(hh_api):
    """Test vacancy pagination"""
    per_page = 20
    pages = [0, 1]  # Тестируем первые две страницы
    
    previous_ids = set()
    for page in pages:
        vacancies = hh_api.get_vacancies("Python", per_page=per_page, page=page)
        
        # Проверяем количество результатов
        assert len(vacancies) <= per_page
        
        # Проверяем уникальность вакансий между страницами
        current_ids = {v.vacancy_id for v in vacancies}
        assert not (previous_ids & current_ids)  # Не должно быть пересечений
        previous_ids.update(current_ids)

def test_get_vacancies_empty_search(hh_api):
    """Test search with no results"""
    nonsense_query = "ThisVacancyDefinitelyDoesNotExist12345"
    vacancies = hh_api.get_vacancies(nonsense_query)
    assert len(vacancies) == 0

def test_get_vacancies_special_characters(hh_api):
    """Test search with special characters"""
    special_queries = [
        "Python!@#$%",
        "Python & Django",
        "Python (Junior)",
        "Python/Flask"
    ]
    
    for query in special_queries:
        vacancies = hh_api.get_vacancies(query)
        # Проверяем, что API не падает с ошибкой
        assert isinstance(vacancies, list)

def test_get_vacancies_with_all_filters(hh_api):
    """Test search with all filters combined"""
    vacancies = hh_api.get_vacancies(
        text="Python",
        salary_from=150000,
        salary_to=300000,
        experience="between1And3",
        area=1,
        per_page=20,
        page=0
    )
    
    assert isinstance(vacancies, list)
    if vacancies:
        vacancy = vacancies[0]
        assert isinstance(vacancy, Vacancy)
        assert vacancy.salary is None or isinstance(vacancy.salary, Salary)

def test_get_vacancies_response_structure(hh_api):
    """Test detailed structure of vacancy response"""
    vacancies = hh_api.get_vacancies("Python", per_page=1)
    
    if vacancies:
        vacancy = vacancies[0]
        # Проверяем все обязательные поля
        assert vacancy.vacancy_id
        assert vacancy.title
        assert vacancy.url
        assert vacancy.employer
        assert vacancy.experience
        
        # Проверяем формат зарплаты
        if vacancy.salary:
            assert isinstance(vacancy.salary.from_amount, (int, type(None)))
            assert isinstance(vacancy.salary.to_amount, (int, type(None)))
            assert vacancy.salary.currency in ["RUR", "USD", "EUR"]
            assert isinstance(vacancy.salary.gross, bool) 