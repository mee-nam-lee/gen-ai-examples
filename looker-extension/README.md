# Looker - Extention

이 코드는 Generative AI을 이용한 Looker Extension Exampple 이다.
여기서 사용한 코드는 [looker-explore-assistant](https://github.com/LukaFontanilla/looker-explore-assistant/)에서 많은 부분을 참고했다. 특히 Looker App (UI) 쪽 부분은 거의 유사하지만 다음 부분을 수정하였다.

* 기존 looker-explore-assistant와 다른 점
   * 기존 코드는 Model과 Explore를 입력으로 받아서 처리했기 때문에, 하나의 Model, Explore만 사용할 수 있는 형태였음.
   * 환경 변수에서 참조한 Model, Explore를 이용하여 Fields들을 Looker에서 조회하고 Backend의 Cloud Functions에 보내어서 입력된 Fields를 바탕으로 few shot LLM을 수행하여 질의에 해당되는 Field들만 리턴하는 형태.
   * 여기서는 다수의 모델, Explore를 사용할 수 있도록 하기 위해 question만 Cloud Functions의 input으로 보내고, Cloud Functions에서 Embedding 기반의 유사도 검색을 하여 Question에 적합한 Model을 찾아내고 이를 바탕을 LLM을 통해 Explore에 Query를 생성하는 형태로 변경하였다.

* looker-app
  * Looker Extension으로 question을 입력받아 Cloud Functions를 호출한다.

* cloud-function
  * question을 input으로 받아서 LLM을 통해 Looker의 Model Name, Explore Name, Query ID를 리턴한다.
  * 전제 조건 : 유사도 검색을 위해 Looker Model이 사전 Embedding되어 Embedding Vector에 저장되어 있어야 한다. (이 예제이셔는 BigQuery를 Embedding Vector DB로 사용하였다)

* Cloud Fuctions Deploy
```
gcloud functions deploy explore-assistant-endpoint-prod --region=${REGION} --runtime=python310 --env-vars-file .env.yaml --trigger-http
```



