"""Shared MongoEngine test DB setup (mongomock)."""

from mongoengine import connect, disconnect


def use_mongomock():
    """Reset MongoEngine and connect to mongomock for unit tests."""
    disconnect()
    connect(host="mongomock://localhost")


def teardown_mongomock():
    disconnect()
