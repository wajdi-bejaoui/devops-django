pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "wajdibejaoui/django-app"
        // DOCKER_TAG = "latest" // Or dynamically set with BUILD_NUMBER or GIT_COMMIT
        DOCKER_TAG = "${env.BUILD_NUMBER ?: 'latest'}" // Use BUILD_NUMBER if available, fallback to 'latest'

        MYSQL_DATABASE = 'django_db'
        MYSQL_USER = 'test'
        MYSQL_PASSWORD = 'test'
        MYSQL_ROOT_PASSWORD = 'test'
        DJANGO_SECRET_KEY = 'your-secret-key'


    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    // Checkout the code to make sure the docker-compose.yml file is available
                    checkout scm
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    // Build the Docker image
                    sh '''
                    echo "Building Docker Images with Docker Compose"
                    ls -l /usr/local/bin/docker-compose
                    /usr/local/bin/docker-compose --version
                    
                    
                    docker-compose build
                    '''
                }
            }
        }

         stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-pass', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    script {
                        sh '''
                        echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                        docker tag ${DOCKER_IMAGE}:latest ${DOCKER_IMAGE}:${DOCKER_TAG}
                        docker push ${DOCKER_IMAGE}:${DOCKER_TAG}
                        '''
                    }
                }
            }
        }



    }
}

// echo "Checking deployed resources"
//                     kubectl get pods
//                     kubectl get svc
//                     minikube service django-service --url 

// echo "Setting up Minikube context for kubectl"
//                      minikube start
                    // echo "Set Minikube's Docker environment to use local images"
                    // sh 'eval $(minikube docker-env)'

        // stage('Setup Minikube') {
        //     steps {
        //         script {
        //             sh '''
        //             echo "Starting Minikube"
        //             minikube start --driver=docker

        //             echo "Configuring Minikube Docker environment"
        //             eval $(minikube docker-env)

        //             echo "Minikube setup complete"
        //             '''
        //         }
        //     }
        // }

// pipeline {
//     agent any

//     environment {
//         // Store the kubeconfig file path as an environment variable
//         KUBECONFIG_PATH = "${env.WORKSPACE}/kubeconfig" // Use the workspace path
//     }

//     stages {
//         stage('Checkout Code') {
//             steps {
//                 checkout scm  // Checkout the repository containing your Terraform code
//             }
//         }

//         stage('Install Terraform') {
//             steps {
//                 script {
//                     // Ensure Terraform is installed
//                     sh 'terraform --version'
//                 }
//             }
//         }

//         stage('Fetch Kubeconfig') {
//             steps {
//                 script {
//                     // Create a directory for the kubeconfig file in the workspace
//                     sh 'mkdir -p ${WORKSPACE}/.kube'

//                     sh 'ls -ld /var/jenkins_home/workspace/Django_auth'


//                     // Use `withCredentials` to securely copy the kubeconfig file
//                     withCredentials([file(credentialsId: 'kubeconfig-file', variable: 'KUBECONFIG_FILE')]) {
//                         sh "cp ${KUBECONFIG_FILE} ${KUBECONFIG_PATH}" // Copy the kubeconfig securely
//                     }
//                 }
//             }
//         }

//         stage('Terraform Init') {
//             steps {
//                 script {
//                     // Initialize Terraform, ensuring you are in the correct directory
//                     dir('terraform') {
//                         sh 'terraform init -backend-config="path=${KUBECONFIG_PATH}"'
//                     }
//                 }
//             }
//         }

//         stage('Terraform Apply') {
//             steps {
//                 script {
//                     // Apply the Terraform configuration, ensuring you are in the correct directory
//                     dir('terraform') {
//                         sh 'terraform apply -auto-approve -var="kubeconfig_path=${KUBECONFIG_PATH}"'
//                     }
//                 }
//             }
//         }
//     }
// }


   


    //     stage('Deploy to Kubernetes') {
    //         steps {
    //             script {
    //                 sh '''
                     

                    
    //                 echo "Applying Kubernetes manifests"
    //                 sed -i "s|DOCKER_IMAGE|${DOCKER_IMAGE}|g" k8s/django_deploy.yml
    //                 sed -i "s|DOCKER_TAG|${DOCKER_TAG}|g" k8s/django_deploy.yml

    //                 echo "${DOCKER_IMAGE}:${DOCKER_TAG}"

    //                 kubectl apply -f k8s/configmap.yml
    //                 kubectl apply -f k8s/secret.yml
    //                 kubectl apply -f k8s/mysql_deploy.yml
    //                 kubectl apply -f k8s/django_deploy.yml


                    

    //                 '''
    //             }
    //         }
    //     }