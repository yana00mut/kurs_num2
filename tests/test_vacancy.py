import pytest
from datetime import datetime
from src.vacancy import Vacancy, Salary


class TestSalary:
    """Tests for Salary class"""
    
    def test_salary_creation(self, sample_salary_data):
        """Test creating Salary object"""
        salary = Salary(
            min_value=sample_salary_data["from"],
            max_value=sample_salary_data["to"],
            currency=sample_salary_data["currency"],
            gross=sample_salary_data["gross"]
        )
        assert salary.min_value == 100000
        assert salary.max_value == 150000
        assert salary.currency == "RUR"
        assert not salary.gross

    def test_salary_without_min(self, sample_salary_data):
        """Test Salary without minimum value"""
        salary = Salary(
            min_value=None,
            max_value=sample_salary_data["to"],
            currency=sample_salary_data["currency"],
            gross=sample_salary_data["gross"]
        )
        assert salary.min_value is None
        assert salary.max_value == 150000
        assert str(salary) == "до 150000 RUR"

    def test_salary_without_max(self, sample_salary_data):
        """Test Salary without maximum value"""
        salary = Salary(
            min_value=sample_salary_data["from"],
            max_value=None,
            currency=sample_salary_data["currency"],
            gross=sample_salary_data["gross"]
        )
        assert salary.min_value == 100000
        assert salary.max_value is None
        assert str(salary) == "от 100000 RUR"

    def test_salary_str_representation(self, sample_salary):
        """Test string representation of Salary"""
        assert str(sample_salary) == "от 100000 до 150000 RUR"

    def test_salary_with_gross(self, sample_salary_data):
        """Test Salary with gross flag"""
        salary = Salary(
            min_value=sample_salary_data["from"],
            max_value=sample_salary_data["to"],
            currency=sample_salary_data["currency"],
            gross=True
        )
        assert salary.gross
        assert str(salary) == "от 100000 до 150000 RUR"

    def test_salary_equality(self, sample_salary_data):
        """Test Salary equality comparison"""
        salary1 = Salary(
            min_value=sample_salary_data["from"],
            max_value=sample_salary_data["to"],
            currency=sample_salary_data["currency"],
            gross=sample_salary_data["gross"]
        )
        salary2 = Salary(
            min_value=sample_salary_data["from"],
            max_value=sample_salary_data["to"],
            currency=sample_salary_data["currency"],
            gross=sample_salary_data["gross"]
        )
        assert salary1.min_value == salary2.min_value
        assert salary1.max_value == salary2.max_value
        assert salary1.currency == salary2.currency

        salary3 = Salary(
            min_value=110000,
            max_value=sample_salary_data["to"],
            currency=sample_salary_data["currency"],
            gross=sample_salary_data["gross"]
        )
        assert salary1.min_value != salary3.min_value

    def test_salary_invalid_currency(self, sample_salary_data):
        """Test Salary with invalid currency"""
        salary = Salary(
            min_value=sample_salary_data["from"],
            max_value=sample_salary_data["to"],
            currency="INVALID",
            gross=sample_salary_data["gross"]
        )
        assert salary.currency == "INVALID"


