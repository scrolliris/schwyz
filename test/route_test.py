# pylint: disable=invalid-name
import pytest


@pytest.fixture(autouse=True)
def setup(config):  # pylint: disable=unused-argument
    pass


def test_routing_to_humans_txt(dummy_app):
    res = dummy_app.get('/humans.txt', status=200)
    assert 200 == res.status_code


def test_routing_to_robots_txt(dummy_app):
    res = dummy_app.get('/robots.txt', status=200)
    assert 200 == res.status_code
