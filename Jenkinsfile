@Library('cae-pipeline-helpers@master') _
pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'containers.cisco.com/atlas_noops/atlas-notification'
        REGISTRY_CREDENTIALS = 'atlas-ech-repo-credentials'
        APP_NAME = 'atlas_notification'
        APP_VERSION = "0.1.${env.BUILD_NUMBER}"
        TAG_VER = "v1.0.${env.BUILD_NUMBER}"
        RANDOM_SEED = "${new Random().nextInt(10000)}"
        dockerBuildImage = "golang:1.22.7"
        appPath = "/go/src/${appName}"
    }
    
    stages {

        stage('Source Code Analysis') {
            steps {
                runSonar(env.APP_NAME)
            }
        }

        stage('Check for Docker Image Updates') {
            steps {
                script {
                    def hasDockerfileChanged = {
                        echo "Checking for changes in Dockerfile and related files..."
                        def changes = []
                        changes.addAll(currentBuild.changeSets.collect { cs ->
                            cs.items.collect { item ->
                                item.affectedFiles.collect { file ->
                                    file.path
                                }
                            }
                        }.flatten())
                        
                        def hasChanges = changes.any { change ->
                            change =~ /[Dd]ockerfile$/ ||
                            change =~ /requirements\.txt$/
                        }
                        echo "Changes detected in build files: ${hasChanges}"
                        return hasChanges
                    }
                    
                    env.NEEDS_BUILD = hasDockerfileChanged().toString()
                    echo "Build required: ${env.NEEDS_BUILD}"
                }
            }
        }

        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    withCredentials([sshUserPrivateKey(credentialsId: 'cae_ci8_github_access', keyFileVariable: 'key', passphraseVariable: '', usernameVariable: 'eps-automation.gen_github')]) {
                        // Copy the private key into the Docker build process and configure SSH
                        sh """
                            mkdir -p $HOME/.ssh
                            cat ${key} > $HOME/.ssh/id_rsa
                            cp $HOME/.ssh/id_rsa ${WORKSPACE}/private_key
                            chmod 600 $HOME/.ssh/id_rsa

                            # Set up Git to use SSH for GitHub URLs
                            git config --global url."git@github.com:".insteadOf "https://github.com/"
                        """

                        // Build Docker image with the updated environment (with SSH key)
                        sh """
                            docker build --platform linux/amd64 \
                                -t ${DOCKER_IMAGE} \
                                --build-arg GITHUB_SSH_KEY_PATH=private_key .
                        """
                    }
            }
        }
        }
        stage('Push to Registry') {
            steps {
                script {
                    withCredentials([usernamePassword(
                        credentialsId: REGISTRY_CREDENTIALS,
                        usernameVariable: 'REGISTRY_USER',
                        passwordVariable: 'REGISTRY_PASSWORD'
                    )]) {
                        sh """
                            docker login containers.cisco.com \
                                -u ${REGISTRY_USER} \
                                -p ${REGISTRY_PASSWORD}
                        """
                        
                        sh "docker push ${DOCKER_IMAGE}"
                    }
                }
            }
        }
        stage('Pull Latest Image for Testing') {
            when {
                expression { env.NEEDS_BUILD == 'false' }
            }
            steps {
                script {
                    echo "No changes detected in build files. Pulling latest image from registry..."
                    withCredentials([usernamePassword(
                        credentialsId: REGISTRY_CREDENTIALS,
                        usernameVariable: 'REGISTRY_USER',
                        passwordVariable: 'REGISTRY_PASSWORD'
                    )]) {
                        sh """
                            docker login containers.cisco.com \
                                -u ${REGISTRY_USER} \
                                -p ${REGISTRY_PASSWORD}
                            docker pull ${DOCKER_IMAGE}
                        """
                    }
                    echo "Successfully pulled latest image"
                }
            }
        }
        stage('Scava Scan') {
            steps {
                script {
                   sastSecurityScan(webexTeamsId: "Y2lzY29zcGFyazovL3VzL1JPT00vZWNlZTllOTAtYjJjNC0xMWVmLTlkZTQtODU1NDkwYWUwNzg1")
                }
            }
        }
        
        stage('Tagging to main commit in git') {
            steps {
                script {
                    if (env.GIT_BRANCH.contains('main')) {
                        tagpolicy(env.TAG_VER)
                    } else {
                        println "Skipping tagging on branch ${env.GIT_BRANCH}"
                    }
                }
            }
        }
    }
    post {
        aborted {
            script {
                println "Build was interrupted"
                currentBuild.result = "ABORTED"
            }
        }
        failure {
            script {
                println "Caught an exception"
                currentBuild.result = "FAILURE"
            }
        }
        always {
            script {
                updateBitbucket(currentBuild.currentResult == "SUCCESS")
                emailBuildEnd([])
                sparkBuildEnd()
            }
        }
    }
}