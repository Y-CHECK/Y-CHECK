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

    # 2) 추가 정보
    student_id = request.POST.get('student_id')      # 학번
    real_name = request.POST.get('real_name')        # 실명
    current_semester = request.POST.get('current_semester')
    major_department = request.POST.get('major_department')  # ⭐ 새 필드
    interest = request.POST.get('interest')
    interest_text = request.POST.get('interest_text')
    data_consent = request.POST.get('data_consent')

    # 필수 체크
    if not username or not password:
        return JsonResponse({'message': '아이디와 비밀번호는 필수입니다.'}, status=400)

    if not student_id or not real_name:
        return JsonResponse({'message': '학번과 이름은 필수입니다.'}, status=400)

    # 학년/학기 값 체크
    valid_semesters = {"1-1","1-2","2-1","2-2","3-1","3-2","4-1","4-2"}
    if current_semester not in valid_semesters:
        return JsonResponse({'message': '학년/학기 값이 올바르지 않습니다.'}, status=400)

    # 학과/학부 체크
    valid_departments = {
        "SOFTWARE",
        "DATASCIENCE",
        "AI_SEMI",
        "BIOMED",
        "CLINICAL",
        "OCC_THERAPY"
    }
    if major_department not in valid_departments:
        return JsonResponse({'message': '학과/학부 값이 올바르지 않습니다.'}, status=400)

    # 관심 분야 체크
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

    if interest == "OTHER" and not interest_text:
        return JsonResponse({'message': '기타를 선택하셨다면 내용을 입력해 주세요.'}, status=400)

    # 데이터 동의 확인
    consent_ok = str(data_consent).lower() in ("on", "true", "1", "yes")
    if not consent_ok:
        return JsonResponse({'message': '데이터 사용에 동의해야 회원가입이 가능합니다.'}, status=400)

    # 중복 체크
    if User.objects.filter(username=username).exists():
        return JsonResponse({'message': '이미 존재하는 아이디입니다.'}, status=409)

    if UserProfile.objects.filter(student_id=student_id).exists():
        return JsonResponse({'message': '이미 등록된 학번입니다.'}, status=409)

    try:
        with transaction.atomic():
            # 1) Django User 생성 (email 사용 안 함)
            user = User.objects.create_user(
                username=username,
                password=password,
                email=""   # 이메일 비사용
            )

            # 2) 프로필 생성
            UserProfile.objects.create(
                user=user,
                student_id=student_id,
                real_name=real_name,
                current_semester=current_semester,
                major_department=major_department,
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
