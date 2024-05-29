# Implementing a Read Eval Print Loop for industrial Cobots.
This is the code for our bachelor project in Software engineering.

# Abstract
This project aims to address the problem of long feedback loops in the domain of programming industrial collaborative robots (CoBots). 
By developing a Read-Eval-Print Loop (REPL)for CoBots, this project explores the possibilities of shortening the feedback loop combined with reversibility to foster an interactive and exploratory setting for CoBot development. 
The project utilizes the Universal Robots UR5e as a test platform for which the REPL is implemented. 
Key challenges addressed include the implementation of reversibility through state restoration, fetching and displaying feedback from the robot and automatically recovering from certain errors.
The project successfully shortens the feedback loop by providing an interactive and exploratory programming environment through the REPL, illustrating the potential of the system to improve the development experience for CoBots. 
Additionally, the project showcases the feasibility of state logging for reversibility, demonstrating that it is a viable, but severely limited method. 
Future work will focus on improving feedback mechanisms, command cancellation, and exploring language understanding to further refine reversibility.

# Running the project
The project consists of a TypeScript frontend and a Python backend.
The backend runs in docker using the provided docker-compose file.
```shell
docker compose up -d
```
From the root of the project will start the backend and the Universal Robots simulator.
The frontend is run using node.js from the subdirectory `js_client`.
It can be started from the root using 
```shell
cd js_client
npm start
```