TP part 01 - Docker

1 Database

docker network create app-network
Cela permet de créer un nouveau network dans lequel il y aura nos docker.

docker run --name some-postgres -e POSTGRES_PASSWORD=pwd -e POSTGRES_USER=usr -e POSTGRES_DB=db -d --network=app-network postgres //on crée la BDD sous postrgre

Why should we run the container with a flag -e to give the environment variables ?
Le -e permet de déclarer les variables d'environnement. On peut aussi utiliser un -env. 

docker run -d --link test:db --network=app-network -p 8080:8080 adminer //on utilise admirer pour se connecter à la bdd
Server	: test
Username : usr
Password : pwd
Database : bd

on crée un dossier : initdb où on place les script sql
on rajoute dans Dockerfile "COPY initdb/ /docker-entrypoint-initdb.d" avec 
docker build -t romyn/test . //docker rm test sert à supprimer test
docker run -d --network=app-network -p 8888:5000 --name test romyn/test
docker run -d --network=app-network -p 8888:5000 -v /my/own/datadir:/var/lib/postgresql/data --name test romyn/test : avec persistance

dockerfile :
FROM postgres:11.6-alpine #Image utilisée
ENV POSTGRES_DB=db \   #différentes variables d'env nécessaires pour la base postgres
POSTGRES_USER=usr \
POSTGRES_PASSWORD=pwd

COPY initdb/ /docker-entrypoint-initdb.d #permet de copier les script sql présents dans initdb pour qu'ils soient exécutés

2 Backend API :

datafile : 
FROM openjdk:11
COPY Main.java /usr/src/app/ #On copy Main.java dans app
CMD cd /usr/src/app/ ; javac Main.java  #on build avec javac
CMD cd /usr/src/app/ ; java Main.java #puis on run

#attention le controller est un .java

docker build -t romyn/hello .
commande : docker run  -p 5000:8080 --name hello romyn/hello #pour tester on met le port 5000.

on rajoute dans le dockerfile : CMD mvn dependency:go-offline #pour qu'il ne télécharge pas toutes les dépendances à chaque fois ce qui prend du temps et , si on est sur 4g, coûte en terme de quantité de données téléchargés.

