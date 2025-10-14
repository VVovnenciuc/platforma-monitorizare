Proiectul "Platforma monitorizare" contine doua servicii Docker:
    'monitoring' - care verifica starea sistemului la un anumit interval (default 5s) si inscrie informatia in fisierul system-state.log
    'backup' - care verifica o data la un anumit interval (default 5s) daca s-a modificat fisierul si ii face backup in directorul /backup

## Cerinte

- [Docker](https://docs.docker.com/get-docker/) (versiune recentă)
- [Docker Compose](https://docs.docker.com/compose/install/) (de preferat integrat în Docker)
    sudo apt install docker-compose
- (Opțional) [kubectl](https://kubernetes.io/docs/tasks/tools/) — pentru rulare în Kubernetes
- (Opțional) acces la un cluster Kubernetes (local: Minikube, Kind, sau remote)

## Configurare variabile de mediu

În docker-compose.yaml și manifestul Kubernetes, poți configura intervale și directoare prin variabilele de mediu:

| Variabilă        | Serviciu   | Descriere                                 | Exemplu        |
|------------------|------------|-------------------------------------------|----------------|
| `INTERVAL`       | monitoring | Intervalul de monitorizare (secunde)      | `5`            |
| `BACKUP_INTERVAL`| backup     | Intervalul de backup (secunde)            | `5`            |
| `BACKUP_DIR`     | backup     | Directorul unde se salvează backup-ul     | `/data/backup` |

## Volume partajate

Atât în Docker Compose, cât și în Kubernetes, serviciile folosesc un volum partajat numit shared-data montat pe /data, pentru a permite schimbul de date între containere.

## Instrucțiuni de pornire locală cu Docker Compose (rulati instructiunile din directorul radacina al proiectului)
1. Clonarea proiectului
    git clone https://github.com/VVovnenciuc/platforma-monitorizare.git
    cd platforma-monitorizare

2. Construirea și pornirea containerelor
    docker-compose -f docker/docker-compose.yaml up --build -d

3. Verificarea containerelor
    docker-compose -f docker/docker-compose.yaml ps

4. Vizualizarea log-urilor
    docker-compose -f docker/docker-compose.yaml logs -f
    docker-compose -f docker/docker-compose.yaml logs -f monitoring
    docker-compose -f docker/docker-compose.yaml logs -f backup

5. Oprirea containerelor
    docker-compose -f docker/docker-compose.yaml down
    Daca doriti sa stergeti si volumele:
    docker-compose -f docker/docker-compose.yaml down -v


## Construirea și publicarea imaginilor în Docker Hub

Pentru a folosi imaginile în Kubernetes sau în alte medii, este recomandat să le construiești și să le urci într-un registry public sau privat.

1. Autentificare în Docker Hub
    docker login

2. Construirea imaginilor
    docker-compose -f docker/docker-compose.yaml build

3. Etichetarea imaginilor 
    docker tag docker_monitoring dockerhubuser/monitoring_image:latest
    docker tag pdocker_backup dockerhubuser/backup_image:latest
    (înlocuiește dockerhubuser cu username-ul propriu de Docker Hub)

4. Publicarea imaginilor
    docker push dockerhubuser/monitoring_image:latest
    docker push dockerhubuser/backup_image:latest

## Pornirea aplicației în Kubernetes

1. Actualizează manifestul Kubernetes k8s/deployment.yaml cu numele imaginilor tale (din Docker Hub)
    image: dockerhubuser/monitoring_image:latest
    image: dockerhubuser/backup_image:latest

2. Aplică manifestul
    kubectl apply -f k8s/deployment.yaml

3. Verifică starea pod-urilor
    kubectl get pods

4. Pentru vizualizarea log-urilor pod-urilor
    kubectl logs <nume-pod> -c monitoring
    kubectl logs <nume-pod> -c backup


