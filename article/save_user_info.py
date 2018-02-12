
from article.models import UserStatus, NewsRecord

'''
article/save_user_info
'''


def save_user_status(user_status):
    """
    :param user_status: 사용자의 정보를 저장하는 class (사용자의 user_key, 성별, 생년, 지역, 열람한 뉴스 목록, 서비스 제공을 위한 파라미터 정보를 저장한다.)
    :return: None
    """
    if user_status.recommend_service == 'Y':
        user_status_recommend_service = True
    else:
        user_status_recommend_service = False

    if user_status.remove_seen_news == 'Y':
        user_status_remove_seen_news = True
    else:
        user_status_remove_seen_news = False

    user_status_instance = UserStatus(
        user_key=user_status.user_key,
        gender=user_status.gender,
        birth_year=user_status.birth_year,
        location=user_status.location,
        recommend_service=user_status_recommend_service,
        remove_seen_news=user_status_remove_seen_news,
    )
    user_status_instance.save()


def update_user_status(user_status):
    user_status_instance = UserStatus.objects.get(user_status.user_key)
    user_status_instance.save(update_user_status(user_status))


def save_news_record(user_key, news_record):
    news_record_instance = NewsRecord(
        request_news_id=news_record.document_id,
        request_press=news_record.press,
        request_category=news_record.category,
        request_title=news_record.title,
        request_time=news_record.request_time,
        user_status=UserStatus.objects.get(user_key=user_key),
    )
    news_record_instance.save()

