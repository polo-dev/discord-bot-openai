# Initialiser le bot

## Environnement

Dupliquer le fichier .env.dist en .env
Ajouter vos tokens discord et token openapi

## Construire l'image Docker :

```
docker-compose build && docker-compose up -d
```

## Commandes bot discord 

* /chat 
    * Utilise l'api de complétion d'openAI
    * Options:
        * message: Prompt
        * systemprompt: Remplace le système prompt par défaut (optionel)
        * model: C'est le model à utiliser (ex: "gpt-4o")
        * maxtokens: Nombre de tokens maximum

* /generate :
    * Génère une image à l'aide d'un prompt 
    * Options:
        * todo