class TestVacancy:
    """Tests for Vacancy class"""
    
    def test_vacancy_creation(self, sample_vacancy_data):
        """Test creating Vacancy object"""
        vacancy = Vacancy(
            vacancy_id=sample_vacancy_data["id"],
            title=sample_vacancy_data["name"],
            salary=Salary(
                min_value=sample_vacancy_data["salary"]["from"],
                max_value=sample_vacancy_data["salary"]["to"],
                currency=sample_vacancy_data["salary"]["currency"],
                gross=sample_vacancy_data["salary"]["gross"]
            ),
            description=sample_vacancy_data["snippet"]["responsibility"],
            company_name=sample_vacancy_data["employer"]["name"],
            url=sample_vacancy_data["alternate_url"],
            requirements=sample_vacancy_data["snippet"]["requirement"],
            experience=sample_vacancy_data["experience"]["name"],
            employment=sample_vacancy_data["employment"]["name"]
        )
        assert vacancy.id == "12345"
        assert vacancy.title == "Python Developer"
        assert isinstance(vacancy.salary, Salary)
        assert vacancy.company_name == "IT Company"
        assert vacancy.url == "https://hh.ru/vacancy/12345"
        assert vacancy.experience == "От 1 года до 3 лет"
        assert vacancy.employment == "Полная занятость"

    def test_vacancy_without_salary(self, sample_vacancy_data):
        """Test Vacancy without salary"""
        vacancy = Vacancy(
            vacancy_id=sample_vacancy_data["id"],
            title=sample_vacancy_data["name"],
            salary=None,
            description=sample_vacancy_data["snippet"]["responsibility"],
            company_name=sample_vacancy_data["employer"]["name"],
            url=sample_vacancy_data["alternate_url"],
            requirements=sample_vacancy_data["snippet"]["requirement"],
            experience=sample_vacancy_data["experience"]["name"],
            employment=sample_vacancy_data["employment"]["name"]
        )
        assert vacancy.salary is None
        assert str(vacancy) == "Python Developer (IT Company)"

    def test_vacancy_str_representation(self, sample_vacancy):
        """Test string representation of Vacancy"""
        expected = "Python Developer (IT Company)"
        assert str(sample_vacancy) == expected

    def test_vacancy_equality(self, sample_vacancy_data):
        """Test Vacancy equality comparison"""
        vacancy1 = Vacancy(
            vacancy_id=sample_vacancy_data["id"],
            title=sample_vacancy_data["name"],
            salary=Salary(
                min_value=sample_vacancy_data["salary"]["from"],
                max_value=sample_vacancy_data["salary"]["to"],
                currency=sample_vacancy_data["salary"]["currency"],
                gross=sample_vacancy_data["salary"]["gross"]
            ),
            description=sample_vacancy_data["snippet"]["responsibility"],
            company_name=sample_vacancy_data["employer"]["name"],
            url=sample_vacancy_data["alternate_url"],
            requirements=sample_vacancy_data["snippet"]["requirement"],
            experience=sample_vacancy_data["experience"]["name"],
            employment=sample_vacancy_data["employment"]["name"]
        )
        vacancy2 = Vacancy(
            vacancy_id=sample_vacancy_data["id"],
            title=sample_vacancy_data["name"],
            salary=Salary(
                min_value=sample_vacancy_data["salary"]["from"],
                max_value=sample_vacancy_data["salary"]["to"],
                currency=sample_vacancy_data["salary"]["currency"],
                gross=sample_vacancy_data["salary"]["gross"]
            ),
            description=sample_vacancy_data["snippet"]["responsibility"],
            company_name=sample_vacancy_data["employer"]["name"],
            url=sample_vacancy_data["alternate_url"],
            requirements=sample_vacancy_data["snippet"]["requirement"],
            experience=sample_vacancy_data["experience"]["name"],
            employment=sample_vacancy_data["employment"]["name"]
        )
        assert vacancy1.id == vacancy2.id

        vacancy3 = Vacancy(
            vacancy_id="67890",
            title=sample_vacancy_data["name"],
            salary=Salary(
                min_value=sample_vacancy_data["salary"]["from"],
                max_value=sample_vacancy_data["salary"]["to"],
                currency=sample_vacancy_data["salary"]["currency"],
                gross=sample_vacancy_data["salary"]["gross"]
            ),
            description=sample_vacancy_data["snippet"]["responsibility"],
            company_name=sample_vacancy_data["employer"]["name"],
            url=sample_vacancy_data["alternate_url"],
            requirements=sample_vacancy_data["snippet"]["requirement"],
            experience=sample_vacancy_data["experience"]["name"],
            employment=sample_vacancy_data["employment"]["name"]
        )
        assert vacancy1.id != vacancy3.id

    def test_vacancy_without_optional_fields(self, sample_vacancy_data):
        """Test Vacancy creation without optional fields"""
        vacancy = Vacancy(
            vacancy_id=sample_vacancy_data["id"],
            title=sample_vacancy_data["name"],
            salary=Salary(
                min_value=sample_vacancy_data["salary"]["from"],
                max_value=sample_vacancy_data["salary"]["to"],
                currency=sample_vacancy_data["salary"]["currency"],
                gross=sample_vacancy_data["salary"]["gross"]
            ),
            description="",
            company_name=sample_vacancy_data["employer"]["name"],
            url=sample_vacancy_data["alternate_url"],
            requirements="",
            experience=sample_vacancy_data["experience"]["name"],
            employment=""
        )
        assert vacancy.requirements == ""
        assert vacancy.employment == ""

    def test_vacancy_with_special_characters(self, sample_vacancy_data):
        """Test Vacancy with special characters in fields"""
        vacancy = Vacancy(
            vacancy_id=sample_vacancy_data["id"],
            title="Senior Python/Django Developer (Remote)",
            salary=Salary(
                min_value=sample_vacancy_data["salary"]["from"],
                max_value=sample_vacancy_data["salary"]["to"],
                currency=sample_vacancy_data["salary"]["currency"],
                gross=sample_vacancy_data["salary"]["gross"]
            ),
            description="Backend & API development",
            company_name="Company & Co.",
            url=sample_vacancy_data["alternate_url"],
            requirements="Python 3.x, Django 4.x, SQL & NoSQL",
            experience=sample_vacancy_data["experience"]["name"],
            employment=sample_vacancy_data["employment"]["name"]
        )
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
    return Salary(
        min_value=sample_salary_data["from"],
        max_value=sample_salary_data["to"],
        currency=sample_salary_data["currency"],
        gross=sample_salary_data["gross"]
    )

@pytest.fixture
def sample_vacancy(sample_vacancy_data):
    """Fixture for Vacancy instance"""
    return Vacancy(
        vacancy_id=sample_vacancy_data["id"],
        title=sample_vacancy_data["name"],
        salary=Salary(
            min_value=sample_vacancy_data["salary"]["from"],
            max_value=sample_vacancy_data["salary"]["to"],
            currency=sample_vacancy_data["salary"]["currency"],
            gross=sample_vacancy_data["salary"]["gross"]
        ),
        description=sample_vacancy_data["snippet"]["responsibility"],
        company_name=sample_vacancy_data["employer"]["name"],
        url=sample_vacancy_data["alternate_url"],
        requirements=sample_vacancy_data["snippet"]["requirement"],
        experience=sample_vacancy_data["experience"]["name"],
        employment=sample_vacancy_data["employment"]["name"]
    ) 