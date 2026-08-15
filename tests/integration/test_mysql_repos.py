"""Integration tests for raw SQL repositories against local MySQL."""

import mysql.connector
import pytest

from app.config import get_settings
from app.db.repositories.assignment import get_assignment, get_submission
from app.db.repositories.certificate import get_certificate
from app.db.repositories.enrollment import get_enrollment
from app.db.repositories.payment import get_payment, get_payments_by_student_course
from app.db.repositories.student import get_course_by_external_id, get_student


def _require_mysql() -> None:
    settings = get_settings()
    if not settings.mysql_password:
        pytest.fail(
            "MYSQL_PASSWORD is empty in .env. "
            "Run Workbench SQL setup and set the student_ai password."
        )
    try:
        connection = mysql.connector.connect(
            host=settings.mysql_host,
            port=settings.mysql_port,
            database=settings.mysql_database,
            user=settings.mysql_user,
            password=settings.mysql_password,
        )
        connection.close()
    except mysql.connector.Error as exc:
        pytest.fail(
            "Could not connect to local MySQL. "
            "Ensure MySQL Server is running and Workbench setup is complete. "
            f"Details: {exc}"
        )


@pytest.fixture(scope="module", autouse=True)
def mysql_available() -> None:
    _require_mysql()


def test_get_student_stu_a() -> None:
    student = get_student("stu_A")
    assert student is not None
    assert student["external_id"] == "stu_A"
    assert student["status"] == "active"


def test_enrollment_scenarios() -> None:
    course = get_course_by_external_id("crs_ds")
    assert course is not None

    student_a = get_student("stu_A")
    student_b = get_student("stu_B")
    student_d = get_student("stu_D")
    assert student_a and student_b and student_d

    enrollment_a = get_enrollment(student_a["id"], course["id"])
    enrollment_b = get_enrollment(student_b["id"], course["id"])
    enrollment_d = get_enrollment(student_d["id"], course["id"])

    assert enrollment_a is not None
    assert enrollment_a["status"] == "active"
    assert enrollment_b is not None
    assert enrollment_b["status"] == "pending"
    assert enrollment_d is not None
    assert enrollment_d["status"] == "pending"


def test_payment_scenarios() -> None:
    course_ds = get_course_by_external_id("crs_ds")
    course_ml = get_course_by_external_id("crs_ml")
    assert course_ds and course_ml

    student_d = get_student("stu_D")
    student_e = get_student("stu_E")
    assert student_d and student_e

    failed_payment = get_payment("TXN_D_DS_001")
    assert failed_payment is not None
    assert failed_payment["status"] == "failed"

    duplicate_payments = get_payments_by_student_course(student_e["id"], course_ml["id"])
    assert len(duplicate_payments) == 2
    assert all(payment["status"] == "success" for payment in duplicate_payments)


def test_certificate_scenarios() -> None:
    course = get_course_by_external_id("crs_ds")
    student_a = get_student("stu_A")
    student_c = get_student("stu_C")
    assert course and student_a and student_c

    certificate_a = get_certificate(student_a["id"], course["id"])
    certificate_c = get_certificate(student_c["id"], course["id"])

    assert certificate_a is not None
    assert certificate_a["status"] == "issued"
    assert certificate_c is None


def test_assignment_and_submission() -> None:
    assignment = get_assignment(1)
    assert assignment is not None
    assert assignment["title"] == "Exploratory Data Analysis"

    student_a = get_student("stu_A")
    student_c = get_student("stu_C")
    assert student_a and student_c

    submission_a = get_submission(1, student_a["id"])
    submission_c = get_submission(1, student_c["id"])

    assert submission_a is not None
    assert submission_a["status"] == "graded"
    assert submission_c is not None
    assert submission_c["status"] == "submitted"
