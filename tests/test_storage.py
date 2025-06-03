import pytest
import json
import os
from datetime import datetime
from src.storage import JSONVacancyStorage
from src.vacancy import Vacancy
from src.vacancy import Salary

@pytest.fixture
def temp_storage(tmp_path):
    """Create temporary storage directory"""
    storage_dir = tmp_path / "vacancies"
    storage_dir.mkdir()
    return JSONVacancyStorage(str(storage_dir))

@pytest.fixture
def sample_vacancy():
    """Create sample vacancy for testing"""
    return Vacancy(
        vacancy_id="12345",
        title="Python Developer",
        salary={
            "from": 100000,
            "to": 150000,
            "currency": "RUR",
            "gross": False
        },
        description="Разработка веб-приложений",
        company_name="IT Company",
        url="https://hh.ru/vacancy/12345",
        requirements="Python, Django, REST",
        experience="От 1 года до 3 лет",
        employment="Полная занятость"
    )

@pytest.fixture
def multiple_vacancies():
    """Create multiple vacancies for testing"""
    return [
        Vacancy(
            vacancy_id=str(i),
            title=f"Python Developer {i}",
            salary={
                "from": 100000 + i * 10000,
                "to": 150000 + i * 10000,
                "currency": "RUR",
                "gross": False
            },
            description="",
            company_name=f"Company {i}",
            url=f"https://hh.ru/vacancy/{i}",
            requirements="",
            experience="От 1 года до 3 лет",
            employment="Полная занятость"
        ) for i in range(1, 4)
    ]

def test_storage_initialization(tmp_path):
    """Test storage initialization and directory creation"""
    storage_path = tmp_path / "test_storage"
    storage = JSONVacancyStorage(str(storage_path))
    
    assert os.path.exists(storage.file_path.parent)
    assert os.path.isdir(storage.file_path.parent)

def test_save_and_load_single_vacancy(temp_storage, sample_vacancy):
    """Test saving and loading a single vacancy"""
    temp_storage.add_vacancy(sample_vacancy)
    
    loaded_vacancies = temp_storage.get_vacancies()
    assert len(loaded_vacancies) == 1
    loaded_vacancy = loaded_vacancies[0]
    
    assert loaded_vacancy.id == sample_vacancy.id
    assert loaded_vacancy.title == sample_vacancy.title
    assert loaded_vacancy.salary.min_value == sample_vacancy.salary.min_value
    assert loaded_vacancy.salary.max_value == sample_vacancy.salary.max_value

def test_save_and_load_multiple_vacancies(temp_storage, multiple_vacancies):
    """Test saving and loading multiple vacancies"""
    for vacancy in multiple_vacancies:
        temp_storage.add_vacancy(vacancy)
    
    loaded_vacancies = temp_storage.get_vacancies()
    assert len(loaded_vacancies) == len(multiple_vacancies)
    
    for original, loaded in zip(sorted(multiple_vacancies, key=lambda x: x.id), 
                              sorted(loaded_vacancies, key=lambda x: x.id)):
        assert original.id == loaded.id
        assert original.title == loaded.title

def test_delete_vacancy(temp_storage, sample_vacancy):
    """Test vacancy deletion"""
    temp_storage.add_vacancy(sample_vacancy)
    loaded_vacancies = temp_storage.get_vacancies()
    assert len(loaded_vacancies) == 1
    
    temp_storage.remove_vacancy(sample_vacancy.id)
    loaded_vacancies = temp_storage.get_vacancies()
    assert len(loaded_vacancies) == 0

def test_update_existing_vacancy(temp_storage, sample_vacancy):
    """Test updating an existing vacancy"""
    temp_storage.add_vacancy(sample_vacancy)
    
    updated_vacancy = Vacancy(
        vacancy_id=sample_vacancy.id,
        title="Senior Python Developer",
        salary={
            "from": 150000,
            "to": 200000,
            "currency": "RUR",
            "gross": False
        },
        description="",
        company_name=sample_vacancy.company_name,
        url=sample_vacancy.url,
        requirements="",
        experience="От 3 до 6 лет",
        employment="Полная занятость"
    )
    
    temp_storage.add_vacancy(updated_vacancy)
    loaded_vacancies = temp_storage.get_vacancies()
    assert len(loaded_vacancies) == 1
    loaded_vacancy = loaded_vacancies[0]
    
    assert loaded_vacancy.title == "Senior Python Developer"
    assert loaded_vacancy.salary.min_value == 150000

