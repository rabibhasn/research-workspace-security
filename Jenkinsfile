
pipeline {
    agent any

    environment {
        PYTHON = 'C:\\Users\\rabib\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe'
        VENV = '.venv-ci'
        REPORT_DIR = 'reports'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Create Fresh Environment') {
            steps {
                bat 'if exist "%VENV%" rmdir /s /q "%VENV%"'
                bat '"%PYTHON%" -m venv "%VENV%"'
                bat '"%VENV%\\Scripts\\python.exe" --version'
                bat '"%VENV%\\Scripts\\python.exe" -m pip install --upgrade pip'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '"%VENV%\\Scripts\\python.exe" -m pip install -r requirements.txt'
                bat '"%VENV%\\Scripts\\python.exe" -m pip install -e helper_package'
                bat '"%VENV%\\Scripts\\python.exe" -m pip install pip-audit'
            }
        }

        stage('Bandit Security Scan') {
            steps {
                bat 'if not exist "%REPORT_DIR%" mkdir "%REPORT_DIR%"'

                script {
                    def banditStatus = bat(
                        returnStatus: true,
                        script: '"%VENV%\\Scripts\\python.exe" -m bandit -r api_service resource_service processing_service helper_package\\research_helper -f json -o reports\\bandit-report.json'
                    )

                    echo "Bandit exit code: ${banditStatus}"

                    if (banditStatus > 1) {
                        error('Bandit could not complete the scan. Check the console log.')
                    }
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



        stage('Dependency Security Audit') {
    steps {
        script {
            def auditStatus = bat(
                returnStatus: true,
                script: '"%VENV%\\Scripts\\python.exe" -m pip_audit -r requirements.txt --format json --output reports\\pip-audit.json'
            )

            if (auditStatus != 0) {
                error('Dependency audit failed. Inspect the pip-audit report.')
            }
        }
    }
    post {
        always {
            archiveArtifacts(
                artifacts: 'reports/pip-audit.json',
                allowEmptyArchive: true
            )
        }
    }
}

        stage('Run Tests') {
            steps {
                bat '"%VENV%\\Scripts\\python.exe" -m pytest -v'
            }
        }
    }

    post {
        always {
            junit(
                testResults: 'test-results.xml',
                allowEmptyResults: true
            )
            archiveArtifacts(
                artifacts: 'reports/**',
                allowEmptyArchive: true
            )
        }
    }
}
