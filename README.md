<div align="center">

```
   _____      _  __         _ ______
  / ___/____ | |/ /      __(_)_  __/
  \__ \/ __ `/   / | /| / / / / /   
 ___/ / /_/ /   || |/ |/ / / / /    
/____/\__,_/_/|_||__/|__/_/ /_/     
```

🌴 **S**ingle **A**ccess **X**-ray **W**eb **I**ntel **T**oolkit 🌴

*A Python-based OSINT CLI — clean, lightweight, and easy to use*

[![License: MIT](https://img.shields.io/badge/License-MIT-3a7d44.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3a7d44.svg)](https://www.python.org/)

Author: **AldX**

</div>

---

## 🌿 About SaXwiT

SaXwiT is a Python-based OSINT (*Open Source Intelligence*) CLI that brings
5 popular tools together under one clean, consistent interface. One command
is all it takes to look up phone numbers, emails, and usernames.

| Module | Dependency | Function |
|---|---|---|
| 🌱 Phone Number Intelligence | `phonenumbers` | Validate a number, carrier, region, timezone, line type |
| 🌱 Email OSINT | `holehe` | Check if an email is registered on 120+ platforms |
| 🌱 Phone Account OSINT | `ignorant` | Check if a phone number is registered on Instagram/Snapchat/Amazon |
| 🌱 Username OSINT | `maigret` | Check a username across hundreds of social sites |
| 🌱 Quick Availability Scan | `socialscan` | Quickly check username/email availability on major platforms |

---

## 📋 Requirements

- Python **3.9** or newer
- `pip` (usually bundled with your Python install)
- An internet connection (all checks are performed online)

---

## 📦 Installation

Pick the guide that matches your platform.

### 🐧 Linux

```bash
# 1. Clone or extract the project folder, then cd into it
cd saxwit

# 2. (Recommended) create a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install all dependencies
pip install -r requirements.txt

# 4. Run it
python3 saxwit_run.py
```

### 🪟 Windows

```powershell
# 1. Make sure Python is installed and added to PATH
python --version

# 2. Go to the project folder
cd saxwit

# 3. (Recommended) create a virtual environment
python -m venv venv
venv\Scripts\activate

# 4. Install all dependencies
pip install -r requirements.txt

# 5. Run it
python saxwit_run.py
```

> If `python` isn't recognized, try `py` instead
> (e.g. `py -m venv venv`, then `py saxwit_run.py`).

### 📱 Termux (Android)

```bash
# 1. Update Termux packages
pkg update && pkg upgrade -y

# 2. Install Python and supporting tools
pkg install python git clang -y

# 3. Go to the project folder (after cloning/extracting)
cd saxwit

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run it
python saxwit_run.py
```

> Some dependencies need a light compile step. If installation fails, make
> sure `clang` and Python's build tools (via `pkg install python`) are
> installed, then re-run `pip install -r requirements.txt`.

---

## 🚀 Usage

### Interactive Menu Mode

```bash
python saxwit_run.py
```

### Direct Command Mode (scripting-friendly)

```bash
# Analyze a phone number
python saxwit_run.py phone "+14155552671" --region US

# Check an email across many platforms
python saxwit_run.py email target@example.com

# Check which services a phone number is registered on
python saxwit_run.py phoneacc +1 4155552671

# Check a username across hundreds of sites (maigret)
python saxwit_run.py username johndoe --top 300 --timeout 10

# Quick availability check for username/email
python saxwit_run.py scan "johndoe,jane.doe@example.com"
```

> Use `python3` instead of `python` if that's what your system expects.

---

## 🗂️ Project Structure

```
saxwit/
├── saxwit_run.py            # entry point
├── requirements.txt
├── LICENSE
└── saxwit/
    ├── banner.py             # color theme & ASCII banner
    ├── cli.py                # interactive menu + argparse
    └── modules/
        ├── phone_intel.py         # phonenumbers
        ├── email_osint.py         # holehe
        ├── phone_osint.py         # ignorant
        ├── username_maigret.py    # maigret
        └── username_socialscan.py # socialscan
```

---

## 🧭 Usage Ethics

This tool is built for education, security research, and verifying your own
identity online. Do not use it to stalk, harass, or otherwise violate anyone
else's privacy. You are solely responsible for how you use this tool.

---

## 🛠️ Quick Troubleshooting

- **`ModuleNotFoundError`** → make sure you ran `pip install -r requirements.txt` in the active environment.
- **Slow/failed install on Termux** → make sure `clang` and `git` are installed, then try again.
- **`python` command not found (Windows)** → use `py` instead.

---

## 📄 License

This project is licensed under the [MIT License](./LICENSE).

---

<div align="center">

🌴 **SaXwiT** — built with good intentions for security research and self-verification 🌴

**Author: AldX**

</div>
