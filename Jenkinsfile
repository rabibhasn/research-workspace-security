
pipeline {
    agent any

    environment {
        PYTHON = 'C:\\Users\\rabib\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Check Python') {
            steps {
                bat '"%PYTHON%" --version'
                bat '"%PYTHON%" -c "import sys; print(sys.executable)"'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '"%PYTHON%" -m pip install -r requirements.txt'
                bat '"%PYTHON%" -m pip install -e helper_package'
                bat '"%PYTHON%" -m pip install pytest bandit'
            }
        }

        
        
        stage('Bandit Security Scan') {
            steps {
                script {
                    bat 'if not exist reports mkdir reports'

                    def banditStatus = bat(
                        returnStatus: true,
                        script: '"%PYTHON%" -m bandit -r api_service resource_service processing_service helper_package/research_helper -f json -o reports/bandit-report.json'
                    )

                    echo "Bandit exit code: ${banditStatus}"
                    echo "Report generated for review; security gate is not enabled yet."
                }
            }
            post {
                always {
                    archiveArtifacts(
                        artifacts: 'reports/bandit-report.json',
                        allowEmptyArchive: true
                    )
                }
            }
        }



        stage('Run Tests') {
            steps {
                bat '"%PYTHON%" -m pytest -v'
            }
        }
    }
}
