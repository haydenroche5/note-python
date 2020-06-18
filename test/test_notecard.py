import os
import sys
import serial
import periphery
import pytest

from unittest.mock import Mock, MagicMock, patch

sys.path.insert(0, os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..')))

import notecard  # noqa: E402
from notecard import card, service  # noqa: E402


def get_serial_and_port():
    serial = Mock()  # noqa: F811
    port = serial.Serial("/dev/tty.foo", 9600)
    port.read.side_effect = [b'\r', b'\n', None]

    nCard = notecard.OpenSerial(port)

    return (nCard, port)


def get_i2c_and_port():
    periphery = Mock()  # noqa: F811
    port = periphery.I2C("dev/i2c-foo")
    port.try_lock.return_value = True

    nCard = notecard.OpenI2C(port, 0x17, 255)

    return (nCard, port)


def test_open_serial():
    nCard, _ = get_serial_and_port()

    assert nCard.uart is not None


def test_open_i2c():
    nCard, _ = get_i2c_and_port()

    assert nCard.i2c is not None


def test_transaction():
    nCard, port = get_serial_and_port()

    port.read.side_effect = [char.encode('utf-8')
                             for char in "{\"connected\":true}\r\n"]

    response = nCard.Transaction({"req": "service.status"})

    assert "connected" in response
    assert response["connected"] is True


def test_service_set():
    nCard, port = get_serial_and_port()

    port.read.side_effect = [char.encode('utf-8')
                             for char in "{}\r\n"]

    response = service.set(nCard, product="com.blues.tester",
                           sn="foo",
                           mode="continuous",
                           minutes=2,
                           hours=1,
                           sync=True)

    assert response == {}


def test_service_set_invalid_card():
    with pytest.raises(Exception, match="Notecard object required"):
        service.set(None, product="com.blues.tester")


def test_service_sync():
    nCard, port = get_serial_and_port()

    port.read.side_effect = [char.encode('utf-8')
                             for char in "{}\r\n"]

    response = service.sync(nCard)

    assert response == {}


def test_service_sync_status():
    nCard, port = get_serial_and_port()

    port.read.side_effect = [char.encode('utf-8')
                             for char in "{\"status\":\"connected\"}\r\n"]

    response = service.syncStatus(nCard)

    assert "status" in response
    assert response["status"] == "connected"


def test_service_status():
    nCard, port = get_serial_and_port()

    port.read.side_effect = [char.encode('utf-8')
                             for char in "{\"connected\":true}\r\n"]

    response = service.status(nCard)

    assert "connected" in response
    assert response["connected"] is True


def test_service_log():
    nCard, port = get_serial_and_port()

    port.read.side_effect = [char.encode('utf-8')
                             for char in "{}\r\n"]

    response = service.log(nCard, "there's been an issue!", False)

    assert response == {}


def test_service_get():
    nCard, port = get_serial_and_port()

    port.read.side_effect = [char.encode('utf-8')
                             for char in "{\"mode\":\"continuous\"}\r\n"]

    response = service.get(nCard)

    assert "mode" in response
    assert response["mode"] == "continuous"


def test_card_time():
    nCard, port = get_serial_and_port()

    port.read.side_effect = [char.encode('utf-8')
                             for char in
                             "{\"time\":1592490375}\r\n"]

    response = card.time(nCard)

    assert "time" in response
    assert response["time"] == 1592490375


def test_card_status():
    nCard, port = get_serial_and_port()

    port.read.side_effect = [char.encode('utf-8')
                             for char in
                             "{\"usb\":true,\"status\":\"{normal}\"}\r\n"]

    response = card.status(nCard)

    assert "status" in response
    assert response["status"] == "{normal}"
