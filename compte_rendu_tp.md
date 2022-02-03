docker network create app-network

docker run --name some-postgres -e POSTGRES_PASSWORD=pwd -e POSTGRES_USER=usr -e POSTGRES_DB=db -d --network=app-network postgres //on crée la BDD sous postrgre

docker run -d --link test:db --network=app-network -p 8080:8080 adminer //on utilise admirer pour s'y connecter
Server	: test
Username : usr
Password : pwd
Database : bd

on crée un dossier : initdb où on place les script sql
on rajoute dans Dockerfile "COPY initdb/ /docker-entrypoint-initdb.d" avec 
docker build -t romyn/test . //docker rm test
docker run -d --network=app-network -p 8888:5000 --name test romyn/test
docker run -d --network=app-network -p 8888:5000 -v /my/own/datadir:/var/lib/postgresql/data --name test romyn/test : avec persistance


2 Hello word :

datafile : 
FROM openjdk:11
# TODO: Add the compiled java (aka bytecode, aka .class)
# TODO: Run the Java with: “java Main” command.
COPY Main.java /usr/src/app/ 
CMD cd /usr/src/app/ ; javac Main.java  #on build avec javac
CMD cd /usr/src/app/ ; java Main.java #puis on run

#attention le controller un un .java

docker build -t romyn/hello .
commande : docker run  -p 5000:8080 --name hello romyn/hello #pour tester on met le port 5000 mais à terme, ce sera le port 

on rajoute dans le dockerfile : CMD mvn dependency:go-offline pour qu'il ne télécharge pas toutes les dépendances


on run : docker run -d --network=app-network -p 8888:5000 --name some-postgres romyn/test // dans docker ps on voit que le port 5432
Dans application.yml : on remplit 
- url: "jdbc:postgresql://some-postgres:5432/db"
- username: usr
- password: pwd
docker build -t romyn/hello .
docker run  -p 8080:8080 --name hello --network=app-network romyn/hello //on pense à le metttre dans le même network que la bdd
3 HTTP :
docker stats affiche : 
CONTAINER ID   NAME      CPU %     MEM USAGE / LIMIT     MEM %     NET I/O           BLOCK I/O   PIDS
4c58e1467abb   httpapp   0.02%     15.48MiB / 15.59GiB   0.10%     5.42kB / 1.29kB   0B / 0B     1



docker logs
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
172.17.0.1 - - [01/Feb/2022 10:51:44] "GET / HTTP/1.1" 200 -

recupérer la conf : aller dans le dossier ou l'on veut qu'elle soit copié puis : docker run --rm httpd:2.4 cat /usr/local/apache2/conf/httpd.conf > my-httpd.conf

Dockerfile :
FROM httpd:2.4
COPY ./index.html/ /usr/local/apache2/htdocs/ #copy l'index qui sert d'affichage
COPY my-httpd.conf /usr/local/apache2/conf/httpd.conf #copy la conf que l'on a préalablement récup dans le fichier conf

docker build -t romyn/http .
docker run -dit --name httpapp --network=app-network -p 80:80 romyn/http


Pour le poxy : dans my-httpd.conf
On décommente les lignes : mod_proxy_http et mod_proxy.
On ajoute  

ServerName localhost

<VirtualHost *:80>
ProxyPreserveHost On
ProxyPass / http://hello:8080/
ProxyPassReverse / http://hello:8080/ #adresse de notre container
</VirtualHost>

docker run -dit --name httpapp --network=app-network -p 80:80 romyn/http

DOCKER COMPOSE :


On modifie le docker compose
On change le nom des services du docker compose pour faire correspondre au noms que l'on a mis dans le my-httpd.conf et dans le application.yml
On execute : docker-compose up --build

docker push
On met les images dans un repo online pour pouvoir les stocker quelque part. Ainsi les collègues travaillant sur le même projet pourront les utiliser.





GITHUB
On crée un key ssh :
ssh-keygen -t ed25519 -C romyn.roy@cpe.fr
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub
Puis on colle dans new key sur github

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

Sur github, on va dans action et on crée un new Workflows.
On remplit le workflow avec un main
On accede à la version de java avec : java --version


On securise les variables docker dans github. Cela permet de ne pas les mettre en public et donc à la vision de tous.
On crée donc un DOCKERHUB_TOKEN et un DOCKERHUB_USERNAME.

Le test du main dans le workflow à fonctionner.
![Photo_validation](https://github.com/RomynRoy/DEVOPS/tree/master/img/docker.png.png?raw=true)

Il faut maintenant rajouter  la partie build-and-push-docker-image.
On modifie les tag en rajoutant pour la datatbase : tags: ${{secrets.DOCKERHUB_USERNAME}}/some-postgres
pour le backend : tags: ${{secrets.DOCKERHUB_USERNAME}}/backend
pour le http :  tags: ${{secrets.DOCKERHUB_USERNAME}}/httpd 
Ce sont les nom donnés dans le docker compose.

=> cela génère bien le image sur docker.

On se connecte à sonar
on génère un token que l'on rentre dans github
sonar : on decoche dans analyse methode
On integre le code fournit dans le main du workflow et on rajoute les lignes d'environnement sinon il y a une erreur.
Dans le code fournit, on pense à changer le chemin du pom.xml, la Project Key et la Organization Key.
On va dans new code dans le quality gate et on coche Previous version.

![Photo_validation](https://github.com/RomynRoy/DEVOPS/tree/master/img/sonar_passed.png?raw=true)

ANSIBLE :

chmod 400 id_rsa #pour securiser le fichier key
ssh -i ~/Bureau/DEVOPS/key_DEVOPS/id_rsa centos@romyn.roy.takima.cloud

On crée les dossier ansible et inventories et on place setup.yml dedans.
On rempit le fichier setup avec le chemin absolu de la clé
ansible all -i DEVOPS/TP_TD_3/ansible/inventories/setup.yml -m ping

![Ping](https://github.com/RomynRoy/DEVOPS/tree/master/img/ping.png?raw=true)

ansible all -i DEVOPS/TP_TD_3/ansible/inventories/setup.yml -m setup -a "filter=ansible_distribution*"

![Photo setup](https://github.com/RomynRoy/DEVOPS/tree/master/img/ping2.png?raw=true)

ansible-playbook -i inventories/setup.yml playbook.yml
et  ansible-playbook -i inventories/setup.yml playbook.yml --syntax-check
![Photo playbook](https://github.com/RomynRoy/DEVOPS/tree/master/img/playbook.png?raw=true)


1 role docker : ansible-galaxy init roles/docker
1 role network : ansible-galaxy init roles/network
1 role database : ansible-galaxy init roles/database
1 role app  :  ansible-galaxy init roles/app
1 role proxy : ansible-galaxy init roles/proxy

docker : comme le playbook execute les task, on peut deplacer l'ensemble des commandes qu ise trouvaient en lui dans le main de la task docker
network : on crée le docker_network
database : on recupère l'image docker, on met dans le network et on passe les identifiants en variable d'environnement
app : on récupère l'image docker, on met dans le network, On pense a rajouter le lien vers la database dans l'app.
proxy :  on récupère l'image docker, on met dans le network, sur le port 80 

![Photo validation](https://github.com/RomynRoy/DEVOPS/tree/master/img/takima.png?raw=true)