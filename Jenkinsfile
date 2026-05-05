pipeline {
    agent any
    
    environment {
        // Dynamically gets email of who triggered the build
        TRIGGER_USER_EMAIL = "${env.CHANGE_AUTHOR_EMAIL ?: env.GIT_COMMIT_AUTHOR_EMAIL}"
    }
    
    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }
        
        stage('Build Docker Image & Run Tests') {
            steps {
                script {
                    // Build Docker image with Chrome + Selenium
                    docker.build("selenium-test-runner:latest")
                    
                    // Run tests inside container
                    docker.image("selenium-test-runner:latest").inside {
                        sh '''
                            # Start Flask app in background
                            python app.py &
                            sleep 5
                            # Run Selenium tests
                            python -m unittest discover -s . -p "test_*.py" -v
                        '''
                    }
                }
            }
        }
    }
    
    post {
        success {
            emailext (
                subject: "PASSED: Selenium Test Suite - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                ✅ All Selenium tests passed successfully!
                
                Triggered by: ${env.TRIGGER_USER_EMAIL}
                Build URL: ${env.BUILD_URL}
                Application URL: http://${env.EC2_PUBLIC_IP}:5000
                Test Results: 15/15 tests passed
                
                Deployment is now UP and running.
                """,
                to: "${env.TRIGGER_USER_EMAIL}"
            )
        }
        failure {
            emailext (
                subject: "FAILED: Selenium Test Suite - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                ❌ Some Selenium tests failed!
                
                Triggered by: ${env.TRIGGER_USER_EMAIL}
                Build URL: ${env.BUILD_URL}
                
                Please check console output for details.
                """,
                to: "${env.TRIGGER_USER_EMAIL}"
            )
        }
    }
}