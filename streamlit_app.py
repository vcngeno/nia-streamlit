import streamlit as st
import requests
import os
import time

# Page configuration
st.set_page_config(
    page_title="Nia - Your Learning Friend",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stChatMessage {
        background-color: white;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    h1 {
        color: white;
        text-align: center;
        font-size: 3em;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stat-number {
        font-size: 2.5em;
        font-weight: bold;
        color: #667eea;
    }
    .stat-label {
        font-size: 1.2em;
        color: #666;
    }
    </style>
""", unsafe_allow_html=True)

# API Configuration
API_URL = "https://web-production-a4ec.up.railway.app"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "questions_asked" not in st.session_state:
    st.session_state.questions_asked = 0
if "learning_streak" not in st.session_state:
    st.session_state.learning_streak = 0
if "topics_explored" not in st.session_state:
    st.session_state.topics_explored = set()
if "achievements" not in st.session_state:
    st.session_state.achievements = []
if "student_id" not in st.session_state:
    st.session_state.student_id = None
if "student_name" not in st.session_state:
    st.session_state.student_name = None

# Function to create student
def create_student(name, age, grade, special_needs=None, interests=None, reading_level=None):
    try:
        response = requests.post(
            f"{API_URL}/students/create",
            json={
                "name": name,
                "age": age,
                "grade": grade,
                "special_needs": special_needs or [],
                "interests": interests or ["learning", "reading"],
                "reading_level": reading_level
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data.get("student_id"), data.get("message")
        return None, f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return None, f"Connection error: {str(e)}"

# Function to login existing student
def login_student(student_id):
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={"message": "Hi Nia!", "student_id": student_id},
            timeout=10
        )
        if response.status_code == 200:
            return True, "Welcome back!"
        else:
            return False, "Student not found"
    except Exception as e:
        return False, str(e)

# Student registration/login form
if st.session_state.student_id is None:
    st.markdown("# 🌟 Welcome to Nia! 🌟")
    
    tab1, tab2 = st.tabs(["🆕 New Student", "🔑 Returning Student"])
    
    with tab2:
        st.markdown("### Welcome back!")
        st.markdown("Enter your Student ID to continue where you left off.")
        
        with st.form("student_login"):
            student_id_input = st.text_input("Student ID", placeholder="student_1_...")
            login_button = st.form_submit_button("Login 🚀", use_container_width=True)
            
            if login_button:
                if student_id_input:
                    with st.spinner("Logging in..."):
                        success, message = login_student(student_id_input)
                        if success:
                            st.session_state.student_id = student_id_input
                            st.session_state.student_name = "Student"
                            st.success("Welcome back! 🎉")
                            st.rerun()
                        else:
                            st.error(f"Login failed: {message}")
                else:
                    st.warning("Please enter your Student ID")
        
        st.info("💡 Tip: Your Student ID was shown when you first registered.")
    
    with tab1:
        st.markdown("### Let's get to know you first!")
        
        with st.form("student_registration"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("What's your name?", placeholder="Enter your name")
                age = st.number_input("How old are you?", min_value=5, max_value=18, value=10)
            
            with col2:
                grade = st.number_input("What grade are you in?", min_value=1, max_value=12, value=5)
            
            st.markdown("---")
            st.markdown("### 🎯 How do you learn best? (Optional)")
            
            col3, col4 = st.columns(2)
            
            with col3:
                autism_support = st.checkbox("✨ I like clear, step-by-step instructions")
                visual_learner = st.checkbox("🎨 I learn better with pictures")
            
            with col4:
                literal_language = st.checkbox("📝 I prefer straightforward explanations")
                special_interest = st.text_input("🌟 Favorite topic:", placeholder="trains, space...")
            
            reading_level_choice = st.selectbox("📚 Reading level:", 
                                        ["Same as my grade", "I prefer easier words", "I can read harder books"])
            
            submitted = st.form_submit_button("Start Learning! 🚀", use_container_width=True)
            
            if submitted:
                if name:
                    special_needs_list = []
                    if autism_support:
                        special_needs_list.extend(["autism", "step_by_step_instructions", "clear_communication"])
                    if visual_learner:
                        special_needs_list.append("visual_learner")
                    if literal_language:
                        special_needs_list.append("literal_language_preference")
                    
                    interests_list = ["learning", "reading"]
                    if special_interest:
                        interests_list.append(special_interest.lower())
                    
                    read_level = grade
                    if reading_level_choice == "I prefer easier words":
                        read_level = max(1, grade - 1)
                    elif reading_level_choice == "I can read harder books":
                        read_level = min(12, grade + 1)
                    
                    with st.spinner("Creating your profile..."):
                        student_id, message = create_student(
                            name, age, grade,
                            special_needs=special_needs_list,
                            interests=interests_list,
                            reading_level=read_level
                        )
                        if student_id:
                            st.session_state.student_id = student_id
                            st.session_state.student_name = name
                            st.success(f"Welcome, {name}! 🎉")
                            st.info(f"📝 Your Student ID: **{student_id}**")
                            st.warning("⚠️ SAVE THIS ID to login later!")
                            st.balloons()
                            time.sleep(3)
                            st.rerun()
                        else:
                            st.error(f"Error: {message}")
                else:
                    st.warning("Please enter your name!")
    
    st.stop()

# Header
st.markdown(f"# 🌟 Hi {st.session_state.student_name}! 🌟")
st.markdown("### *Ask me anything, and let's learn together!*")

# Sidebar
with st.sidebar:
    st.markdown(f"## 👋 {st.session_state.student_name}")
    
    with st.expander("📝 My Student ID"):
        st.code(st.session_state.student_id, language=None)
        st.caption("Save this to login later!")
    
    st.markdown("---")
    st.markdown("## 🎯 Your Learning Journey")
    
    st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{st.session_state.questions_asked}</div>
            <div class="stat-label">Questions Asked</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{len(st.session_state.topics_explored)}</div>
            <div class="stat-label">Topics Explored</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("## 🏆 Achievements")
    if st.session_state.achievements:
        for achievement in st.session_state.achievements:
            st.success(achievement)
    else:
        st.info("Complete challenges to earn achievements!")
    
    st.markdown("## 💡 Quick Topics")
    topics = ["Math 🔢", "Science 🔬", "Reading 📚", "History 🏛️", "Geography 🌍"]
    for topic in topics:
        if st.button(topic, key=topic):
            st.session_state.quick_topic = topic
    
    st.markdown("---")
    if st.button("🔄 Start New Conversation"):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("👤 Switch Student"):
        st.session_state.student_id = None
        st.session_state.student_name = None
        st.session_state.messages = []
        st.rerun()

# Chat area
st.markdown("---")

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🌟" if message["role"] == "assistant" else "😊"):
        st.markdown(message["content"])

if len(st.session_state.messages) == 0:
    with st.chat_message("assistant", avatar="🌟"):
        welcome_msg = f"""👋 Hi {st.session_state.student_name}! I'm Nia!
        
I'm here to help you learn! Ask me about math, science, reading, history, geography, and more!
        
What would you like to learn today?"""
        st.markdown(welcome_msg)
        st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

if prompt := st.chat_input("Type your question... ✨"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user", avatar="😊"):
        st.markdown(prompt)
    
    with st.chat_message("assistant", avatar="🌟"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/chat",
                    json={"message": prompt, "student_id": st.session_state.student_id},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("response", "Let me think about that differently...")
                    st.markdown(answer)
                    
                    st.session_state.questions_asked += 1
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                    topics_keywords = {
                        "Math": ["math", "number", "calculate"],
                        "Science": ["science", "experiment"],
                        "Reading": ["read", "book", "spell"],
                        "History": ["history", "past"],
                        "Geography": ["geography", "country", "map"]
                    }
                    
                    for topic, keywords in topics_keywords.items():
                        if any(kw in prompt.lower() for kw in keywords):
                            st.session_state.topics_explored.add(topic)
                    
                    if st.session_state.questions_asked == 5 and "First Steps! 🎉" not in st.session_state.achievements:
                        st.session_state.achievements.append("First Steps! 🎉")
                        st.balloons()
                    
                    if len(st.session_state.topics_explored) >= 3 and "Explorer! 🗺️" not in st.session_state.achievements:
                        st.session_state.achievements.append("Explorer! 🗺️")
                        st.snow()
                else:
                    st.error("Connection issue. Try again!")
                    
            except Exception as e:
                st.error("Something went wrong! Try again.")

st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: white; padding: 20px;'>
        <p>Made with ❤️ for curious learners everywhere</p>
        <p>Part of the Abraham Accords Literacy Initiative</p>
    </div>
""", unsafe_allow_html=True)
