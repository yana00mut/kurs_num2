import pytest
from datetime import datetime
from src.vacancy import Vacancy, Salary


class TestSalary:
    """Tests for Salary class"""
    
    def test_salary_creation(self, sample_salary_data):
        """Test creating Salary object"""
        salary = Salary(sample_salary_data)
        assert salary.min_value == 100000
        assert salary.max_value == 150000
        assert salary.currency == "RUR"
        assert not salary.gross

    def test_salary_without_min(self, sample_salary_data):
        """Test Salary without minimum value"""
        sample_salary_data["from"] = None
        salary = Salary(sample_salary_data)
        assert salary.min_value is None
        assert salary.max_value == 150000
        assert str(salary) == "до 150000 RUR (на руки)"

    def test_salary_without_max(self, sample_salary_data):
        """Test Salary without maximum value"""
        sample_salary_data["to"] = None
        salary = Salary(sample_salary_data)
        assert salary.min_value == 100000
        assert salary.max_value is None
        assert str(salary) == "от 100000 RUR (на руки)"

    def test_salary_str_representation(self, sample_salary):
        """Test string representation of Salary"""
        assert str(sample_salary) == "100000-150000 RUR (на руки)"

    def test_salary_with_gross(self, sample_salary_data):
        """Test Salary with gross flag"""
        sample_salary_data["gross"] = True
        salary = Salary(sample_salary_data)
        assert salary.gross
        assert str(salary) == "100000-150000 RUR (до вычета налогов)"

    def test_salary_equality(self, sample_salary_data):
        """Test Salary equality comparison"""
        salary1 = Salary(sample_salary_data)
        salary2 = Salary(sample_salary_data)
        assert salary1 == salary2

        # Test with different values
        sample_salary_data["from"] = 110000
        salary3 = Salary(sample_salary_data)
        assert salary1 != salary3

    def test_salary_invalid_currency(self, sample_salary_data):
        """Test Salary with invalid currency"""
        sample_salary_data["currency"] = "INVALID"
        salary = Salary(sample_salary_data)
        assert salary.currency == "INVALID"  # We don't validate currency


class TestVacancy:
    """Tests for Vacancy class"""
    
    def test_vacancy_creation(self, sample_vacancy_data):
        """Test creating Vacancy object"""
        vacancy = Vacancy(sample_vacancy_data)
        assert vacancy.id == "12345"
        assert vacancy.title == "Python Developer"
        assert isinstance(vacancy.salary, Salary)
        assert vacancy.company_name == "IT Company"
        assert vacancy.url == "https://hh.ru/vacancy/12345"
        assert vacancy.experience == "От 1 года до 3 лет"
        assert vacancy.employment == "Полная занятость"
        assert isinstance(vacancy.created_at, datetime)

    def test_vacancy_without_salary(self, sample_vacancy_data):
        """Test Vacancy without salary"""
        sample_vacancy_data["salary"] = None
        vacancy = Vacancy(sample_vacancy_data)
        assert vacancy.salary is None
        assert str(vacancy) == "Python Developer (IT Company) - З/п не указана"

    def test_vacancy_str_representation(self, sample_vacancy):
        """Test string representation of Vacancy"""
        expected = "Python Developer (IT Company) - 100000-150000 RUR (на руки)"
        assert str(sample_vacancy) == expected

    def test_vacancy_to_dict(self, sample_vacancy):
        """Test converting Vacancy to dictionary"""
        vacancy_dict = sample_vacancy.to_dict()
        assert vacancy_dict["id"] == "12345"
        assert vacancy_dict["title"] == "Python Developer"
        assert vacancy_dict["company_name"] == "IT Company"
        assert vacancy_dict["url"] == "https://hh.ru/vacancy/12345"
        assert vacancy_dict["requirements"] == "Python, Django, REST"
        assert vacancy_dict["experience"] == "От 1 года до 3 лет"
        assert vacancy_dict["employment"] == "Полная занятость"

    def test_vacancy_equality(self, sample_vacancy_data):
        """Test Vacancy equality comparison"""
        vacancy1 = Vacancy(sample_vacancy_data)
        vacancy2 = Vacancy(sample_vacancy_data)
        assert vacancy1 == vacancy2

        # Test with different ID
        sample_vacancy_data["id"] = "67890"
        vacancy3 = Vacancy(sample_vacancy_data)
        assert vacancy1 != vacancy3

    def test_vacancy_without_optional_fields(self, sample_vacancy_data):
        """Test Vacancy creation without optional fields"""
        # Remove optional fields
        del sample_vacancy_data["snippet"]
        del sample_vacancy_data["employment"]
        
        vacancy = Vacancy(sample_vacancy_data)
        assert vacancy.requirements == ""
        assert vacancy.employment == ""

    def test_vacancy_with_invalid_date(self, sample_vacancy_data):
        """Test Vacancy with invalid publication date"""
        sample_vacancy_data["published_at"] = "invalid-date"
        vacancy = Vacancy(sample_vacancy_data)
        assert isinstance(vacancy.created_at, datetime)  # Should use current time

    def test_vacancy_full_data_conversion(self, sample_vacancy):
        """Test full data conversion cycle"""
        # Convert to dict and back
        vacancy_dict = sample_vacancy.to_dict()
        new_vacancy = Vacancy.from_dict(vacancy_dict)
        
        # Check equality
        assert new_vacancy == sample_vacancy
        assert str(new_vacancy) == str(sample_vacancy)

    def test_vacancy_with_special_characters(self, sample_vacancy_data):
        """Test Vacancy with special characters in fields"""
        sample_vacancy_data.update({
            "name": "Senior Python/Django Developer (Remote)",
            "employer": {"name": "Company & Co."},
            "snippet": {
                "requirement": "Python 3.x, Django 4.x, SQL & NoSQL",
                "responsibility": "Backend & API development"
            }
        })
        
        vacancy = Vacancy(sample_vacancy_data)
        assert vacancy.title == "Senior Python/Django Developer (Remote)"
        assert vacancy.company_name == "Company & Co."
        assert "SQL & NoSQL" in vacancy.requirements


@pytest.fixture
def sample_salary_data():
    """Fixture for salary test data"""
    return {
        "from": 100000,
        "to": 150000,
        "currency": "RUR",
        "gross": False
    }

@pytest.fixture
def sample_vacancy_data():
    """Fixture for vacancy test data"""
    return {
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
    }

@pytest.fixture
def sample_salary(sample_salary_data):
    """Fixture for Salary instance"""
    return Salary(sample_salary_data)

@pytest.fixture
def sample_vacancy(sample_vacancy_data):
    """Fixture for Vacancy instance"""
    return Vacancy(sample_vacancy_data) 