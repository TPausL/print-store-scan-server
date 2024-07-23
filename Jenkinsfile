@Library("teckdigital") _
def appName = "print-store-scan-server"

pipeline {
   agent {
    kubernetes {
        inheritFrom "kaniko-template"
    }
  }
    
    stages {
        stage('Build and Tag Image') {
            steps {
                container('kaniko') {
                    script {
                        buildDockerImage(additionalImageTags: ["latest"])
                    }
                }
            }
        }
    }
}
