# pylint: disable=invalid-name
import pytest


def routing_to(service_name='script', version_id='v1.0',
               project_id='PROJECT_ID', path='', api_key='123'):
    return '/{:s}/{:s}/projects/{:s}/{:s}?api_key={:s}'.format(
        service_name, version_id, project_id, path, api_key)


@pytest.fixture(autouse=True)
def setup(request, mocker, config):
    # pylint: disable=unused-argument
    mocker.patch('pyramid_services.find_service', autospec=True)

    def teardown():
        mocker.stopall()

    request.addfinalizer(teardown)


def test_route_path_to_measure(dummy_request):
    route_path = dummy_request.route_path(
        'measure',
        project_id='PROJECT_ID',
        ext='js',
        _query={'api_key': '123'})

    assert '/script/v1.0/projects/PROJECT_ID/' \
           'measure.js?api_key=123' == route_path


def test_route_path_to_heatmap(dummy_request):
    route_path = dummy_request.route_path(
        'heatmap',
        project_id='PROJECT_ID',
        ext='js',
        _query={'api_key': '123'})

    assert '/widget/v1.0/projects/PROJECT_ID/' \
           'heatmap.js?api_key=123' == route_path


def test_route_path_to_heatmap_minimap(dummy_request):
    # js
    route_path = dummy_request.route_path(
        'heatmap_minimap',
        project_id='PROJECT_ID',
        ext='js',
        _query={'api_key': '123'})

    assert '/widget/v1.0/projects/PROJECT_ID/' \
           'heatmap-minimap.js?api_key=123' == route_path

    # css
    route_path = dummy_request.route_path(
        'heatmap_minimap',
        project_id='PROJECT_ID',
        ext='css',
        _query={'api_key': '123'})

    assert '/widget/v1.0/projects/PROJECT_ID/' \
           'heatmap-minimap.css?api_key=123' == route_path


def test_route_path_to_heatmap_overlay(dummy_request):
    # js
    route_path = dummy_request.route_path(
        'heatmap_overlay',
        project_id='PROJECT_ID',
        ext='js',
        _query={'api_key': '123'})

    assert '/widget/v1.0/projects/PROJECT_ID/' \
           'heatmap-overlay.js?api_key=123' == route_path

    # css
    route_path = dummy_request.route_path(
        'heatmap_overlay',
        project_id='PROJECT_ID',
        ext='css',
        _query={'api_key': '123'})

    assert '/widget/v1.0/projects/PROJECT_ID/' \
           'heatmap-overlay.css?api_key=123' == route_path


def test_routing_to_measure(dummy_app):
    url = routing_to(service_name='script', path='measure.js')
    res = dummy_app.get(url, status=200)
    assert 200 == res.status_code


def test_routing_to_heatmap(dummy_app):
    url = routing_to(service_name='widget', path='heatmap.js')
    res = dummy_app.get(url, status=200)
    assert 200 == res.status_code


def test_routing_to_heatmap_minimap(dummy_app):
    # js
    url = routing_to(service_name='widget',
                     path='heatmap-minimap.js')
    res = dummy_app.get(url, status=200)
    assert 200 == res.status_code

    # css
    url = routing_to(service_name='widget',
                     path='heatmap-minimap.css')
    res = dummy_app.get(url, status=200)
    assert 200 == res.status_code


def test_routing_to_heatmap_overlay(dummy_app):
    # js
    url = routing_to(service_name='widget',
                     path='heatmap-overlay.js')
    res = dummy_app.get(url, status=200)
    assert 200 == res.status_code

    # css
    url = routing_to(service_name='widget',
                     path='heatmap-overlay.css')
    res = dummy_app.get(url, status=200)
    assert 200 == res.status_code


def test_routing_to_humans_txt(dummy_app):
    res = dummy_app.get('/humans.txt', status=200)
    assert 200 == res.status_code


def test_routing_to_robots_txt(dummy_app):
    res = dummy_app.get('/robots.txt', status=200)
    assert 200 == res.status_code
