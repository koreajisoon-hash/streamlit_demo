import streamlit as st
import json
import os
import uuid
from datetime import datetime

# --- 데이터 파일 경로 설정 ---
DATA_FILE = 'hospital_sns_data.json'

# --- 데이터 로드 및 저장 함수 ---
def load_data():
    """데이터 파일을 로드하거나, 파일이 없으면 초기 데이터를 반환합니다."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"users": {}, "posts": []}

def save_data(data):
    """현재 데이터를 파일에 저장합니다."""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 초기 데이터 로드 ---
data = load_data()

# --- 현재 사용자 관리 (MVP를 위해 단순화) ---
# 세션 상태에 사용자 ID와 이름을 저장하여 앱 내에서 사용자를 구분합니다.
if 'current_user_id' not in st.session_state:
    st.session_state.current_user_id = None
if 'current_username' not in st.session_state:
    st.session_state.current_username = None

def get_current_user_info():
    """현재 로그인된 사용자 ID와 이름을 반환합니다."""
    return st.session_state.current_user_id, st.session_state.current_username

def set_current_user_info(user_id, username):
    """현재 사용자 정보를 설정합니다."""
    st.session_state.current_user_id = user_id
    st.session_state.current_username = username

# --- 사용자 로그인/등록 UI ---
def user_login_section():
    """사용자 로그인 및 등록 섹션을 렌더링합니다."""
    st.sidebar.header("환자 정보")
    if st.session_state.current_user_id:
        st.sidebar.write(f"현재 로그인: **{st.session_state.current_username}**")
        if st.sidebar.button("로그아웃"):
            set_current_user_info(None, None)
            st.rerun() # 로그아웃 후 앱 새로고침
    else:
        username_input = st.sidebar.text_input("사용자 이름 입력", key="username_input")
        if st.sidebar.button("로그인 / 사용자 등록"):
            if username_input:
                # 기존 사용자인지 확인
                found_user_id = None
                for user_id, user_info in data["users"].items():
                    if user_info["username"] == username_input:
                        found_user_id = user_id
                        break

                if found_user_id:
                    set_current_user_info(found_user_id, username_input)
                    st.sidebar.success(f"환영합니다, {username_input}님!")
                else:
                    # 새 사용자 등록
                    new_user_id = str(uuid.uuid4())
                    data["users"][new_user_id] = {"username": username_input}
                    save_data(data)
                    set_current_user_info(new_user_id, username_input)
                    st.sidebar.success(f"새로운 환자 {username_input}님으로 등록되었습니다!")
                st.rerun() # 사용자 설정 후 앱 새로고침
            else:
                st.sidebar.warning("사용자 이름을 입력해주세요.")

# --- 메인 앱 시작 ---
def main():
    st.set_page_config(page_title="병원 환자 소통 공간", layout="centered")

    # 커스텀 CSS를 사용하여 앱 전체의 스타일을 개선합니다.
    st.markdown("""
        <style>
        .main {
            background-color: #f0f2f6; /* 연한 배경색 */
            padding: 20px;
            border-radius: 10px;
        }
        .stButton>button {
            border-radius: 20px;
            border: 1px solid #4CAF50;
            color: #4CAF50;
            background-color: white;
            padding: 8px 16px;
            font-size: 16px;
            transition: all 0.2s ease-in-out;
        }
        .stButton>button:hover {
            background-color: #4CAF50;
            color: white;
            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        }
        .post-card {
            background-color: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.1);
            border-left: 5px solid #4CAF50; /* 포인트 색상 */
        }
        .post-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .post-username {
            font-weight: bold;
            font-size: 1.2em;
            color: #333;
        }
        .post-time {
            color: #888;
            font-size: 0.85em;
        }
        .retweet-indicator {
            color: #666;
            font-style: italic;
            margin-bottom: 5px;
        }
        .original-post-quote {
            background-color: #f9f9f9;
            border-left: 3px solid #ccc;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        }
        </style>
        """, unsafe_allow_html=True)

    st.title("👨‍👩‍👧‍👦 병원 환자 소통 공간")
    st.markdown("---")

    user_login_section()

    current_user_id, current_username = get_current_user_info()

    if not current_user_id:
        st.info("왼쪽 사이드바에서 사용자 이름으로 로그인하거나 등록해주세요.")
        return # 로그인하지 않으면 다른 기능 표시 안 함

    # --- 게시글 작성 섹션 ---
    st.header("📝 새 게시글 작성")
    with st.form("new_post_form", clear_on_submit=True):
        post_content = st.text_area("당신의 생각을 공유해주세요...", height=100, max_chars=500,
                                     placeholder="오늘 있었던 일이나, 궁금한 점을 적어보세요!")
        submitted = st.form_submit_button("게시하기")
        if submitted:
            if post_content:
                new_post_id = str(uuid.uuid4())
                new_post = {
                    "id": new_post_id,
                    "user_id": current_user_id,
                    "content": post_content,
                    "timestamp": datetime.now().isoformat(),
                    "likes": [], # 좋아요를 누른 사용자 ID 목록
                    "retweet_count": 0, # 이 게시글이 리트윗된 횟수 (오리지널 게시글만 해당)
                    "original_post_id": None # 리트윗된 게시글의 원본 ID
                }
                data["posts"].insert(0, new_post) # 최신 게시글을 맨 위에 추가
                save_data(data)
                st.success("게시글이 성공적으로 작성되었습니다! ✨")
                st.rerun()
            else:
                st.warning("내용을 입력해주세요. 😅")

    st.markdown("---")

    # --- 게시글 목록 조회 섹션 ---
    st.header("⏳ 최신 게시글")

    if not data["posts"]:
        st.info("아직 게시글이 없습니다. 첫 게시글을 작성해보세요! ✍️")
        return

    # 시간순으로 정렬 (최신글이 위에 오도록)
    sorted_posts = sorted(data["posts"], key=lambda x: x['timestamp'], reverse=True)

    for post in sorted_posts:
        with st.container(): # 각 게시글을 컨테이너로 묶어 스타일 적용
            st.markdown('<div class="post-card">', unsafe_allow_html=True) # 커스텀 CSS 클래스 적용
            post_user_id = post["user_id"]
            # 게시글 작성자 이름 찾기
            post_username = data["users"].get(post_user_id, {}).get("username", "알 수 없음")
            post_time = datetime.fromisoformat(post['timestamp']).strftime("%Y년 %m월 %d일 %H:%M")

            # 리트윗 여부 확인 및 원본 게시글 정보 가져오기
            is_retweet = post.get("original_post_id") is not None
            original_post_content = ""
            original_post_username = ""

            if is_retweet:
                original_post_id = post["original_post_id"]
                original_post = next((p for p in data["posts"] if p["id"] == original_post_id), None)
                if original_post:
                    original_post_content = original_post["content"]
                    original_post_username = data["users"].get(original_post["user_id"], {}).get("username", "알 수 없음")

            st.markdown(f'<div class="post-header"><span class="post-username">{post_username}</span><span class="post-time">{post_time}</span></div>', unsafe_allow_html=True)
            if is_retweet:
                st.markdown(f'<p class="retweet-indicator">🔄 **{post_username} 님이 리트윗했습니다.**</p>', unsafe_allow_html=True)
                st.markdown(f'<div class="original-post-quote">', unsafe_allow_html=True)
                st.markdown(f"> *원본: **{original_post_username}***")
                st.markdown(f"> \"{original_post_content}\"")
                st.markdown(f'</div>', unsafe_allow_html=True) # original-post-quote 닫기
            st.write(post['content'])

            # 좋아요 및 리트윗 버튼
            col1, col2 = st.columns([1, 10]) # 버튼 공간을 위해 컬럼 분할

            with col1:
                liked_by_current_user = current_user_id in post.get("likes", [])
                like_button_label = "❤️ 좋아요" if not liked_by_current_user else "💔 좋아요 취소"
                if st.button(f"{like_button_label} {len(post.get('likes', []))}", key=f"like_{post['id']}"):
                    if liked_by_current_user:
                        post["likes"].remove(current_user_id)
                    else:
                        post["likes"].append(current_user_id)
                    save_data(data)
                    st.rerun() # 상태 변경 후 새로고침

            with col2:
                if not is_retweet: # 리트윗된 게시글은 다시 리트윗할 수 없도록
                    if st.button(f"🔄 리트윗 {post.get('retweet_count', 0)}", key=f"retweet_{post['id']}"):
                        retweet_id = str(uuid.uuid4())
                        retweet_content = f"\" {post['content'][:50]}... \"" if len(post['content']) > 50 else f"\" {post['content']} \""
                        new_retweet_post = {
                            "id": retweet_id,
                            "user_id": current_user_id,
                            "content": f"리트윗: {retweet_content}", # 리트윗 내용
                            "timestamp": datetime.now().isoformat(),
                            "likes": [],
                            "retweet_count": 0, # 리트윗 자체는 리트윗 카운트가 없음
                            "original_post_id": post['id'] # 원본 게시글 ID 저장
                        }
                        data["posts"].insert(0, new_retweet_post) # 새 게시글로 추가

                        # 원본 게시글의 리트윗 카운트 증가
                        original_post_index = next((i for i, p in enumerate(data["posts"]) if p["id"] == post['id']), None)
                        if original_post_index is not None:
                            data["posts"][original_post_index]["retweet_count"] += 1

                        save_data(data)
                        st.success("게시글을 리트윗했습니다! 👍")
                        st.rerun()
                else:
                    st.write(f"") # 리트윗된 게시글은 리트윗 버튼 숨김

            st.markdown("</div>", unsafe_allow_html=True) # post-card 닫기
            # st.markdown("---") # 각 게시글 구분선을 이제 post-card 스타일로 대체


if __name__ == "__main__":
    main()


