#!groovy

// tag image, push to repo, remove local tagged image
def tag_image_as(tag) {
  script {
    docker.image("${DOCKER_IMAGE_URL}:${env.COMMIT_HASH}").push(tag)
    sh "docker rmi ${DOCKER_IMAGE_URL}:${tag} || true"
  }
}

def deploy(environment) {
  build job: 'Subtask_Openstack_Playbook',
    parameters: [
        [$class: 'StringParameterValue', name: 'INFRASTRUCTURE', value: 'secure'],
        [$class: 'StringParameterValue', name: 'INVENTORY', value: 'acceptance'],
        [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy-looplijsten-backend.yml'],
    ]
}

pipeline {
  agent any
  environment {
    APP = "looplijsten-api"
    DOCKER_IMAGE_URL = "${DOCKER_REGISTRY_NO_PROTOCOL}/fixxx/looplijsten"
  }

  stages {
    stage("Checkout") {
      steps {
        checkout scm
        script {
          env.COMMIT_HASH = sh(returnStdout: true, script: "git log -n 1 --pretty=format:'%h'").trim()
        }
      }
    }

    stage("Run tests") {
      steps {
        script {
          sh "docker-compose run --rm api python manage.py test"
          sh "docker-compose down --rmi local || true"
        }
      }
    }

    stage("Build docker image") {
      // We only build a docker image when we're not deploying to production,
      // to make make sure images deployed to production are deployed to
      // acceptance first.
      //
      // To deploy to production, tag an existing commit (that has already been
      // build) and push the tag.
      // (looplijsten actually wants to be able to hotfix to production,
      // without passing through acceptance)
      //when { not { buildingTag() } }

      steps {
        script {
          def image = docker.build("${DOCKER_IMAGE_URL}:${env.COMMIT_HASH}",
            "--no-cache " +
            "--shm-size 1G " +
            " ./app")
          image.push()
          tag_image_as("latest")
        }
      }
    }

    stage("Push and deploy acceptance image") {
      when {
        not { buildingTag() }
        branch 'master'
      }
      steps {
        tag_image_as("acceptance")
        deploy("acceptance")
      }
    }

    stage("Push and deploy production image") {
      when { buildingTag() }
      steps {
        tag_image_as("production")
        tag_image_as(env.TAG_NAME)
        deploy("production")
      }
    }

  }

  post {
    always {
      script {
        // delete original image built on the build server
        sh "docker rmi ${DOCKER_IMAGE_URL}:${env.COMMIT_HASH} || true"
      }
    }
  }
}
