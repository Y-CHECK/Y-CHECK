# users/register.py
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError, transaction

from .models import UserProfile


@csrf_exempt
def register_api(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'POST만 지원합니다.'}, status=405)

    # 1) 기본 로그인 정보
    username = request.POST.get('username')
    password = request.POST.get('password')
    email = request.POST.get('email')

    # 2) 추가 정보
    student_id = request.POST.get('student_id')      # 학번
    real_name = request.POST.get('real_name')        # 실명
    current_semester = request.POST.get('current_semester')  # "1-1" 이런 값으로 올 걸 기대
    interest = request.POST.get('interest')          # 위에서 정의한 코드값
    interest_text = request.POST.get('interest_text')  # 기타일 때만
    data_consent = request.POST.get('data_consent')  # 체크박스: "on" 이나 "true" 로 올 수 있음

    # 0. 필수값 체크
    if not username or not password:
        return JsonResponse({'message': '아이디와 비밀번호는 필수입니다.'}, status=400)

    if not student_id or not real_name:
        return JsonResponse({'message': '학번과 이름은 필수입니다.'}, status=400)

    # 학년/학기 값이 우리가 정한 드롭다운 중 하나인지 확인
    valid_semesters = {"1-1","1-2","2-1","2-2","3-1","3-2","4-1","4-2"}
    if current_semester not in valid_semesters:
        return JsonResponse({'message': '학년/학기 값이 올바르지 않습니다.'}, status=400)

    # 관심 분야 값 확인
    valid_interests = {
        "AI_ML",
        "SECURITY_NETWORK",
        "GAME_MEDIA",
        "EMBEDDED_SYSTEM",
        "STARTUP_SERVICE",
        "OTHER",
    }
    if interest not in valid_interests:
        return JsonResponse({'message': '관심 분야 값이 올바르지 않습니다.'}, status=400)

    # 기타인데 내용이 비어 있으면 에러
    if interest == "OTHER" and not interest_text:
        return JsonResponse({'message': '기타를 선택하셨다면 내용을 입력해 주세요.'}, status=400)

    # 데이터 사용 동의 확인 (체크박스면 보통 "on", "true", "1" 같은 값이 옴)
    consent_ok = str(data_consent).lower() in ("on", "true", "1", "yes")
    if not consent_ok:
        return JsonResponse({'message': '데이터 사용에 동의해야 회원가입이 가능합니다.'}, status=400)

    # 이미 존재하는 유저 체크
    if User.objects.filter(username=username).exists():
        return JsonResponse({'message': '이미 존재하는 아이디입니다.'}, status=409)

    # 학번도 유니크하게 관리하고 싶으면 여기서도 한 번 더 체크
    if UserProfile.objects.filter(student_id=student_id).exists():
        return JsonResponse({'message': '이미 등록된 학번입니다.'}, status=409)

    try:
        with transaction.atomic():
            # 1) 기본 User 생성
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
            )

            # 2) 프로필 생성
            UserProfile.objects.create(
                user=user,
                student_id=student_id,
                real_name=real_name,
                current_semester=current_semester,
                interest=interest,
                interest_text=interest_text or "",
                data_consent=consent_ok,
            )

    except IntegrityError as e:
        return JsonResponse(
            {'message': 'DB 처리 중 오류가 발생했습니다.', 'error': str(e)},
            status=500,
        )

    return JsonResponse(
        {
            'message': '회원가입 성공',
            'user_id': user.id,
        },
        status=201,
    )