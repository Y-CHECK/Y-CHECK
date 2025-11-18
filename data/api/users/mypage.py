# api/users/mypage.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def mypage_view(request):
    user = request.user  # 로그인한 사용자

    if request.method == "POST":
        # 수정 가능한 필드들만 업데이트
        email = request.POST.get("email")
        grade_semester = request.POST.get("grade_semester")
        interest_field = request.POST.get("interest_field")
        info_agree = request.POST.get("info_agree") == "on"
        new_password = request.POST.get("password")

        if email:
            user.email = email

        if grade_semester:
            user.grade_semester = grade_semester

        user.interest_field = interest_field
        user.info_agree = info_agree

        # 비밀번호 변경은 입력이 있을 때만
        if new_password:
            user.set_password(new_password)

        user.save()

        # 비밀번호 변경 시 다시 로그인 필요할 수 있음 (나중에 처리 가능)
        return redirect("users:mypage")  # 자기 자신으로 리다이렉트

    context = {
        "user_obj": user,
    }
    return render(request, "users/mypage.html", context)