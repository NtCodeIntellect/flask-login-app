pipeline {
    agent any

    environment {
        IMAGE_NAME     = "flask-login-app"
        CONTAINER_NAME = "flask-app-container"
        APP_PORT       = "5000"
    }

    stages {

        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${IMAGE_NAME}:latest ."
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    // Run Flask + tests inside container; seed DB first via setUpClass
                    def result = sh(
                        script: """
                            docker run --rm \
                                --name test-runner \
                                -e APP_BASE_URL=http://127.0.0.1:5000 \
                                ${IMAGE_NAME}:latest \
                                bash -c "
                                    cd /app &&
                                    python app.py &
                                    sleep 5 &&
                                    python -m unittest tests -v 2>&1
                                "
                        """,
                        returnStatus: true
                    )
                    if (result != 0) {
                        error("Selenium tests FAILED")
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                // Stop old container if running, start fresh one
                sh "docker stop ${CONTAINER_NAME} || true"
                sh "docker rm   ${CONTAINER_NAME} || true"
                sh """
                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        -p ${APP_PORT}:5000 \
                        --restart unless-stopped \
                        ${IMAGE_NAME}:latest \
                        python app.py
                """
                echo "App deployed at http://\$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):${APP_PORT}"
            }
        }
    }

    post {
        always {
            script {
                // Get email of whoever made the push (this is what the assignment requires)
                env.PUSHER_EMAIL = sh(
                    script: "git log -1 --format='%ae'",
                    returnStdout: true
                ).trim()
                echo "Sending results to: ${env.PUSHER_EMAIL}"
            }
        }

        success {
            emailext(
                subject: "✅ PASSED: Selenium Tests — ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
All 15 Selenium test cases passed successfully.

Job:       ${env.JOB_NAME}
Build:     #${env.BUILD_NUMBER}
Pushed by: ${env.PUSHER_EMAIL}
Build URL: ${env.BUILD_URL}

The Flask application is now LIVE and running.
Visit: http://<your-ec2-ip>:5000
                """,
                to: "${env.PUSHER_EMAIL}"
            )
        }

        failure {
            emailext(
                subject: "❌ FAILED: Selenium Tests — ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
One or more Selenium test cases FAILED.

Job:       ${env.JOB_NAME}
Build:     #${env.BUILD_NUMBER}
Pushed by: ${env.PUSHER_EMAIL}
Build URL: ${env.BUILD_URL}

Please check the Jenkins console output for details.
                """,
                to: "${env.PUSHER_EMAIL}"
            )
        }
    }
}