from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import UserProfile, UserSummary

@login_required
def main_profile_api(request):
    user = request.user

    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return JsonResponse({"success": False, "message": "Profile not found"}, status=400)

    return JsonResponse({
        "success": True,
        "profile": {
            "real_name": profile.real_name,
            "student_id": profile.student_id,
            "current_semester": profile.current_semester,
            "major_department": profile.major_department,
        }
    })


@login_required
def main_summary_api(request):
    try:
        summary = UserSummary.objects.get(user=request.user)
    except UserSummary.DoesNotExist:
        return JsonResponse({"success": False, "message": "No summary data"}, status=404)

    return JsonResponse({
        "success": True,
        "summary": {
            "total_credits": summary.total_credits,
            "major_basic": summary.major_basic,
            "major_deep": summary.major_deep,
            "general": summary.general,
            "selected_courses": summary.selected_courses[:3],  # 3개만
        }
    })
