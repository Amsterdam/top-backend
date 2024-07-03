from datetime import datetime


def get_days_in_range(start_date, end_date):
    """
    Return the number of days within a range
    Any days that fall outside of the current year are not counted
    """
    if end_date < start_date:
        raise ValueError("The end date is earlier then start date")

    current_year = datetime.now().year
    start_year = start_date.year
    end_year = end_date.year

    # Normal case, when both dates fall into the current year
    if start_year == current_year and end_year == current_year:
        return (end_date - start_date).days
    if start_year != current_year and end_year == current_year:
        # If the start date doesn't fall in the current year, start counting from the first day
        start_date = datetime(current_year, 1, 1)
        return (end_date - start_date).days
    if start_year == current_year and end_year != current_year:
        # If the end date doesn't fall in the current year, count until the first day of the next year
        end_date = datetime(current_year + 1, 1, 1)
        return (end_date - start_date).days

    return 0
