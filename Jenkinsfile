// Define an empty map for storing remote SSH connection parameters
def remote = [:]

pipeline {

    agent any

    environment {
        user = credentials('fertalizer_user')
        host = credentials('fertalizer_host')
        name = credentials('fertalizer_name')
        ssh_key = credentials('fertalizer_devops')
    }

    stages {
        stage('Ssh to connect Tesla server') {
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
                        cd /var/www/docs/webapi/
                        sudo kill -9 \$(sudo netstat -nepal | grep 5000 | awk '{print \$9}' | awk -F '/' '{print \$1}')
                        rm -fr api_backup_\$(date +"%Y%m%d")
                        mv api api_backup_\$(date +"%Y%m%d")
                        rm -fr releaseApi.zip
                        curl -LOk https://github.com/CIAT-DAPA/fertilizer_webapi/releases/latest/download/releaseApi.zip
                        unzip -o releaseApi.zip
                        rm -fr releaseApi.zip
                        mkdir api
                        mv src/webapi/* api
                        rm -fr src
                    """
                }
            }
        }
        stage('Init Api') {
            steps {
                script {
                    sshCommand remote: remote, command: """
                        cd /var/www/docs/webapi/
                        source env/bin/activate
                        export DEBUG=False
                        export WORKSPACE=fertilizer_et
                        export LAYER_NAME=:et_wheat_fertilizer_recommendation_normal
                        export SERVICE=WFS
                        export GEOSERVER_URL="https://geo.aclimate.org/geoserver/"
                        export FERTILIZER_RASTERS_DIR="./raster_files/cropped/"
                        export PORT=5000
                        export CONNECTION_DB=mongodb://localhost:27017/nextgen_db
                        export HOST=0.0.0.0
                        cd api/
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
