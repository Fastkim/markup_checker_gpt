# MARKUP_CHECKER_GPT
Chat GPT api를 활용한 웹 마크업오류방지 지침 탐색 프로그램, AI코딩으로 개발(ChatGPT 사용)
<br>

# 왜 개발하였는가?
비영리기관 프로젝트에서 마크업오류방지 지침을 검사하던중 [W3C Markup Validator](https://validator.w3.org/) 마크업 오류 탐지 툴을 사용하여 봤는데 생각보다 정확도가 떨어지며 잘 찾아내지 못한다고 생각이 들었습니다.
하여 AI를 활용하여 코드를 분석하면 조금 더 효율적으로 업무수행이 가능할것이라고 생각하여 개발을 진행해보게 되었습니다.
<br>

# 어떻게 만들었나?
풀스텍 개발 교육프로그램을 2회수료하고 풀스텍 웹개발 프로젝트를 3~4개정도 완료한 경험이 있습니다. <br>이 경험을 기반으로 AI 도구(ChatGPT)를 활용하여 개발하였습니다.
문제정의와 검증은 제가하고 대부분의 코딩은 AI가 수행하였습니다. 

# 주의사항
- 오픈된 사이트, 보안적으로 허용된 사이트에만 해당프로그램을 사용해야함.
- API키는 한번만 노출되므로 개인공간에 저장되어야하며, 외부에 키가 노출되면 안됨.
- API키 설정으로 소프트웨어에 저장하면 시스템 내부 환경변수에 저장되는것이므로 API키를 변경하고 싶다면 새로 발급받은후 저장하면 새로운키로 덮어씌어짐
- GPT의 분석내용을 가지고 맹신하면 안되며 리포터가 대상페이지 개발자도구에서 더블체크가 필요함.

# 주요기능
- 마크업 검사가 필요한 웹페이지 링크를 입력하여 검사버튼을 클릭하며 AI가 답변해줍니다.
- ChatGPT 검색창형태에서는 링크를 제공할경우 AI가 직접적으로 해당링크 프론트코드에 접근하지못하지만, 해당 소프트웨어 내부에서 필터링한 코드들을 전달받어 해석하는것은 가능해요!
- 웹 프론트 코드 -> 마크업오류방지 탐지프로그램 -> GPT api -> GPT분석 -> 답변도출

# GPT api의 보안정책
- API 요청 데이터는 모델학습에 사용되지 않음
- API 요청 데이터는 공개 데이터로 전환되지 않음
- 그럼에도 핵심보안사항이 있는 내부링크는 검사요청에 부적합함.
- 오픈페이지, 오픈소스 기반의 웹 어플리케이션이 해당범주에 속함.
<br>

# 테스트 환경
- windows 11
- 비영리기관 대상페이지 : [링크](https://www.libertyinnorthkorea.or.kr/)

# ChatGPT api key 발급
1. [API 발급페이지 접속](https://platform.openai.com/api-keys)
2. 우측상단에 Create new secret key 버튼 실행
   <img width="1899" height="845" alt="image" src="https://github.com/user-attachments/assets/cfd125a7-6a98-4a9e-9c61-b12e1dac13d9" />
3. Owned by -> You, Name -> 키이름, Project -> Default project, Permissions -> ALL, api키 세부내용 작성 후 Create secrete key 버튼 실행
   <img width="1899" height="845" alt="image" src="https://github.com/user-attachments/assets/7b8846db-a071-4057-9986-896fc5bb2116" />
4. 생성된 빨간 박스안에 키를 별도의 개인공간에 Copy & Paste 하여 저장해놓기. <주의> 해당키는 외부에 노출되면 절대안됨.
<br>

# 프로그램 시작하기
1. [릴리즈 페이지](https://github.com/Fastkim/markup_checker_gpt/releases/tag/v1.0.0)에서 최신 버전 다운로드
2. 압축풀고 MarkupCherckerAI 실행
3. API 키 설정 버튼 실행 후 발급받은 API키를 넣고 저장하기 버튼 실행
   <img width="1370" height="749" alt="image" src="https://github.com/user-attachments/assets/30c402ca-2e44-4853-96fe-d9454a916e16" />
5. 검사할 대상페이지를 대상URL에 넣고 검사하기 버튼 실행
6. GPT가 분석해준 내용 확인하기
7. 내용을 지우고 싶다면 초기화버튼
   <img width="987" height="749" alt="image" src="https://github.com/user-attachments/assets/a18df655-d9d3-4d1c-a82b-88feaaccd828" />
