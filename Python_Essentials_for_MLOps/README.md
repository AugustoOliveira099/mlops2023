# Python essencials for MLOps
Para que comecemos a desenvolver códigos de machine learning, algumas práticas práticas e tecnologias são essenciais. São elas: refatoração de código, principíos de código limpo, linting, lidar com exceções, logging, testes unitários e interface de linha de comando. Aqui estão desenvolvidos três projetos, que tiveram a finalidade de colocar em uso essas práticas.

### Projeto 1
O [projeto 1](Projeto_1/) faz uso de mineração de texto  partir de um título de filme passado como parâmetro, com o auxílio da biblioteca ``scikit-learn`` para isso. Compara avaliações de filmes de pessoas com o gosto parecido com o do usuçario que informou o título do filme e com avaliações de pessoas no geral para que sejam indicados, então, que o usuãrio do script poderá gostar.

### Projeto 2
[Neste projeto](Projeto_1/) é utilizado o [Apache Airflow](https://airflow.apache.org/) para fazer uma pipeline que é executada diariamente e faz download de novos episódios de podcast.

### Projeto 3
No [projeto 3](Projeto_1/) é introduzido machine learning com o algoritmo k-NN(k-Nearest Neighbors). Nele, ao executar o script, é possível prever, com uma certa acurácia, se uma pessoa tem doenças cardíacas.

## Requisitos e tecnologias
* Python 3.10.x
* Pacotes python:
  * tqdm
  * pandas
  * pytest
  * pylint
  * numpy
  * requests
  * argparse
  * scikit-learn
  * pytest-sugar
  * apache-airflow[pandas]
  * xmltodict
  * pendulum
  * seaborn
  * matplotlib
 
Você pode instalar todos os pacotes necessárias para executar todos os projetos com o seguinte comando, no diretório ``Python_Essentials_for_MLOps``:
```
pip install -r requirements.txt
```

Ou, caso você queira executar apenas um dos projetos e não quer dependências desnecessárias, basta executar o comando acima na pasta dos projetos (instruções mais detalhadas no ``README.md`` de cada projeto).

## Praticas a serem seguidas
O professor pediu que algumas práticas e tecnologias fossem utilizadas no projeto. É possível vê-las a seguir:
* Refatoração de código: Refatoração é o processo de reestruturar o código sem alterar seu comportamento externo. O objetivo é melhorar a qualidade interna do código, tornando-o mais legível, eficiente e fácil de manter. Isso pode incluir a reorganização de código, extração de funções, renomeação de variáveis e outras mudanças que não afetam o resultado final do programa;
* Princípios de código limpo: Código limpo, refere-se à prática de escrever código de forma clara e compreensível. Os princípios de código limpo, como DRY (Don't Repeat Yourself) e KISS (Keep It Simple, Stupid), enfatizam a importância de evitar repetições desnecessárias, manter a simplicidade e tornar o código fácil de entender;
* Linting:  É o processo de analisar o código em busca de possíveis erros, violações de estilo e más práticas. Ferramentas de linting, como pylint em Python, ajudam os desenvolvedores a manter um código consistente e identificar potenciais problemas antes mesmo da execução do programa;
* Tratamento de exceções: Tratamento de exceções é a prática de lidar com situações excepcionais que podem ocorrer durante a execução do programa. Isso é feito usando blocos ``try``, ``except`` e ``finally`` para capturar e tratar erros de maneira controlada, tornando o código mais robusto e facilitando a depuração;
* Testes unitários: São testes automatizados que verificam se partes específicas do código funcionam conforme esperado. Eles são essenciais para garantir que as unidades individuais de código (funções, métodos, classes) produzam os resultados corretos. A inclusão de testes unitários facilita a manutenção do código e as mudanças futuras;
* Command Line Interface (CLI) - Interface de Linha de Comando: Uma CLI é uma interface que permite aos usuários interagirem com um programa por meio de comandos inseridos na linha de comando. Implementar uma CLI em um projeto oferece uma maneira versátil e eficiente de executar diferentes funcionalidades e opções, tornando o projeto mais acessível para usuários e automatização;
* GitHub codespaces: É um ambiente de desenvolvimento configurável hospedado no GitHub. Ele permite que os desenvolvedores acessem e desenvolvam seus projetos diretamente no navegador, fornecendo um ambiente completo para codificação, testes e depuração.

## Referências
* [Repositório do professor Dr. Ivanovitch Silva](https://github.com/ivanovitchm/mlops
* [Build a Movie Recommendation System in Python](https://app.dataquest.io/c/93/m/99994/build-a-movie-recommendation-system-in-python/13/next-steps)
* [Build an Airflow Data Pipeline to Download Podcasts](https://app.dataquest.io/c/93/m/999911/build-an-airflow-data-pipeline-to-download-podcasts/6/conclusions-and-next-steps)
* [Guided Project: Predicting Heart Disease](https://app.dataquest.io/c/134/m/740/guided-project%3A-predicting-heart-disease/8/hyperparameter-tuning?path=23&slug=machine-learning-in-python-skill&version=1)

## Links
* [Certificado do curso do Dataquest](https://app.dataquest.io/view_cert/OVQ502HZ2I2Y8NVCE7R2)
* [Vídeo de explicação no Loom]()
