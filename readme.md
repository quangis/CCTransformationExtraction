# Installation (Miniconda on Windows)

Download and extract the parser source code into some folder, for example to folder “*D:/qparserSrc*”.

Follow the below steps to setup the python environment.

1. Install the 64-Bit version of Miniconda from (https://repo.anaconda.com/miniconda/).

2. Open a new window of anaconda prompt. Create a new conda environment with a name “*D:/condaEnv/qparserSOA*”. This creates the conda environment inside the folder “*D:/condaEnv/qparserSOA*”.
```
conda create -p D:/condaEnv/qparserSOA python=3.9.7
```
3. Activate the new environment:
```
conda activate D:/condaEnv/qparserSOA
```
4. Move to the folder *qparserSOA*. Packages from github will be installed here. 
```
d:
cd D:\condaEnv\qparserSOA
```
5. Install *spacy* package from conda-forge
```
conda install -c conda-forge spacy
```
6. Install *spacy* trained pipeline. If the installation throws error, then try executing the command again.
```
python -m spacy download en_core_web_sm
```
7. Install other packages from conda-forge:
```
conda install -c conda-forge antlr4-python3-runtime=4.9.3 word2number pyzmq 
```
8. Optionally, it may be necessary to install the checklist package:
```
pip install checklist
```

# Test running the parser

1. In the anaconda prompt, make sure the “*D:/condaEnv/qparserSOA*” environment is activated.
2. Move to the folder “*D:/qparserSrc/test*”. Packages from github will be installed here. 
```
cd D:\qparserSrc\test
```
3. Execute the "*Test.py*" script:
```
python Test.py
```
4. The output of the script should look like below:
```
============================== TESTING retrieval dataset
============================== TESTING GeoAnQu dataset
============================== TESTING MS student dataset

Process finished with exit code 0
```

# Running the parser as a service (SOA)

1. Make sure “*D:/condaEnv/qparserSOA*” is activated in the anaconda prompt.
2. In the anaconda prompt, navigate to the folder “*D:/qparserSrc*”. This folder should contain the batch file “*runAsyncWorker.bat*”.
3. Run the batch file by typing
```
runAsyncWorker.bat
```
4. If the server starts correctly then you should see a message like below:
```
error loading _jsonnet (this is expected on Windows), treating config.json as plain json
INFO: Bound broker frontend to 'tcp://127.0.0.1:5570' in method 'QparserBroker.run'
INFO: Bound broker backend to an inter-process port 'inproc://backend' in method 'QparserBroker.run'
INFO: Started worker '0' on a inter-process socket 'inproc://backend' in method 'QparserWorker.run'
INFO: Started worker '1' on a inter-process socket 'inproc://backend' in method 'QparserWorker.run'
INFO: Started worker '2' on a inter-process socket 'inproc://backend' in method 'QparserWorker.run'
INFO: Started the poller in the broker in method 'QparserBroker.run'
```

To stop the server press the combo “*Ctrl+C*” in the anaconda prompt. Enter ‘*Y*’ when asked “*Terminate batch job (Y/N)?*”.

Two parameters can be changed in the batch file “*runAsyncWorker.bat*”. “*FRONT_PORT*” sets to which port server should be bound to. “*INST_COUNT*” sets the number of concurrent worker threads. In other words, it is the number of requests the server can handle simultaneously without requests blocking each other. For example, if “*INST_COUNT*” is set to 1 then only one request is processed at the time, and all other incoming requests are queued until the current request is handled.  “*INST_COUNT*” can be any integer number above 0.

## Running the test client for the parser service

1. Make sure the parser server is up and running.
2. Open a new Anaconda prompt window.
3. In the newly opened prompt window, activate the environment “*D:/condaEnv/qparserSOA*”.
4. Navigate to the folder “*D:/qparserSrc*”.
5. Execute the "*asyncClient.py*" script:
6. The expected output should look like below:
```
Starting the client
Setting the client poller
Sending a request to the remove service
Waiting for a reply ...
Client received a reply: {"question": "What is the shortest path through my workplace, a gym and a supermarket 
from my home in Amsterdam", "placename": ["Amsterdam"], "replaceQ": "What is shortest path through workplace , 
gym and supermarket from home extent", "network": ["shortest path"], "object": ["supermarket", "workplace", 
"home", "gym"], "ner_Question": "what is network0 through object1 , object3 and object0 from object2 extent", 
"parseTreeStr": "(start what is (measure (networkC network 0) through (destination (objectC object 1) (objectC 
object 3) and (objectC object 0)) from (origin (objectC object 2))) (extent extent))", "cctrans": {"types": 
[{"type": "object", "id": "0", "keyword": "home", "cct": "R(Obj,_)"}, {"type": "object", "id": "1", "keyword": 
"supermarket", "cct": "R(Obj,_)"}, {"type": "object", "id": "2", "keyword": "gym", "cct": "R(Obj,_)"}, {"type": 
"object", "id": "3", "keyword": "workplace", "cct": "R(Obj,_)"}, {"type": "network", "id": "4", "keyword": 
"shortest path", "cct": "R(Obj*Obj,Reg)"}, {"type": "object", "id": "5", "keyword": "Amsterdam", "cct": 
"R(Obj,_)"}], "extent": ["5"], "transformations": [{"before": ["1", "2", "3", "0"], "after": ["4"]}]}, "valid": 
"T", "query": {"afterId": "4", "after": "R(Obj*Obj,Reg)", "before": ["R(Obj,_)", "R(Obj,_)", "R(Obj,_)", 
"R(Obj,_)"]}, "queryEx": {"after": {"id": "4", "cct": "R(Obj*Obj,Reg)"}, "before": [{"after": {"id": "1", "cct":
 "R(Obj,_)"}}, {"after": {"id": "2", "cct": "R(Obj,_)"}}, {"after": {"id": "3", "cct": "R(Obj,_)"}}, {"after": 
 {"id": "0", "cct": "R(Obj,_)"}}]}}

Process finished with exit code 0
```

# Usage
```Python
from QuestionParser import *
from TypesToQueryConverter import *

qBlock = '{"question": "What is the  shortest path through my workplace,' + \
            ' a gym and a supermarket from my home in Amsterdam","placename":' + \
            '["Amsterdam"],"replaceQ": "What is the  shortest path through my' + \
            ' workplace, a gym and a supermarket from my home extent"}'

# identify types and transformations steps
parser = QuestionParser()
qParsed = parser.parseQuestionBlock(qBlock)
# annotate types with cct expressions and generate a query
cctAnnotator = TQConverter()
cctAnnotator.cctToExpandedQuery(qParsed, True, True)
```

# Structure

Check the `Grammar` folder for more details of the functional grammar in `GeoAnQu.g4`.
Check the `Dictionary` folder for the concept dictionary.


## License
[CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/)
