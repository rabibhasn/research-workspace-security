
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        
    stage('Check Python') {
        steps {
            bat '"C:\\Users\\rabib\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe" --version'
            bat '"C:\\Users\\rabib\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe" -c "import sys; print(sys.executable)"'
        }
    }


        stage('Install Dependencies') {
            steps {
                bat 'py -m pip install -r requirements.txt'
                bat 'py -m pip install -e helper_package'
                bat 'py -m pip install pytest bandit'
            }
        }

        stage('Run Tests') {
            steps {
                bat 'py -m pytest -v'
            }
        }
    }
}
