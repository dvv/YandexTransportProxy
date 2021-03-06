"""
Yandex Transport Core unit tests.

NOTE: These are Unit Tests, they should test function behaviour based on input data only, and should NOT
      rely on current state of Yandex API. These tests are executed once during "build" stage.
      Do not use Live Data from Yandex MassTransit here, only saved one. Live Data is tested in
      Integration Tests/Continuous Monitoring tests.
"""

import pytest
import random
import selenium
import time
import json
from yandex_transport_core import YandexTransportCore

# STOP URL's
# Probably replace this to "ConstructURL" in the future to increase randomness.
# Template: {'name': '', 'url': ''}
stop_urls = [{'name': 'Сходненская улица', 'url': 'https://yandex.ru/maps/213/moscow/?ll=37.439156%2C55.841917&masstransit%5BstopId%5D=stop__9640231&mode=stop&z=17'},
             {'name': 'Метро Марьино (южная)', 'url':'https://yandex.ru/maps/213/moscow/?ll=37.744465%2C55.650011&masstransit%5BstopId%5D=stop__9647488&mode=stop&z=17'},
             {'name': 'Улица Столетова', 'url': 'https://yandex.ru/maps/213/moscow/?ll=37.504978%2C55.703850&masstransit%5BstopId%5D=stop__9646267&mode=stop&z=17'},
             {'name': '3-я Рощинская улица', 'url': 'https://yandex.ru/maps/213/moscow/?ll=37.610832%2C55.707313&masstransit%5BstopId%5D=stop__9646344&mode=stop&z=18'},
             {'name': 'Метро Бауманская', 'url': 'https://yandex.ru/maps/213/moscow/?ll=37.678664%2C55.772171&masstransit%5BstopId%5D=stop__9643291&mode=stop&z=19'},
             {'name': 'Метро Войковская', 'url': 'https://yandex.ru/maps/213/moscow/?ll=37.498648%2C55.818952&masstransit%5BstopId%5D=stop__9649585&mode=stop&z=17'}]

# NOTE: It's a good idea to wait random time between queries so to be very sure Yandex will not ban this.
#       Stress tests to check Yandex patience limits with no delays are considered only, from dedicated IP address.
def wait_random_time():
    '''
    Wait random time between queries.
    :return:
    '''
    time.sleep(random.randint(15, 45))

# ---------------------------------------------      warm-up        -------------------------------------------------- #

def test_initial():
    """
    Most basic test to ensure pytest DEFINITELY works
    """
    assert True == True

# ---------------------------------------------   start_webdriver    -------------------------------------------------- #
def test_start_webdriver_invalid_webdriver_location():
    """
    Start ChromeDriver with invalid webdriver location supplied.
    Should raise selenium.common.exceptions.WebDriverException

    """
    core = YandexTransportCore()
    core.chrome_driver_location = '/opt/usr/bin/this-dir-does-not-exist'
    with pytest.raises(selenium.common.exceptions.WebDriverException):
        result = core.start_webdriver()


# ------------------------------------------   yandexAPIToLocalAPI    ------------------------------------------------ #
def test_yandex_api_to_local_api():
    """
    Test Yandex API to Local API conversions.
    """
    assert YandexTransportCore.yandex_api_to_local_api('maps/api/masstransit/getStopInfo') == 'getStopInfo'
    assert YandexTransportCore.yandex_api_to_local_api('maps/api/masstransit/getRouteInfo') == 'getRouteInfo'
    assert YandexTransportCore.yandex_api_to_local_api('maps/api/masstransit/getLine') == 'getLine'
    assert YandexTransportCore.yandex_api_to_local_api('maps/api/masstransit/getVehiclesInfo') == 'getVehiclesInfo'
    assert YandexTransportCore.yandex_api_to_local_api('maps/api/masstransit/getVehiclesInfoWithRegion') == \
           'getVehiclesInfoWithRegion'
    assert YandexTransportCore.yandex_api_to_local_api('maps/api/masstransit/getLayerRegions') == 'getLayerRegions'
    # Unknown API method, should return the input
    assert YandexTransportCore.yandex_api_to_local_api('maps/api/masstransit/getNonExistent') == \
                                                   'maps/api/masstransit/getNonExistent'


# ------------------------------------------   get_chromium_networking_data    ------------------------------------------ #
def test_get_chromium_networking_data():
    """
    Test getting Chromium Networking Data.
    Basically this will test "Stack Overflow" script to get Networking Data from Chromium, it is expected for this
    test to fail if something will change in Chromium later regarding this functionality.

    The test picks random URL from stop_urlsst, performs "GET" operation, then checks if actual data was returned and will
    try to wind the URL query.

    # Getting constant "Chrome Not Reacheable" error here if run in Docker container.
    """
    core = YandexTransportCore()
    core.start_webdriver()
    url = stop_urls[random.randint(0, len(stop_urls) - 1)]
    print("Stop name:", url['url'])
    core.driver.get(url['url'])
    # Getting Chromium Network Data
    data = json.loads(core.get_chromium_networking_data())
    found_input_url = False
    for entry in data:
        if entry['name'] == url['url']:
            found_input_url = True
            break

    # Wait random amount of time
    assert found_input_url
    wait_random_time()

# ------------------------------------------------- _get_yandex_json --------------------------------------------------- #
def test_get_yandex_json():
    """
    Test "_get_yandex_json" function, should not break no matter what is supplied.
    :return:
    """
    core = YandexTransportCore()
    core.start_webdriver()

    # URL is None, existing method
    url = None
    method = "maps/api/masstransit/getRouteInfo"
    result, error = core._get_yandex_json(url, method)
    assert (result is None) and (error == YandexTransportCore.RESULT_GET_ERROR)

    # URL is gibberish, existing method
    url = 'abrabgarilsitlsdxyb4396t6'
    method = "maps/api/masstransit/getRouteInfo"
    result, error = core._get_yandex_json(url, method)
    assert (result is None) and (error == YandexTransportCore.RESULT_GET_ERROR)
