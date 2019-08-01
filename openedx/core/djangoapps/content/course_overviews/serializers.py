from rest_framework import serializers


class CourseOverviewBaseSerializer(serializers.ModelSerializer):
    """
    Serializer for a course run overview.
    """
    STATUS_CHOICES = [
        CourseRunProgressStatuses.IN_PROGRESS,
        CourseRunProgressStatuses.UPCOMING,
        CourseRunProgressStatuses.COMPLETED
    ]

    class Meta(object):
        model = CourseOverview
        fields = (
            'id',
            'start',
            'end',
        )


class CourseOverviewExtendedSerializer(CourseOverviewBaseSerializer):

    def to_representation(self, instance):
        representation = super(CourseOverviewExtendedSerializer, self).to_representation(instance)

        representation['course_run_status'] = '______'
        representation['display_name'] = '______'
        representation['resume_course_run_url'] = '______'
        representation['course_run_url'] = '______'
        representation['emails_enabled'] = '______'
        representation['due_dates'] = '______'
        representation['micromasters_title'] = '______'
        representation['certificate_download_url'] = '______'

        return representation

