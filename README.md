# Crypto Tracker

Crypto Tracker is a Django-based web application designed to help users monitor and manage their cryptocurrency portfolios. It provides insights into assets, staking, protocol participation, and rewards across multiple networks and protocols.

## Features

- **Portfolio Management**: Track cryptocurrency holdings, staking balances, and protocol participation.
- **Real-Time Updates**: Fetch the latest prices, staking rewards, and protocol data.
- **Protocol Support**: Supports popular protocols like Liquity V1/V2, Aave V3, and Uniswap V3.
- **Multi-Network Support**: Works across Ethereum, Arbitrum, Avalanche, Gnosis Chain, and Base networks.
- **User Accounts**: Secure user authentication and personalized portfolio tracking.
- **Statistics and Insights**: View wallet and account balances, staking rewards, and protocol-specific data.

## Installation

### Prerequisites

- Python 3.8+
- Django 4.0+
- Redis (for Celery task queue)
- APE framework (for blockchain interactions)

### Common Setup Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/crypto_tracker.git
   cd crypto_tracker
   ```

2. **Create a `.env` File**:
   Create a `.env` file in the project root and add the following:
   ```
   DJANGO_SECRET_KEY=your_secret_key
   WEB3_ALCHEMY_PROJECT_ID=your_alchemy_project_id
   ETHERSCAN_API_KEY=your_etherscan_api_key
   API_KEY_THE_GRAPH=your_graph_api_key
   COINGECKO_API_KEY=your_coingecko_api_key
   ```

   - **WEB3_ALCHEMY_PROJECT_ID**: Required for blockchain interactions via Alchemy.
   - **ETHERSCAN_API_KEY**: Used for fetching blockchain data from Etherscan.
   - **API_KEY_THE_GRAPH**: Required for querying data from The Graph.
   - **COINGECKO_API_KEY**: Used for fetching cryptocurrency price data.

### Run Locally

1. **Create a Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Apply Migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Load Initial Data**:
   ```bash
   python manage.py initialize_db
   ```

5. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```

6. **Start Celery Worker**:
   ```bash
   celery -A crypto_tracker worker --loglevel=info
   ```

7. **Access the Application**:
   Open your browser and navigate to `http://127.0.0.1:8000`.

### Run in Production Using Docker Compose

1. **Build and Run the Application**:
   Use `docker-compose.yml` to build and run the application:
   ```bash
   docker-compose up --build
   ```

2. **Additional Environment Variables for Production**:
   Modify  `django_production_env` file with your preferences:
   ```
   REDIS_URL=redis://redis:6379/0
   DJANGO_ALLOWED_HOSTS=your_production_domain
   DJANGO_DEBUG=False
   ```
   - **REDIS_URL**: Specifies the Redis connection string for Celery.
   - **DJANGO_ALLOWED_HOSTS**: Specifies the allowed hosts for the production environment.
   - **DJANGO_DEBUG**: Set to `False` for production.

3. **Access the Application**:
   Open your browser and navigate to `http://$IP_HOST:8000`.

## Usage

1. **Sign Up**: Create an account to start tracking your portfolio.
2. **Add Addresses**: Add your cryptocurrency wallet addresses.
3. **View Portfolio**: Monitor your assets, staking balances, and protocol participation.
4. **Refresh Data**: Use the "Refresh" button to fetch the latest data.
5. **Explore Statistics**: View detailed statistics for wallets and accounts.

## Technologies Used

- **Backend**: Django, Celery, Celery Beat
- **Blockchain**: Web3.py, Ape Framework
- **Frontend**: HTML, CSS, JavaScript (Django templates and React)
- **Task Queue**: Redis + Celery

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.


