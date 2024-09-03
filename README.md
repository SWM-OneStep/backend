### 초기 설정

필요한 파일을 당겨옵니다.

<pre><code>git clone [레포지토리_주소]</code></pre><br/>

git에서 필요한 파일을 당겨옵니다. 이때 main 브랜치도 좋으나 보통 develop 브랜치가 최근에 개발된 feature들까지 포함되어 있기 때문에, develop을 당기셔도 좋습니다.

<pre><code>git origin pull develop</code></pre><br/>

이때 .env 파일이 필요하고, 이 파일을 프로젝트의 루트 디렉토리에 위치시켜야 합니다.
.env 파일의 경우 팀 notion을 참고해주세요.

가상환경을 만들어줍니다.

<pre><code>python3 -m venv [가상환경명]</code></pre><br/>

가상환경을 실행시켜줍니다. mac의 경우 다음과 같이 입력합니다.

<pre><code>source [가상환경명]/bin/activate</code></pre><br/>

필요한 파일들을 설치해줍니다.

<pre><code>pip install -r requirements.txt</code></pre><br/>

mysql 서버가 실행 중인지 확인합니다. (mac 기준입니다.)
이렇게 입력했을 때 로그가 있다면 실행 중인 것입니다.

<pre><code>ps aux | grep mysqld</code></pre><br/>

.env 파일에 맞게 DB의 비밀번호를 설정합니다.
그리고 DB에 마이그레이션을 진행합니다.

<pre><code>python manage.py migrate</code></pre><br/>

마이그레이션이 성공적으로 진행되었다면, 서버를 실행합니다.

<pre><code>python manage.py runserver</code></pre><br/>

Ruff 적용 관련

<pre><code>"[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    },
    "editor.defaultFormatter": "charliermarsh.ruff"
  }</code></pre>

ruff 를 적용하기 위해 vscode 의 경우 cmd shift p 를 누른 후 settings.json 파일에 위의 코드를 추가해주세요.
혹시 api 설명과 같은 안내 주석에 E501 에러가 발생하면 # noqa : E501 을 넣어주세요.

To get started, set your OPENAI_API_KEY environment variable, or other required keys for the providers you selected.

Next, edit promptfooconfig.yaml.

Then run:

```
promptfoo eval
```

Afterwards, you can view the results by running `promptfoo view`
