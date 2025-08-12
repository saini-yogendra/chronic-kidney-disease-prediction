# CKD Prediction System

A modern, AI-powered web application for early detection of Chronic Kidney Disease (CKD) using machine learning.

## 🚀 Features

- **AI-Powered Prediction**: Advanced machine learning model for CKD detection with fallback prediction system
- **Modern UI/UX**: Responsive design with intuitive user interface
- **Comprehensive Form**: Detailed medical test input with validation
- **Personalized Results**: Stage-specific CKD information and diet recommendations
- **PDF Reports**: Downloadable detailed health reports
- **Error Handling**: Robust error handling and user feedback
- **Mobile Responsive**: Works seamlessly on all devices

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Machine Learning**: Scikit-learn, NumPy
- **Database**: MySQL (optional)
- **PDF Generation**: ReportLab
- **Styling**: Modern CSS with CSS Variables

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- MySQL (optional, for diet recommendations)

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CKD_college_project
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory with the following content:
   ```env
   # Flask Configuration
   SECRET_KEY=your-super-secret-key-change-this-in-production
   
   # Database Configuration (optional)
   MYSQL_HOST=localhost
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password
   MYSQL_DB=ckd
   
   # Application Configuration
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```
   
   **Note**: Replace `your-super-secret-key-change-this-in-production` with a strong secret key, and update the database credentials if you plan to use MySQL for diet recommendations.

5. **Database Setup (Optional)**
   If you want to use diet recommendations:
   ```sql
   CREATE DATABASE ckd;
   USE ckd;
   
   CREATE TABLE diet_plan (
       id INT AUTO_INCREMENT PRIMARY KEY,
       Stage VARCHAR(10),
       dietType VARCHAR(10),
       Breakfast TEXT,
       MorningSnack TEXT,
       Lunch TEXT,
       AfternoonSnack TEXT,
       Dinner TEXT
   );
   ```

## 🚀 Running the Application

1. **Start the Flask application**
   ```bash
   python app.py
   ```

2. **Access the application**
   Open your browser and go to: `http://localhost:5000`

## 📱 Usage

1. **Homepage**: Learn about CKD, kidney care, and causes
2. **Prediction Form**: Fill in your medical test results
3. **Results**: Get AI-powered prediction with detailed analysis
4. **Download Report**: Get a comprehensive PDF report
5. **Diet Recommendations**: View personalized diet plans (if database is configured)

## 🎨 UI/UX Improvements

### Modern Design Features:
- **Clean Layout**: Minimalist design with clear visual hierarchy
- **Color Scheme**: Professional medical color palette
- **Typography**: Inter font for better readability
- **Icons**: Font Awesome icons for better visual communication
- **Animations**: Smooth transitions and hover effects
- **Responsive**: Mobile-first design approach

### User Experience Enhancements:
- **Form Validation**: Real-time input validation with helpful feedback
- **Loading States**: Visual feedback during form submission
- **Error Handling**: Clear error messages and recovery options
- **Navigation**: Smooth scrolling and active state indicators
- **Accessibility**: ARIA labels and keyboard navigation support

## 🔒 Security Features

- **Input Validation**: Server-side validation for all form inputs
- **Error Handling**: Graceful error handling without exposing sensitive information
- **Environment Variables**: Secure configuration management
- **CSRF Protection**: Built-in Flask CSRF protection

## 📊 Model Information

The application uses a pre-trained machine learning model (`ckd.pkl`) that analyzes:
- Blood pressure, specific gravity, albumin, sugar
- Red blood cells, pus cells, bacteria presence
- Blood glucose, urea, creatinine, electrolytes
- Hemoglobin, cell counts, medical history
- Age, gender, and other demographic factors

## 🏥 Medical Disclaimer

This application is for educational and research purposes only. The predictions are based on AI analysis and should not replace professional medical advice. Always consult with healthcare professionals for proper diagnosis and treatment.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section below
2. Create an issue in the repository
3. Contact the development team

## 🔧 Troubleshooting

### Common Issues:

1. **ModuleNotFoundError**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Flask-MySQLdb Import Error**: If you see `ImportError: cannot import name '_app_ctx_stack' from 'flask'`, this is a version compatibility issue. The requirements.txt file has been updated with compatible versions. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

2. **Database Connection Error**: 
   - Check MySQL is running
   - Verify database credentials in `.env` file
   - The app will work without database (diet recommendations won't be available)

3. **Model Loading Error**:
   - Ensure `ckd.pkl` file is in the root directory
   - Check file permissions

4. **Model Compatibility Error**: If you see `'DecisionTreeClassifier' object has no attribute 'monotonic_cst'`, this is a scikit-learn version compatibility issue. The application now includes a fallback prediction system that will work even if the model has compatibility issues.

4. **Port Already in Use**:
   ```bash
   # Change port in app.py or kill existing process
   lsof -ti:5000 | xargs kill -9
   ```

## 📈 Future Enhancements

- [ ] User authentication and profiles
- [ ] Historical data tracking
- [ ] Advanced analytics dashboard
- [ ] Mobile app version
- [ ] Integration with electronic health records
- [ ] Multi-language support
- [ ] Advanced ML model with more features

## 📞 Contact

For support or questions, please contact:
- Email: support@ckdprediction.com
- GitHub Issues: [Repository Issues](https://github.com/your-repo/issues)

---

**Made with ❤️ for better healthcare outcomes**
