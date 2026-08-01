pipeline {
    // Keep in sync with the playwright== version in requirements.txt.
    agent {
        docker {
            image 'mcr.microsoft.com/playwright/python:v1.61.0-noble'
            args '-u root:root'   // needed to apt-install Node.js inside the container
        }
    }

    environment {
        ALLURE_RESULTS  = "${WORKSPACE}/allure-results"
        ALLURE_REPORT   = "${WORKSPACE}/allure-report"

        // ---- EDIT THESE FOR YOUR REPO ----
        GH_PAGES_REPO   = "git@github.com:ruby-leo/P2-HR-Management-Web-Automation-Using-Playwright-Pytest-BDD.git"
        GH_PAGES_BRANCH = "gh-pages"
        // Jenkins credential: SSH Username with private key, deploy key with write access
        GH_DEPLOY_KEY_ID = "github-deploy-key"
    }

    options {
        timestamps()
        disableConcurrentBuilds()
        ansiColor('xterm')
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Trust GitHub SSH host key') {
            steps {
                // Fresh container every run -> no known_hosts yet, so SSH git
                // operations to GitHub would fail host verification without this.
                sh '''
                    mkdir -p ~/.ssh
                    ssh-keyscan -H github.com >> ~/.ssh/known_hosts 2>/dev/null
                '''
            }
        }

        stage('Install Node.js (for Allure CLI)') {
            steps {
                sh '''
                    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
                    apt-get install -y nodejs
                    node --version
                    npm install -g allure
                    allure --version
                '''
            }
        }

        stage('Install Python dependencies') {
            steps {
                sh '''
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        // Browsers ship with the Playwright Docker image, so no separate install step.

        stage('Run tests') {
            steps {
                // Keep pytest's non-zero exit from aborting the pipeline, so the
                // Allure report still gets generated and published on failures.
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    sh '''
                        pytest
                    '''
                }
            }
            post {
                always {
                   allure allureVersion: '3',
                            includeProperties: false,
                            results: [[path: 'allure-results']]
                }
            }
        }

        stage('Fetch previous Allure history') {
            steps {
                sshagent(credentials: ["${GH_DEPLOY_KEY_ID}"]) {
                    sh '''
                        rm -rf gh-pages-tmp
                        git clone --depth 1 --branch ${GH_PAGES_BRANCH} ${GH_PAGES_REPO} gh-pages-tmp || \
                            echo "gh-pages branch not found yet (first run) - continuing without history"
                        if [ -d gh-pages-tmp/history ]; then
                            cp -r gh-pages-tmp/history allure-results/history
                        fi
                    '''
                }
            }
        }

        stage('Generate Allure report') {
            steps {
                // Uses the global Allure 3 CLI (npm install -g allure)
                sh '''
                    rm -rf ${ALLURE_REPORT}
                    allure generate ${ALLURE_RESULTS} -o ${ALLURE_REPORT}
                '''
                // Build status badge for the README (shields.io endpoint badge
                // reads this from gh-pages). Rides along with the report files
                // into gh-pages in the next stage.
                script {
                    switch (currentBuild.currentResult) {
                        case 'SUCCESS':
                            env.BADGE_MESSAGE = 'passing'
                            env.BADGE_COLOR   = 'brightgreen'
                            break
                        case 'UNSTABLE':
                            env.BADGE_MESSAGE = 'unstable'
                            env.BADGE_COLOR   = 'yellow'
                            break
                        default:
                            env.BADGE_MESSAGE = 'failing'
                            env.BADGE_COLOR   = 'red'
                    }
                }
                sh '''
                    cat > ${ALLURE_REPORT}/badge.json <<EOF
{"schemaVersion":1,"label":"build","message":"${BADGE_MESSAGE}","color":"${BADGE_COLOR}"}
EOF
                '''
            }
        }

        stage('Publish to GitHub Pages') {
            steps {
                sshagent(credentials: ["${GH_DEPLOY_KEY_ID}"]) {
                    sh '''
                        rm -rf gh-pages-tmp
                        git clone --depth 1 --branch ${GH_PAGES_BRANCH} ${GH_PAGES_REPO} gh-pages-tmp || {
                            mkdir gh-pages-tmp
                            cd gh-pages-tmp
                            git init
                            git checkout -b ${GH_PAGES_BRANCH}
                            git remote add origin ${GH_PAGES_REPO}
                            cd ..
                        }

                        rm -rf gh-pages-tmp/*
                        cp -r ${ALLURE_REPORT}/. gh-pages-tmp/

                        cd gh-pages-tmp
                        # Local identity only - required for the commit, not a real account.
                        git config user.email "ci@jenkins.com"
                        git config user.name "Jenkins CI"
                        git add -A
                        git commit -m "Allure report for build #${BUILD_NUMBER}" || echo "Nothing new to commit"
                        git push origin HEAD:${GH_PAGES_BRANCH}
                    '''
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'allure-report/**', allowEmptyArchive: true
        }
        cleanup {
            cleanWs()
        }
    }
}
