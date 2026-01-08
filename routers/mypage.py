from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
import os

from database import get_db
from models import UserAction, Policy, User, categoryColorMap, get_image_for_category, FRONT_TO_DB_CATEGORY, normalize_region_name

# 라우터 설정 (태그 및 프리픽스 설정)
router = APIRouter(prefix="/api/mypage", tags=["mypage"])

# ==================== [Pydantic 스키마] ====================

class ActionCreate(BaseModel):
    user_email: str
    policy_id: int
    type: str  # 'like', 'pass' 등

class PolicyDto(BaseModel):
    id: int
    title: str
    desc: str
    category: str
    date: str
    image: str
    link: str
    region: str
    colorCode: str

class StatsDto(BaseModel):
    labels: List[str]
    data: List[int]

class IconUpdate(BaseModel):
    user_email: str
    icon_name: str

class LikeDeleteRequest(BaseModel):
    user_email: str
    policy_ids: List[int]

# ==================== [API 엔드포인트] ====================

# 4. 사용자 프로필 및 활동 지수 조회 (우선 배치)
@router.get("/profile")
def get_user_profile(user_email: str, db: Session = Depends(get_db)):
    """
    사용자 기본 정보(이름, 이메일, 지역)와 활동 지수(레벨, 뱃지)를 반환합니다.
    """
    # 1. 유저 정보 조회
    user = db.query(User).filter(User.email == user_email).first()
    
    if not user:
        # 유저가 없으면 에러보다는 기본값 반환 (로그인 세션 문제일 수 있음)
        return {"error": "User not found", "name": "알 수 없음", "region": "지역 미설정"}

    # 2. 활동 지수 계산 분모: 해당 지역 정책 개수
    user_region = user.region or "전국"
    search_region = normalize_region_name(user_region)
    
    # 지역 정책 개수
    if search_region == "전국":
        total_policies = db.query(Policy).count()
    else:
        from sqlalchemy import or_
        total_policies = db.query(Policy).filter(
            or_(Policy.region.like(f"%{search_region}%"), Policy.region == "전국")
        ).count()
        
    if total_policies == 0:
        total_policies = 1

    # 3. 활동 지수 계산 분자: 내가 찜한 활동 개수
    like_count = db.query(UserAction).filter(
        UserAction.user_email == user_email, 
        UserAction.type == 'like'
    ).count()

    # 4. 퍼센트 계산
    percentage = int((like_count / total_policies) * 100)
    
    # 5. 레벨 및 칭호 부여
    level_badge = "#정책_기웃러 👀"
    if percentage >= 100:
        level_badge = "#정책_오지라퍼 🗣️📢"
    elif percentage >= 61:
        level_badge = "#인간_정책백과 📖"
    elif percentage >= 31:
        level_badge = "#지원금_사냥꾼 🏹"
    elif percentage >= 11:
        level_badge = "#혜택_줍줍러 🍬"
        
    return {
        "name": user.name,
        "email": user.email,
        "region": user_region,
        "region_badge": f"#{user_region}",
        "activity_index": percentage,
        "level_badge": level_badge,
        "like_count": like_count,
        "like_count": like_count,
        "apply_count": 0,
        "profile_icon": user.profile_icon or "avatar_1" # [NEW]
    }

