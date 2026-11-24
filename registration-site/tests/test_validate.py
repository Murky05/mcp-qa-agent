"""Unit tests for ``registration-site/app.py``'s ``validate()``.

``validate()`` is the single server-side gate protecting the ``students``
table from bad data: it enforces name/email/phone/age/course/experience rules
and normalizes the accepted payload. A regression here either rejects valid
students or lets malformed rows reach the database, so every branch is covered.

Dates of birth are derived relative to ``date.today()`` using the same
``(today - born).days // 365`` arithmetic the production code uses, so the
age-boundary assertions stay deterministic regardless of the day they run.
"""
import datetime

import pytest


def dob_for_age(age_years):
    """ISO date string that ``validate()`` reads back as exactly ``age_years``.

    ``validate`` computes ``age = (today - born).days // 365``. Using
    ``age_years * 365 + 1`` days puts the remainder safely below 365, so the
    floor division yields ``age_years`` exactly.
    """
    born = datetime.date.today() - datetime.timedelta(days=age_years * 365 + 1)
    return born.isoformat()


def base_payload():
    return {
        "full_name": "Rahul Sharma",
        "email": "rahul@example.com",
        "phone": "9876543210",
        "gender": "Male",
        "dob": dob_for_age(25),
        "course": "Python",
        "city": "Bengaluru",
        "experience_years": "3",
        "terms": True,
    }


def test_valid_payload_passes_and_is_normalized(app):
    clean, errors = app.validate(base_payload())
    assert errors == {}
    assert clean == {
        "full_name": "Rahul Sharma",
        "email": "rahul@example.com",
        "phone": "9876543210",
        "gender": "Male",
        "dob": clean["dob"],
        "course": "Python",
        "city": "Bengaluru",
        "experience_years": 3,
    }
    assert isinstance(clean["experience_years"], int)


def test_empty_payload_reports_every_field_and_returns_safe_clean(app):
    clean, errors = app.validate({})
    # experience_years is intentionally absent: a missing value defaults to the
    # valid "0", so it is not flagged. Every other field is required.
    assert set(errors) == {
        "full_name",
        "email",
        "phone",
        "gender",
        "dob",
        "course",
        "city",
        "terms",
    }
    assert "experience_years" not in errors
    # Even on total failure, clean must be well-formed with a safe default.
    assert clean["experience_years"] == 0
    assert clean["full_name"] == ""


# ---- full_name -----------------------------------------------------------
@pytest.mark.parametrize("name", ["", "a", "ab", "  x  "])
def test_name_too_short_is_rejected(app, name):
    payload = base_payload()
    payload["full_name"] = name
    _, errors = app.validate(payload)
    assert "full_name" in errors


def test_name_is_trimmed_before_length_check(app):
    payload = base_payload()
    payload["full_name"] = "   abc   "
    clean, errors = app.validate(payload)
    assert "full_name" not in errors
    assert clean["full_name"] == "abc"


# ---- email ---------------------------------------------------------------
@pytest.mark.parametrize("email", ["", "bad", "no-at.com", "a@b", "a b@c.com", "a@b.", "@b.com"])
def test_invalid_emails_are_rejected(app, email):
    payload = base_payload()
    payload["email"] = email
    _, errors = app.validate(payload)
    assert "email" in errors


def test_email_is_lowercased_and_trimmed_in_clean(app):
    payload = base_payload()
    payload["email"] = "  Rahul@Example.COM  "
    clean, errors = app.validate(payload)
    assert "email" not in errors
    assert clean["email"] == "rahul@example.com"


# ---- phone ---------------------------------------------------------------
@pytest.mark.parametrize("phone", ["", "123456789", "12345678901", "12345abcde", "987 654 321"])
def test_phone_must_be_exactly_ten_digits(app, phone):
    payload = base_payload()
    payload["phone"] = phone
    _, errors = app.validate(payload)
    assert "phone" in errors


def test_phone_exactly_ten_digits_passes(app):
    payload = base_payload()
    payload["phone"] = "1234567890"
    _, errors = app.validate(payload)
    assert "phone" not in errors


