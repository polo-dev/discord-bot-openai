Construire l'image Docker :

bash
Copier le code
docker build -t discord-bot .

docker run --rm --name discord-bot-container -v $(pwd):/app -d discord-bot