# 5. 프로필 아이콘 변경
@router.put("/profile/icon")
def update_profile_icon(data: IconUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.profile_icon = data.icon_name
    db.commit()
    
    return {"message": "Profile icon updated", "icon": user.profile_icon}

# 1. 사용자 액션 저장 (좋아요/패스/좋아요 취소)
@router.post("/action")
def save_user_action(action: ActionCreate, db: Session = Depends(get_db)):
    """
    사용자의 스와이프 액션(like/pass) 또는 모달 찜하기(like/unlike)를 처리합니다.
    """
    # 1. 좋아요 취소 (unlike) 처리
    if action.type == 'unlike':
        db.query(UserAction).filter(
            UserAction.user_email == action.user_email,
            UserAction.policy_id == action.policy_id,
            UserAction.type == 'like'
        ).delete()
        db.commit()
        return {"message": "Like removed"}

    # 2. 좋아요 (like) 중복 방지 처리
    if action.type == 'like':
        existing = db.query(UserAction).filter(
            UserAction.user_email == action.user_email,
            UserAction.policy_id == action.policy_id,
            UserAction.type == 'like'
        ).first()
        
        if existing:
            return {"message": "Already liked"}

    # 3. 새로운 액션 저장 (like or pass)
    new_action = UserAction(
        user_email=action.user_email,
        policy_id=action.policy_id,
        type=action.type
    )
    db.add(new_action)
    db.commit()
    
    return {"message": "Action saved", "action_id": new_action.id}

# 1-1. 특정 정책에 대한 좋아요 여부 확인 (버튼 활성화용)
@router.get("/check")
def check_action_status(user_email: str, policy_id: int, db: Session = Depends(get_db)):
    """
    특정 유저가 특정 정책을 이미 'like' 했는지 확인합니다.
    """
    existing = db.query(UserAction).filter(
        UserAction.user_email == user_email,
        UserAction.policy_id == policy_id,
        UserAction.type == 'like'
    ).first()
    
    return {"liked": True if existing else False}


# 2. 찜한 정책 목록 조회 (마이페이지용)
# 2. 찜한 정책 목록 조회 (마이페이지용 - 페이지네이션 적용)
@router.get("/likes")
def get_liked_policies(
    user_email: str, 
    page: int = 1, 
    limit: int = 12, 
    db: Session = Depends(get_db)
):
    """
    해당 유저가 'like'한 정책들의 상세 정보를 반환합니다. (페이지네이션 적용)
    """
    # 1. 쿼리 베이스 (최신순 정렬)
    query = db.query(UserAction).filter(
        UserAction.user_email == user_email, 
        UserAction.type == 'like'
    )
    
    # 2. 전체 개수 계산
    total_count = query.count()
    if total_count == 0:
        return {
            "policies": [],
            "total_count": 0,
            "total_pages": 0,
            "current_page": page
        }

    total_pages = (total_count + limit - 1) // limit
    
    # 페이지 보정
    if page < 1: page = 1
    if page > total_pages: page = total_pages

    offset = (page - 1) * limit

    # 3. 페이지네이션 적용하여 액션 조회
    actions = query.order_by(UserAction.created_at.desc())\
                   .offset(offset)\
                   .limit(limit)\
                   .all()
    
    if not actions:
         return {
            "policies": [],
            "total_count": total_count,
            "total_pages": total_pages,
            "current_page": page
        }

    # 4. Policy ID 리스트 추출 (기존 로직 유지)
    policy_ids = [a.policy_id for a in actions]
    
    # 5. Policy 정보 조회
    policies = db.query(Policy).filter(Policy.id.in_(policy_ids)).all()
    policy_map = {p.id: p for p in policies}
    
    result = []
    seen_ids = set()

    # 6. 순서대로 매핑
    for action in actions:
        pid = action.policy_id
        if pid in seen_ids:
            continue
        
        policy = policy_map.get(pid)
        if policy:
            seen_ids.add(pid)
            
            # 이미지 처리
            img_src = get_image_for_category(policy.genre)
            
            # 날짜 처리
            date_str = "상시 모집"
            if policy.end_date:
                date_str = f"{policy.end_date} 마감"
            elif policy.period:
                date_str = policy.period

            result.append({
                "id": policy.id,
                "title": policy.title,
                "summary": policy.summary or "상세 내용을 확인하세요.",
                "genre": policy.genre or "기타",
                "period": date_str,
                "image": img_src,
                "link": policy.link or "#",
                "region": policy.region or "전국"
            })
            
    return {
        "policies": result,
        "total_count": total_count,
        "total_pages": total_pages,
        "current_page": page
    }


# 2-1. 찜한 정책 선택 삭제 [NEW]
@router.post("/likes/delete")
def delete_liked_policies(data: LikeDeleteRequest, db: Session = Depends(get_db)):
    """
    사용자가 선택한 찜한 정책들을 일괄 삭제합니다.
    """
    # 1. 조건에 맞는(이메일, like타입, 정책ID리스트) 데이터 삭제
    #    synchronize_session=False는 대량 삭제 시 세션 동기화 비용을 줄임
    deleted_count = db.query(UserAction).filter(
        UserAction.user_email == data.user_email,
        UserAction.type == 'like',
        UserAction.policy_id.in_(data.policy_ids)
    ).delete(synchronize_session=False)
    
    db.commit()
    
    return {"message": "Deleted successfully", "count": deleted_count}


# 3. 관심 키워드 트렌드 통계 (차트용)
@router.get("/stats")
def get_user_stats(user_email: str, db: Session = Depends(get_db)):
    """
    유저의 like/pass 데이터를 분석하여 카테고리별 관심도를 반환합니다.
    """
    # 1. 해당 유저의 모든 액션 + 정책 장르 조인 조회
    #    SELECT action.type, policy.genre 
    #    FROM users_action AS action 
    #    JOIN being_test AS policy ON action.policy_id = policy.id
    #    WHERE action.user_email = ...
    
    results = db.query(UserAction.type, Policy.genre)\
        .join(Policy, UserAction.policy_id == Policy.id)\
        .filter(UserAction.user_email == user_email)\
        .all()
        
    # 2. 점수 집계
    #    Like: +10점, Pass: +1점 (예시 로직)
    #    또는 단순히 Like 개수만 셀 수도 있음
    
    category_scores = {}
    
    # 초기화 (모든 카테고리 0점으로 시작하고 싶다면)
    base_categories = ["취업", "창업", "주거", "금융", "교육", "복지"]
    for cat in base_categories:
        category_scores[cat] = 0
        
    for type_, genre in results:
        if not genre: continue
        
        # DB에 저장된 genre가 "취업/직무" 처럼 되어있을 수 있으므로 매핑 확인 필요
        # models.py의 FRONT_TO_DB_CATEGORY는 프론트->DB용이므로, 여기선 DB값을 기준으로 그룹핑
        
        # 간단하게 앞 2글자만 따서 분류하거나 포함여부 확인
        key = "기타"
        if "취업" in genre: key = "취업"
        elif "창업" in genre: key = "창업"
        elif "주거" in genre: key = "주거"
        elif "금융" in genre: key = "금융"
        elif "교육" in genre: key = "교육"
        elif "복지" in genre: key = "복지"
        
        score = 0
        if type_ == 'like':
            score = 10
        elif type_ == 'pass':
            score = 2  # 패스해도 봤다는 것에 의미를 둔다면 점수 부여 (선택사항)
            
        category_scores[key] = category_scores.get(key, 0) + score
        
    # 3. 차트용 데이터 변환
    labels = list(category_scores.keys())
    data = list(category_scores.values())
    
    return {"labels": labels, "data": data}
