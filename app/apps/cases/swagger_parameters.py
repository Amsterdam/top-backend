from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

"""
Manual parameters for the unplanned view in Swagger API documentation
"""
date = OpenApiParameter(
    name="date",
    type=OpenApiTypes.DATE,
    location=OpenApiParameter.QUERY,
    description="Date",
)

postal_code = OpenApiParameter(
    name="postalCode",
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,
    description="Postal Code",
)

street_number = OpenApiParameter(
    name="streetNumber",
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,
    description="Street Number",
)

street_name = OpenApiParameter(
    name="streetName",
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,
    description="Street Name",
)

suffix = OpenApiParameter(
    name="suffix",
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,
    required=False,
    description="Suffix",
)

case_search_parameters = [postal_code, street_number, street_name, suffix]
