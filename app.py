import streamlit as st
from datetime import datetime

# --- 세션 상태 초기화 및 예시 게시글 추가 ---
if 'init_state' not in st.session_state:
    st.session_state.init_state = True
    st.session_state['posts'] = [
        {
            "id": 0,
            "author": "김의료",
            "title": "[질병 정보] 고혈압 환자 식단 관리 팁 공유해요",
            "content": "안녕하세요. 고혈압 진단받고 식단 관리 중인 3년차 환자입니다. 짠 음식을 줄이는 게 정말 중요한데, 저염식을 맛있게 만드는 몇 가지 팁을 공유하고 싶어요. 먼저...",
            "created_at": "2025-08-15 10:00:00"
        },
        {
            "id": 1,
            "author": "익명",
            "title": "[치료 후기] 강남세브란스병원 암 수술 후기입니다",
            "content": "얼마 전 강남세브란스에서 위암 수술을 받았습니다. 수술 전후 과정이 궁금하실 분들을 위해 상세한 후기를 남겨봅니다. 입원부터 퇴원까지 전반적으로...",
            "created_at": "2025-08-16 14:30:00"
        },
        {
            "id": 2,
            "author": "박간호",
            "title": "[일상 공유] 입원 중 소소한 행복 찾기",
            "content": "병원에 오래 있다 보면 답답할 때가 많죠. 저는 작은 화분을 키우거나, 창가에서 좋아하는 음악을 들으며 기분 전환을 해요. 여러분은 어떤 방법으로 힘든 시간을 이겨내시나요?",
            "created_at": "2025-08-17 09:15:00"
        }
    ]
    st.session_state['comments'] = {0: [], 1: [], 2: []}
    st.session_state['likes'] = {0: 15, 1: 28, 2: 5}
    st.session_state['search_query'] = ""
    st.session_state['current_tab'] = "main"
    st.session_state['sort_option'] = "최신순"

