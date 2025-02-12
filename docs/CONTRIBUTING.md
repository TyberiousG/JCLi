
# 🤝 Contributing to JCLi

Thank you for your interest in contributing to **JCLi**! This guide will help you get started with contributing code, reporting issues, and improving documentation.

---

## 🚀 How to Contribute

1. **Fork the Repository**  
   - Click the **"Fork"** button at the top of the GitHub repo.

2. **Clone Your Fork Locally**  
   ```bash
   git clone https://github.com/TyberiousG/JCLi.git
   cd JCLi
   ```

3. **Create a New Branch**  
   ```bash
   git checkout -b feature/new-feature
   ```

4. **Make Your Changes**  
   - Write clean, well-documented code.
   - Add tests if applicable.

5. **Commit Your Changes**  
   ```bash
   git add .
   git commit -m "Add: New feature description"
   ```

6. **Push to Your Fork**  
   ```bash
   git push origin feature/new-feature
   ```

7. **Open a Pull Request (PR)**  
   - Go to the original JCLi repo.
   - Click **"New Pull Request"**.
   - Provide a clear description of your changes.

---

## 🗂️ Project Structure

```
JCLi/
├── ControlInterface/   # CLI commands
├── Daemon/             # Job scheduling & lifecycle
├── Interpreter/        # JCLi script parser
├── Executor/           # Job execution engine
├── QueueInterface/     # Interactive queue management
├── Logging/            # System & job logging
└── Examples/           # Sample JCLi scripts
```

---

## ✅ Code Style Guidelines

- **Language:** Python 3.x  
- **Naming Conventions:**
  - Classes: `CamelCase`
  - Functions/Variables: `snake_case`
- **Formatting:** Use `black` for consistent code formatting.

```bash
pip install black
black .
```

---

## 📦 Adding New Features

1. **Open an Issue:** Discuss your feature idea before starting development.  
2. **Follow Project Structure:** Place new modules in the appropriate directory.  
3. **Documentation:** Update `README.md` or relevant docs if your feature affects usage.

---

## 🚨 Reporting Bugs

1. **Search for Existing Issues:** Avoid duplicates.  
2. **Open a New Issue:** Include:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs. actual behavior
   - Logs or error messages

Example:
```markdown
**Bug:** Job stuck in QUEUED status after submission  
**Steps to Reproduce:**  
1. Submit a job using SUBMIT command  
2. Check STATUS  
**Expected:** Job should transition to RUNNING  
**Actual:** Job remains QUEUED indefinitely  
```

---

## 🔍 Running Tests

If tests are available:
```bash
python -m unittest discover tests
```

---

## 🙌 Community Guidelines

- Be respectful and constructive.  
- Review other PRs if you have time.  
- Keep discussions professional and on-topic.

For more, see `CODE_OF_CONDUCT.md`.

---

## 💡 License

By contributing, you agree that your code will be licensed under the **GNU General Public License (GPL)**.

Happy coding! 🚀
