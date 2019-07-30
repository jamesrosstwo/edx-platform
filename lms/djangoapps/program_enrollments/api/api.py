# -*- coding: utf-8 -*-
"""
ProgramEnrollment internal api
"""
from __future__ import absolute_import, unicode_literals

from datetime import datetime, timedelta
from pytz import UTC

from django.urls import reverse

from six import iteritems

from bulk_email.api import is_bulk_email_feature_enabled, is_user_opted_out_for_course
from edx_when.api import get_dates_for_course
from xmodule.modulestore.django import modulestore
from lms.djangoapps.program_enrollments.api.v1.constants import (
    CourseEnrollmentResponseStatuses,
    CourseRunProgressStatuses,
    MAX_ENROLLMENT_RECORDS,
    ProgramEnrollmentResponseStatuses,
)


def get_due_dates(request, course_key, user):
    """
    Get due date information for a user for blocks in a course.

    Arguments:
        request: the request object
        course_key (CourseKey): the CourseKey for the course
        user: the user object for which we want due date information

    Returns:
        due_dates (list): a list of dictionaries containing due date information
            keys:
                name: the display name of the block
                url: the deep link to the block
                date: the due date for the block
    """
    dates = get_dates_for_course(
        course_key,
        user,
    )

    store = modulestore()

    due_dates = []
    for (block_key, date_type), date in iteritems(dates):
        if date_type == 'due':
            block = store.get_item(block_key)

            # get url to the block in the course
            block_url = reverse('jump_to', args=[course_key, block_key])
            block_url = request.build_absolute_uri(block_url)

            due_dates.append({
                'name': block.display_name,
                'url': block_url,
                'date': date,
            })
    return due_dates


def get_course_run_url(request, course_id):
    """
    Get the URL to a course run.

    Arguments:
        request: the request object
        course_id (string): the course id of the course

    Returns:
        (string): the URL to the course run associated with course_id
    """
    course_run_url = reverse('openedx.course_experience.course_home', args=[course_id])
    return request.build_absolute_uri(course_run_url)


def get_emails_enabled(user, course_id):
    """
    Get whether or not emails are enabled in the context of a course.

    Arguments:
        user: the user object for which we want to check whether emails are enabled
        course_id (string): the course id of the course

    Returns:
        (bool): True if emails are enabled for the course associated with course_id for the user;
        False otherwise
    """
    if is_bulk_email_feature_enabled(course_id=course_id):
        return not is_user_opted_out_for_course(user=user, course_id=course_id)
    else:
        return None


def get_course_run_status(course_overview, is_certificate_passing, certificate_creation_date):
    """
    Get the progress status of a course run.

    Arguments:
        course_overview (CourseOverview): the overview for the course run
        is_certificate_passing (bool): True if the user has a passing certificate in
            this course run; False otherwise
        certificate_creation_date: the date the certificate was created

    Returns:
        status: one of CourseRunProgressStatuses.COMPLETE,
            CourseRunProgressStatuses.IN_PROGRESS,
            or CourseRunProgressStatuses.UPCOMING
    """
    if course_overview.pacing == 'instructor':
        if course_overview.has_ended():
            return CourseRunProgressStatuses.COMPLETED
        elif course_overview.has_started():
            return CourseRunProgressStatuses.IN_PROGRESS
        else:
            return CourseRunProgressStatuses.UPCOMING
    elif course_overview.pacing == 'self':
        has_ended = course_overview.has_ended()
        thirty_days_ago = datetime.now(UTC) - timedelta(30)
        # a self paced course run is completed when either the course run has ended
        # OR the user has earned a certificate 30 days ago or more
        if has_ended or is_certificate_passing and (certificate_creation_date and certificate_creation_date <= thirty_days_ago):
            return CourseRunProgressStatuses.COMPLETED
        elif course_overview.has_started():
            return CourseRunProgressStatuses.IN_PROGRESS
        else:
            return CourseRunProgressStatuses.UPCOMING
    return None
