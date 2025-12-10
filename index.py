from flask import Flask, request, render_template, jsonify, session
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Import LangChain components
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here-change-in-production-2024')

# ================= MULTI-USER CONFIGURATION =================

# Directory untuk menyimpan data per user
USERS_DATA_DIR = "users_data"
if not os.path.exists(USERS_DATA_DIR):
    os.makedirs(USERS_DATA_DIR)

# File untuk menyimpan daftar username yang terdaftar
USERS_FILE = "registered_users.json"

def load_registered_users():
    """Load list of registered usernames"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_registered_user(username):
    """Save new username to registered users"""
    users = load_registered_users()
    if username not in users:
        users.append(username)
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

def get_user_directory(username):
    """Get or create user's data directory"""
    user_dir = os.path.join(USERS_DATA_DIR, username)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    return user_dir

def get_user_chat_history_file(username):
    """Get path to user's chat history file"""
    user_dir = get_user_directory(username)
    return os.path.join(user_dir, "chat_history.json")

def get_user_portfolio_file(username):
    """Get path to user's portfolio data file"""
    user_dir = get_user_directory(username)
    return os.path.join(user_dir, "portfolio_data.json")

def get_user_chroma_dir(username):
    """Get path to user's ChromaDB directory"""
    user_dir = get_user_directory(username)
    chroma_dir = os.path.join(user_dir, "chroma_db")
    if not os.path.exists(chroma_dir):
        os.makedirs(chroma_dir)
    return chroma_dir

# ================= PERSISTENT STORAGE =================

CHAT_HISTORY_FILE = "chat_history.json"  # Legacy, akan diganti dengan per-user

