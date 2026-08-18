# 🎬 CinemaSharif

A comprehensive Cinema Ticket Reservation and Management System built with Django and PostgreSQL.

## ✨ Key Features

*   **Smart Authentication:** Phone-number based login and registration system.
*   **Interactive Seat Selection:** Visual seat map for users to select available seats, backed by robust concurrency control (Database Locks) to prevent double-booking.
*   **Internal Wallet System:** Users can deposit funds and purchase tickets directly using their wallet, complete with a transaction history log.
*   **Custom Admin Dashboard:** A dedicated, user-friendly control panel for administrators to manage cinemas, movies, showtimes, and monitor system revenue.
*   **Software Design Patterns:** Implements the **Factory Pattern** for dynamic ticket pricing strategies (e.g., VIP vs. Normal) and the **Singleton Pattern** for global system configurations.

## 🛠 Tech Stack

*   **Backend:** Python 3, Django 5+
*   **Database:** PostgreSQL
*   **Frontend:** HTML5, Tailwind CSS, Vanilla JavaScript

## 🚀 Quick Setup (Linux)

We have provided fully automated bash scripts to streamline the installation and execution process.

**1. Clone the repository:**
```bash
git clone https://github.com/AliMajedi-83/CinemaSharif.git
cd CinemaSharif
```
**2. Run the automated setup script:**
This script automatically handles the virtual environment (.venv), installs all dependencies, manages PostgreSQL database creation, applies Django migrations, and helps you create an admin superuser.
Bash
```bash
chmod +x setup_cinema.sh run_cinema.sh
./setup_cinema.sh
```
**3. Start the application:**

```Bash
./run_cinema.sh
```
The server will start, and the application/dashboard will automatically open in your default web browser.

## 👥 Development Team

Developed by: Majedi, Kashfian, Tafti
