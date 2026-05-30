"""
Azure code <-> AWS code mapping

"""
# ─── 클라우드 코드 매핑 테이블 ──────────────────────────────────────────────

AZURE_TO_AWS = {
    "koreacentral": "ap-northeast-2",   # 서울
    "japaneast":    "ap-northeast-1",   # 도쿄
    "eastus":       "us-east-1",        # 버지니아
}

# 역방향 매핑 (자동 생성)
AWS_TO_AZURE = {v: k for k, v in AZURE_TO_AWS.items()}


# ─── 변환 함수 ──────────────────────────────────────────────────────────────

def azure_to_aws(azure_code: str) -> str:
    """
    Azure region code(AI) -> AWS region code(backend)
    """
    if azure_code not in AZURE_TO_AWS:
        supported = ", ".join(AZURE_TO_AWS.keys())
        raise ValueError(
            f"매핑되지 않은 Azure 리전: {azure_code} (지원: {supported})"
        )
    return AZURE_TO_AWS[azure_code]


def aws_to_azure(aws_code: str) -> str:
    """
    AWS region code -> Azure region code
    """
    if aws_code not in AWS_TO_AZURE:
        supported = ", ".join(AWS_TO_AZURE.keys())
        raise ValueError(
            f"매핑되지 않은 AWS 리전: {aws_code} (지원: {supported})"
        )
    return AWS_TO_AZURE[aws_code]


def get_supported_azure_regions() -> list[str]:
    """ 지원하는 Azure 리전 코드 목록 """
    return list(AZURE_TO_AWS.keys())


def get_supported_aws_regions() -> list[str]:
    """ 지원하는 AWS 리전 코드 목록 """
    return list(AWS_TO_AZURE.keys())