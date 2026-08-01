from .schema import (
    ValidationIssue,
    IssueSeverity
)


class ReviewQueue:

    def __init__(self):
        print("Review Queue Initialized")

    def generate_review_queue(self, issues):

        review_items = []

        for issue in issues:

            if issue.severity in [
                IssueSeverity.WARNING,
                IssueSeverity.ERROR
            ]:
                review_items.append(issue)

        return review_items