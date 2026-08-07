# tests/conftest.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from dotenv import load_dotenv
load_dotenv()

@pytest.fixture
def client_id():
    return "client_test_123"