def load_chat_history(username=None):
    """Load chat history dari file JSON"""
    if username:
        chat_file = get_user_chat_history_file(username)
    else:
        chat_file = CHAT_HISTORY_FILE

    if os.path.exists(chat_file):
        try:
            with open(chat_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading chat history: {e}")
            return []
    return []

def save_chat_history(messages, username=None):
    """Save chat history ke file JSON"""
    if username:
        chat_file = get_user_chat_history_file(username)
    else:
        chat_file = CHAT_HISTORY_FILE

    try:
        with open(chat_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving chat history: {e}")

def add_to_vectorstore(user_message, ai_response):
    """
    Menambahkan percakapan baru ke ChromaDB sebagai knowledge tambahan
    Format: "User bertanya: [question]. Jawabannya: [answer]"
    """
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        embeddings = OpenAIEmbeddings(api_key=api_key)
        persist_dir = "./chroma_db"
        
        # Load existing vectorstore
        vectorstore = Chroma(
            persist_directory=persist_dir,
            embedding_function=embeddings
        )
        
        # Format percakapan sebagai knowledge
        conversation_text = f"User bertanya: {user_message}. Jawabannya: {ai_response}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Tambahkan metadata untuk tracking
        vectorstore.add_texts(
            texts=[conversation_text],
            metadatas=[{
                "source": "chat_history",
                "timestamp": timestamp,
                "type": "conversation"
            }]
        )
        
        print(f">>> Conversation added to vectorstore at {timestamp}")
        
    except Exception as e:
        print(f"Error adding to vectorstore: {e}")

# ================= RAG SETUP =================

def setup_rag_chain(username=None):
    """
    Menginisialisasi Vector Store (ChromaDB) dan Conversational RAG Chain.
    Jika username diberikan, akan load data portfolio spesifik user.
    """
    # Tentukan file portfolio yang akan digunakan
    if username:
        file_path = get_user_portfolio_file(username)
        # Jika file user belum ada, copy dari template default
        if not os.path.exists(file_path):
            import shutil
            default_file = 'portfolio_data.json'
            if os.path.exists(default_file):
                shutil.copy(default_file, file_path)
        chroma_persist_dir = get_user_chroma_dir(username)
    else:
        file_path = 'portfolio_data.json'
        chroma_persist_dir = "./chroma_db"

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("WARNING: OPENAI_API_KEY not found in environment")
        return None

    # Import Knowledge base dari file portfolio
    if not os.path.exists(file_path):
        print(f"WARNING: Portfolio file not found: {file_path}")
        return None

    with open(file_path, 'r', encoding='utf-8') as f:
        knowledge_base = json.load(f)

    try:
        embeddings = OpenAIEmbeddings(api_key=api_key)
        persist_dir = chroma_persist_dir

        # 2. Cek apakah DB sudah ada
        if os.path.exists(persist_dir) and len(os.listdir(persist_dir)) > 0:
            print(f">>> Loading existing ChromaDB Vector Store for user: {username or 'default'}...")
            vectorstore = Chroma(
                persist_directory=persist_dir,
                embedding_function=embeddings
            )
        else:
            print(f">>> Creating new ChromaDB Vector Store for user: {username or 'default'}...")
            vectorstore = Chroma.from_texts(
                texts=knowledge_base,
                embedding=embeddings,
                persist_directory=persist_dir
            )
        
        # Retriever dengan K=6 untuk mendapat lebih banyak konteks
        retriever = vectorstore.as_retriever(search_kwargs={"k": 6})

        # 3. Model (LLM)
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, api_key=api_key)

        # PROMPT + RETRIEVER HISTORY/MEMORY PERCAKAPAN SEBELUMNYA SET UP >>>>>>>>>>>>>>>>>>>>>>> START
        # 4. History-Aware Retriever
        contextualize_q_system_prompt = """
        Anda adalah pengolah pertanyaan cerdas untuk portfolio profesional. Tugas Anda adalah menganalisis riwayat percakapan (chat_history) dan pertanyaan user saat ini (input) untuk menghasilkan **satu pertanyaan mandiri yang lengkap**.

        Tujuan:
        1.  Jika pertanyaan user saat ini memiliki dependensi konteks dari riwayat percakapan (misalnya, menggunakan kata ganti seperti "itu", "dia", "tersebut", "skill tersebut", "proyek itu"), maka gabungkan konteks yang relevan untuk membuat pertanyaan baru yang **eksplisit dan lengkap** (tidak ambigu).
        2.  Jika pertanyaan user saat ini sudah jelas, berdiri sendiri, dan tidak membutuhkan konteks dari riwayat percakapan, maka kembalikan pertanyaan user tersebut **apa adanya**.

        Aturan Keras:
        * Output Anda HANYA berupa pertanyaan tunggal yang telah dikontekstualisasikan.
        * Jangan pernah menambahkan komentar, penjelasan, atau informasi tambahan di luar pertanyaan yang dihasilkan.
        """
        
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        history_aware_retriever = create_history_aware_retriever(
            llm, retriever, contextualize_q_prompt
        )

        # PROMPT + RETRIEVER HISTORY SET UP >>>>>>>>>>>>>>>>>>>>>>> END

        # PROMPT + RETRIEVER PRESENT atau sekarang SET UP >>>>>>>>>>>>>>>>>>>>>>> START
        # 5. Answer Chain
        qa_system_prompt = """
        Anda adalah **CareerBot**, seorang AI Assistant profesional yang membantu visitor memahami profil karir Adam Muhammad. Tugas utama Anda adalah menjawab pertanyaan tentang pengalaman kerja, skills, proyek, pendidikan, dan informasi profesional lainnya secara akurat, natural, dan membantu, **hanya berdasarkan** informasi yang tersedia dalam `Konteks dari knowledge base`.

        ### ATURAN UTAMA (WAJIB DIIKUTI):

        1.  **WAJIB Gunakan Context Knowledge Base:**
            - **PRIORITAS UTAMA**: Cari jawaban dari `{context}` yang disediakan di bawah
            - Baca SEMUA informasi dalam context dengan teliti sebelum menjawab
            - Jika ada informasi relevan di context (walaupun partial), GUNAKAN informasi tersebut
            - **DILARANG KERAS** mengatakan "tidak ada informasi" jika context berisi data relevan

        2.  **Jawaban Natural dan Profesional:**
            - **JANGAN** pernah gunakan kata "Maaf" di awal jawaban kecuali benar-benar tidak ada data
            - Gunakan intro singkat yang natural (1 kalimat) sebelum memberikan detail/list
            - Akhiri dengan kalimat penutup yang engaging jika relevan
            - Contoh BAIK: "Adam memiliki pengalaman 5+ tahun dengan expertise di beberapa teknologi:" [list skills]
            - Contoh BURUK: "Maaf, saya tidak memiliki informasi..." (jika data ADA di context)

        3.  **Format Keterbacaan:**
            - Jika jawaban berisi 3+ item atau data kompleks, gunakan format bullet points atau numbered list
            - Berikan intro singkat sebelum list untuk konteks
            - Tambahkan detail relevan dalam list (tech stack, achievement, duration)

        4.  **Struktur Jawaban Ideal:**
            ```
            [Intro singkat 1 kalimat yang menjawab pertanyaan]

            [Detail dalam format list jika > 3 item:]
            - Item 1 (detail tambahan: tech stack, tahun, achievement)
            - Item 2 (detail tambahan)
            - Item 3 (detail tambahan)

            [Penutup engaging - opsional]
            ```

        5.  **Handling Pertanyaan Spesifik:**
            - **"Apa saja skill Adam?"** → Ekstrak SEMUA skills dari context, kategorikan (Programming Languages, Frameworks, Tools, dll) dengan level expertise
            - **"Pengalaman kerja apa saja?"** → List SEMUA pengalaman kerja dengan posisi, perusahaan, tahun, dan achievement utama
            - **"Proyek apa yang pernah dikerjakan?"** → List proyek dengan nama, deskripsi singkat, tech stack, dan link jika ada
            - **"Pendidikan/Sertifikasi?"** → Berikan detail lengkap dengan institusi, tahun, dan credential ID jika ada
            - **"Kontak/Hubungi?"** → Berikan info kontak yang tersedia (email, LinkedIn, GitHub, phone)

        6.  **Jika Data Benar-Benar Tidak Ada di Context:**
            - Hanya jika **BENAR-BENAR** tidak ada informasi relevan sama sekali di context
            - Berikan jawaban yang helpful dan suggest topik lain yang bisa ditanyakan
            - Contoh: "Informasi tersebut tidak tersedia saat ini. Namun saya bisa membantu dengan informasi tentang pengalaman kerja, skills, atau proyek Adam."

        7.  **Nada Bahasa:** Profesional, informatif, dan approachable. Seperti recruiter yang membantu hiring manager.

        ### PROFIL DAN TUGAS:

        * **Identitas:** CareerBot - AI Assistant untuk Portfolio Adam Muhammad
        * **Konsistensi:** Jaga konsistensi jawaban dengan riwayat percakapan
        * **Tujuan:** Membantu visitor memahami profil profesional Adam dengan informasi yang jelas dan lengkap DARI KNOWLEDGE BASE
        * **Tone:** Professional namun friendly, seperti HR representative yang experienced

        Konteks dari knowledge base:
        {context}
        """
        
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

        # PROMPT + RETRIEVER PRESENT atau sekarang SET UP >>>>>>>>>>>>>>>>>>>>>>> END

        # 6. Final Retrieval Chain // #Ini Final Chain atau sebelum data kita dikirim ke LLM/OPEN AI
        # history_aware_retriever = Retriever dan Prompt untuk memberi pemahaman dan kemampuan RAG berdasarkan history
        # question_answer_chain = Retriever dan Prompt untuk menjawab pertanyaan present bukan pertanyaan sebelum sebelumnya
        # rag_chain = Gabungan antara kemampuan menjawab pertanyaan saat ini + pemahaman percakapan sebelumnya
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
        
        print(">>> ChromaDB & Conversational RAG Initialized Successfully")
        return rag_chain

    except Exception as e:
        print(f"Error initializing RAG: {e}")
        return None

# Initialize Chain Global (akan di-override per user saat login)
rag_chain = None

# ================= ROUTES (AJAX API) =================

def get_or_create_guest_id():
    """Generate atau ambil guest ID dari session"""
    import uuid
    if 'guest_id' not in session:
        session['guest_id'] = f"guest_{uuid.uuid4().hex[:12]}"
    return session['guest_id']

def get_current_user_id():
    """Get current user ID (username jika login, guest_id jika guest)"""
    if session.get('logged_in'):
        return session.get('username')
    else:
        return get_or_create_guest_id()

@app.route('/')
def index():
    """Render halaman utama"""
    # Auto-create guest session
    get_or_create_guest_id()
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    """API endpoint untuk login user"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip().lower()

        # Validasi username
        if not username:
            return jsonify({"success": False, "error": "Username tidak boleh kosong"}), 400

        if len(username) < 3:
            return jsonify({"success": False, "error": "Username minimal 3 karakter"}), 400

        # Username hanya boleh alphanumeric dan underscore
        if not username.replace('_', '').isalnum():
            return jsonify({"success": False, "error": "Username hanya boleh huruf, angka, dan underscore"}), 400

        # Save username to session
        session['username'] = username
        session['logged_in'] = True

        # Register user if new
        save_registered_user(username)

        # Setup RAG chain untuk user ini
        global rag_chain
        rag_chain = setup_rag_chain(username)

        if rag_chain is None:
            return jsonify({"success": False, "error": "Gagal menginisialisasi sistem RAG"}), 500

        return jsonify({
            "success": True,
            "username": username,
            "message": f"Login berhasil! Selamat datang, {username}"
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/logout', methods=['POST'])
def logout():
    """API endpoint untuk logout user - kembali ke guest mode"""
    try:
        # Clear login info tapi keep guest_id
        guest_id = session.get('guest_id')
        session.clear()
        if guest_id:
            session['guest_id'] = guest_id
        global rag_chain
        rag_chain = None
        return jsonify({"success": True, "message": "Logout berhasil", "guest_id": get_or_create_guest_id()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/check_session', methods=['GET'])
def check_session():
    """API endpoint untuk check status user (logged in atau guest)"""
    try:
        if 'logged_in' in session and session.get('logged_in'):
            return jsonify({
                "logged_in": True,
                "is_guest": False,
                "username": session.get('username'),
                "user_id": session.get('username')
            })
        else:
            guest_id = get_or_create_guest_id()
            return jsonify({
                "logged_in": False,
                "is_guest": True,
                "guest_id": guest_id,
                "user_id": guest_id
            })
    except Exception as e:
        return jsonify({"logged_in": False, "is_guest": True, "error": str(e)}), 500

@app.route('/get_history', methods=['GET'])
def get_history():
    """API endpoint untuk mengambil chat history (support guest mode)"""
    try:
        user_id = get_current_user_id()
        messages = load_chat_history(user_id)
        return jsonify({"success": True, "messages": messages})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def detect_actions(user_message, ai_response):
    """
    Mendeteksi intent dari percakapan dan menentukan action buttons yang sesuai
    Returns: list of action objects
    """
    actions = []
    user_lower = user_message.lower()
    ai_lower = ai_response.lower()

    # Deteksi intent proyek
    project_keywords = ['proyek', 'project', 'portfolio', 'karya', 'aplikasi yang dibuat']
    if any(keyword in user_lower for keyword in project_keywords) or any(keyword in ai_lower for keyword in project_keywords):
        actions.append({
            "type": "project_list",
            "label": "Lihat Semua Proyek",
            "icon": "💼",
            "style": "primary"
        })

    # Deteksi intent skills
    skill_keywords = ['skill', 'kemampuan', 'keahlian', 'teknologi', 'tech stack', 'bahasa pemrograman']
    if any(keyword in user_lower for keyword in skill_keywords) or any(keyword in ai_lower for keyword in skill_keywords):
        actions.append({
            "type": "skills_detail",
            "label": "Detail Skills",
            "icon": "🚀",
            "style": "info"
        })

    # Deteksi intent pengalaman kerja
    experience_keywords = ['pengalaman', 'kerja', 'pekerjaan', 'karir', 'career', 'work experience']
    if any(keyword in user_lower for keyword in experience_keywords) or any(keyword in ai_lower for keyword in experience_keywords):
        actions.append({
            "type": "experience_timeline",
            "label": "Timeline Karir",
            "icon": "📊",
            "style": "secondary"
        })

    # Deteksi intent CV/Resume
    cv_keywords = ['cv', 'resume', 'download', 'unduh']
    if any(keyword in user_lower for keyword in cv_keywords):
        actions.append({
            "type": "download_cv",
            "label": "Download CV",
            "icon": "📄",
            "style": "success"
        })

    # Deteksi intent kontak
    contact_keywords = ['kontak', 'hubungi', 'contact', 'email', 'linkedin', 'github']
    if any(keyword in user_lower for keyword in contact_keywords):
        actions.append({
            "type": "contact_info",
            "label": "Info Kontak",
            "icon": "📧",
            "style": "warning"
        })

    # Tambahkan action default "Tanya Lainnya?"
    if len(actions) > 0:
        actions.append({
            "type": "help",
            "label": "Tanya Lainnya?",
            "icon": "❓",
            "style": "light"
        })

    return actions

@app.route('/send_message', methods=['POST'])
def send_message():
    """API endpoint untuk mengirim pesan dan mendapat response (support guest mode)"""
    try:
        # Get user ID (username atau guest_id)
        user_id = get_current_user_id()
        is_guest = not session.get('logged_in', False)

        # Setup RAG chain jika belum ada
        global rag_chain
        if rag_chain is None:
            rag_chain = setup_rag_chain(user_id)

        data = request.get_json()
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400

        if not os.getenv('OPENAI_API_KEY'):
            return jsonify({"error": "OpenAI API key is not set!"}), 500

        # Load chat history for this user (guest atau logged in)
        messages = load_chat_history(user_id)

        if rag_chain:
            # --- PROSES HISTORY ---
            # Ambil maksimal 20 pesan terakhir (10 percakapan)
            recent_messages = messages[-20:]

            chat_history = []
            for msg in recent_messages:
                if msg.get("is_user"):
                    chat_history.append(HumanMessage(content=msg["q"]))
                else:
                    chat_history.append(AIMessage(content=msg["a"]))

            # --- INVOKE RAG ---
            response = rag_chain.invoke({
                "input": user_message,
                "chat_history": chat_history
            })

            answer = response["answer"]

            # Simpan percakapan baru ke vectorstore
            add_to_vectorstore(user_message, answer)
        else:
            answer = "Maaf, sistem AI sedang tidak dapat diinisialisasi."

        # Deteksi actions berdasarkan percakapan
        actions = detect_actions(user_message, answer)

        # Simpan ke file dengan timestamp
        timestamp = datetime.now().isoformat()
        new_messages = [
            {
                "is_user": True,
                "q": user_message,
                "timestamp": timestamp
            },
            {
                "is_user": False,
                "a": answer,
                "timestamp": timestamp,
                "actions": actions  # Tambahkan actions ke message
            }
        ]

        messages.extend(new_messages)
        save_chat_history(messages, user_id)

        return jsonify({
            "success": True,
            "response": answer,
            "timestamp": timestamp,
            "actions": actions,  # Return actions ke frontend
            "is_guest": is_guest,
            "user_id": user_id
        })

    except Exception as e:
        app.logger.error(f"Error in send_message: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/reset', methods=['POST'])
def reset():
    """Reset chat history (support guest mode)"""
    try:
        user_id = get_current_user_id()
        save_chat_history([], user_id)
        return jsonify({"success": True, "message": "Chat history reset successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/clear_all', methods=['POST'])
def clear_all():
    """
    Menghapus semua data (chat history + vectorstore)
    HATI-HATI: Ini akan menghapus semua data termasuk knowledge base!
    """
    try:
        import shutil
        
        # Hapus chat history
        if os.path.exists(CHAT_HISTORY_FILE):
            os.remove(CHAT_HISTORY_FILE)
        
        # Hapus vectorstore
        persist_dir = "./chroma_db"
        if os.path.exists(persist_dir):
            shutil.rmtree(persist_dir)
        
        # Reinitialize RAG dengan knowledge base baru
        global rag_chain
        rag_chain = setup_rag_chain()
        
        return jsonify({"success": True, "message": "All data cleared successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)