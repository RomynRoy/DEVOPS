# TP DEVOPS Romyn ROY 2022

## TP part 01 - Docker

### 1 Database

docker network create app-network <br/>
Cela permet de créer un nouveau network dans lequel il y aura nos docker.

docker run --name some-postgres -e POSTGRES_PASSWORD=pwd -e POSTGRES_USER=usr -e POSTGRES_DB=db -d --network=app-network postgres //on crée la BDD sous postrgre

Why should we run the container with a flag -e to give the environment variables ? <br/>
Le -e permet de déclarer les variables d'environnement. On peut aussi utiliser un -env. Cela permet donc de passer les identifiants de connexion à la BDD.

docker run -d --link test:db --network=app-network -p 8080:8080 adminer //on utilise admirer pour se connecter à la bdd <br/>
Server	: test <br/>
Username : usr <br/>
Password : pwd <br/>
Database : bd

on crée un dossier : initdb où on place les script sql <br/>
on rajoute dans Dockerfile "COPY initdb/ /docker-entrypoint-initdb.d" avec  <br/>
docker build -t romyn/test . //docker rm test sert à supprimer test <br/>
docker run -d --network=app-network -p 8888:5000 --name test romyn/test <br/>
docker run -d --network=app-network -p 8888:5000 -v /my/own/datadir:/var/lib/postgresql/data --name test romyn/test : avec persistance <br/>

dockerfile : <br/>
FROM postgres:11.6-alpine #Image utilisée <br/>
ENV POSTGRES_DB=db \   #différentes variables d'env nécessaires pour la base postgres <br/>
POSTGRES_USER=usr \ <br/>
POSTGRES_PASSWORD=pwd 

COPY initdb/ /docker-entrypoint-initdb.d #permet de copier les script sql présents dans initdb pour qu'ils soient exécutés

### 2 Backend API :

datafile :  <br/>
FROM openjdk:11 <br/>
COPY Main.java /usr/src/app/ #On copie Main.java dans app <br/>
CMD cd /usr/src/app/ ; javac Main.java  #on build avec javac <br/>
CMD cd /usr/src/app/ ; java Main.java #puis on run

#attention le controller est un .java

docker build -t romyn/hello . <br/>
commande : docker run  -p 5000:8080 --name hello romyn/hello #pour tester on met le port 5000.

on rajoute dans le dockerfile : CMD mvn dependency:go-offline #pour qu'il ne télécharge pas toutes les dépendances à chaque fois ce qui prend du temps et , si on est sur 4g, coûte en terme de quantité de données téléchargés.

