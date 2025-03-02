# LedgerLab-v2

LedgerLab is an innovative meme token project that leverages the Reddit API and NEAR Protocol technology to create a decentralized, user-driven ecosystem. This project aligns with the vision of building a future where AI agents serve users' interests rather than corporate agendas. This project is part of the One Trillion Agents Hackathon 2025, where we aim to contribute to the next wave of autonomous agents on NEAR Protocol.

## Repository Setup

- Clone the repository:

```bash
git clone https://github.com/Hackathon-center/LedgerLab-v2.git
```

- Navigate to the cloned project:

```bash
cd LedgerLab-v2
```

## Front-end

This is the user interface that let's you see the memes , connect your wallet and mint meme :

### Setup and Running

- Navigate to the appropriate directory:

```bash
cd front-end/
```

- Install the required packages:

```bash
npm install
```

- Set up environment variables:
  Create a .env file in the root directory and add the following:

```bash
VITE_CONTRACT_ID=ledgerlab2.testnet
VITE_NETWORK=testnet
```

- Run the application:

```bash
npm run dev
```

## General-backend

This is the backend for the Meme Minting application, built with Flask and SQLAlchemy.

### Setup and Running

- Navigate to the appropriate directory:

```bash
cd general-backend/
```

- Install the required packages:

```bash
pip install -r requirements.txt
```

- Initialize the database:

```bash
flask db init
flask db migrate
flask db upgrade
```

- Run the application:

```bash
python main.py
```

## AI Integration Microservice

The AI Integration microservice is responsible for processing meme images with metadata. It provides a Flask API endpoint for this functionality.

### Setup and Running

- Ensure you have Python installed.
- Navigate to the appropriate directory:

```bash
cd ai-integration/microservices/image_processing
```

- Install the required dependencies:

```bash
pip install -r requirements.txt
```

- To run the Flask application:
  Navigate to root directory

```bash
cd general-backend/
python main.py
```

The server will start, and the API will be accessible at http://localhost:5000 by default.

## LICENSE

This project is licensed under the terms specified in the LICENSE file located in the root directory of the repository.
