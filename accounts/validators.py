from django.core.exceptions import ValidationError
import re

def validate_nickname(value):
    if len(value) < 2:
        raise ValidationError("닉네임은 최소 2자 이상이어야 합니다.")
    if len(value) > 20:
        raise ValidationError("닉네임은 최대 20자까지 허용됩니다.")
    if not re.match(r'^[a-zA-Z0-9가-힣_]+$', value):
        raise ValidationError("닉네임은 영문, 숫자, 한글, 언더스코어(_)만 포함할 수 있습니다.")

def validate_password(value):
    if len(value) < 8:
        raise ValidationError("비밀번호는 최소 8자 이상이어야 합니다.")
    if not re.search(r'[A-Z]', value):
        raise ValidationError("비밀번호는 최소 하나의 대문자를 포함해야 합니다.")
    if not re.search(r'[a-z]', value):
        raise ValidationError("비밀번호는 최소 하나의 소문자를 포함해야 합니다.")
    if not re.search(r'\d', value):
        raise ValidationError("비밀번호는 최소 하나의 숫자를 포함해야 합니다.")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError("비밀번호는 최소 하나의 특수문자를 포함해야 합니다.")