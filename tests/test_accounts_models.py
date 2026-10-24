import pytest
from django.contrib.auth import authenticate, get_user_model
from django.db import IntegrityError

User = get_user_model()

pytestmark = pytest.mark.django_db


def test_create_user_lowercases_email():
    user = User.objects.create_user("Alice@Example.COM", password="s3cret-pass")

    assert user.email == "alice@example.com"
    assert user.check_password("s3cret-pass")
    assert not user.is_staff
    assert not user.is_superuser


def test_create_user_requires_email():
    with pytest.raises(ValueError):
        User.objects.create_user("", password="s3cret-pass")


def test_create_superuser_sets_flags():
    user = User.objects.create_superuser("admin@example.com", password="s3cret-pass")

    assert user.is_staff
    assert user.is_superuser


def test_case_only_duplicate_email_raises_integrity_error():
    # Bypass the manager so the stored email keeps its capitals; only the
    # Lower("email") constraint can catch the duplicate.
    User(email="Bob@x.com").save()

    with pytest.raises(IntegrityError):
        User.objects.create_user("bob@x.com")


def test_authenticate_with_mixed_case_email():
    User.objects.create_user("carol@example.com", password="s3cret-pass")

    user = authenticate(email="Carol@Example.com", password="s3cret-pass")

    assert user is not None
    assert user.email == "carol@example.com"
