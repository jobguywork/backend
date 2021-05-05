from datetime import datetime, timedelta

from utilities.exceptions import CustomException
from question.models import Question, Answer


def check_create_question_permission(user, company):
    last_question = Question.objects.filter(company=company, creator=user).last()
    if not last_question:
        return
    elif last_question.created + timedelta(days=5) < datetime.now():
        return
    else:
        raise CustomException(detail='You question before', code=403)


def check_create_answer_permission(user, question):
    answered = Answer.objects.filter(creator=user, question=question).last()
    if not answered:
        return
    else:
        raise CustomException(detail='You answered before', code=403)
