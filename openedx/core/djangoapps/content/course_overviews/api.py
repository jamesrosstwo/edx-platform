# -*- coding: utf-8 -*-
"""
CourseOverview internal api
"""
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

from openedx.core.djangoapps.content.course_overviews.serializers import (
    CourseOverviewBaseSerializer,
    CourseOverviewRequestUserSerializer,
)


def get_course_overviews(course_ids, request=None):
    """
    Return course_ovewview data for a given list of course_ids.
    """
    overviews = CourseOverview.objects.filter(id__in=course_ids)

    if request:
        return CourseOverviewRequestUserSerializer(
            overviews,
            many=True,
            context={'request': request}
        ).data
    return CourseOverviewBaseSerializer(overviews, many=True).data

