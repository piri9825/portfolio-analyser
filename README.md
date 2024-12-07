# Portfolio Analyser
Analyse portfolio of long only equities.

## Prerequisites
- Docker

## Setup Instructions

### Using Docker
1. Clone the repository
2. Go to the cloned repository directory
3. Build the Docker image and run the container:
```bash
docker build -t portfolioanalyser .
docker run -p 8050:8050 portfolioanalyser
```
5. In your browser go to: http://localhost:8050