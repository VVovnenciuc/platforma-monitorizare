# Platforma de Monitorizare

Acest proiect conține două servicii care colaborează pentru a monitoriza și salva starea sistemului:

- **monitoring** — verifică starea sistemului la un interval definit și scrie rezultatul în `system-state.log`
- **backup** — verifică modificările din fișierul de log și salvează backup-uri în `/backup`

## Cerințe

- [Docker](https://docs.docker.com/get-docker/) (versiune recentă)
- [Docker Compose](https://docs.docker.com/compose/install/)
- Python 3 și pip
- [kubectl](https://kubernetes.io/docs/tasks/tools/) — pentru rulare în Kubernetes
- Un cluster Kubernetes local (ex: Minikube) sau remote (opțional)

## Configurare

### Variabile de mediu

Poți personaliza comportamentul serviciilor prin variabile de mediu, atât în Docker Compose, cât și în Kubernetes:

| Variabilă        | Serviciu   | Descriere                                 | Exemplu        |
|------------------|------------|-------------------------------------------|----------------|
| `INTERVAL`       | monitoring | Intervalul de monitorizare (secunde)      | `5`            |
| `BACKUP_INTERVAL`| backup     | Intervalul de backup (secunde)            | `5`            |
| `BACKUP_DIR`     | backup     | Directorul unde se salvează backup-ul     | `/data/backup` |

Valorile implicite sunt deja definite în Docker Compose, deci nu e obligatoriu să le setezi.

### Volume partajate

Ambele servicii folosesc un volum partajat montat în `/data`, pentru a permite schimbul de fișiere (`system-state.log`) între containere.


## Rulare locală cu Docker Compose


1. Clonarea proiectului
    git clone https://github.com/VVovnenciuc/platforma-monitorizare.git
    cd platforma-monitorizare

Execută toate comenzile de mai jos din directorul **rădăcină al proiectului**

2. Construirea și pornirea containerelor
    docker compose -f docker/docker-compose.yaml up --build -d

3. Verificarea containere si loguri:
    docker compose -f docker/docker-compose.yaml ps
    docker compose -f docker/docker-compose.yaml logs -f
    docker compose -f docker/docker-compose.yaml logs -f monitoring
    docker compose -f docker/docker-compose.yaml logs -f backup

4. Oprirea containerelor
    docker compose -f docker/docker-compose.yaml down          # fără volume
    docker compose -f docker/docker-compose.yaml down -v       # cu volume


## Construirea și publicarea imaginilor în Docker Hub

1. Autentificare în Docker Hub
    docker login

2. Construirea imaginilor
    docker compose -f docker/docker-compose.yaml build

3. Etichetarea imaginilor 
    docker tag monitoring_image:latest dockerhubuser/monitoring_image:latest
    docker tag backup_image:latest dockerhubuser/backup_image:latest

    !!! Înlocuiește dockerhubuser cu numele tău Docker Hub. 

4. Publicarea imaginilor
    docker push dockerhubuser/monitoring_image:latest
    docker push dockerhubuser/backup_image:latest

## Rularea în Kubernetes

> Asigură-te că imaginile sunt publicate în Docker Hub sau accesibile de către cluster

1. Actualizează manifestul Kubernetes k8s/02-deployment.yaml cu numele imaginilor tale (din Docker Hub)
    image: dockerhubuser/monitoring_image:latest
    image: dockerhubuser/backup_image:latest

2. Porneste minikube:
    minikube start

3. Aplică toate manifestele
    kubectl apply -f k8s/

4. Verifică resurse:
    kubectl get all -n monitoring
    kubectl get ns
    kubectl get hpa -n monitoring
    kubectl get pods -n monitoring
    kubectl get svc -n monitoring

5. Testează accesul la nginx:
    kubectl port-forward svc/nginx-service 8080:80 -n monitoring
    # apoi deschide http://localhost:8080

  Sau fara port-forward:
    http://<minikube-ip>:30080
    (minikube ip  - pentru a afla ip)

6. Verificare loguri containere:
    kubectl logs <nume-pod> -c monitoring -n monitoring
    kubectl logs <nume-pod> -c backup -n monitoring
    kubectl logs <nume-pod> -c nginx -n monitoring

    !!! Înlocuiește <nume-pod> cu numele podului. Pentru a afla numele podurilor executa:
    kubectl get pods -n monitoring

7. Sterge toate resursele:
    kubectl delete -f k8s/

## Rulare cu Ansible

1. Instalare Docker pe host-uri:
    ansible-playbook -i ansible/inventory.ini ansible/playbooks/install_docker.yaml

2. Deploy platforma:
    ansible-playbook -i ansible/inventory.ini ansible/playbooks/deploy_platform.yaml

3. Verificare containere și loguri prin Ansible:
    ansible all -i ansible/inventory.ini -m shell -a "docker ps"
    ansible all -i ansible/inventory.ini -m shell -a "docker logs monitoring_service"
    ansible all -i ansible/inventory.ini -m shell -a "docker logs backup_service"






## Recomandari verificare cod:
Script bash:
    bash -n scripts/monitoring.sh   # pentru a testa dacă scriptul are erori de sintaxă
    bash -x scripts/monitoring.sh   # pentru debug, util dacă scriptul se blochează sau nu produce rezultatul așteptat
    
Script python:
    python3 -m py_compile scripts/backup.py
    pylint scripts/backup.py
    flake8 scripts/backup.py   # găsește probleme stil/bug-uri
    black scripts/backup.py    # reformatează automat codul
    flake8 scripts/backup.py   # verifică din nou eventualele probleme rămase
    python3 scripts/backup.py --dry-run

Verificarea fisierelor yaml pentru erori (yamllint) si bune practici Ansible (ansible-lint):
    yamllint docker/docker-compose.yaml
    yamllint ansible/playbooks/deploy_platform.yaml
    yamllint ansible/playbooks/install_docker.yaml
    ansible-lint ansible/playbooks/deploy_platform.yaml
    ansible-lint ansible/playbooks/install_docker.yaml

Dry run fără a porni containerele complet:
    docker compose -f docker/docker-compose.yaml up --no-start