# --- 페이지 설정 ---
st.set_page_config(
    page_title="따뜻한 동행",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 함수 정의 ---
def create_header():
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        st.header("커뮤니티")
    with col2:
        st.markdown("<h1 style='text-align: center;'>💚 따뜻한 동행</h1>", unsafe_allow_html=True)
    with col3:
        if st.button("새 글 작성", key="header_write_button"):
            st.session_state.current_tab = "write"
    st.markdown("---")

def create_left_sidebar():
    with st.sidebar:
        st.subheader("🔍 검색")
        search_query = st.text_input("제목 또는 내용", value=st.session_state['search_query'], key="sidebar_search_bar")
        
        st.markdown("---")
        st.subheader("📋 카테고리")
        categories = ["전체", "질병 정보", "치료 후기", "일상 공유", "병원 정보"]
        for cat in categories:
            if st.button(cat, use_container_width=True, key=f"sidebar_cat_{cat}"):
                st.session_state.current_tab = "main"
        
        st.markdown("---")
        st.subheader("🏥 병원별 게시판")
        hospitals = ["강남세브란스병원", "서울아산병원", "삼성서울병원"]
        for hosp in hospitals:
             if st.button(hosp, use_container_width=True, key=f"sidebar_hosp_{hosp}"):
                st.session_state.current_tab = "main"
        
        return search_query

def create_right_sidebar():
    with st.expander("🔥 인기 게시글", expanded=True):
        sorted_posts_by_likes = sorted(st.session_state['posts'], key=lambda x: st.session_state['likes'].get(x['id'], 0), reverse=True)
        if sorted_posts_by_likes:
            for i, post in enumerate(sorted_posts_by_likes[:5]):
                st.markdown(f"**{i+1}. {post['title']}**")
                st.markdown(f"<small>{st.session_state['likes'].get(post['id'], 0)} 공감</small>", unsafe_allow_html=True)
        else:
            st.info("인기 게시글이 없습니다.")

    st.markdown("---")

    with st.expander("🔔 새 소식", expanded=True):
        notices = ["커뮤니티 이용 수칙 안내", "시스템 점검 안내", "새로운 기능 업데이트"]
        for notice in notices:
            st.write(f"- {notice}")

def display_post_card(post):
    with st.container(border=True):
        tag = ""
        if "질병" in post['title']:
            tag = "[질병 정보]"
        elif "치료" in post['title']:
            tag = "[치료 후기]"
        else:
            tag = "[자유 게시판]"
            
        st.subheader(f"{tag} {post['title']}")
        st.markdown(f"<small><b>{post['author']}</b> | {post['created_at']}</small>", unsafe_allow_html=True)
        
        content_preview = post['content'].replace('\n', ' ')
        content_preview = content_preview[:100] + "..." if len(content_preview) > 100 else content_preview
        st.markdown(f"<p style='margin-top: 10px; margin-bottom: 10px;'>{content_preview}</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.markdown(f"💬 {len(st.session_state['comments'].get(post['id'], []))}")
        with col2:
            st.markdown(f"👍 {st.session_state['likes'].get(post['id'], 0)}")
        with col3:
            st.markdown("🔗 공유하기")
        
        with st.expander("전체 내용 및 댓글 보기", expanded=False):
            st.write(post['content'])
            
            st.markdown("---")
            st.write("##### 댓글")
            if st.session_state['comments'].get(post['id']):
                for comment in st.session_state['comments'][post['id']]:
                    st.markdown(f"- {comment}")
            else:
                st.info("아직 댓글이 없습니다.")

            with st.form(f"comment_form_{post['id']}", clear_on_submit=True):
                comment_text = st.text_input("댓글을 작성하세요", key=f"comment_{post['id']}", placeholder="따뜻한 한마디를 남겨주세요...")
                comment_submit = st.form_submit_button("댓글 달기")
                if comment_submit and comment_text:
                    st.session_state['comments'][post['id']].append(comment_text)
                    st.rerun()

            if st.button("공감", key=f"like_button_{post['id']}", use_container_width=True):
                st.session_state['likes'][post['id']] = st.session_state['likes'].get(post['id'], 0) + 1
                st.rerun()
                
def create_write_form():
    st.subheader("새 게시글 작성")
    with st.form("new_post_form", clear_on_submit=True):
        col1, col2 = st.columns([1, 2])
        with col1:
            author = st.text_input("작성자 (선택)", placeholder="익명")
        with col2:
            title = st.text_input("제목", placeholder="제목을 입력하세요")
        content = st.text_area("내용", height=200, placeholder="내용을 입력하세요")
        
        submitted = st.form_submit_button("글쓰기")
        
        if submitted and title and content:
            post_id = len(st.session_state['posts'])
            new_post = {
                "id": post_id,
                "author": author if author else "익명",
                "title": title,
                "content": content,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state['posts'].append(new_post)
            st.session_state['comments'][post_id] = []
            st.session_state['likes'][post_id] = 0
            st.success("게시글이 성공적으로 등록되었습니다.")
            st.session_state.current_tab = "main"
            st.rerun()

def create_main_content(search_query):
    col_main, col_right_sidebar = st.columns([4, 1], gap="large")

    with col_main:
        if st.session_state.current_tab == "main":
            st.markdown("### 👋 따뜻한 동행에 오신 것을 환영합니다!")
            st.info("이곳은 서로에게 힘이 되어주는 따뜻한 공간입니다. 궁금한 점을 물어보거나 치료 경험을 나눠보세요.")
            
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.metric("총 게시글", len(st.session_state['posts']))
            with col_info2:
                total_comments = sum(len(c) for c in st.session_state['comments'].values())
                st.metric("총 댓글 수", total_comments)
            
            st.markdown("---")
            st.subheader("📋 전체 게시판")
            
            sort_option = st.radio("정렬 기준", ["최신순", "인기순"], horizontal=True, key="sort_radio")
            
            filtered_posts = [
                p for p in st.session_state['posts']
                if search_query.lower() in p['title'].lower() or search_query.lower() in p['content'].lower()
            ]

            if sort_option == "최신순":
                sorted_posts = sorted(filtered_posts, key=lambda x: x['created_at'], reverse=True)
            else:
                sorted_posts = sorted(filtered_posts, key=lambda x: st.session_state['likes'].get(x['id'], 0), reverse=True)

            if sorted_posts:
                for post in sorted_posts:
                    display_post_card(post)
            else:
                st.info("게시글이 없거나 검색 결과가 없습니다.")
            
            st.markdown("---")
            st.markdown("### 📢 자주 묻는 질문 (FAQ)")
            with st.expander("Q. 이 커뮤니티는 어떤 곳인가요?"):
                st.write("A. 환우들이 서로의 경험과 정보를 나누고, 위로와 응원을 주고받는 공간입니다.")
            with st.expander("Q. 개인 정보가 안전한가요?"):
                st.write("A. 익명으로 활동할 수 있으며, 민감한 개인 정보는 공유하지 않도록 권장하고 있습니다.")
                
        elif st.session_state.current_tab == "write":
            create_write_form()

    with col_right_sidebar:
        create_right_sidebar()

# --- 앱 실행 ---
create_header()
search_query = create_left_sidebar()
create_main_content(search_query)