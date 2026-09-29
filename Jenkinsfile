// Define an empty map for storing remote SSH connection parameters
def remote = [:]

pipeline {

    agent any

    environment {
        user = credentials('agroadvisory_user')
        host = credentials('agroadvisory_host')
        name = credentials('agroadvisory_name')
        ssh_key = credentials('agroadvisory_key')
    }

    stages {
        stage('Ssh to connect 192.168.199.121 server') {
            steps {
                script {
                    // Set up remote SSH connection parameters
                    remote.allowAnyHosts = true
                    remote.identityFile = ssh_key
                    remote.user = user
                    remote.name = name
                    remote.host = host
                    
                }
            }
        }
        stage('Download latest release') {
            steps {
                script {
                    sshCommand remote: remote, command: """
                        cd /opt/nagroadvisory/back
                        sudo kill -9 \$(sudo netstat -nepal | grep 5000 | awk '{print \$9}' | awk -F '/' '{print \$1}')
                        git pull origin main
                    """
                }
            }
        }
        stage('Init Api') {
            steps {
                script {
                    sshCommand remote: remote, command: """
                        cd /opt/nagroadvisory/back/src
                        nohup python agroadvisory_api.py > log.txt 2>&1 &
                    """
                }
            }
        }
    }
    
    post {
        failure {
            script {
                echo 'fail'
            }
        }

        success {
            script {
                echo 'everything went very well!!'
            }
        }
    }
 
}
