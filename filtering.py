
import os
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationKGMemory

os.environ["OPENAI_API_KEY"]

def Filtering(user_input):
    llm = OpenAI(temperature=0.9)

    template = """You are the helpful agent that creates the filter that matches the user's input. You define the filters and choices in Typescript, and present the selected filters and choices as results using the given filter data.
    - An OR operation is performed between the choices.
    - output should be only one URL. do not add any description about output.
    - The filter name and choices given to the data in typescript file should be written exactly as it is.

    ```TypeScript
    interface Filter (
      name: string;
      choices: ( [code: string]: string );
    );

    //data
    const filters: Filter[] = [
      (
        "name": "카테고리",
        "choices": (
          "001": "상의",
          "002": "아우터",
          "003": "바지",
          "004": "가방",
          "005": "신발",
          "006": "시계",
          "007": "모자",
          "008": "양말/레그웨어",
          "009": "선글라스/안경테"
          "011": "액세서리",
          "012": "디지털/테크",
          "015": "뷰티",
          "017": "스포츠/용품",
	        "015": "스니커즈",
          "020": "원피스",
	        "022": "스커트",
          "025": "주얼리",
          "026": "속옷",
	        "054": "여성가방",
          "058": "리빙"
        )
      ),
      (
        "name" : "상의",
        "choices" : (
          "001001" : "반소매티셔츠",
          "001002" : "셔츠/블라우스",
          "001003" : "피케/카라티셔츠",
          "001004" : "후드티셔츠",
          "001005" : "맨투맨/스웨트셔츠",
          "001006" : "니트/스웨터",
          "001008" : "기타상의",
          "001010" : "긴소매티셔츠",
          "001011" : "민소매티셔츠"
        )
      ),
      (
        "name" : "아우터",
        "choices" : (
          "002001" : "블루종/MA-1",
          "002002" : "레더/라이더스재킷",
          "002003" : "슈트/블레이저재킷",
          "002004" : "스타디움재킷",
          "002005" : "나일론/코치재킷",
          "002006" : "겨울싱글코트",
          "002007" : "환절기코트",
          "002008" : "겨울기타코트",
        )
      ),
      (
        "name" : "바지",
        "choices" : (
          "003002" : "데님팬츠",
          "003004" : "트레이닝/조거팬츠",
          "003005" : "레깅스",
          "003006" : "기타바지",
          "003007" : "코튼팬츠",
          "003008" : "슈트팬츠/슬랙스",
          "003009" : "숏팬츠",
          "003010" : "점프슈트/오버올",
          "003011" : "스포츠하의",
        )
      ),
      (
        "name" : "가방",
        "choices" : (
          "004001": "백팩",
          "004002": "메신저/크로스백",
          "004003": "숄더백",
          "004005": "클러치백",
          "004006": "보스턴/드럼/더플백",
          "004007": "웨이스트백",
          "004008": "브리프케이스",
          "004009": "캐리어",
          "004012": "가방소품",
          "004013": "파우치백",
          "004014": "에코백",
        )
      ),
      (
        "name": "정렬",
        "choices": (
          "create_date": "최신순",
          "hit": "조회순",
          "total_comment_count": "많은댓글순",
          "comment_date": "최신댓글순"
        )
      )
    ]```

    If there is something not including in Filter, you have to add "includeKeywords=" and the component like this.


    Example 1)
    user input:키치 찾아줘
    URL:https://www.musinsa.com/search/musinsa/magazine?q=키치

    Example 2)
    user input:연예인이 착용한 가방 보여줘
    URL:https://www.musinsa.com/search/musinsa/magazine?q=연예인착용&category1DepthCode=054&selectedFilters=여성가방%3Acategory1DepthCode&category1DepthName=여성+가방&openFilterLayout=N

    Example 3)
    user input:레트로한 신발 찾아줘
    URL:https://www.musinsa.com/search/musinsa/magazine?q=레트로&category1DepthCode=005&selectedFilters=신발%3Acategory1DepthCode&category1DepthName=신발&openFilterLayout=N

    Example 4)
    user input:요즘 트렌디한 상의 찾아줘
    URL:https://www.musinsa.com/search/musinsa/magazine?q=트렌디&category1DepthCode=001&selectedFilters=상의%3A001%3Acategory1DepthCode&category1DepthName=상의&openFilterLayout=N

    Example 5)
    user input:힙한 옷 최신댓글순으로 보여줘
    URL:https://www.musinsa.com/search/musinsa/magazine?q=힙한&sortCode=comment_date

    Example 6)
    user input:유행하는 긴소매 보여줘
    URL:https://www.musinsa.com/search/musinsa/magazine?q=유행하는&category1DepthCode=001&category2DepthCodes=001010&selectedFilters=상의%3A001%3Acategory1DepthCode%7C긴소매%3A001010%3Acategory2DepthCodes&category1DepthName=상의&openFilterLayout=N

    Example 7)
    user input:여름에 입을만한 반소매티셔츠나 블라우스 보여줘
    URL:https://www.musinsa.com/search/musinsa/magazine?q=여름에+입을만한&category1DepthCode=001&category2DepthCodes=001001%2C001002&selectedFilters=상의%3A001%3Acategory1DepthCode%7C반소매+티셔츠%3A001001%3Acategory2DepthCodes%7C셔츠%2F블라우스%3A001002%3Acategory2DepthCodes&category1DepthName=상의&openFilterLayout=N


    Example 8)
    user input:y2k 패션 추천해줘
    URL:https://www.musinsa.com/search/musinsa/magazine?q=키치

    Example 9)
    user input:요즘 트렌디한 옷이 뭐야?
    URL:https://www.musinsa.com/search/musinsa/magazine?q=트렌디

    Example 10)
    user input:뉴진스가 입을 것 같은 옷 알려줘
    URL:https://www.musinsa.com/search/musinsa/magazine?q=뉴진스

    Example 11)
    user input:바캉스 갈 때 입을 옷 추천해봐
    URL:https://www.musinsa.com/search/musinsa/magazine?q=바캉스

    Example 12)
    user input:일본 여행 갈 때 뭐입을지 정해줘
    URL:https://www.musinsa.com/search/musinsa/magazine?q=일본+여행

    Relavant Information: 
    {history}

    Conversation:
    user input: {input}
    URL:"""

    prompt = PromptTemplate(
        input_variables=["history", "input"], 
        template=template
    )

    memory = ConversationKGMemory(llm=llm)
    memory.save_context({"input":"요즘 인기있는 스타일 보여줘"}, {"output":"https://www.musinsa.com/search/musinsa/magazine?q=인기있는"})
    memory.save_context({"input":"연예인이 착용한 옷들 보여줘"}, {"output":"https://www.musinsa.com/search/musinsa/magazine?q=연예인착용"})

    conversation_with_kg = ConversationChain(
        llm=llm,
        verbose=True,
        prompt=prompt,
        memory=memory
    )

    return conversation_with_kg.predict(input=user_input)