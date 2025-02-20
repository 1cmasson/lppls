# LPPLS Asset Analyzer

This repository contains tools for analyzing and displaying Log-Periodic Power Law Singularity (LPPLS) values for various assets, with a focus on cryptocurrencies and related stocks. Currently, it supports assets such as MSTR (MicroStrategy) and BTC (Bitcoin).

## Overview

The LPPLS model is used to detect bubbles and predict potential crash times in financial markets. This tool applies the LPPLS model to selected assets and visualizes the results.

### Prerequisites

- Python 3.7+
- pip (Python package installer)
- Node.js and npm (for frontend, if applicable)

## Usage

### Backend Setup

1. Navigate to the frontend directory:

```
cd backend
```
    
2. Create a virtual environment:

```
python -m venv venv
```

2. Activate the virtual environment:
- On Windows:
```
venv\Scripts\activate
```

- On macOS and Linux:
```
source venv/bin/activate
```
3. Install the required packages:

```
pip install -r requirements.txt
```

4. Run the backend server:

```
python app.py
```
5. Navigate to graphql playground at http://127.0.0.1:5000/graphql to interact with the API.

### Frontend Setup (if applicable)

1. Navigate to the frontend directory:

```
cd ../frontend
```

2. Install the required npm packages:
```
npm install
```

3. Run the frontend server:

```
npm start
```



## Features

- Calculate LPPLS values for supported assets
- Visualize LPPLS indicators over time
- Compare LPPLS values between different assets
- Track potential bubble formations and crash predictions

## Supported Assets

- MSTR (MicroStrategy)
- BTC (Bitcoin)

## Getting Started

(Instructions for setting up and running the project will be added here)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details

## Acknowledgments

I want to give thanks to [Giovanni Santostasi](https://x.com/giovann35084111/status/1863682797900272021) for introducing me to Bitcoin Power Law and LPPLS model. 

I also want to thank founder of the LPPLS model, [Didier Sornette](https://scholar.google.com/citations?user=HGsSmMAAAAAJ&hl=en)
, for his work on the subject.



