import pytest
from abc import ABC
from src.abstract_api import JobAPIBase
from src.vacancy import Vacancy

class TestAPI(JobAPIBase):
    """Concrete implementation of JobAPIBase for testing"""
    
    def __init__(self):
        self.vacancies = []
        self.search_params = {}
    
    def get_vacancies(self, text, **kwargs):
        self.search_params = {"text": text, **kwargs}
        return self.vacancies
    
    def set_test_vacancies(self, vacancies):
        """Helper method to set test vacancies"""
        self.vacancies = vacancies

@pytest.fixture
def test_api():
    """Fixture for test API instance"""
    return TestAPI()

@pytest.fixture
def sample_vacancy():
    """Fixture for sample vacancy"""
    return Vacancy({
        "id": "12345",
        "name": "Python Developer",
        "salary": {
            "from": 100000,
            "to": 150000,
            "currency": "RUR",
            "gross": False
        },
        "snippet": {
            "requirement": "Python, Django, REST",
            "responsibility": "Разработка веб-приложений"
        },
        "employer": {
            "name": "IT Company"
        },
        "alternate_url": "https://hh.ru/vacancy/12345",
        "experience": {
            "name": "От 1 года до 3 лет"
        },
        "employment": {
            "name": "Полная занятость"
        },
        "published_at": "2024-02-20T10:00:00+0300"
    })

def test_abstract_api_is_abstract():
    """Test that AbstractAPI is abstract class"""
    assert issubclass(JobAPIBase, ABC)
    
    with pytest.raises(TypeError):
        JobAPIBase()

def test_get_vacancies_implementation(test_api, sample_vacancy):
    """Test that concrete implementation can get vacancies"""
    test_api.set_test_vacancies([sample_vacancy])
    
    vacancies = test_api.get_vacancies("Python")
    
    assert len(vacancies) == 1
    assert vacancies[0] == sample_vacancy
    assert test_api.search_params["text"] == "Python"

def test_get_vacancies_with_params(test_api):
    """Test getting vacancies with additional parameters"""
    test_api.get_vacancies(
        "Python",
        salary_from=100000,
        experience="between1And3",
        area=1
    )
    

    assert test_api.search_params["text"] == "Python"
    assert test_api.search_params["salary_from"] == 100000
    assert test_api.search_params["experience"] == "between1And3"
    assert test_api.search_params["area"] == 1

def test_get_vacancies_empty_result(test_api):
    """Test getting vacancies with empty result"""
    vacancies = test_api.get_vacancies("Python")
    
    assert isinstance(vacancies, list)
    assert len(vacancies) == 0

def test_get_vacancies_multiple_results(test_api):
    """Test getting multiple vacancies"""
    test_vacancies = [
        Vacancy({
            "id": str(i),
            "name": f"Python Developer {i}",
            "employer": {"name": f"Company {i}"},
            "alternate_url": f"https://hh.ru/vacancy/{i}",
            "published_at": "2024-02-20T10:00:00+0300"
        }) for i in range(1, 4)
    ]
    
    test_api.set_test_vacancies(test_vacancies)
    vacancies = test_api.get_vacancies("Python")
    
    assert len(vacancies) == 3
    assert all(isinstance(v, Vacancy) for v in vacancies)
    assert [v.id for v in vacancies] == ["1", "2", "3"]

def test_get_vacancies_preserves_order(test_api):
    """Test that get_vacancies preserves the order of vacancies"""
    test_vacancies = [
        Vacancy({
            "id": "3",
            "name": "Senior Python Developer",
            "employer": {"name": "Company A"},
            "alternate_url": "https://hh.ru/vacancy/3",
            "published_at": "2024-02-20T10:00:00+0300"
        }),
        Vacancy({
            "id": "1",
            "name": "Junior Python Developer",
            "employer": {"name": "Company B"},
            "alternate_url": "https://hh.ru/vacancy/1",
            "published_at": "2024-02-20T10:00:00+0300"
        }),
        Vacancy({
            "id": "2",
            "name": "Middle Python Developer",
            "employer": {"name": "Company C"},
            "alternate_url": "https://hh.ru/vacancy/2",
            "published_at": "2024-02-20T10:00:00+0300"
        })
    ]
    
    test_api.set_test_vacancies(test_vacancies)
    vacancies = test_api.get_vacancies("Python")
    
    assert [v.id for v in vacancies] == ["3", "1", "2"]
    assert [v.title for v in vacancies] == [
        "Senior Python Developer",
        "Junior Python Developer",
        "Middle Python Developer"
    ]

def test_get_vacancies_with_special_characters(test_api):
    """Test getting vacancies with special characters in search""" 
    special_queries = [
        "Python!@#$%",
        "Python & Django",
        "Python (Junior)",
        "Python/Flask",
        "C++ Developer",
        "Node.js"
    ]
    
    for query in special_queries:
        vacancies = test_api.get_vacancies(query)
        assert isinstance(vacancies, list)
        assert test_api.search_params["text"] == query 