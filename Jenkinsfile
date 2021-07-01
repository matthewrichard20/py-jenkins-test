// pipeline{
//     agent any
//     stages {
//         stage('Docker Turn On'){
//             steps{
//                 sh 'sudo systemctl start docker'
//             }
//         }
//         stage('build'){
//             steps{
//                 sh 'sudo docker-compose up -d'
//             }
//         }
//     }
// }



// def dbVariables = [:]
// dbVariables.name = "Intern Instance 2"
// remote.host = "54.255.128.73"
// remote.allowAnyHosts = true
node {
    // withCredentials([string(credentialsId: 'dbName', variable: 'dbName'), string(credentialsId: 'snapRole', variable: 'IAMKey'),string(credentialsId: 'zebrax-cmk-sym-prod', variable: 'kmsKey')]) { //set SECRET with the credential content
        stage ("Git pull") {
            sh "git pull"
        
        }
        stage("Create Snap"){
            sh "cd py-jenkins-test && /Users/RichardMatthew/miniconda3/bin/python3 createSnap.py 'devops-rds-staging' 'arn:aws:iam::475194349913:role/zebrax-SnapshotDB-staging'"
            // sh "/Users/RichardMatthew/miniconda3/bin/python3 -c 'import pyjenkins; pyjenkins.createSnap(${dbName},${IAMKey})' "
        }
              
            
        
    // } 





//   withCredentials([usernamePassword(credentialsId: 'Matt-Github', passwordVariable: 'gitPassword', usernameVariable: 'gitUsername'), 
//                     sshUserPrivateKey(credentialsId: 'ec2-user', keyFileVariable: 'sshIdentity', passphraseVariable: '', usernameVariable: 'sshUsername')]) {
//       // def gitPass = gitPassword.toURL()
//       remote.user = sshUsername
//       remote.identityFile = sshIdentity

//       stage("SSH, Clean Up") {
//         sshCommand remote: remote, command: "cd /home/ec2-user && sudo rm -rf test"
//         }
//       stage("SSH, Pulling Last Commit") {
//         sshCommand remote: remote, command: "cd /home/ec2-user && mkdir test"
//         sshCommand remote: remote, command: "cd /home/ec2-user/test && sudo git clone https://$gitUsername:$gitPassword@github.com/matthewrichard20/test-git-jenkins.git"
        
//         }

//       stage("SSH, Docker Turn on") {
//         // sshCommand remote: remote, command: "cd /home/ec2-user && mkdir test"
//         sshCommand remote: remote, command: "sudo systemctl start docker"
//         }
//       stage("SSH, Docker Compose") {
//         // sshCommand remote: remote, command: "cd /home/ec2-user && mkdir test"
//         sshCommand remote: remote, command: "cd /home/ec2-user/test/test-git-jenkins && sudo docker-compose up -d"
//         }
//   }
}
