# IDEAR-Dash


## Installation

#### Step 1. Clone this repository by running

    git clone https://github.com/dkedar7/Data-Analyzer
    
#### Step 2. Create a virtual environement by running

    python -m venv DataAnalyzer
        
#### Step 3. Active this environment, on Windows:

    DataAnalyzer\Source\Activate

MacOS or Linux:

    source DataAnalyzer/bin/activate
    
#### Step 4. Open the directory and install dependencies

    cd Analyzer/
    pip install -r requirements.txt
    
#### Step 5. Launch the web application

    python run.py
    
Use `localhost:8080` to interact with the application.

## About the demo deployment

The [demo deployment] utilizes Google Build to containerize the application, Google Container Registry for storing and managing a container and Google Cloud Run to deploy it as a web endpoint.

![Cloud Run Architecture](https://github.com/dkedar7/Data-Analyzer/blob/master/Analyzer/assets/architecture.png?raw=true)

[More about Google Cloud Run](https://cloud.google.com/run/docs/)


## License
Data analyzer uses the [MIT license](https://github.com/dkedar7/IDEAR-Dash/blob/master/LICENSE).

## Dependencies

You need [Python 3](https://python3statement.org/) to run this application. Other dependencies can be found in the [requirements.txt](https://github.com/dkedar7/IDEAR-Dash/blob/master/Analyzer/requirements.txt) file.
