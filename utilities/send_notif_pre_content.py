from question.models import Question, Answer
from review.models import CompanyReview, Interview, ReviewComment, InterviewComment
from utilities import utilities


def send_notif():
    # review
    for review in CompanyReview.objects.filter(approved=False):
        utilities.telegram_notify('Previous review: on {}, \n {}'.format(
            review.company.name, '#pre_review'
        ), review.id, 'review', review.title, review.description)

    # interview
    for interview in Interview.objects.filter(approved=False):
        utilities.telegram_notify('Previous interview: on {}, \n {}'.format(
            interview.company.name, '#pre_interview'
        ), interview.id, 'interview', interview.title, interview.description)

    # comment review
    for comment in ReviewComment.objects.filter(approved=False):
        utilities.telegram_notify('Previous Review Comment: {}'.format(
            '#pre_review_comment'
        ), comment.id, 'review_comment', None, comment.body)
    # comment interview
    for comment in InterviewComment.objects.filter(approved=False):
        utilities.telegram_notify('Previous Interview Comment: {}'.format(
            '#pre_interview_comment'
        ), comment.id, 'interview_comment', None, comment.body)
    # question
    for question in Question.objects.filter(approved=False):
        utilities.telegram_notify('Previous Question: on {}, \n {}'.format(
            question.company.name, '#pre_question'
        ), question.id, 'question', question.title, question.body)
    # answer
    for answer in Answer.objects.filter(approved=False):
        utilities.telegram_notify('New Answer: on {}, \n {}'.format(
            answer.company.name, '#answer'
        ), answer.id, 'answer', None, answer.body)
