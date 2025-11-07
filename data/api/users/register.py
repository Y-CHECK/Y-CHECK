from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError

@csrf_exempt
def register_api(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'POST만 지원합니다.'}, status=405)

    username = request.POST.get('username')
    password = request.POST.get('password')
    email = request.POST.get('email')

    if not username or not password:
        return JsonResponse({'message': '아이디와 비밀번호는 필수입니다.'}, status=400)

    # 이미 존재하는 유저 체크
    if User.objects.filter(username=username).exists():
        return JsonResponse({'message': '이미 존재하는 아이디입니다.'}, status=409)

    try:
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
        )
    except IntegrityError as e:
        # DB 제약조건 위반 등
        return JsonResponse(
            {'message': 'DB 처리 중 오류가 발생했습니다.', 'error': str(e)},
            status=500,
        )

    return JsonResponse({'message': '회원가입 성공', 'user_id': user.id}, status=201)
