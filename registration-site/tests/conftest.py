"""Shared pytest setup for the registration-site unit tests.

The production module (``app.py``) imports ``mysql.connector`` at module load
and, in ``main()``, binds a network server. The pure ``validate()`` logic needs
neither a database nor a running server, so we install a lightweight stub for
``mysql.connector`` before importing the module. This keeps the unit tests
deterministic, hermetic, and runnable without MySQL installed.
"""
import importlib.util
import sys
import types
from pathlib import Path

import pytest

APP_PATH = Path(__file__).resolve().parent.parent / "app.py"


def _install_mysql_stub():
    if "mysql.connector" in sys.modules:
        return

    mysql_mod = types.ModuleType("mysql")
    connector_mod = types.ModuleType("mysql.connector")

    class _Error(Exception):
        pass

    class _IntegrityError(_Error):
        pass

    def _connect(**_kwargs):
        raise _Error("MySQL is unavailable in unit tests")

    connector_mod.Error = _Error
    connector_mod.IntegrityError = _IntegrityError
    connector_mod.connect = _connect
    mysql_mod.connector = connector_mod

    sys.modules["mysql"] = mysql_mod
    sys.modules["mysql.connector"] = connector_mod


def _load_app():
    _install_mysql_stub()
    spec = importlib.util.spec_from_file_location("registration_app", APP_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def app():
    return _load_app()
