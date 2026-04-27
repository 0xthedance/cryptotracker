# Crypto Tracker

Crypto Tracker is a Django-based web application designed to help users monitor and manage their cryptocurrency portfolios. It provides insights into assets, staking, protocol participation, and rewards across multiple networks and protocols.

## Features

- **Portfolio Management**: Track cryptocurrency holdings, staking balances, and protocol participation.
- **Real-Time Updates**: Fetches latest prices, staking rewards, and protocol data.
- **Protocol Support**: Supports popular protocols like Liquity V1/V2, Aave V3, and Uniswap V3.
- **Multi-Network Support**: Works across Ethereum, Arbitrum, Avalanche, Gnosis Chain, and Base networks.
- **User Accounts**: Secure user authentication and personalized portfolio tracking.
- **Invite-Based Registration**: Restricted signup requiring invite codes for controlled access.
- **Admin Panel**: Comprehensive admin interface for user and invite code management.
- **User Roles**: Admin users can manage invite codes and promote other users to admin status.
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
   git clone git@github.com:0xthedance/cryptotracker.git
   cd cryptotracker
   ```

2. **Create a `.env` File**:
   Create a `.env` file in the project root and add the following:
   ```
   export DJANGO_SECRET_KEY=your_secret_key
   export WEB3_ALCHEMY_PROJECT_ID=your_alchemy_project_id
   export ETHERSCAN_API_KEY=your_etherscan_api_key
   export THE_GRAPH_API_KEY=your_graph_api_key
   export COINGECKO_API_KEY=your_coingecko_api_key
   ```

   - **WEB3_ALCHEMY_PROJECT_ID**: Required for blockchain interactions via Alchemy.
   - **ETHERSCAN_API_KEY**: Used for fetching blockchain data from Etherscan.
   - **API_KEY_THE_GRAPH**: Required for querying data from The Graph.
   - **COINGECKO_API_KEY**: Used for fetching cryptocurrency price data.

  (For docker, remove the export keywords)

  You can use the template given by first copying into the final env file and then filling in your keys.
  For local running:
   ```bash
   cp env.local.template .env.local
   # Fill in your keys, then:
   source .env.local
   ```

  For docker:
   ```bash
   cp env.docker.template .env.docker
   ```

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
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Load Initial Data**:
   ```bash
   python manage.py initialize_db
   ```

5. **Setup Invite System** (Optional):
   This command creates an initial admin user and generates sample invite codes:
   ```bash
   python manage.py setup_invite_system
   ```

6. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```

7. **Start Celery Worker**:
   If you don't have Redis running, you can do it with:
   ```bash
   docker run -d -p 6379:6379 --name redis redis:latest
   ```

   Then start celery with:
   ```bash
   celery -A dcp worker --loglevel=info
   ```

8. **Access the Application**:
   Open your browser and navigate to `http://127.0.0.1:8000`.

### Run in Production Using Docker Compose

1. **Additional Environment Variables for Production**:
   Modify  `.env` file with your preferences:
   ```
   export REDIS_URL=redis://redis:6379
   export DJANGO_ALLOWED_HOSTS=your_production_domain
   export DJANGO_DEBUG=False
   ```
   - **REDIS_URL**: Specifies the Redis connection string for Celery.
   - **DJANGO_ALLOWED_HOSTS**: Specifies the allowed hosts for the production environment.
   - **DJANGO_DEBUG**: Set to `False` for production.

2. **Build and Run the Application**:
   Use `docker-compose.yml` to build (optional):
   ```bash
   docker-compose build
   ```
   and run the application:
   ```bash
   docker-compose up
   ```

3. **Access the Application**:
   Open your browser and navigate to `http://$IP_HOST:8000`.

## Usage

### For Regular Users

1. **Sign Up**: Create an account using a valid invite code (first user becomes admin automatically).
2. **Add UserAddresses**: Add your cryptocurrency wallet addresses.
3. **View Portfolio**: Monitor your assets, staking balances, and protocol participation.
4. **Refresh Data**: Use the "Refresh" button to fetch the latest data.
5. **Explore Statistics**: View detailed statistics for wallets and accounts.

### For Admin Users

Admin users have access to additional functionality through the Admin tab:

1. **Access Admin Panel**: Click the "Admin" tab in the navigation.
2. **Generate Invite Codes**: Create new invite codes for user registration.
3. **Manage Invite Codes**: View all codes, their status, and revoke unused codes.
4. **User Management**: View all users and promote/demote admin status.
5. **Monitor Usage**: Track which codes have been used and by whom.

### Invite Code System

- **First User**: The very first user to sign up automatically becomes admin and doesn't need an invite code.
- **Subsequent Users**: Must provide a valid, unused invite code to register.
- **Code Generation**: Only admins can generate invite codes.
- **Code Status**: Invite codes can be active, used, or revoked.
- **Security**: Each invite code can only be used once.

## Management Commands

### setup_invite_system
Sets up the invite code system with initial data:
- Creates admin user if no users exist (username: admin, password: admin123)
- Generates 5 sample invite codes for testing

```bash
python manage.py setup_invite_system
```

### Available Commands
- `initialize_db`: Load basic application data (networks, tokens, etc.)
- `setup_invite_system`: Configure invite system and create initial admin user
- Other Django management commands as usual

## Technologies Used

- **Backend**: Django, Celery, Celery Beat
- **Authentication**: Django's built-in auth system with custom user profiles
- **Blockchain**: Web3.py, Ape Framework
- **Frontend**: HTML, CSS, JavaScript (Django templates and Bulma CSS)
- **Task Queue**: Redis + Celery

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Security Considerations

- **Invite Code System**: Only admins can generate invite codes, ensuring controlled access.
- **First User Protection**: The first user is automatically made admin to prevent lockout.
- **Admin Privileges**: Admin status cannot be toggled by users themselves (except when changing other users).
- **Code Uniqueness**: Each invite code is unique and can only be used once.
- **Code Revocation**: Admins can revoke unused invite codes if needed.

## Contributing

When contributing to this project, please note the invite code system restrictions:
- New users will need invite codes for testing (unless you reset the database).
- Use `setup_invite_system` command to quickly set up test environment.
- Admin functionality is restricted to users with admin status.