# ---- gender --------------------------------------------------------------
@pytest.mark.parametrize("gender", ["Male", "Female", "Other"])
def test_accepted_genders(app, gender):
    payload = base_payload()
    payload["gender"] = gender
    _, errors = app.validate(payload)
    assert "gender" not in errors


@pytest.mark.parametrize("gender", ["", "male", "MALE", "Unknown"])
def test_rejected_genders(app, gender):
    payload = base_payload()
    payload["gender"] = gender
    _, errors = app.validate(payload)
    assert "gender" in errors


# ---- dob / age -----------------------------------------------------------
@pytest.mark.parametrize("age", [16, 17, 40, 79, 80])
def test_age_within_range_passes(app, age):
    payload = base_payload()
    payload["dob"] = dob_for_age(age)
    _, errors = app.validate(payload)
    assert "dob" not in errors


@pytest.mark.parametrize("age", [0, 15, 81, 120])
def test_age_out_of_range_is_rejected(app, age):
    payload = base_payload()
    payload["dob"] = dob_for_age(age)
    _, errors = app.validate(payload)
    assert "dob" in errors


@pytest.mark.parametrize("dob", ["", "not-a-date", "2020-13-01", "31-12-2000", "2000/01/01"])
def test_unparseable_dob_is_rejected(app, dob):
    payload = base_payload()
    payload["dob"] = dob
    _, errors = app.validate(payload)
    assert "dob" in errors


# ---- course --------------------------------------------------------------
def test_every_offered_course_is_accepted(app):
    for course in app.COURSES:
        payload = base_payload()
        payload["course"] = course
        _, errors = app.validate(payload)
        assert "course" not in errors, course


@pytest.mark.parametrize("course", ["", "Cooking", "python"])
def test_unknown_course_is_rejected(app, course):
    payload = base_payload()
    payload["course"] = course
    _, errors = app.validate(payload)
    assert "course" in errors


# ---- city ----------------------------------------------------------------
@pytest.mark.parametrize("city,ok", [("", False), ("B", False), (" B ", False), ("Be", True), ("Pune", True)])
def test_city_minimum_length(app, city, ok):
    payload = base_payload()
    payload["city"] = city
    _, errors = app.validate(payload)
    assert ("city" not in errors) is ok


# ---- experience_years ----------------------------------------------------
@pytest.mark.parametrize("exp", ["0", "50", "07", 12])
def test_valid_experience_is_accepted_and_coerced_to_int(app, exp):
    payload = base_payload()
    payload["experience_years"] = exp
    clean, errors = app.validate(payload)
    assert "experience_years" not in errors
    assert clean["experience_years"] == int(exp)


@pytest.mark.parametrize("exp", ["51", "100", "-1", "abc", "3.5"])
def test_invalid_experience_is_rejected(app, exp):
    payload = base_payload()
    payload["experience_years"] = exp
    clean, errors = app.validate(payload)
    assert "experience_years" in errors
    # Non-digit input must still produce a safe integer default in clean.
    assert isinstance(clean["experience_years"], int)


def test_missing_experience_defaults_to_zero(app):
    payload = base_payload()
    del payload["experience_years"]
    clean, errors = app.validate(payload)
    assert "experience_years" not in errors
    assert clean["experience_years"] == 0


# ---- terms ---------------------------------------------------------------
@pytest.mark.parametrize("terms", [True, "on", 1])
def test_accepted_terms(app, terms):
    payload = base_payload()
    payload["terms"] = terms
    _, errors = app.validate(payload)
    assert "terms" not in errors


@pytest.mark.parametrize("terms", [False, "", 0, None])
def test_unaccepted_terms_is_rejected(app, terms):
    payload = base_payload()
    payload["terms"] = terms
    _, errors = app.validate(payload)
    assert "terms" in errors


def test_missing_terms_is_rejected(app):
    payload = base_payload()
    del payload["terms"]
    _, errors = app.validate(payload)
    assert "terms" in errors
