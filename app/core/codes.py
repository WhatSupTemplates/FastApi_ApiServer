"""
공통 코드 Enum 정의
Python 코드에서 직접 사용 가능하며, 서버 시작 시 DB와 자동 동기화됩니다.
"""
from enum import Enum


# ============================================================
# 코드 그룹 정의
# ============================================================
class CodeGroup(str, Enum):
    """공통 코드 그룹"""
    USER_STATUS = "USER_STATUS"
    SAMPLE_POST_TYPE = "SAMPLE_POST_TYPE"
    SAMPLE_TASK_PRIORITY = "SAMPLE_TASK_PRIORITY"


# ============================================================
# 개별 코드 Enum 정의
# ============================================================
class UserStatus(str, Enum):
    """사용자 상태 코드"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class SamplePostType(str, Enum):
    """샘플 게시물 유형 코드"""
    NOTICE = "NOTICE"
    GENERAL = "GENERAL"
    FAQ = "FAQ"


class SampleTaskPriority(str, Enum):
    """샘플 할일 우선순위 코드"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


# ============================================================
# 코드 메타데이터 (DB 동기화용)
# ============================================================
CODE_METADATA = {
    CodeGroup.USER_STATUS: {
        "group_name": "사용자 상태",
        "description": "사용자 계정의 활성화 상태를 나타냅니다",
        "codes": {
            UserStatus.ACTIVE: {"name": "활성", "order": 1},
            UserStatus.INACTIVE: {"name": "비활성", "order": 2},
            UserStatus.SUSPENDED: {"name": "정지", "order": 3},
        }
    },
    CodeGroup.SAMPLE_POST_TYPE: {
        "group_name": "게시물 유형",
        "description": "샘플 게시물의 카테고리를 구분합니다",
        "codes": {
            SamplePostType.NOTICE: {"name": "공지사항", "order": 1},
            SamplePostType.GENERAL: {"name": "일반", "order": 2},
            SamplePostType.FAQ: {"name": "FAQ", "order": 3},
        }
    },
    CodeGroup.SAMPLE_TASK_PRIORITY: {
        "group_name": "할일 우선순위",
        "description": "샘플 할일의 중요도를 나타냅니다",
        "codes": {
            SampleTaskPriority.LOW: {"name": "낮음", "order": 1},
            SampleTaskPriority.MEDIUM: {"name": "보통", "order": 2},
            SampleTaskPriority.HIGH: {"name": "높음", "order": 3},
            SampleTaskPriority.URGENT: {"name": "긴급", "order": 4},
        }
    },
}