1-2 Why do we need a multistage build ? <br/>
On a besoin de multisage buid car le build et le run ne s'effectuent pas das la même image, respectivement, maven:3.6.3-jdk-11 et openjdk:11-jre. <br/>
1-2 And explain each steps of this dockerfile : <br/>
#Build <br/>
FROM maven:3.6.3-jdk-11 AS myapp-build  #définit l’image de base pour les instructions suivantes <br/>
ENV MYAPP_HOME /opt/myapp #env permet de déclarer les variables d'environnement <br/>
WORKDIR $MYAPP_HOME  #WORKDIR définit le répertoire de travail pour toutes les instructions qui suivent. Si le  répertoire n’existe pas, il sera créé. Ici il s'agit du dossier /opt/myapp définit par la variable MYAPP_HOME <br/>
COPY pom.xml . #L’instruction copie les nouveaux fichiers ou répertoires et les ajoute au système de fichiers du conteneur au niveau du chemin d’accès. Ici pom.xml est positionner à la racine du conteneur. <br/>
COPY src ./src  <br/>
RUN mvn package -DskipTests #cela va exécuter dans maven. <br/>
#Run <br/>
FROM openjdk:11-jre #initialise une nouvelle étape de génération <br/>
ENV MYAPP_HOME /opt/myapp <br/>
WORKDIR $MYAPP_HOME <br/>
COPY --from=myapp-build $MYAPP_HOME/target/*.jar $MYAPP_HOME/myapp.jar #récupère ce qui a été build précédemment et le place dans myapp.jar <br/>
ENTRYPOINT java -jar myapp.jar #programme par défault lorsque le container démarre <br/>

on run : docker run -d --network=app-network -p 8888:5000 --name some-postgres romyn/test // dans docker ps on voit que le port 5432 <br/>
Dans application.yml : on remplit  <br/>
- url: "jdbc:postgresql://some-postgres:5432/db" #position de la bdd <br/>
- username: usr <br/>
- password: pwd <br/>
docker build -t romyn/hello . <br/>
docker run  -p 8080:8080 --name hello --network=app-network romyn/hello //on pense à le metttre dans le même network que la bdd <br/>

### 3 Http server :

docker stats affiche :  <br/>
CONTAINER ID   NAME      CPU %     MEM USAGE / LIMIT     MEM %     NET I/O           BLOCK I/O   PIDS <br/>
4c58e1467abb   httpapp   0.02%     15.48MiB / 15.59GiB   0.10%     5.42kB / 1.29kB   0B / 0B     1

docker logs <br/>
 * Running on http://0.0.0.0:80/ (Press CTRL+C to quit) <br/>
172.17.0.1 - - [01/Feb/2022 10:51:44] "GET / HTTP/1.1" 200 -

recupérer la conf : aller dans le dossier ou l'on veut qu'elle soit copiée puis : docker run --rm httpd:2.4 cat /usr/local/apache2/conf/httpd.conf > my-httpd.conf

#### Dockerfile : <br/>
FROM httpd:2.4 <br/>
COPY ./index.html/ /usr/local/apache2/htdocs/ #copy l'index qui sert d'affichage <br/>
COPY my-httpd.conf /usr/local/apache2/conf/httpd.conf #copy la conf que l'on a préalablement récup dans le fichier conf

docker build -t romyn/http . <br/>
docker run -dit --name httpapp --network=app-network -p 80:80 romyn/http

#### Proxy :

Pour le proxy : dans my-httpd.conf <br/>
On décommente les lignes : mod_proxy_http et mod_proxy pour activer le proxy. <br/>
On ajoute  

ServerName localhost

<VirtualHost *:80> <br/>
ProxyPreserveHost On <br/>
ProxyPass / http://hello:8080/ <br/>
ProxyPassReverse / http://hello:8080/ #adresse de notre container <br/>
</VirtualHost>

docker run -dit --name httpapp --network=app-network -p 80:80 romyn/http

Why do we need a reverse proxy ? <br/>
On en a besoin pour protéger l'identité du serveur web.

### DOCKER COMPOSE :

1-3 Document docker-compose most important commands <br/>
Parmis les lignes du docker-compose fournies, 'depends_on' permet d'attendre la fin d'un container avant d'en exécuter un autre. 'build' doit avoir le chemin du dockerfile pour chaque container. 'network' tous les container sont dans le même network.

On modifie le docker compose <br/>
On change le nom des services du docker compose pour faire correspondre aux noms que l'on a mis dans le my-httpd.conf et dans le application.yml <br/>
On execute : docker-compose up --build

1-4 Document your docker-compose file (voir le docker-compose pour les cometaires)


Why is docker-compose so important ? <br/>
Docker Compose est un outil qui a été développé pour aider à définir et partager des applications multi-conteneurs. Avec Compose, nous pouvons créer un fichier YAML pour définir les services et avec une seule commande, nous pouvons tout faire tourner, c'est donc très important qu'il soit correct et fonctionnel.

1-5 Document your publication commands and published images in dockerhub <br/>
On peut maintenant publier les images que l'on a créées :

docker tag some-postgres romyn/my-bdd:1.0 <br/>
docker push my-bdd

Why do we put our images into an online repository ? <br/>
On met les images dans un repo online pour pouvoir les stocker quelque part. Ainsi les collègues travaillant sur le même projet pourront les utiliser.




## TP part 02 - CI/CD

GITHUB <br/>
On crée un key ssh : <br/>
ssh-keygen -t ed25519 -C romyn.roy@cpe.fr <br/>
eval "$(ssh-agent -s)" <br/>
ssh-add ~/.ssh/id_ed25519 <br/>
cat ~/.ssh/id_ed25519.pub <br/>
Puis on colle dans new key sur github

#On configure notre repo git : <br/>
git init DEVOPS <br/>
git config --global user.email romyn.roy@cpe.fr <br/>
git config --global user.username RomynRoy <br/>
cd DEVOPS <br/>
touch README.md <br/>
git add -A <br/>
git commit -m "Initial commit" <br/>
git status <br/>
git remote add origin https://github.com/RomynRoy/DEVOPS.git <br/>
git push --set-upstream origin master #demande <br/>
Problem de token : générer un token sur Github qui servira de mdp

On se met dans le repertoire qui contient le POM.xml et on lance 'mvn clean verify'. <br/>
'mvn clean' permet de supprimer les fichiers générés par les précédentes générations	 <br/>
'verify' permet d'exécuter des contrôles de validation et de qualité

2-1 What are testcontainers? <br/>
Testcontainers est une bibliothèque Java qui prend en charge les tests JUnit, fournissant des instances légères et jetables de bases de données. <br/>
Les testcontainers facilitent les types de tests suivants : <br/>
Tests d’intégration de la couche d’accès aux données <br/>
Tests d’intégration d’application <br/>
Testcontainers est dépandant de maven.

2-2 Document your Github Actions configurations (voir le main.yml) <br/>
Sur github, on va dans action et on crée un new Workflows. <br/>
On remplit le workflow avec un main.yml <br/>
On accède à la version de java de l'ordinateur avec : java --version

Secured variables, why ? <br/>
On securise les variables docker dans github. Cela permet de ne pas les mettre en public et donc à la vision de tous. <br/>
On crée donc un DOCKERHUB_TOKEN et un DOCKERHUB_USERNAME.

Le test du main dans le workflow a fonctionné. <br/>
![Photo_validation](https://github.com/RomynRoy/DEVOPS/tree/master/img/docker.png?raw=true)

Il faut maintenant rajouter  la partie build-and-push-docker-image. <br/>
On modifie les tag en rajoutant pour la datatbase : tags: ${{secrets.DOCKERHUB_USERNAME}}/some-postgres <br/>
pour le backend : tags: ${{secrets.DOCKERHUB_USERNAME}}/backend <br/>
pour le http :  tags: ${{secrets.DOCKERHUB_USERNAME}}/httpd <br/>
Ce sont les nom donnés dans le docker compose.

=> cela génère bien le image sur docker.

2-3 Document your quality gate configuration <br/>
On se connecte à sonar <br/>
on génère un token que l'on rentre dans github <br/>
sonar : on décoche dans analyse methode <br/>
On integre le code fournit dans le main du workflow et on rajoute les lignes d'environnement sinon il y a une erreur. <br/>
Dans le code fournit, on pense à changer le chemin du pom.xml, la Project Key et la Organization Key. <br/>
On va dans new code dans le quality gate et on coche Previous version.

![Photo_validation](https://github.com/RomynRoy/DEVOPS/tree/master/img/sonar_passed.png?raw=true)






## TP part 03 - Ansible <br/>
### 1 Intro

3-1 Document your inventory and base commands <br/>
chmod 400 id_rsa #pour securiser le fichier key <br/>
ssh -i ~/Bureau/DEVOPS/key_DEVOPS/id_rsa centos@romyn.roy.takima.cloud pour lancer le serveur ssh

Commandes : ansible all --list-hosts : cette commande va lister tous les hosts présents 

On crée les dossiers ansible et inventories et on place setup.yml dedans. <br/>
On rempit le fichier setup avec le chemin absolu de la clé <br/>
ansible all -i DEVOPS/TP_TD_3/ansible/inventories/setup.yml -m ping permet de ping le serveur <br/>
'all' : ansible exécute la commande sur tous les hôtes présents dans l'inventaire <br/>
'-m ping' : on utilise le module ping <br/>
'-i' : permet de spécifier un chemin d'inventaire différent qui est de base sur /etc/ansible/hosts

![Ping](https://github.com/RomynRoy/DEVOPS/tree/master/img/ping.png?raw=true)

ansible all -i inventories/setup.yml -m yum -a "name=httpd state=absent" --become : supprime httpd server
"--become" : super utilisateur
ansible all -i DEVOPS/TP_TD_3/ansible/inventories/setup.yml -m setup -a "filter=ansible_distribution*" <br/>
'-a' permet permet de fournir des informations suplémentaires à la commande '-m' <br/>
![Photo setup](https://github.com/RomynRoy/DEVOPS/tree/master/img/ping2.png?raw=true)


### 2 Playbooks

3-2 Document your playbook (voir commentaires du playbook) <br/>
ansible-playbook -i inventories/setup.yml playbook.yml #permet d'executer le playbook <br/>
et  ansible-playbook -i inventories/setup.yml playbook.yml --syntax-check <br/>
![Photo playbook](https://github.com/RomynRoy/DEVOPS/tree/master/img/playbook.png?raw=true)


1 role docker : ansible-galaxy init roles/docker <br/>
1 role network : ansible-galaxy init roles/network <br/>
1 role database : ansible-galaxy init roles/database <br/>
1 role app  :  ansible-galaxy init roles/app <br/>
1 role proxy : ansible-galaxy init roles/proxy

3-3 Document your docker_container tasks configuration.(voir les commentaires des tasks) <br/>
docker : comme le playbook execute les task, on peut deplacer l'ensemble des commandes qui se trouvaient en lui dans le main de la task docker <br/>
network : on crée le docker_network <br/>
database : on recupère l'image docker, on met dans le network et on passe les identifiants en variable d'environnement <br/>
app : on récupère l'image docker, on met dans le network, On pense a rajouter le lien vers la database dans l'app. <br/>
proxy :  on récupère l'image docker, on met dans le network, sur le port 80 

![Photo validation](https://github.com/RomynRoy/DEVOPS/tree/master/img/takima.png?raw=true)





## SURPRISE : 
il faut d'abord tester si le serveur marche avec : ssh -i ~/Bureau/DEVOPS/key_DEVOPS/id_rsa centos@romyn.roy.takima.cloud <br/>
Cela nous donne une commande à exécuter pour supprimer la clé ECDSA présent dans le répertoire .ssh/known_hosts (présente depuis la dèrnière fois que l'on  a généré le serveur): ssh-keygen -f "/fs03/share/users/romyn.roy/home/.ssh/known_hosts" -R "romyn.roy.takima.cloud" <br/>
On relance le playbook : ansible-playbook -i inventories/setup.yml playbook.yml
