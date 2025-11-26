import json
from decimal import Decimal
from django.core.management.base import BaseCommand
from curriculum.models import Course, Track, TrackCourse

CATEGORY_MAP = {
    "전공필수": "MAJOR_BASIC",
    "전공선택": "MAJOR_BASIC",
    "심화전공": "MAJOR_DEEP",
    "전공탐색": "EXPLORATION",
    "교양기초": "GE_BASIC",
    "교양필수": "GE_UNIV_REQUIRED",

    "교양-1영역": "GE_UNIV_ELECTIVE_1",
    "교양-2영역": "GE_UNIV_ELECTIVE_2",
    "교양-3영역": "GE_UNIV_ELECTIVE_3",
    "교양-4영역": "GE_UNIV_ELECTIVE_4",
    "교양-5영역": "GE_UNIV_ELECTIVE_5",
    "교양-6영역": "GE_UNIV_ELECTIVE_6",
    "교양-9영역": "GE_UNIV_ELECTIVE_9",
}

REQUIRED_MAP = {
    "전공필수": True,
    "교양필수": True,
}

TRACK_MAP = {
    "ai_bigdata": "AI_BIGDATA",
    "ai_media": "AI_MEDIA",
    "ai_science": "AI_SCIENCE",
    "smart_iot": "SMART_IOT",
    "security": "SECURITY",
}


def extract_ge_area(category_name: str):
    """ '교양-3영역' → '3영역' """
    if category_name.startswith("교양-") and category_name.endswith("영역"):
        return category_name.replace("교양-", "")
    return None


class Command(BaseCommand):
    help = "한국어 JSON 기반 과목 + 트랙 데이터 로드"

    def add_arguments(self, parser):
        parser.add_argument("json_path", type=str)

    def handle(self, *args, **options):
        path = options["json_path"]

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR("JSON 파일 없음"))
            return

        total = 0

        for category_name, course_list in data.items():

            if category_name == "트랙전필":
                continue

            if category_name not in CATEGORY_MAP:
                continue

            category_code = CATEGORY_MAP[category_name]
            ge_area = extract_ge_area(category_name)

            for c in course_list:
                code = c.get("code")
                name = c.get("name")
                credits = Decimal(str(c.get("credits", 0)))

                # 자동 레벨 추출
                level = 1000
                if code[0] in ["S", "Y"] and code[3].isdigit():
                    level = int(code[3]) * 1000

                Course.objects.update_or_create(
                    code=code,
                    defaults={
                        "name": name,
                        "credits": credits,
                        "category": category_code,
                        "ge_area": ge_area,
                        "level": level,
                        "is_required": REQUIRED_MAP.get(category_name, False),
                        "is_major_required": (category_name == "전공필수"),
                        "major_type": (
                            "SW_DEEP" if category_code == "MAJOR_DEEP"
                            else "SW_BASIC" if category_code == "MAJOR_BASIC"
                            else "NONE"
                        )
                    }
                )
                total += 1

        # 트랙 처리
        track_data = data.get("트랙전필", {})
        for track_key, items in track_data.items():
            if track_key not in TRACK_MAP:
                continue

            track_obj, _ = Track.objects.get_or_create(name=TRACK_MAP[track_key])

            for item in items:
                try:
                    course = Course.objects.get(code=item["code"])
                except Course.DoesNotExist:
                    continue

                TrackCourse.objects.update_or_create(
                    track=track_obj,
                    course=course,
                    defaults={"is_track_required": True}
                )

        self.stdout.write(self.style.SUCCESS(f"총 {total}개 과목 등록 완료"))