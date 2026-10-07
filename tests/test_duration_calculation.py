import pytest
from datetime import datetime, timedelta

def test_duration_calculation():
    start = datetime(2026, 10, 1, 10, 0)
    end = datetime(2026, 10, 4, 10, 0)
    days = max(1, int((end - start).total_seconds() // 86400))
    assert days == 3, 'La durée calculée doit être de 3 jours'
