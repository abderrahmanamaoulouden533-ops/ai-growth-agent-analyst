import pytest
from common.metrics import cpl, cpq, cpql, cpbd, roas, stage_conversion_rate

def test_cpl():
    result = cpl(1000, 50)
    assert result["value"] == 20.0
    assert result["numerator"] == 1000
    assert result["denominator"] == 50

def test_cpq():
    result = cpq(1000, 25)
    assert result["value"] == 40.0

def test_cpql():
    result = cpql(1000, 10)
    assert result["value"] == 100.0

def test_cpbd():
    result = cpbd(1000, 5)
    assert result["value"] == 200.0

def test_roas():
    result = roas(1500, 1000)
    assert result["value"] == 1.5

def test_stage_conversion_rate():
    result = stage_conversion_rate(100, 50)
    assert result["value"] == 50.0