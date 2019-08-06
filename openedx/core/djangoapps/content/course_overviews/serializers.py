# -*- coding: utf-8 -*-
"""
CourseOverview serializers
"""
from rest_framework import serializers

from lms.djangoapps.certificates.api import get_certificate_for_user
from lms.djangoapps.program_enrollments.api.api import (
    get_due_dates,
    get_course_run_url,
    get_emails_enabled,
    get_course_run_status
)
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from student.helpers import get_resume_urls_for_enrollments
from student.models import CourseEnrollment


class CourseOverviewBaseSerializer(serializers.ModelSerializer):
    """
    Serializer for a course run overview.
    """

    class Meta(object):
        model = CourseOverview
        fields = (
            'id',
            'start',
            'end',
        )


class CourseOverviewRequestUserSerializer(CourseOverviewBaseSerializer):
    """
    A Serializer that adds a number of extra calculated fields for a given
    user included in the request context.
    """

    def to_representation(self, instance):
        representation = super(CourseOverviewRequestUserSerializer, self).to_representation(instance)

        request = self.context['request']

        # Following fields optionally added to representation
        # Certificate
        certificate_download_url = None
        is_certificate_passing = None
        certificate_creation_date = None
        certificate_info = get_certificate_for_user(
            request.user.username,
            instance.id
        )
        if certificate_info:
            certificate_download_url = certificate_info['download_url']
            is_certificate_passing = certificate_info['is_passing']
            certificate_creation_date = certificate_info['created']
        if certificate_download_url:
            representation['certificate_download_url'] = certificate_download_url

        # Resume url
        enrollment = CourseEnrollment.objects.get(
            user__username=request.user.username,
            course_id=instance.id,
        )
        resume_course_run_url = get_resume_urls_for_enrollments(
            request.user,
            [enrollment],
        )[instance.id]
        if resume_course_run_url:
            representation['resume_course_run_url'] = resume_course_run_url

        # Email enabled
        emails_enabled = get_emails_enabled(request.user, instance.id)
        if emails_enabled is not None:
            representation['emails_enabled'] = emails_enabled

        # Following fields always added to the representation
        representation['course_run_id'] = str(instance.id),
        representation['course_run_status'] = get_course_run_status(
            instance,
            is_certificate_passing,
            certificate_creation_date,
        )
        representation['start_date'] = instance.start,
        representation['end_date'] = instance.end,
        representation['display_name'] = instance.display_name_with_default
        representation['course_run_url'] = get_course_run_url(request, instance.id)
        representation['due_dates'] = get_due_dates(request, instance.id, request.user)

        return representation

