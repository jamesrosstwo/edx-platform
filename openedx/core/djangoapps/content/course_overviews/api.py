
from lms.djangoapps.program_enrollments.api.v1.constants import (
    CourseRunProgressStatuses,
    ProgramEnrollmentResponseStatuses
)

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

from openedx.core.djangoapps.content.course_overviews.serializers import (
    CourseOverviewBaseSerializer,
    CourseOverviewExtendedSerializer,
)


def get_course_overviews(course_ids, extra_fields=False):
    """
    Placeholder.
    """
    overviews = CourseOverview.objects.filter(id__in=course_ids)

    if extra_fields:
        return CourseOverviewExtendedSerializer(overviews, many=True).data
    return CourseOverviewBaseSerializer(overviews, many=True).data

