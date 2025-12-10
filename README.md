# Portfolio RAG - AI-Powered Interactive Portfolio

Sebuah website portfolio interaktif yang dilengkapi dengan **AI Chatbot menggunakan RAG (Retrieval-Augmented Generation)** untuk menjawab pertanyaan tentang pengalaman profesional, skills, proyek, dan informasi karir lainnya.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5-orange.svg)
![LangChain](https://img.shields.io/badge/LangChain-Latest-purple.svg)

---

## Fitur Utama

### AI Chatbot dengan RAG
- **Conversational AI** menggunakan OpenAI GPT-3.5-turbo
- **ChromaDB Vector Database** untuk knowledge base yang efisien
- **Multi-turn Conversation Memory** - Chatbot memahami konteks percakapan
- **LangChain Framework** untuk RAG pipeline yang robust
- **Context-Aware Responses** - Jawaban yang relevan dan natural

### Multi-User System
- **User Login System** dengan validasi username
- **Per-User Data Isolation**:
  - Chat history terpisah per user
  - Portfolio knowledge base per user
  - ChromaDB vector store per user
- **Guest Mode** untuk visitor tanpa login
- **Session Management** dengan Flask sessions

### Portfolio Sections
- **About Me** - Profil profesional lengkap
- **Skills & Technologies** - Dikategorisasi dengan level expertise
- **Work Experience** - Timeline karir dengan achievement
- **Education** - Pendidikan formal dan bootcamp
- **Certifications** - Sertifikasi profesional
- **Organizations** - Keanggotaan komunitas
- **Projects** - Portfolio proyek dengan tech stack
- **Contact Information** - Email, LinkedIn, GitHub, Phone

### UI/UX Features
- **Mountain Theme Design** dengan animasi CSS
  - Gradient sky dengan multiple mountain layers
  - Glowing sun dengan breathing animation
  - Swaying trees dengan animasi natural
  - Jagged rocks untuk realistic landscape
- **Light/Dark Mode** dengan theme persistence
- **Responsive Design** untuk semua device
- **Quick Prompt Buttons** untuk pertanyaan umum
- **Real-time Chat Interface** dengan typing indicators
- **Download CV** dalam format text file
- **Action Buttons** - Deteksi intent dan suggest action

---

## Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Flask** | Web framework |
| **LangChain** | RAG orchestration |
| **OpenAI GPT-3.5** | Language model |
| **ChromaDB** | Vector database |
| **OpenAI Embeddings** | Text embeddings |
| **Python 3.8+** | Runtime |

### Frontend
| Technology | Purpose |
|------------|---------|
| **HTML5** | Structure |
| **CSS3** | Styling + Animations |
| **JavaScript ES6+** | Interactivity |
| **localStorage** | Theme persistence |

### Data Storage
- **ChromaDB** - Vector store (persistent)
- **JSON Files** - Chat history, user registry, knowledge base
- **Flask Sessions** - User authentication state

---

## Installation & Setup

### Prerequisites
```bash
Python 3.8 atau lebih tinggi
OpenAI API Key
```

### 1. Clone Repository
```bash
git clone https://github.com/Adamite123/portfolio_RAG.git
cd portfolio_RAG
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Buat file `.env` di root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
FLASK_SECRET_KEY=your_secret_key_here_change_in_production
```

### 4. Run Application
```bash
# Development mode
flask --app index.py --debug run

# Production mode
flask --app index.py run
```

### 5. Access Application
Buka browser dan kunjungi:
```
http://127.0.0.1:5000
```

---

## Project Structure

```
portfolio_RAG/
│
├── index.py                      # Flask backend application
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (not tracked)
│
├── templates/
│   └── index.html               # Frontend HTML (v3.0 Mountain Theme)
│
├── static/                      # Static assets (if any)
│
├── portfolio_data.json          # Default knowledge base template
├── registered_users.json        # User registry
│
├── users_data/                  # Per-user data directory
│   └── {username}/
│       ├── chat_history.json    # User's chat history
│       ├── portfolio_data.json  # User's portfolio data
│       └── chroma_db/           # User's vector store
│
├── chroma_db/                   # Default ChromaDB vector store
│
├── CLEANUP_REPORT.md            # Project cleanup documentation
├── MOUNTAIN_THEME.md            # Design documentation
└── README.md                    # This file
```

---

## Usage Guide

### 1. First Time Visitor (Guest Mode)
- Langsung bisa chat tanpa login
- Chat history tersimpan dalam session
- Data hilang setelah logout/close browser

### 2. Login User
- Klik tombol "Login" di navbar
- Masukkan username (minimal 3 karakter, alfanumerik + underscore)
- Chat history akan tersimpan permanent per user
- Setiap user memiliki vector store terpisah

### 3. Chat dengan AI
- Ketik pertanyaan di chat input
- Gunakan quick prompt buttons untuk pertanyaan umum
- AI akan menjawab berdasarkan knowledge base
- Percakapan tersimpan otomatis

### 4. Download CV
- Klik tombol "Download CV" di chat atau navbar
- CV dalam format text akan terdownload otomatis

### 5. Browse Portfolio
- Scroll halaman untuk melihat semua section
- Klik links untuk ke external resources (LinkedIn, GitHub, dll)

---

## API Endpoints

### Authentication
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/login` | POST | Login user |
| `/logout` | POST | Logout user |
| `/check_session` | GET | Check user status |

### Chat Operations
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/send_message` | POST | Send chat message |
| `/get_history` | GET | Get chat history |
| `/reset` | POST | Reset chat history |
| `/clear_all` | POST | Clear all data (DANGEROUS) |

### Page
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Render main page |

---

## Configuration

### RAG System Configuration
Edit di `index.py`:

```python
# Retriever settings
retriever = vectorstore.as_retriever(search_kwargs={"k": 6})  # Jumlah context chunks

# LLM settings
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, api_key=api_key)

# Chat history limit
recent_messages = messages[-20:]  # 10 percakapan terakhir
```

### System Prompts
Customize prompts di `index.py`:
- `contextualize_q_system_prompt` - Untuk history-aware retriever
- `qa_system_prompt` - Untuk question answering

### Knowledge Base
Edit `portfolio_data.json` untuk update portfolio content:
```json
[
  "Adam Muhammad adalah Full Stack Developer dengan 5+ tahun pengalaman...",
  "Skills: Python, JavaScript, React, Flask, Django...",
  "Proyek: E-commerce Platform menggunakan React dan Node.js..."
]
```

---

## Customization

### 1. Change Color Theme
Edit CSS di `templates/index.html`:
```css
:root {
    --primary-color: #2d5016;      /* Forest Green */
    --secondary-color: #ff6b6b;    /* Coral */
    --accent-color: #ffd700;       /* Gold */
}
```

### 2. Update Portfolio Content
Edit `portfolio_data.json` dan restart server untuk rebuild vector store

### 3. Add New Sections
Tambahkan section HTML di `templates/index.html` dan update knowledge base

### 4. Change AI Model
Edit di `index.py`:
```python
llm = ChatOpenAI(model="gpt-4", temperature=0.7, api_key=api_key)  # Ganti ke GPT-4
```

---

## Deployment

### Option 1: Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login & deploy
railway login
railway init
railway up
```

### Option 2: Render
1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: portfolio-rag
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn index:app
```
2. Connect GitHub repo di Render dashboard

### Option 3: Heroku
```bash
# Create Procfile
echo "web: gunicorn index:app" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
heroku config:set OPENAI_API_KEY=your_key
```

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key untuk GPT-3.5 | Yes |
| `FLASK_SECRET_KEY` | Secret key untuk Flask sessions | Yes |

---

## Dependencies

Lihat `requirements.txt` untuk full list. Key dependencies:

```
flask==3.0.0
langchain==0.1.0
langchain-openai==0.0.2
langchain-chroma==0.1.0
chromadb==0.4.22
openai==1.6.1
python-dotenv==1.0.0
```

---

## Troubleshooting

### Issue: "OpenAI API key is not set!"
**Solution**: Pastikan file `.env` ada dan berisi `OPENAI_API_KEY=your_key`

### Issue: ChromaDB error saat startup
**Solution**: Hapus folder `chroma_db/` dan restart server untuk rebuild

### Issue: Chat history tidak tersimpan
**Solution**: Check permissions folder `users_data/` dan pastikan writable

### Issue: AI response lambat
**Solution**:
- Reduce `k` value di retriever settings (default 6)
- Limit chat history yang diload (default 20 messages)

---

## Performance Optimization

### 1. Vector Store
- ChromaDB sudah persistent, tidak perlu rebuild setiap restart
- Gunakan `k=3-6` untuk optimal retrieval speed vs accuracy

### 2. Chat History
- Default: Load 20 pesan terakhir (10 percakapan)
- Bisa disesuaikan di `send_message()` endpoint

### 3. Caching
- Browser localStorage untuk theme preference
- Flask sessions untuk user state

---

## Security Notes

- **Username Validation**: Alphanumeric + underscore only
- **Session Secret**: Gunakan strong random string di production
- **API Key**: JANGAN commit `.env` ke git
- **Input Sanitization**: User input di-strip dan divalidasi
- **No SQL Injection**: Menggunakan ChromaDB (vector DB) bukan SQL

---

## Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## License

MIT License - Lihat file `LICENSE` untuk detail

---

## Author

**Adam Muhammad**
- Full Stack Developer & AI Engineer
- 5+ years experience in web development and AI systems

### Contact
- Email: adam.example@email.com
- LinkedIn: [Adam Muhammad](https://linkedin.com/in/adammuhammad)
- GitHub: [Adamite123](https://github.com/Adamite123)
- Portfolio: [portfolio-rag.com](https://portfolio-rag.com)

---

## Acknowledgments

- **OpenAI** - GPT-3.5-turbo API
- **LangChain** - RAG framework
- **ChromaDB** - Vector database
- **Flask** - Web framework
- **Community** - Open source contributors

---

## Changelog

### Version 3.0 (December 2025)
- Mountain theme design dengan advanced CSS animations
- Multi-user support dengan per-user data isolation
- Guest mode untuk anonymous visitors
- Action detection dan smart suggestions
- Improved RAG prompts untuk natural responses

### Version 2.0
- Conversational RAG dengan memory
- ChromaDB integration
- Chat history persistence

### Version 1.0
- Basic portfolio website
- Static content sections

---

## Future Enhancements

- [ ] Admin dashboard untuk manage users
- [ ] Export chat history ke PDF
- [ ] Voice input untuk chat
- [ ] Multi-language support
- [ ] Analytics dashboard
- [ ] Real-time collaboration
- [ ] Mobile app (React Native)
- [ ] Integration dengan calendar untuk booking

---

**Made with by Adam Muhammad**

**Powered by OpenAI GPT-3.5, LangChain, and ChromaDB**

---

*Last Updated: December 2025*
*Version: 3.0*
*Status: Active Development*
