pipeline {
    // Pin the exact Playwright version to match requirements.txt so browsers on the
    // agent always match what pip installs. Update this tag whenever there is a bump for
    // playwright== in requirements.txt.
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
        // Jenkins credential ID of an SSH deploy key with write access to the repo above
        // (Manage Jenkins -> Credentials -> add "SSH Username with private key")
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

        stage('Install Node.js (for Allure CLI)') {
            steps {
                sh '''
                    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
                    apt-get install -y nodejs
                    node --version
                '''
            }
        }

        stage('Install Python dependencies') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        // Browsers are already present in the mcr.microsoft.com/playwright/python image,
        // so there's no separate "playwright install" stage needed.

        stage('Fetch previous Allure history') {
            // Copies the history/ folder from the last published report so the new
            // report keeps trend/retry graphs instead of resetting every build.
            steps {
                sh '''
                    rm -rf gh-pages-tmp
                    git clone --depth 1 --branch ${GH_PAGES_BRANCH} ${GH_PAGES_REPO} gh-pages-tmp || \
                        echo "gh-pages branch not found yet (first run) - continuing without history"
                    mkdir -p allure-results
                    if [ -d gh-pages-tmp/history ]; then
                        cp -r gh-pages-tmp/history allure-results/history
                    fi
                '''
            }
        }

        stage('Run tests') {
            steps {
                sh '''
                    . .venv/bin/activate
                    pytest
                '''
            }
            // Don't fail the whole pipeline immediately on test failures - we still
            // want the Allure report generated and published so failures are visible.
            post {
                always {
                    script {
                        currentBuild.result = currentBuild.result ?: 'SUCCESS'
                    }
                }
            }
        }

        stage('Generate Allure report') {
            steps {
                sh '''
                    npm install allure
                    npx allure generate ${ALLURE_RESULTS} -o ${ALLURE_REPORT} --clean
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
                        git config user.email "ci@yourdomain.com"
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