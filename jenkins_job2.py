import requests
import time
from requests.auth import HTTPBasicAuth
import sys
import argparse


def trigger_jenkins_job(urlrepo, entorno, user, token, rama):
    jenkins_url = f"http://mat.qualitat.solucions.gencat.cat/jenkins/job/functional-test-jenkinsfile/buildWithParameters?repositorio={urlrepo}&entorno={entorno}&rama={rama}"
    response = requests.post(jenkins_url, auth=HTTPBasicAuth(user, token))

    if response.status_code == 201:
        print("El trabajo de Jenkins se ha iniciado correctamente.")
    else:
        print(f"Error al iniciar el trabajo de Jenkins: {response.status_code}")
        sys.exit(1)

    time.sleep(10)
    
    job_url = "http://mat.qualitat.solucions.gencat.cat/jenkins/job/functional-test-jenkinsfile/lastBuild/api/json"
    response = requests.get(job_url, auth=HTTPBasicAuth(user, token))
    data = response.json()
    build_number = data.get('id')  # Obtener el número de compilación
    
    print(f"build number: {build_number}")
    
    while True:
        job_url = f"http://mat.qualitat.solucions.gencat.cat/jenkins/job/functional-test-jenkinsfile/{build_number}/api/json"
        response = requests.get(job_url, auth=HTTPBasicAuth(user, token))
        if response.status_code != 200:
            print(f"Error al obtener el estado del trabajo: {response.status_code}")
            sys.exit(1)       
        
        status = response.json().get('result')
        
        if status is None:
            time.sleep(10)
            continue

        print(f"El trabajo de Jenkins ha terminado con el estado: {status}")

        # Escribir el log completo de Jenkins en un archivo
        log_url = f"http://mat.qualitat.solucions.gencat.cat/jenkins/job/functional-test-jenkinsfile/{build_number}/consoleText"
        response = requests.get(log_url, auth=HTTPBasicAuth(user, token))
        if response.status_code == 200:
            print(response.text)
            with open(f'jenkins_log_{build_number}.txt', 'w') as f:
                f.write(response.text)
            print(f"El log de Jenkins se ha escrito en el archivo 'jenkins_log_{build_number}.txt'.")
        else:
            print(f"Error al obtener el log de Jenkins: {response.status_code}")

        if status == 'SUCCESS':
            sys.exit(0)
        else:
            sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trigger Jenkins Job")
    parser.add_argument('urlrepo', type=str, help='URL of the repository')
    parser.add_argument('entorno', type=str, help='Environment name')
    parser.add_argument('user', type=str, help='Username for authentication')
    parser.add_argument('token', type=str, help='Token for authentication')
    parser.add_argument('rama', type=str, help='Branch name')

    args = parser.parse_args()

    trigger_jenkins_job(args.urlrepo, args.entorno, args.user, args.token, args.rama)
