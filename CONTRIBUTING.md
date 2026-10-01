# Contributing to CSTAN

Thank you for your interest in improving CSTAN (Citizen Safety and Travel Assistance Network)!

## Code of Conduct
We are committed to providing a friendly, safe, and welcoming environment for all contributors. Please be respectful and collaborative.

## How to Contribute
1. **Fork the Repository** on GitHub.
2. **Clone your fork**:
   ```bash
   git clone https://github.com/<your-username>/cstan.git
   cd cstan
   ```
3. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```
4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Run Tests**:
   Ensure all tests pass before making changes:
   ```bash
   python tests/test_cstan.py
   ```
6. **Commit & Push**:
   ```bash
   git commit -m "Add amazing safety feature"
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request** describing your changes.

## Areas for Contribution
- Additional Indian and global language localization dictionaries in `static/js/translations.js`.
- Advanced ML models for trajectory clustering and crowd density prediction.
- Integration with external mapping APIs (Mapbox, OpenRouteService).
- Wearable device BLE integration.
