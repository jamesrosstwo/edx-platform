from rest_framework import serializers

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

from lms.djangoapps.program_enrollments.api.v1.constants import (
    CourseRunProgressStatuses,
)

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


class CourseOverviewExtendedSerializer(CourseOverviewBaseSerializer):
    """
    A Serializer that adds a number of extra calculated fields for a given
    request user.
    """

    STATUS_CHOICES = [
        CourseRunProgressStatuses.IN_PROGRESS,
        CourseRunProgressStatuses.UPCOMING,
        CourseRunProgressStatuses.COMPLETED
    ]

    def to_representation(self, instance):
        representation = super(CourseOverviewExtendedSerializer, self).to_representation(instance)

        # Here is where we will add a bunch of the extra logic from program
        # enrollments endpoint that we're interested in
        representation['course_run_status'] = '______'
        representation['display_name'] = '______'
        representation['resume_course_run_url'] = '______'
        representation['course_run_url'] = '______'
        representation['emails_enabled'] = '______'
        representation['due_dates'] = '______'
        representation['micromasters_title'] = '______'
        representation['certificate_download_url'] = '______'

        return representation