1-2 Why do we need a multistage build ? 
On a besoin de multisage buid car le build et le run ne s'effectuent pas das la même image, respectivement, maven:3.6.3-jdk-11 et openjdk:11-jre.
1-2 And explain each steps of this dockerfile :
#Build
FROM maven:3.6.3-jdk-11 AS myapp-build  #définit l’image de base pour les instructions suivantes
ENV MYAPP_HOME /opt/myapp #env permet de déclarer les variables d'environnement
WORKDIR $MYAPP_HOME  #WORKDIR définit le répertoire de travail pour toutes les instructions qui suivent. Si le  répertoire n’existe pas, il sera créé. Ici il s'agit du dossier /opt/myapp définit par la variable MYAPP_HOME
COPY pom.xml . #L’instruction copie les nouveaux fichiers ou répertoires et les ajoute au système de fichiers du conteneur au niveau du chemin d’accès. Ici pom.xml est positionner à la racine du conteneur.
COPY src ./src 
RUN mvn package -DskipTests #cela va exécuter dans maven.
#Run
FROM openjdk:11-jre #initialise une nouvelle étape de génération
ENV MYAPP_HOME /opt/myapp
WORKDIR $MYAPP_HOME
COPY --from=myapp-build $MYAPP_HOME/target/*.jar $MYAPP_HOME/myapp.jar #récupère ce qui a été build précédemment et le place dans myapp.jar
ENTRYPOINT java -jar myapp.jar #programme par défault lorsque le container démarre

on run : docker run -d --network=app-network -p 8888:5000 --name some-postgres romyn/test // dans docker ps on voit que le port 5432
Dans application.yml : on remplit 
- url: "jdbc:postgresql://some-postgres:5432/db" #position de la bdd
- username: usr
- password: pwd
docker build -t romyn/hello .
docker run  -p 8080:8080 --name hello --network=app-network romyn/hello //on pense à le metttre dans le même network que la bdd

3 Http server :

docker stats affiche : 
CONTAINER ID   NAME      CPU %     MEM USAGE / LIMIT     MEM %     NET I/O           BLOCK I/O   PIDS
4c58e1467abb   httpapp   0.02%     15.48MiB / 15.59GiB   0.10%     5.42kB / 1.29kB   0B / 0B     1

docker logs
 * Running on http://0.0.0.0:80/ (Press CTRL+C to quit)
172.17.0.1 - - [01/Feb/2022 10:51:44] "GET / HTTP/1.1" 200 -

recupérer la conf : aller dans le dossier ou l'on veut qu'elle soit copiée puis : docker run --rm httpd:2.4 cat /usr/local/apache2/conf/httpd.conf > my-httpd.conf

Dockerfile :
FROM httpd:2.4
COPY ./index.html/ /usr/local/apache2/htdocs/ #copy l'index qui sert d'affichage
COPY my-httpd.conf /usr/local/apache2/conf/httpd.conf #copy la conf que l'on a préalablement récup dans le fichier conf

docker build -t romyn/http .
docker run -dit --name httpapp --network=app-network -p 80:80 romyn/http

Proxy :

Pour le proxy : dans my-httpd.conf
On décommente les lignes : mod_proxy_http et mod_proxy pour activer le proxy.
On ajoute  

ServerName localhost

<VirtualHost *:80>
ProxyPreserveHost On
ProxyPass / http://hello:8080/
ProxyPassReverse / http://hello:8080/ #adresse de notre container
</VirtualHost>

docker run -dit --name httpapp --network=app-network -p 80:80 romyn/http

Why do we need a reverse proxy ?
On en a besoin pour protéger l'identité du serveur web.

DOCKER COMPOSE :

1-3 Document docker-compose most important commands
Parmis les lignes du docker-compose fournies, 'depends_on' permet d'attendre la fin d'un container avant d'en exécuter un autre. 'build' doit avoir le chemin du dockerfile pour chaque container. 'network' tous les container sont dans le même network.

On modifie le docker compose
On change le nom des services du docker compose pour faire correspondre aux noms que l'on a mis dans le my-httpd.conf et dans le application.yml
On execute : docker-compose up --build

1-4 Document your docker-compose file (voir le docker-compose pour les cometaires)


Why is docker-compose so important ?
Docker Compose est un outil qui a été développé pour aider à définir et partager des applications multi-conteneurs. Avec Compose, nous pouvons créer un fichier YAML pour définir les services et avec une seule commande, nous pouvons tout faire tourner, c'est donc très important qu'il soit correct et fonctionnel.

1-5 Document your publication commands and published images in dockerhub
On peut maintenant publier les images que l'on a créés :

docker tag some-postgres romyn/my-bdd:1.0
docker push my-bdd

Why do we put our images into an online repository ?
On met les images dans un repo online pour pouvoir les stocker quelque part. Ainsi les collègues travaillant sur le même projet pourront les utiliser.




TP part 02 - CI/CD

GITHUB
On crée un key ssh :
ssh-keygen -t ed25519 -C romyn.roy@cpe.fr
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub
Puis on colle dans new key sur github

#On configure notre repo git :
git init DEVOPS
git config --global user.email romyn.roy@cpe.fr
git config --global user.username RomynRoy
cd DEVOPS
touch README.md
git add -A
git commit -m "Initial commit"
git status
git remote add origin https://github.com/RomynRoy/DEVOPS.git
git push --set-upstream origin master #demande
Problem de token : générer un token sur Github qui servira de mdp

On se met dans le repertoire qui contient le POM.xml et on lance 'mvn clean verify'.
'mvn clean' permet de supprimer les fichiers générés par les précédentes générations	
'verify' permet d'exécuter des contrôles de validation et de qualité

2-1 What are testcontainers?
Testcontainers est une bibliothèque Java qui prend en charge les tests JUnit, fournissant des instances légères et jetables de bases de données.
Les testcontainers facilitent les types de tests suivants :
Tests d’intégration de la couche d’accès aux données
Tests d’intégration d’application
Testcontainers est dépandant de maven.

2-2 Document your Github Actions configurations (voir le main.yml)
Sur github, on va dans action et on crée un new Workflows.
On remplit le workflow avec un main.yml
On accède à la version de java de l'ordinateur avec : java --version

Secured variables, why ?
On securise les variables docker dans github. Cela permet de ne pas les mettre en public et donc à la vision de tous.
On crée donc un DOCKERHUB_TOKEN et un DOCKERHUB_USERNAME.

Le test du main dans le workflow a fonctionné.
![Photo_validation](https://github.com/RomynRoy/DEVOPS/tree/master/img/docker.png?raw=true)

Il faut maintenant rajouter  la partie build-and-push-docker-image.
On modifie les tag en rajoutant pour la datatbase : tags: ${{secrets.DOCKERHUB_USERNAME}}/some-postgres
pour le backend : tags: ${{secrets.DOCKERHUB_USERNAME}}/backend
pour le http :  tags: ${{secrets.DOCKERHUB_USERNAME}}/httpd 
Ce sont les nom donnés dans le docker compose.

=> cela génère bien le image sur docker.

2-3 Document your quality gate configuration
On se connecte à sonar
on génère un token que l'on rentre dans github
sonar : on décoche dans analyse methode
On integre le code fournit dans le main du workflow et on rajoute les lignes d'environnement sinon il y a une erreur.
Dans le code fournit, on pense à changer le chemin du pom.xml, la Project Key et la Organization Key.
On va dans new code dans le quality gate et on coche Previous version.

![Photo_validation](https://github.com/RomynRoy/DEVOPS/tree/master/img/sonar_passed.png?raw=true)






TP part 03 - Ansible
1 Intro

3-1 Document your inventory and base commands
chmod 400 id_rsa #pour securiser le fichier key
ssh -i ~/Bureau/DEVOPS/key_DEVOPS/id_rsa centos@romyn.roy.takima.cloud pour lancer le serveur ssh

On crée les dossiers ansible et inventories et on place setup.yml dedans.
On rempit le fichier setup avec le chemin absolu de la clé
ansible all -i DEVOPS/TP_TD_3/ansible/inventories/setup.yml -m ping permet de ping le serveur
'all' : ansible exécute la commande sur tous les hôtes présents dans l'inventaire
'-m ping' : on utilise le module ping
'-i' : permet de spécifier un chemin d'inventaire différent qui est de base sur /etc/ansible/hosts

![Ping](https://github.com/RomynRoy/DEVOPS/tree/master/img/ping.png?raw=true)

ansible all -i DEVOPS/TP_TD_3/ansible/inventories/setup.yml -m setup -a "filter=ansible_distribution*"
'-a' permet permet de fournir des informations suplémentaires à la commande '-m'
![Photo setup](https://github.com/RomynRoy/DEVOPS/tree/master/img/ping2.png?raw=true)


2 Playbooks

3-2 Document your playbook (voir commentaires du playbook)
ansible-playbook -i inventories/setup.yml playbook.yml #permet d'executer le playbook
et  ansible-playbook -i inventories/setup.yml playbook.yml --syntax-check
![Photo playbook](https://github.com/RomynRoy/DEVOPS/tree/master/img/playbook.png?raw=true)


1 role docker : ansible-galaxy init roles/docker
1 role network : ansible-galaxy init roles/network
1 role database : ansible-galaxy init roles/database
1 role app  :  ansible-galaxy init roles/app
1 role proxy : ansible-galaxy init roles/proxy

3-3 Document your docker_container tasks configuration.(voir les commentaires des tasks)
docker : comme le playbook execute les task, on peut deplacer l'ensemble des commandes qui se trouvaient en lui dans le main de la task docker
network : on crée le docker_network
database : on recupère l'image docker, on met dans le network et on passe les identifiants en variable d'environnement
app : on récupère l'image docker, on met dans le network, On pense a rajouter le lien vers la database dans l'app.
proxy :  on récupère l'image docker, on met dans le network, sur le port 80 

![Photo validation](https://github.com/RomynRoy/DEVOPS/tree/master/img/takima.png?raw=true)





SURPRISE : 
il faut d'abord tester si le serveur marche avec : ssh -i ~/Bureau/DEVOPS/key_DEVOPS/id_rsa centos@romyn.roy.takima.cloud
Cela nous donne une commande à exécuter pour supprimer la clé ECDSA présent dans le répertoire .ssh/known_hosts (présente depuis la dèrnière fois que l'on  a généré le serveur): ssh-keygen -f "/fs03/share/users/romyn.roy/home/.ssh/known_hosts" -R "romyn.roy.takima.cloud"
On relance le playbook : ansible-playbook -i inventories/setup.yml playbook.yml
