import pytest
from src.hh_api import HeadHunterAPI
from src.vacancy import Vacancy, Salary

@pytest.fixture
def hh_api():
    """Fixture for creating HeadHunterAPI instance"""
    return HeadHunterAPI()

def test_get_vacancies_basic_search(hh_api):
    """Test basic vacancy search"""
    vacancies_data = hh_api.get_vacancies("Python Developer")
    vacancies = Vacancy.cast_to_object_list(vacancies_data)
    assert len(vacancies) > 0
    assert all(isinstance(v, Vacancy) for v in vacancies)
    
    for vacancy in vacancies:
        assert vacancy.id
        assert vacancy.title
        assert any(word.lower() in vacancy.title.lower() or word.lower() in vacancy.description.lower() 
                  for word in ["Python", "python"])
        assert vacancy.url.startswith("https://hh.ru/vacancy/")
        assert vacancy.company_name

def test_get_vacancies_with_salary_range(hh_api):
    """Test vacancy search with salary range"""
    min_salary = 150000
    max_salary = 300000
    vacancies_data = hh_api.get_vacancies("Python", salary_from=min_salary, salary_to=max_salary)
    vacancies = Vacancy.cast_to_object_list(vacancies_data)
    
    assert len(vacancies) > 0
    for vacancy in vacancies:
        if vacancy.salary:
            if vacancy.salary.min_value:
                assert vacancy.salary.min_value >= min_salary
            if vacancy.salary.max_value:
                assert vacancy.salary.max_value <= max_salary

def test_get_vacancies_with_experience(hh_api):
    """Test vacancy search with different experience levels"""
    experience_levels = ["noExperience", "between1And3", "between3And6", "moreThan6"]
    
    for exp in experience_levels:
        vacancies_data = hh_api.get_vacancies("Python", experience=exp)
        vacancies = Vacancy.cast_to_object_list(vacancies_data)
        assert len(vacancies) >= 0
        
        if vacancies and exp == "noExperience":
            assert any(v.experience == exp for v in vacancies)

def test_get_vacancies_with_area(hh_api):
    """Test vacancy search in different areas"""
    areas = [1, 2]
    
    for area in areas:
        vacancies_data = hh_api.get_vacancies("Python", area=area)
        vacancies = Vacancy.cast_to_object_list(vacancies_data)
        assert len(vacancies) > 0

def test_get_vacancies_pagination(hh_api):
    """Test vacancy pagination"""
    per_page = 20
    pages = [0, 1]
    
    previous_ids = set()
    for page in pages:
        vacancies_data = hh_api.get_vacancies("Python", per_page=per_page, page=page)
        vacancies = Vacancy.cast_to_object_list(vacancies_data)
        
        assert len(vacancies) <= per_page
        
        current_ids = {v.id for v in vacancies}
        assert not (previous_ids & current_ids)
        previous_ids.update(current_ids)

def test_get_vacancies_empty_search(hh_api):
    """Test search with no results"""
    nonsense_query = "ThisVacancyDefinitelyDoesNotExist12345"
    vacancies_data = hh_api.get_vacancies(nonsense_query)
    vacancies = Vacancy.cast_to_object_list(vacancies_data)
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
        vacancies_data = hh_api.get_vacancies(query)
        vacancies = Vacancy.cast_to_object_list(vacancies_data)
        assert isinstance(vacancies, list)

def test_get_vacancies_with_all_filters(hh_api):
    """Test search with all filters combined"""
    vacancies_data = hh_api.get_vacancies(
        text="Python",
        salary_from=150000,
        salary_to=300000,
        experience="between1And3",
        area=1,
        per_page=20,
        page=0
    )
    vacancies = Vacancy.cast_to_object_list(vacancies_data)
    
    assert isinstance(vacancies, list)
    if vacancies:
        vacancy = vacancies[0]
        assert isinstance(vacancy, Vacancy)
        assert vacancy.salary is None or isinstance(vacancy.salary, Salary)

def test_get_vacancies_response_structure(hh_api):
    """Test detailed structure of vacancy response"""
    vacancies_data = hh_api.get_vacancies("Python", per_page=1)
    vacancies = Vacancy.cast_to_object_list(vacancies_data)
    
    if vacancies:
        vacancy = vacancies[0]
        assert vacancy.id
        assert vacancy.title
        assert vacancy.url
        assert vacancy.company_name
        assert vacancy.experience
        
        if vacancy.salary:
            assert isinstance(vacancy.salary.min_value, (int, type(None)))
            assert isinstance(vacancy.salary.max_value, (int, type(None)))
            assert vacancy.salary.currency in ["RUR", "USD", "EUR"]
            assert isinstance(vacancy.salary.gross, bool) 