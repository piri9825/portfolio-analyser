# Portfolio Analyser
Analyse portfolio of long only equities.

## Prerequisites
- Docker

## Setup Instructions

### Using Docker
1. Clone the repository
2. Go to the cloned repository directory
3. Create a folder named inputs and drop your portfolio csv here. Example portfolio.csv file in docker_inputs folder. There should only be one csv in this folder.
4. Build the Docker image and run the container:
```bash
docker build -t portfolioanalyser .
docker run -p 8050:8050 -v $(pwd)/inputs:/app/docker_inputs portfolioanalyser
```
5. In your browser go to: http://localhost:8050
6. You can switch out the file in the inputs folder and refresh the data while the dashboard is running