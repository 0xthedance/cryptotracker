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
- PostgreSQL (or any preferred database)
- Redis (for Celery task queue)
- APE framework (for blockchain interactions)

### Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/crypto_tracker.git
   cd crypto_tracker
   ```

2. **Create a Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Create a `.env` file in the project root and add the following:
   ```
   SECRET_KEY=your_secret_key
   DEBUG=True
   DATABASE_URL=postgres://user:password@localhost:5432/crypto_tracker
   REDIS_URL=redis://localhost:6379/0
   WEB3_ALCHEMY_PROJECT_ID=your_alchemy_project_id
   ETHERSCAN_API_KEY=your_etherscan_api_key
   API_KEY_THE_GRAPH=your_graph_api_key
   COINGECKO_API_KEY=your_coingecko_api_key
   AWS_ACCESS_KEY_ID=your_aws_access_key_id
   AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
   AWS_REGION=your_aws_region
   AWS_ECS_CLUSTER_NAME=your_aws_ecs_cluster_name
   AWS_ECS_SERVICE_NAME=your_aws_ecs_service_name
   ```

   - **WEB3_ALCHEMY_PROJECT_ID**: Required for blockchain interactions via Alchemy.
   - **ETHERSCAN_API_KEY**: Used for fetching blockchain data from Etherscan.
   - **API_KEY_THE_GRAPH**: Required for querying data from The Graph.
   - **COINGECKO_API_KEY**: Used for fetching cryptocurrency price data.
   - **AWS_ACCESS_KEY_ID** and **AWS_SECRET_ACCESS_KEY**: Required for AWS ECS deployment.
   - **AWS_REGION**: Specifies the AWS region for ECS deployment.
   - **AWS_ECS_CLUSTER_NAME** and **AWS_ECS_SERVICE_NAME**: Used to identify the ECS cluster and service for deployment.

5. **Apply Migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Load Initial Data**:
   ```bash
   python manage.py initialize_db
   ```

7. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```

8. **Start Celery Worker**:
   ```bash
   celery -A crypto_tracker worker --loglevel=info
   ```

9. **Access the Application**:
   Open your browser and navigate to `http://127.0.0.1:8000`.

## Usage

1. **Sign Up**: Create an account to start tracking your portfolio.
2. **Add Addresses**: Add your cryptocurrency wallet addresses.
3. **View Portfolio**: Monitor your assets, staking balances, and protocol participation.
4. **Refresh Data**: Use the "Refresh" button to fetch the latest data.
5. **Explore Statistics**: View detailed statistics for wallets and accounts.

## Technologies Used

- **Backend**: Django, Celery, PostgreSQL
- **Blockchain**: Web3.py, Ape Framework
- **Frontend**: HTML, CSS, JavaScript (Django templates and React)
- **Task Queue**: Redis + Celery

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push the branch.
4. Submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Django](https://www.djangoproject.com/)
- [Web3.py](https://web3py.readthedocs.io/)
- [Ape Framework](https://www.apeworx.io/)
- [The Graph](https://thegraph.com/)
- [CoinGeko] (https://)

