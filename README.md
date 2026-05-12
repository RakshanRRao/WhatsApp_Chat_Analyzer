# 📊 WhatsApp Chat Analyzer

🔗 Live App: [https://rakshan-whatsappchatanalyzer.streamlit.app/](https://rakshan-wca.streamlit.app/)

A Streamlit-based web application to analyze WhatsApp chat exports and generate interactive insights.

---

## 🚀 Features

- 📩 Total Messages, Words, Media & Links
- 📅 Monthly Timeline Analysis
- 📈 Daily Activity Analysis
- 🗓️ Activity Heatmap (Day vs Hour)
- 👥 Most Active Users
- ☁️ WordCloud Visualization
- 🔤 Most Common Words
- 😀 Emoji Analysis with Pie Chart

---

## 🛠 Tech Stack

- Python
- Pandas
- Streamlit
- Matplotlib
- Seaborn
- WordCloud
- URLExtract

---

## ▶️ How to Run Locally

1. Clone the repository:
git clone https://github.com/RakshanRRao/WhatsAppChatAnalyzer.git

2. Navigate into the project folder:
   cd whatsapp-chat-analyzer

3. Install dependencies:
   pip install -r requirements.txt

4. Run the app:
   streamlit run app.py

---

## 📁 Input Format

Upload a WhatsApp exported `.txt` file.

To export chat:
- Open WhatsApp chat
- Click three dots (⋮)
- More → Export Chat
- Choose Without Media
- Upload the exported `.txt` file

---

## 📂 Project Structure

whatsapp-chat-analyzer/
│
├── app.py
├── preprocessor.py
├── helper.py
├── stop_hinglish.txt
├── requirements.txt
├── README.md
└── .gitignore

---

## 📌 Key Highlights

- Supports both bracket and dash WhatsApp export formats
- Processes 20,000+ messages efficiently
- Generates structured communication insights
- Interactive dashboard built using Streamlit
- Clean modular code structure

---

## 👨‍💻 Developed By

Rakshan R Rao
🔗 GitHub: https://github.com/RakshanRRao
