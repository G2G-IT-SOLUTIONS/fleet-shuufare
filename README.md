# FLOS - Fleet Operations & Settlement System

FLOS is a professional fleet management and financial reconciliation platform designed to integrate Yango Fleet API data with Telebirr mobile money deposits. It provides park managers with a real-time, high-density dashboard for overseeing driver performance and financial compliance.

## 🚀 Key Features

- **Yango Integration**: Real-time synchronization of drivers and completed orders via Yango Fleet API.
- **Financial Reconciliation**: Automatic daily settlement tracking (Expected Revenue vs. Telebirr Deposits).
- **Exception Management**: Automatic classification of Missing, Partial, and Excess deposits.
- **Driver Deep-Dive**: Detailed profile views with historical KPIs and transaction feeds.
- **Internal Fleet Management**: Dedicated tools for managing and searching internal drivers.
- **PostgreSQL Persistence**: Robust local caching to bypass API rate limits and ensure lightning-fast performance.

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python 3.14+)
- **Database**: PostgreSQL with SQLModel (ORM)
- **Frontend**: Jinja2 Templates & Tailwind CSS
- **API Clients**: HTTPX (Asynchronous)
- **Environment**: Python-Dotenv for secure configuration

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/G2G-IT-SOLUTIONS/fleet-shuufare.git
   cd fleet-shuufare
   ```

2. **Set up Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file based on the provided requirements:
   ```env
   YANGO_API_KEY=your_key
   YANGO_CLIENT_ID=your_id
   YANGO_PARK_ID=your_park_id
   DATABASE_URL=postgresql://user:password@localhost:5432/fleet-shuufare
   ```

4. **Initialize Database**:
   The system will automatically create tables on startup.

5. **Run the Application**:
   ```bash
   uvicorn app.main:app --reload
   ```

## 📖 Business Rules (FLOS Framework)

- **Exact Match**: Status: *Verified*.
- **Partial Deposit**: Status: *Flagged for managerial review*.
- **Excess Deposit**: Status: *Flagged for investigation*.
- **Missing Deposit**: Status: *Outstanding liability*.

## 🤝 Contributing
For internal use by G2G IT Solutions. Please follow the standard git workflow: feature branches and pull requests to `main`.

---
© 2026 G2G IT Solutions. All rights reserved.
