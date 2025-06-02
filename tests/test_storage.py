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

@pytest.fixture
def multiple_vacancies():
    """Create multiple vacancies for testing"""
    return [
        Vacancy({
            "id": str(i),
            "name": f"Python Developer {i}",
            "salary": {
                "from": 100000 + i * 10000,
                "to": 150000 + i * 10000,
                "currency": "RUR",
                "gross": False
            },
            "employer": {"name": f"Company {i}"},
            "alternate_url": f"https://hh.ru/vacancy/{i}",
            "experience": {"name": "От 1 года до 3 лет"},
            "published_at": "2024-02-20T10:00:00+0300"
        }) for i in range(1, 4)
    ]

def test_storage_initialization(tmp_path):
    """Test storage initialization and directory creation"""
    storage_path = tmp_path / "test_storage"
    storage = JSONVacancyStorage(str(storage_path))
    
    assert os.path.exists(storage.storage_dir)
    assert os.path.isdir(storage.storage_dir)

def test_save_and_load_single_vacancy(temp_storage, sample_vacancy):
    """Test saving and loading a single vacancy"""
    temp_storage.save_vacancy(sample_vacancy)
    
    file_path = os.path.join(temp_storage.storage_dir, f"{sample_vacancy.id}.json")
    assert os.path.exists(file_path)
    
    loaded_vacancy = temp_storage.load_vacancy(sample_vacancy.id)
    assert loaded_vacancy == sample_vacancy
    assert loaded_vacancy.title == sample_vacancy.title
    assert loaded_vacancy.salary.min_value == sample_vacancy.salary.min_value
    assert loaded_vacancy.salary.max_value == sample_vacancy.salary.max_value

def test_save_and_load_multiple_vacancies(temp_storage, multiple_vacancies):
    """Test saving and loading multiple vacancies"""
    temp_storage.save_vacancies(multiple_vacancies)
    
    loaded_vacancies = temp_storage.load_vacancies()
    assert len(loaded_vacancies) == len(multiple_vacancies)
    
    for original, loaded in zip(sorted(multiple_vacancies, key=lambda x: x.id), 
                              sorted(loaded_vacancies, key=lambda x: x.id)):
        assert original == loaded
        assert original.id == loaded.id
        assert original.title == loaded.title

def test_delete_vacancy(temp_storage, sample_vacancy):
    """Test vacancy deletion"""
    temp_storage.save_vacancy(sample_vacancy)
    assert temp_storage.vacancy_exists(sample_vacancy.id)
    
    temp_storage.delete_vacancy(sample_vacancy.id)
    assert not temp_storage.vacancy_exists(sample_vacancy.id)
    
    file_path = os.path.join(temp_storage.storage_dir, f"{sample_vacancy.id}.json")
    assert not os.path.exists(file_path)

def test_update_existing_vacancy(temp_storage, sample_vacancy):
    """Test updating an existing vacancy"""
    temp_storage.save_vacancy(sample_vacancy)
    
    updated_vacancy = Vacancy({
        "id": sample_vacancy.id,
        "name": "Senior Python Developer",
        "salary": {
            "from": 150000,
            "to": 200000,
            "currency": "RUR",
            "gross": False
        },
        "employer": {"name": sample_vacancy.company_name},
        "alternate_url": sample_vacancy.url,
        "experience": {"name": "От 3 до 6 лет"},
        "published_at": "2024-02-20T10:00:00+0300"
    })
    
    temp_storage.save_vacancy(updated_vacancy)
    loaded_vacancy = temp_storage.load_vacancy(sample_vacancy.id)
    
    assert loaded_vacancy == updated_vacancy
    assert loaded_vacancy.title == "Senior Python Developer"
    assert loaded_vacancy.salary.min_value == 150000

def test_load_non_existent_vacancy(temp_storage):
    """Test loading a non-existent vacancy"""
    assert temp_storage.load_vacancy("non_existent") is None

def test_vacancy_exists(temp_storage, sample_vacancy):
    """Test vacancy existence check"""
    assert not temp_storage.vacancy_exists(sample_vacancy.id)
    
    temp_storage.save_vacancy(sample_vacancy)
    assert temp_storage.vacancy_exists(sample_vacancy.id)

def test_save_vacancy_with_special_characters(temp_storage):
    """Test saving vacancy with special characters"""
    vacancy = Vacancy({
        "id": "special123",
        "name": "Python/Django Developer (Remote)",
        "salary": {
            "from": 100000,
            "to": 150000,
            "currency": "RUR",
            "gross": False
        },
        "employer": {"name": "Company & Co."},
        "alternate_url": "https://hh.ru/vacancy/special123",
        "experience": {"name": "1–3 года"},
        "published_at": "2024-02-20T10:00:00+0300"
    })
    
    temp_storage.save_vacancy(vacancy)
    loaded_vacancy = temp_storage.load_vacancy(vacancy.id)
    assert loaded_vacancy == vacancy

def test_save_vacancies_empty_list(temp_storage):
    """Test saving empty list of vacancies"""
    temp_storage.save_vacancies([])
    assert len(temp_storage.load_vacancies()) == 0

def test_add_vacancies(temp_storage, multiple_vacancies):
    """Test adding vacancies to existing storage"""
    temp_storage.save_vacancy(multiple_vacancies[0])
    
    temp_storage.add_vacancies(multiple_vacancies[1:])

    loaded_vacancies = temp_storage.load_vacancies()
    assert len(loaded_vacancies) == len(multiple_vacancies)
    
    for vacancy in multiple_vacancies:
        assert temp_storage.vacancy_exists(vacancy.id)

def test_file_permissions(temp_storage, sample_vacancy):
    """Test file permissions after saving"""
    temp_storage.save_vacancy(sample_vacancy)
    file_path = os.path.join(temp_storage.storage_dir, f"{sample_vacancy.id}.json")
    
    assert os.access(file_path, os.R_OK)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        assert data["id"] == sample_vacancy.id

def test_storage_with_nested_directories(tmp_path):
    """Test storage with nested directory structure"""
    nested_path = tmp_path / "vacancies" / "python" / "2024"
    storage = JSONVacancyStorage(str(nested_path))
    
    assert os.path.exists(storage.storage_dir)
    assert os.path.isdir(storage.storage_dir)

def test_concurrent_vacancy_operations(temp_storage, multiple_vacancies):
    """Test concurrent operations with vacancies"""
    for vacancy in multiple_vacancies:
        temp_storage.save_vacancy(vacancy)
    
    loaded_vacancies = temp_storage.load_vacancies()
    assert len(loaded_vacancies) == len(multiple_vacancies)
    
    temp_storage.delete_vacancy(multiple_vacancies[0].id)
    assert temp_storage.load_vacancy(multiple_vacancies[1].id) is not None
    
    remaining_vacancies = temp_storage.load_vacancies()
    assert len(remaining_vacancies) == len(multiple_vacancies) - 1 