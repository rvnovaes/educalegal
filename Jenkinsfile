pipeline {
   agent any
   stages {
       stage('update_code') {
           steps {
               git (
                   credentialsId: '75810dd9-c7b3-4b29-991d-f8527ddb4f21',
                   url: 'https://github.com/silexsistemas/educalegal.git'
                   )
            }
       }
       stage('update_venv') {
           steps {
               dir('jenkins_scripts/'){
                   sh './update_venv.sh'
               }
           }
       }
       stage('run_tests') {
           steps {
               catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    dir('jenkins_scripts/'){
                        sh './test_educa_legal.sh'
                    }
               }
           }
        }
   }
   post {
        always  {
            emailext (
                to: "sistemas@educalegal.com.br",
                subject: "Result: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                body: """<p>Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]':</p>
                <p>Check console output at &QUOT;<a href='${env.BUILD_URL}'>${env.JOB_NAME} [${env.BUILD_NUMBER}]</a>&QUOT;</p>""",
                attachLog: true
            )
        }
   }
}
