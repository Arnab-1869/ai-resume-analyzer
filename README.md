# 🤖 AI Resume Analyzer

> **Smart Resume Analysis & Enhancement Tool**

AI Resume Analyzer is an intelligent web application that leverages the power of **AI** to help job seekers optimize their resumes. Built with modern technologies including **Python**, **Streamlit**, and the **Groq API**, this tool provides comprehensive resume analysis, personalized feedback, and intelligent job recommendations.

## 🌐 Live Demo

**[Try it now →](https://ai-resume-analyzer-puqpqqcgmze6q9zvasczsw.streamlit.app/)**

---

## ✨ Key Features

### 📄 **Multi-Format Support**
- Upload resumes in **PDF**, **DOCX**, or **TXT** formats
- Intelligent text extraction with advanced parsing capabilities
- Support for various resume layouts and structures

### 🧠 **AI-Powered Analysis**
- Powered by **Groq API** with **Llama 3** model
- Comprehensive resume evaluation and scoring
- Detailed feedback on content, structure, and formatting
- Industry-specific recommendations

### 🎯 **Smart Recommendations**
- **Strengths identification** - Highlight your best qualities
- **Improvement suggestions** - Actionable advice for enhancement
- **Job role matching** - AI-suggested positions based on your profile
- **Skills gap analysis** - Identify missing keywords and competencies

### 📥 **Enhanced Resume Generation**
- **One-click download** of improved resume as PDF
- Professional formatting and layout optimization
- ATS-friendly structure for better job application success

### 🎨 **User Experience**
- Clean, intuitive interface built with **Streamlit**
- Responsive design for desktop and mobile
- Real-time analysis and instant feedback
- Progress indicators for long operations

---

## 🛠️ Technology Stack

| Category | Technologies |
|----------|-------------|
| **Backend** | Python 3.8+ |
| **Frontend** | Streamlit |
| **AI/ML** | Groq API (Llama 3) |
| **Document Processing** | python-docx, PyMuPDF, pdfplumber |
| **PDF Generation** | fpdf |
| **Environment** | python-dotenv |

---

## 📸 Application Preview

### Upload Interface
![Upload Resume Interface](upload.png)

### Analysis Dashboard
![Resume Analysis Results](analysis.png)

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8 or higher
- Groq API key ([Get it here](https://console.groq.com/))
- Git installed on your system

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Arnab-1869/ai-resume-analyzer.git
   cd ai-resume-analyzer
   ```

2. **Create Virtual Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   
   Create a `.streamlit/secrets.toml` file:
   ```toml
   [secrets]
   GROQ_API_KEY = "your-groq-api-key-here"
   ```
   
   Or create a `.env` file:
   ```env
   GROQ_API_KEY=your-groq-api-key-here
   ```

5. **Launch Application**
   ```bash
   streamlit run main.py
   ```

6. **Access the App**
   
   Open your browser and navigate to `http://localhost:8501`

---

## ☁️ Cloud Deployment

### Streamlit Cloud Deployment

1. **Prepare Repository**
   - Push your code to GitHub
   - Ensure all dependencies are in `requirements.txt`

2. **Deploy on Streamlit Cloud**
   - Visit [Streamlit Cloud](https://streamlit.io/cloud)
   - Connect your GitHub repository
   - Select the main branch and `main.py` file

3. **Configure Secrets**
   - Go to App Settings → Secrets
   - Add your environment variables:
   ```toml
   GROQ_API_KEY = "your-groq-api-key-here"
   ```

4. **Deploy & Share**
   - Click "Deploy" and wait for the build to complete
   - Share your live app URL with others

### Alternative Deployment Options

- **Heroku**: Use the included `Procfile` for Heroku deployment
- **Docker**: Containerize the application with the provided `Dockerfile`
- **AWS/GCP**: Deploy on cloud platforms using their Python runtime environments

---

## 📊 How It Works

### 1. **Document Upload & Processing**
- User uploads resume in supported format
- Text extraction using specialized libraries
- Content preprocessing and cleaning

### 2. **AI Analysis Pipeline**
- Resume content sent to Groq API
- Llama 3 model analyzes structure, content, and keywords
- Comparison against industry standards and best practices

### 3. **Feedback Generation**
- Comprehensive analysis report generation
- Strengths and weaknesses identification
- Actionable improvement recommendations

### 4. **Enhanced Resume Creation**
- AI-generated improvements applied
- Professional formatting and structure
- ATS-optimized output generation

---

## 🎯 Use Cases

- **Job Seekers**: Optimize resumes for better job application success
- **Career Counselors**: Provide data-driven resume feedback to clients
- **HR Professionals**: Pre-screen and evaluate candidate resumes
- **Students**: Improve academic and internship applications
- **Career Changers**: Adapt resumes for new industries

---

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### Getting Started
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Contribution Guidelines
- Follow PEP 8 coding standards
- Add docstrings to new functions
- Include unit tests for new features
- Update documentation as needed

---

## 📋 Roadmap

### Upcoming Features
- [ ] **Resume Templates** - Multiple professional templates
- [ ] **Cover Letter Generation** - AI-powered cover letter creation
- [ ] **Interview Prep** - Question suggestions based on resume
- [ ] **Skills Assessment** - Interactive skills evaluation
- [ ] **Industry Insights** - Market trends and salary information
- [ ] **Resume Tracking** - Version control and history
- [ ] **Batch Processing** - Multiple resume analysis

### Performance Improvements
- [ ] **Caching System** - Faster repeated analyses
- [ ] **Database Integration** - User profiles and history
- [ ] **Advanced Analytics** - Success rate tracking
- [ ] **Mobile App** - Native mobile applications

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: "ModuleNotFoundError" when running the app
**Solution**: Ensure all dependencies are installed: `pip install -r requirements.txt`

**Issue**: "Invalid API Key" error
**Solution**: Verify your Groq API key is correctly set in secrets or environment variables

**Issue**: PDF upload fails
**Solution**: Check if the PDF is password-protected or corrupted

**Issue**: Slow analysis performance
**Solution**: Large files may take longer; consider optimizing PDF size

### Getting Help
- Check the [Issues](https://github.com/Arnab-1869/ai-resume-analyzer/issues) page
- Create a new issue with detailed information
- Join our community discussions

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Arnab**
- GitHub: [@Arnab-1869](https://github.com/Arnab-1869)
- LinkedIn: [Connect with me](https://linkedin.com/in/arnab-dolui)

---

## 🙏 Acknowledgments

- **Groq** for providing the powerful AI API
- **Streamlit** for the amazing web framework
- **Open Source Community** for the fantastic libraries
- **Contributors** who help improve this project

---

## ⭐ Show Your Support

If this project helped you, please consider:
- Giving it a **⭐ star** on GitHub
- **Sharing** it with your network
- **Contributing** to make it even better
- **Reporting issues** to help us improve

---

**Made with ❤️ by developers, for developers**