def test_load_non_existent_vacancy(temp_storage):
    """Test loading a non-existent vacancy"""
    loaded_vacancies = temp_storage.get_vacancies()
    assert len(loaded_vacancies) == 0

def test_vacancy_exists(temp_storage, sample_vacancy):
    """Test vacancy existence check"""
    loaded_vacancies = temp_storage.get_vacancies()
    assert len(loaded_vacancies) == 0
    
    temp_storage.add_vacancy(sample_vacancy)
    loaded_vacancies = temp_storage.get_vacancies()
    assert len(loaded_vacancies) == 1
    assert loaded_vacancies[0].id == sample_vacancy.id

def test_save_vacancy_with_special_characters(temp_storage):
    """Test saving vacancy with special characters"""
    vacancy = Vacancy(
        vacancy_id="special123",
        title="Python/Django Developer (Remote)",
        salary={
            "from": 100000,
            "to": 150000,
            "currency": "RUR",
            "gross": False
        },
        description="",
        company_name="Company & Co.",
        url="https://hh.ru/vacancy/special123",
        requirements="",
        experience="1–3 года",
        employment="Полная занятость"
    )
    
    temp_storage.add_vacancy(vacancy)
    loaded_vacancies = temp_storage.get_vacancies()
    assert len(loaded_vacancies) == 1
    loaded_vacancy = loaded_vacancies[0]
    assert loaded_vacancy.id == vacancy.id
    assert loaded_vacancy.title == vacancy.title

def test_save_vacancies_empty_list(temp_storage):
    """Test saving empty list of vacancies"""
    loaded_vacancies = temp_storage.get_vacancies()
    assert len(loaded_vacancies) == 0

def test_add_vacancies(temp_storage, multiple_vacancies):
    """Test adding vacancies to existing storage"""
    temp_storage.add_vacancy(multiple_vacancies[0])
    
    for vacancy in multiple_vacancies[1:]:
        temp_storage.add_vacancy(vacancy)

    loaded_vacancies = temp_storage.get_vacancies()
    assert len(loaded_vacancies) == len(multiple_vacancies)
    
    loaded_ids = {v.id for v in loaded_vacancies}
    original_ids = {v.id for v in multiple_vacancies}
    assert loaded_ids == original_ids

def test_file_permissions(temp_storage, sample_vacancy):
    """Test file permissions after saving"""
    temp_storage.add_vacancy(sample_vacancy)
    
    assert os.access(temp_storage.file_path, os.R_OK)
    
    with open(temp_storage.file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        assert any(v["id"] == sample_vacancy.id for v in data)

def test_storage_with_nested_directories(tmp_path):
    """Test storage with nested directory structure"""
    nested_path = tmp_path / "vacancies" / "python" / "2024" / "data.json"
    storage = JSONVacancyStorage(str(nested_path))
    
    assert os.path.exists(nested_path.parent)
    assert os.path.isdir(nested_path.parent)

def test_concurrent_vacancy_operations(temp_storage, multiple_vacancies):
    """Test concurrent vacancy operations"""
    # Add all vacancies
    for vacancy in multiple_vacancies:
        temp_storage.add_vacancy(vacancy)
    
    # Update first vacancy
    updated_vacancy = Vacancy(
        vacancy_id=multiple_vacancies[0].id,
        title="Updated Python Developer",
        salary={
            "from": 200000,
            "to": 250000,
            "currency": "RUR",
            "gross": False
        },
        description="",
        company_name=multiple_vacancies[0].company_name,
        url=multiple_vacancies[0].url,
        requirements="",
        experience=multiple_vacancies[0].experience,
        employment=multiple_vacancies[0].employment
    )
    temp_storage.add_vacancy(updated_vacancy)
    
    # Remove last vacancy
    temp_storage.remove_vacancy(multiple_vacancies[-1].id)
    
    # Check results
    loaded_vacancies = temp_storage.get_vacancies()
    assert len(loaded_vacancies) == len(multiple_vacancies) - 1
    
    # Check updated vacancy
    updated = next(v for v in loaded_vacancies if v.id == updated_vacancy.id)
    assert updated.title == "Updated Python Developer"
    assert updated.salary.min_value == 200000 